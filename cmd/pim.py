import argparse
import time
from bs4 import BeautifulSoup

import configparser
import paramiko.ssh_exception
import requests
import paramiko
import urllib3

import auth.auth as auth
from auth.auth_exception import AuthError
import app.ai_app as app
from app.ai_app_exception import AiAppError
import partition.activation as activation
import partition.partition as partition
from partition.partition_exception import PartitionError
from pim_exception import PimError
import network.virtual_network as virtual_network
from network.network_exception import NetworkError
import utils.string_util as util
import utils.common as common
import storage.storage as storage
import storage.vopt_storage as vopt
import storage.virtual_storage as vstorage
from storage.storage_exception import StorageError


from scp import SCPClient

def initialize():
    config_file = "config.ini"
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

def get_ssh_client():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    return client

def copy_iso_and_create_disk(config, cookies):
    scp_port = 22
    client = get_ssh_client()

    host_ip = util.get_vios_address(config)
    username = util.get_vios_username(config)
    password = util.get_vios_password(config)
    bootstrap_iso = util.get_bootstrap_iso(config)
    cloud_init_iso = util.get_cloud_init_iso(config)
    src_path = util.get_iso_source_path(config)
    remote_path=util.get_iso_target_path(config)

    client.connect(host_ip, scp_port, username, password)
    scp = SCPClient(client.get_transport())
    scp.put(src_path+cloud_init_iso ,remote_path=remote_path)
    logger.info("Cloud init ISO file copy success!!")
    scp.put(src_path+bootstrap_iso, remote_path=remote_path)
    logger.info("Bootstrap ISO file copy success!!")

    # create virtual optical disk
    bootstrap_disk_name = util.get_vopt_bootstrap_name(config)
    cloud_init_disk_name = util.get_vopt_cloud_init_name(config)

    command1 = f"ioscli mkvopt -name {bootstrap_disk_name} -file {remote_path}/{bootstrap_iso} -ro"
    command2 = f"ioscli mkvopt -name {cloud_init_disk_name} -file {remote_path}/{cloud_init_iso} -ro"

    logger.info("command1 %s", command1)
    logger.info("command2 %s", command2)
    stdin, stdout, stderr = client.exec_command(command1, get_pty=True)
    if stdout.channel.recv_exit_status() != 0:
        logger.error("command1 execution failed %s", command1)
        logger.error(stderr.readlines())
        raise paramiko.SSHException

    stdin, stdout, stderr = client.exec_command(command2, get_pty=True)
    if stdout.channel.recv_exit_status() != 0:
        logger.error("command2 execution failed %s", command2)
        logger.error(stderr.readlines())
        raise paramiko.SSHException

    logger.info("Load vopt to VIOS successful")
    client.close()

def monitor_iso_installation(config, cookies):
    ip = util.get_ip_address(config)
    username = "pim"
    password = util.get_ssh_password(config)
    command = "sudo journalctl -u getcontainer.service -f 2>&1 | awk '{print} /Installation complete/ {print \"Match found: \" $0; exit 0}'"

    for i in range(10):
        scp_port = 22
        client = get_ssh_client()
        try:
            client.connect(ip, scp_port, username, password)
        except (paramiko.BadHostKeyException, paramiko.AuthenticationException,
        paramiko.SSHException, paramiko.ssh_exception.NoValidConnectionsError) as e:
            if i == 9:
                logger.error("failed to establish SSH connection to partition after 10 retries")
                raise paramiko.SSHException
            logger.info("SSH to partition failed, retrying..")
            time.sleep(30)
    logger.info("SSH connection to partition is successful")

    stdin, stdout, stderr = client.exec_command(command, get_pty=True)
    while True:
        out = stdout.readline()
        logger.info(out)
        if stdout.channel.exit_status_ready():
            if stdout.channel.recv_exit_status() == 0:
                logger.info("Received ISO Installation complete message")
                break
            else:
                logger.error("Failed to get ISO installation complete message. Please look at the errors if appear on the console and take appropriate resolution!!")
                raise PimError("Failed to get ISO installation complete message")
    client.close()
    return

