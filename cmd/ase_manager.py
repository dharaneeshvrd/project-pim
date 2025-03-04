import argparse
import time
from bs4 import BeautifulSoup

import configparser
import json
import paramiko.ssh_exception
import requests
import paramiko
import re
import urllib3

import auth.auth as auth
import partition.activation as activation
import app.ai_app as app
import partition.partition as partition
import network.virtual_network as virtual_network
import utils.string_util as util
import utils.common as common
import storage.storage as storage
import storage.vopt_storage as vopt
import storage.virtual_storage as vstorage


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
    scp.put(cloud_init_iso, source_path=src_path ,remote_path=remote_path)
    print("Cloud init ISO file copy success!!")
    scp.put(bootstrap_iso, remote_path=remote_path)
    print("Bootstrap ISO file copy success!!")

    # create virtual optical disk
    bootstrap_disk_name = util.get_vopt_bootstrap_name(config)
    cloud_init_disk_name = util.get_vopt_cloud_init_name(config)

    command1 = f"ioscli mkvopt -name {bootstrap_disk_name} -file {remote_path}/{bootstrap_iso} -ro"
    command2 = f"ioscli mkvopt -name {cloud_init_disk_name} -file {remote_path}/{cloud_init_iso} -ro"

    print("command1 ", command1)
    print("command2 ", command2)
    stdin, stdout, stderr = client.exec_command(command1, get_pty=True)
    print(stderr.readlines())
    print(stdout.readlines())

    if stdout.channel.recv_exit_status() != 0:
        print("command1 execution failed", command1)
        common.cleanup_and_exit(config, cookies, 1)

    stdin, stdout, stderr = client.exec_command(command2, get_pty=True)
    print(stderr.readlines())
    print(stdout.readlines())

    if stdout.channel.recv_exit_status() != 0:
        print("command2 execution failed", command2)
        common.cleanup_and_exit(config, cookies, 1)

    print("Load vopt to VIOS successful")
    client.close()

def monitor_iso_installation(config, cookies):
    ip = util.get_ip_address(config)
    username = "fedora"
    keyfile = util.get_ssh_keyfile(config)
    command = "sudo journalctl -u getcontainer.service -f 2>&1 | awk '{print} /Installation complete/ {print \"Match found: \" $0; exit 0}'"

    for i in range(10):
        scp_port = 22
        client = get_ssh_client()
        try:
            client.connect(ip, scp_port, username, key_filename=keyfile)
        except (paramiko.BadHostKeyException, paramiko.AuthenticationException,
        paramiko.SSHException, paramiko.ssh_exception.NoValidConnectionsError) as e:
            if i == 9:
                print("failed to establish SSH connection to partition after 10 retries")
                common.cleanup_and_exit(config, cookies, 1)
            print("SSH to partition failed, retrying..")
            time.sleep(30)
    print("SSH connection to partition is successful")

    stdin, stdout, stderr = client.exec_command(command, get_pty=True)
    while True:
        out = stdout.readline()
        print(out)
        if stdout.channel.exit_status_ready():
            if stdout.channel.recv_exit_status() == 0:
                print("Received ISO Installation complete message")
                client.close()
                break
            else:
                print("\033[31mFailed to get ISO installation complete message. Please look at the errors if appear on the console and take appropriate resolution!!\033[0m")
                client.close()
                common.cleanup_and_exit(config, cookies, 1)
    return

def get_system_uuid(config, cookies):
    uri = "/rest/api/uom/ManagedSystem/quick/All"
    url = "https://" + util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config)}
    print("headers ", headers)
    response = requests.get(url, headers=headers, cookies=cookies, verify=False)
    if response.status_code != 200:
        print("Failed to get system UUID ", response.text)
        exit(config, cookies, 1)
    systems = []
    try: 
        systems = response.json()
    except requests.JSONDecodeError:
        print("response is not valid json")

    uuid = ""
    sys_name = util.get_system_name(config)
    for system in systems:
        if system["SystemName"] == sys_name:
            uuid = system["UUID"]
            break
    
    if "" == uuid:
        print("Failed to get UUID for the system %s", sys_name)
        common.cleanup_and_exit(config, cookies, 1)
    else:
        print("UUID for the system %s: %s", sys_name, uuid)
    return uuid

def get_vios_uuid(config, cookies, system_uuid):
    uri = f"/rest/api/uom/ManagedSystem/{system_uuid}/VirtualIOServer/quick/All"
    url = "https://" +  util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": "application/vnd.ibm.powervm.uom+xml; Type=VirtualIOServer"}
    response = requests.get(url, headers=headers, cookies=cookies, verify=False)
    if response.status_code != 200:
        print("Failed to get VIOS id")
        common.cleanup_and_exit(config, cookies, 1)

    uuid = ""
    sys_name = util.get_system_name(config)
    for vios in response.json():
        if vios["SystemName"] == sys_name:
            uuid = vios["UUID"]
            break

    if "" == uuid:
        print("Failed to get VIOS uuid")
        common.cleanup_and_exit(config, cookies, 1)
    else:
        print("VIOS UUID for the system %s: %s", sys_name, uuid)
    return uuid