def get_system_uuid(config, cookies):
    uri = "/rest/api/uom/ManagedSystem/quick/All"
    url = "https://" + util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config)}
    logger.debug(f"headers {headers}")
    response = requests.get(url, headers=headers, cookies=cookies, verify=False)
    if response.status_code != 200:
        logger.error("Failed to get system UUID ", response.text)
        raise PimError("Failed to get system UUID")
    systems = []
    try: 
        systems = response.json()
    except requests.JSONDecodeError:
        logger.error("response is not valid json")
        raise

    uuid = ""
    sys_name = util.get_system_name(config)
    for system in systems:
        if system["SystemName"] == sys_name:
            uuid = system["UUID"]
            break
    
    if "" == uuid:
        logger.info("Failed to get UUID for the system %s", sys_name)
        raise PimError("Failed to get UUID for the system")
    else:
        logger.info("UUID for the system %s: %s", sys_name, uuid)
    return uuid

def get_vios_uuid(config, cookies, system_uuid):
    uri = f"/rest/api/uom/ManagedSystem/{system_uuid}/VirtualIOServer/quick/All"
    url = "https://" +  util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": "application/vnd.ibm.powervm.uom+xml; Type=VirtualIOServer"}
    response = requests.get(url, headers=headers, cookies=cookies, verify=False)
    if response.status_code != 200:
        logger.error("Failed to get VIOS id")
        raise PimError("Failed to get VIOS id")

    uuid = ""
    sys_name = util.get_system_name(config)
    for vios in response.json():
        if vios["SystemName"] == sys_name:
            uuid = vios["UUID"]
            break

    if "" == uuid:
        logger.error("Failed to get VIOS uuid from json")
        raise PimError("Failed to get VIOS uuid from json")
    else:
        logger.info("VIOS UUID for the system %s: %s", sys_name, uuid)
    return uuid

def get_vios_details(config, cookies, system_uuid, vios_uuid):
    uri = f"/rest/api/uom/ManagedSystem/{system_uuid}/VirtualIOServer/{vios_uuid}"
    url = "https://" +  util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": "application/vnd.ibm.powervm.uom+xml; Type=VirtualIOServer"}
    response = requests.get(url, headers=headers, cookies=cookies, verify=False)
    if response.status_code != 200:
        logger.error("Failed to get VIOS id")
        raise PimError("Failed to get VIOS id")

    soup = BeautifulSoup(response.text, 'xml')
    vios = str(soup.find("VirtualIOServer"))
    return vios

def get_virtual_slot_number(vios_payload, disk_name):
    soup = BeautifulSoup(vios_payload, 'xml')
    scsi_mappings = soup.find("VirtualSCSIMappings")
    disk = scsi_mappings.find(lambda tag: tag.name == "MediaName" and disk_name in tag.text)
    storage_scsi = disk.parent.parent.parent
    slot_num = storage_scsi.find("VirtualSlotNumber")
    return slot_num.text

def get_volume_group(config, cookies, vios_uuid, vg_name):
    uri = f"/rest/api/uom/VirtualIOServer/{vios_uuid}/VolumeGroup"
    url =  "https://" + util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": "application/vnd.ibm.powervm.uom+xml; type=VolumeGroup"}
    response = requests.get(url, headers=headers, cookies=cookies, verify=False)
    if response.status_code != 200:
        logger.error("Failed to get volume group: %s", response.text)
        raise PimError("Failed to get volume group")

    soup = BeautifulSoup(response.text, 'xml')
    group = soup.find("GroupName", string=vg_name)
    vol_group = group.parent
    vg_id = vol_group.find("AtomID").text
    return vg_id

def get_partition_id(config, cookies, system_uuid):
    uri = f"/rest/api/uom/ManagedSystem/{system_uuid}/LogicalPartition/quick/All"
    url = "https://" +  util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config)}
    response = requests.get(url, headers=headers, cookies=cookies, verify=False)
    if response.status_code != 200:
        logger.error("Failed to get partition id")
        raise PimError("Failed to get partition id")

    uuid = ""
    partition_name = util.get_partition_name(config) + "-pim"
    for partition in response.json():
        if partition["PartitionName"] == partition_name:
            uuid = partition["UUID"]
            break

    if "" == uuid:
        logger.error("Failed to get partition uuid")
        raise PimError("Failed to get partition id")
    else:
        logger.info("partition UUID for the system %s: %s", partition_name, uuid)
    return uuid

def remove_partition(config, cookies, partition_uuid):
    uri = f"/rest/api/uom/LogicalPartition/{partition_uuid}"
    url = "https://" +  util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": "application/vnd.ibm.powervm.uom+xml; Type=LogicalPartition"}
    response = requests.delete(url, headers=headers, cookies=cookies, verify=False)
    if response.status_code != 204:
        logger.error("Failed to delete partition")
        raise PimError("Failed to delete partition")
    logger.info("Partition deleted successfully")

def remove_scsi_mappings(config, cookies, sys_uuid, vios_uuid, vios):
    bootstap_name = util.get_vopt_bootstrap_name(config)
    cloudinit_name = util.get_vopt_cloud_init_name(config)

    logger.info("removing scsi mappings..")
    soup = BeautifulSoup(vios, "xml")
    scsi_mappings = soup.find("VirtualSCSIMappings")
    bootstrap_disk = scsi_mappings.find(lambda tag: tag.name == "BackingDeviceName" and bootstap_name in tag.text)
    scsi1 = bootstrap_disk.parent.parent
    scsi1.decompose()

    cloudinit_disk = scsi_mappings.find(lambda tag: tag.name == "BackingDeviceName" and cloudinit_name in tag.text)
    scsi2 = cloudinit_disk.parent.parent
    scsi2.decompose()
    logger.info("removed scsi mappings from vios payload")

    uri = f"/rest/api/uom/ManagedSystem/{sys_uuid}/VirtualIOServer/{vios_uuid}"
    hmc_host = util.get_host_address(config)
    url =  "https://" +  hmc_host + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": storage.CONTENT_TYPE}
    response = requests.post(url, headers=headers, cookies=cookies, data=str(soup), verify=False)

    if response.status_code != 200:
        logger.error("Failed to update VIOS with removed storage mappings: %s", response.text)
        raise PimError("Failed to update VIOS with removed storage mappings")

    logger.info("Successfully removed scsi mappings and vOpt media repositories and updated VIOS..")
    return


# destroy partition
def destroy(config, cookies, sys_uuid, vios_uuid):
    logger.info("PIM destroy flow")
    try:
        partition_uuid = get_partition_id(config, cookies, sys_uuid)

        # shutdown partition
        activation.shutdown_paritition(config, cookies, partition_uuid)

        vios = get_vios_details(config, cookies, sys_uuid, vios_uuid)
        # remove SCSI mapping from VIOS
        remove_scsi_mappings(config, cookies, sys_uuid, vios_uuid, vios)

        # TODO: delete virtual disk, volumegroup if created by the script during launch

        remove_partition(config, cookies, partition_uuid)
    except (PartitionError, PimError) as e:
        raise e

    logger.info("Delete partition done")
    return