def get_vios_details(config, cookies, system_uuid, vios_uuid):
    uri = f"/rest/api/uom/ManagedSystem/{system_uuid}/VirtualIOServer/{vios_uuid}"
    url = "https://" +  util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": "application/vnd.ibm.powervm.uom+xml; Type=VirtualIOServer"}
    response = requests.get(url, headers=headers, cookies=cookies, verify=False)
    if response.status_code != 200:
        print("Failed to get VIOS id")
        common.cleanup_and_exit(config, cookies, 1)
    soup = BeautifulSoup(response.text, 'xml')
    vios = str(soup.find("VirtualIOServer"))
    return vios

# def get_virtual_slot_number(vios_payload, disk_name):
#     soup = BeautifulSoup(vios_payload, 'xml')
#     disk = soup.find(lambda tag: tag.name == "DiskName" and disk_name in tag.text)
#     storage_scsi = disk.parent.parent.parent
#     slot_num = storage_scsi.find("VirtualSlotNumber")
#     return slot_num.text

def get_virtual_slot_number(vios_payload, disk_name):
    soup = BeautifulSoup(vios_payload, 'xml')
    scsi_mappings = soup.find("VirtualSCSIMappings")
    disk = scsi_mappings.find(lambda tag: tag.name == "VolumeName" and disk_name in tag.text)
    storage_scsi = disk.parent.parent.parent
    slot_num = storage_scsi.find("VirtualSlotNumber")
    return slot_num.text

def get_volume_group(config, cookies, vios_uuid, vg_name):
    uri = f"/rest/api/uom/VirtualIOServer/{vios_uuid}/VolumeGroup"
    url =  "https://" + util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": "application/vnd.ibm.powervm.uom+xml; type=VolumeGroup"}
    response = requests.get(url, headers=headers, cookies=cookies, verify=False)
    if response.status_code != 200:
        print("Failed to get volume groups: ", response.text)
        common.cleanup_and_exit(config, cookies, 1)
    soup = BeautifulSoup(response.text, 'xml')
    group = soup.find("GroupName", string=vg_name)
    vol_group = group.parent
    vg_id = vol_group.find("AtomID").text
    return vg_id

def get_bootorder_string(partition_str):
    soup = BeautifulSoup(partition_str, 'xml')
    boot_str_list = soup.find("BootDeviceList").text
    res = boot_str_list.split(" ")
    boot_str = res[0]

    if "/vdevice/v-scsi@" in boot_str:
        dev_id = re.search('/vdevice/v-scsi@(.*)/', boot_str)
        print("device boot id ", dev_id.group(0))
    else:
        print("failed to get device boot id from bootorder")
    return dev_id.group(0)


# Get logical adresses for physical/virtual disk and bootstrap media, eg: virtual disk - 0x8100000000000000 and bootstrap media - 0x8200000000000000
def get_logical_addresses(vios_details, disk_name, bootstrap_name):
    soup = BeautifulSoup(vios_details, "xml")
    scsi_mappings = soup.find("VirtualSCSIMappings")
    disk = scsi_mappings.find(lambda tag: tag.name == "VolumeName" and disk_name in tag.text)
    scsi = disk.parent.parent.parent
    disk_lun = scsi.find("LogicalUnitAddress").text

    bootstrap_lun = ""
    vopts = soup.find_all("MediaName", string=bootstrap_name)
    for vopt in vopts:
        node = vopt.parent.parent
        if node.name == "Storage":
            scsi = vopt.parent.parent.parent
            bootstrap_lun = scsi.find("LogicalUnitAddress").text

    print(f"disk LUN {disk_lun}, bootstrap LUN {bootstrap_lun}")
    return disk_lun, bootstrap_lun

def get_partition_id(config, cookies, system_uuid):
    uri = f"/rest/api/uom/ManagedSystem/{system_uuid}/LogicalPartition/quick/All"
    url = "https://" +  util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config)}
    response = requests.get(url, headers=headers, cookies=cookies, verify=False)
    if response.status_code != 200:
        print("Failed to get partition id")
        common.cleanup_and_exit(config, cookies, 1)

    uuid = ""
    partition_name = util.get_partition_name(config)
    for partition in response.json():
        if partition["PartitionName"] == partition_name:
            uuid = partition["UUID"]
            break

    if "" == uuid:
        print("Failed to get partition uuid")
        common.cleanup_and_exit(config, cookies, 1)
    else:
        print("VIOS UUID for the system %s: %s", partition_name, uuid)
    return uuid

def remove_partition(config, cookies, partition_uuid):
    uri = f"/rest/api/uom/LogicalPartition/{partition_uuid}"
    url = "https://" +  util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": "application/vnd.ibm.powervm.uom+xml; Type=LogicalPartition"}
    response = requests.delete(url, headers=headers, cookies=cookies, verify=False)
    if response.status_code != 204:
        print("Failed to delete partition")
        common.cleanup_and_exit(config, cookies, 1)
    print("Partition deleted successfully")

def remove_scsi_mappings(config, cookies, sys_uuid, vios_uuid, vios):
    bootstap_name = util.get_vopt_bootstrap_name(config)
    cloudinit_name = util.get_vopt_cloud_init_name(config)

    print("removing scsi mappings..")
    soup = BeautifulSoup(vios, "xml")
    scsi_mappings = soup.find("VirtualSCSIMappings")
    bootstrap_disk = scsi_mappings.find(lambda tag: tag.name == "BackingDeviceName" and bootstap_name in tag.text)
    scsi1 = bootstrap_disk.parent.parent
    scsi1.decompose()

    cloudinit_disk = scsi_mappings.find(lambda tag: tag.name == "BackingDeviceName" and cloudinit_name in tag.text)
    scsi2 = cloudinit_disk.parent.parent
    scsi2.decompose()
    print("removed scsi mappings from vios payload")

    uri = f"/rest/api/uom/ManagedSystem/{sys_uuid}/VirtualIOServer/{vios_uuid}"
    hmc_host = util.get_host_address(config)
    url =  "https://" +  hmc_host + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": storage.CONTENT_TYPE}
    response = requests.post(url, headers=headers, cookies=cookies, data=str(soup), verify=False)

    if response.status_code != 200:
        print("Failed to update VIOS with removed storage mappings", response.text)
        common.cleanup_and_exit(config, cookies, 1)

    print("Successfully removed scsi mappings and vOpt media repositories and updated VIOS..")
    return


# delete partition
def delete_partition(config, cookies, sys_uuid, vios_uuid):
    partition_uuid = get_partition_id(config, cookies, sys_uuid)

    # shutdown partition
    activation.shutdown_paritition(config, cookies, partition_uuid)

    vios = get_vios_details(config, cookies, sys_uuid, vios_uuid)
    #Remove SCSI mapping from VIOS
    remove_scsi_mappings(config, cookies, sys_uuid, vios_uuid, vios)

    remove_partition(config, cookies, partition_uuid)
    print("Delete partition done")
    return