def launch(config, cookies, sys_uuid):
    logger.info("PIM launch flow")
    try:
        logger.info("4. Copy ISO file to VIOS server")
        copy_iso_and_create_disk(config, cookies)
        logger.info("---------------------- Copy ISO done ----------------------")

        logger.info("5. Create Partition on the target host")
        partition_uuid = partition.create_partition(config, cookies, sys_uuid)

        logger.info("partition creation success. partition UUID: %s", partition_uuid)
        logger.info("---------------------- Create partition done ----------------------")

        logger.info("6. Attach Network to the partition")
        virtual_network.attach_network(config, cookies, sys_uuid, partition_uuid)
        logger.info("---------------------- Attach network done ----------------------")

        logger.info("7. Attach storage to the partition")
        vios_uuid = get_vios_uuid(config, cookies, sys_uuid)
        vios_payload = get_vios_details(config, cookies, sys_uuid, vios_uuid)

        # Attach boostrap vopt
        vopt_bootstrap = util.get_vopt_bootstrap_name(config)
        vopt.attach_vopt(vios_payload, config, cookies, partition_uuid, sys_uuid, vios_uuid, vopt_bootstrap, -1)
        logger.info("a. bootstrap virtual optical device attached")

        updated_vios_payload = get_vios_details(config, cookies, sys_uuid, vios_uuid)
        # Get VirtualSlotNumber for the disk(physical/virtual)
        slot_num = get_virtual_slot_number(updated_vios_payload, vopt_bootstrap)

        vopt_cloud_init = util.get_vopt_cloud_init_name(config)
        vopt.attach_vopt(updated_vios_payload, config, cookies, partition_uuid, sys_uuid, vios_uuid, vopt_cloud_init, slot_num)
        logger.info("b. cloudinit virtual optical device attached")

        updated_vios_payload = get_vios_details(config, cookies, sys_uuid, vios_uuid)
        use_vdisk = util.use_virtual_disk(config)
        if use_vdisk:
            use_existing_vd = util.use_existing_vd(config)
            if use_existing_vd:
                vstorage.attach_virtualdisk(updated_vios_payload, config, cookies, partition_uuid, sys_uuid, vios_uuid)
            else:
                # Create volume group, virtual disk and attach storage
                use_existing_vg = util.use_existing_vg(config)
                if not use_existing_vg:
                    # Create volume group
                    vg_id = vstorage.create_volumegroup(config, cookies, vios_uuid)
                else:
                    vg_id = get_volume_group(config, cookies, vios_uuid, util.get_volume_group(config))
                    logger.info("volume group id ", vg_id)
                    vstorage.create_virtualdisk(config, cookies, vios_uuid, vg_id)
                    time.sleep(60)
                    updated_vios_payload = get_vios_details(config, cookies, sys_uuid, vios_uuid)
                    vstorage.attach_virtualdisk(updated_vios_payload, config, cookies, partition_uuid, sys_uuid, vios_uuid)
                    diskname = util.get_virtual_disk_name(config)
        else:
            storage.attach_storage(updated_vios_payload, config, cookies, partition_uuid, sys_uuid, vios_uuid, slot_num)
            diskname = util.get_physical_volume_name(config)
            logger.info("c. physical storage attached")
        logger.info("---------------------- Attach storage done ----------------------")

        logger.info("9. Activate partition")
        activation.activate_partititon(config, cookies, partition_uuid)

        time.sleep(120)
        # monitor ISO installation
        logger.info("10. Monitor ISO installation")
        monitor_iso_installation(config, cookies)
        logger.info("---------------------- Monitor ISO installation done ----------------------")

        logger.info("11. Wait for lpar to boot from the disk")
        # Poll for the 8080 AI application port
        time.sleep(200)
        logger.info("14. Check for AI app to be running")
        for i in range(10):
            up = app.check_app(config)
            if not up:
                logger.info("AI application is still not up and running, retyring..")
                time.sleep(30)
                continue
            else:
                logger.info("AI application is up and running. Now checking response for prompt from bot")
                resp = app.check_bot_service(config)
                logger.info("Response from bot service: \n%s" % resp)
                logger.info("---------------------- PIM workflow complete ----------------------")
                return
        logger.error("AI application failed to load from bootc")
        raise AiAppError("AI application failed to load from bootc")
    except (AiAppError, AuthError, NetworkError, PartitionError, StorageError, PimError, paramiko.SSHException) as e:
        raise e

def start_manager():
    try:
        parser = argparse.ArgumentParser(description="PIM lifecycle manager")
        parser.add_argument("action", choices=["launch", "destroy"] , help="Launch and destroy flow of bootc partition.")
        args = parser.parse_args()

        logger.info("1. Initilaize and parse configuration")
        config = initialize()
        logger.info("---------------------- Initialize done ----------------------")

        logger.info("2. Authenticate with HMC host")
        session_token, cookies = auth.authenticate_hmc(config)
        logger.info("---------------------- Authenticate to HMC done ----------------------")

        config.add_section("SESSION")
        config.set("SESSION", "x-api-key", session_token)

        logger.info("3. Get System UUID for target host")
        sys_uuid = get_system_uuid(config, cookies)
        logger.info("---------------------- Get System UUID done ----------------------")

        logger.info("4. Get VIOS UUID for target host")
        vios_uuid = get_vios_uuid(config, cookies, sys_uuid)

        if args.action == "launch":
            launch(config, cookies, sys_uuid)
        elif args.action == "destroy":
            destroy(config, cookies, sys_uuid, vios_uuid)
    except (AiAppError, AuthError, NetworkError, PartitionError, StorageError, PimError) as e:
        logger.error(f"encountered an error {e}")
    finally:
        common.cleanup_and_exit(config, cookies, 0)

logger = common.get_logger("pim-manager")
logger.info("Starting PIM lifecycle manager")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
start_manager()