def launch_ase(config, cookies, sys_uuid):
    print("4. Copy ISO file to VIOS server")
    copy_iso_and_create_disk(config, cookies)
    print("----------- Copy ISO done -----------")

    print("5. Create Partion on the target host")
    partition_uuid = partition.create_partition(config, cookies, sys_uuid)

    print("partition creation success. partition UUID: %s", partition_uuid)
    print("----------- Create partition done -----------")

    print("6. Attach Network to the partition")
    virtual_network.attach_network(config, cookies, sys_uuid, partition_uuid)
    print("----------- Attach network done -----------")

    print("7. Attach storage to the partition")
    vios_uuid = get_vios_uuid(config, cookies, sys_uuid)
    vios_payload = get_vios_details(config, cookies, sys_uuid, vios_uuid)
    use_vdisk = util.use_virtual_disk(config)
    if use_vdisk:
        use_existing_vd = util.use_existing_vd(config)
        if use_existing_vd:
            vstorage.attach_virtualdisk(vios_payload, config, cookies, partition_uuid, sys_uuid, vios_uuid)
        else:
            # Create volume group, virtual disk and attach storage
            use_existing_vg = util.use_existing_vg(config)
            if not use_existing_vg:
                # Create volume group
                vg_id = vstorage.create_volumegroup(config, cookies, vios_uuid)
            else:
                vg_id = get_volume_group(config, cookies, vios_uuid, util.get_volume_group(config))
            print("volume group id ", vg_id)
            vstorage.create_virtualdisk(config, cookies, vios_uuid, vg_id)
            time.sleep(60)
            vios_payload = get_vios_details(config, cookies, sys_uuid, vios_uuid)
            vstorage.attach_virtualdisk(vios_payload, config, cookies, partition_uuid, sys_uuid, vios_uuid)
            diskname = util.get_virtual_disk_name(config)
    else:
        storage.attach_storage(vios_payload, config, cookies, partition_uuid, sys_uuid, vios_uuid)
        diskname = util.get_physical_volume_name(config)
    print("----------- Attach storage done -----------")

    print("8. Attach vOpt to the partition")
    updated_vios_payload = get_vios_details(config, cookies, sys_uuid, vios_uuid)
    # Get VirtualSlotNumber for the disk(physical/virtual)
    slot_num = get_virtual_slot_number(updated_vios_payload, diskname)

    # Attach boostrap vopt
    vopt_bootstrap = util.get_vopt_bootstrap_name(config)
    vopt.attach_vopt(updated_vios_payload, config, cookies, partition_uuid, sys_uuid, vios_uuid, vopt_bootstrap, slot_num)

    # Attach cloud-init vopt
    updated_vios_payload = get_vios_details(config, cookies, sys_uuid, vios_uuid)
    vopt_cloud_init = util.get_vopt_cloud_init_name(config)
    vopt.attach_vopt(updated_vios_payload, config, cookies, partition_uuid, sys_uuid, vios_uuid, vopt_cloud_init, slot_num)
    print("----------- Attach vOpt done -----------")

    print("9. Get bootorder string")
    activation.activate_partititon(config, cookies, partition_uuid)
    time.sleep(30)

    # Get bootstring pattern
    partition_payload = partition.get_partition_details(config, cookies, sys_uuid, partition_uuid)
    dev_boot_id = get_bootorder_string(partition_payload)
    print("----------- Get bootorder string done -----------")

    # Shutdown partition and update boot order to boot from disk
    print("10. Update bootorder to boot Bootstrap ISO")
    activation.shutdown_paritition(config, cookies, partition_uuid)
    updated_vios_payload = get_vios_details(config, cookies, sys_uuid, vios_uuid)
    disk_lun, bootstrap_lun = get_logical_addresses(updated_vios_payload, diskname, vopt_bootstrap)
    partition.update_partition(config, cookies, sys_uuid, partition_uuid, partition_payload, dev_boot_id + "disk@" + bootstrap_lun)
    activation.activate_partititon(config, cookies, partition_uuid)
    print("----------- Updated bootorder to boot Bootstrap ISO -----------")

    time.sleep(120)
    # monitor ISO installation
    print("11. Monitor ISO installation")
    monitor_iso_installation(config, cookies)
    print("----------- Monitor ISO installation done -----------")

    # Shutdown partition and update boot order to boot from disk
    print("12. Update bootorder to boot from Disk")
    activation.shutdown_paritition(config, cookies, partition_uuid)
    partition.update_partition(config, cookies, sys_uuid, partition_uuid, partition_payload, dev_boot_id + "disk@" + disk_lun)
    print("----------- Update bootorder to boot from Disk -----------")

    print("13. Activate the partition")
    activation.activate_partititon(config, cookies, partition_uuid)
    print("----------- Activate partition done -----------")

    # Poll for the 8080 AI application port
    time.sleep(100)
    print("14. Check for AI app to be running")
    for i in range(10):
        up = app.check_app(config)
        if not up:
           print("AI application is still not up and running, retyring..")
           time.sleep(30)
        else:
            print("AI application is up and running. Now checking response for prompt from bot")
            resp = app.check_bot_service(config)
            print("Response from bot service: \n%s" % resp)
            print("----------- ASE workflow complete -----------")
            auth.delete_session(config, cookies)
            exit(0)
    print("AI application failed to load from bootc")
    auth.delete_session(config, cookies)

def start_manager():
    print("1. Initilaize and parse configuration")
    config = initialize()
    print("----------- Initialize done ----------------------")

    print("2. Authenticate with HMC host")
    session_token, cookies = auth.authenticate_hmc(config)
    print("----------- Authenticate to HMC done -----------")

    config.add_section("SESSION")
    config.set("SESSION", "x-api-key", session_token)

    print("3. Get System UUID for target host")
    sys_uuid = get_system_uuid(config, cookies)
    print("----------- Get System UUID done -----------")

    print("4. Get VIOS UUID for target host")
    vios_uuid = get_vios_uuid(config, cookies, sys_uuid)

    parser = argparse.ArgumentParser(description="ASE lifecycle manager")
    parser.add_argument("action", choices=["launch", "delete"] , help="Launch and delete flow of bootc partition.")
    args = parser.parse_args()
    print("args: ", args.action)
    
    if args.action == "launch":
        launch_ase(config, "", "")
    elif args.action == "delete":
        delete_partition(config, "", "", "")
    # match args:
    #     case "--launch":
    #         launch_ase(config, cookies, sys_uuid)
    #     case "--delete":
    #         delete_partition(config, cookies, sys_uuid, vios_uuid)

print("Starting ASE lifecycle manager")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
start_manager()
