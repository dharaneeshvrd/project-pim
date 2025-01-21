import time
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

import configparser
import paramiko.ssh_exception
import requests
import paramiko
import re

import auth
import activation
import partition
import virtual_network
import storage
import string_util as util
import vopt_storage as vopt
import virtual_storage as vstorage

from scp import SCPClient

DISK_LUN = "8100000000000000"
BOOTSTRAP_LUN = "8200000000000000"

def initialize():
    config_file = "config.ini"
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

def get_ssh_client():
    client = paramiko.SSHClient()
    #client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    return client

def copy_iso_and_create_disk(config):
    scp_port = 22
    client = get_ssh_client()

    host_ip = util.get_vios_address(config)
    username = util.get_vios_username(config)
    password = util.get_vios_password(config)
    bootstrap_iso = util.get_bootstrap_iso(config)
    cloud_init_iso = util.get_cloud_init_iso(config)
    remote_path=util.get_iso_target_path(config)

    client.connect(host_ip, scp_port, username, password)
    scp = SCPClient(client.get_transport())
    scp.put(cloud_init_iso, remote_path=remote_path)
    print("Cloud init ISO file copy success!!")
    scp.put(bootstrap_iso, remote_path=remote_path)
    print("Bootstrap ISO file copy success!!")

    # create virtual optical disk
    bootstrap_disk_name = util.get_disk_name(config) + "-bootstrap"
    cloud_init_disk_name = util.get_disk_name(config) + "-cloud-init"

    command1 = f"ioscli mkvopt -name {bootstrap_disk_name} -file {remote_path}/{bootstrap_iso} -ro"
    command2 = f"ioscli mkvopt -name {cloud_init_disk_name} -file {remote_path}/{cloud_init_iso} -ro"

    print("command1 ", command1)
    print("command2 ", command2)
    stdin, stdout, stderr = client.exec_command(command1, get_pty=True)
    print(stderr.readlines())
    print(stdout.readlines())
    stdin, stdout, stderr = client.exec_command(command2, get_pty=True)
    print(stderr.readlines())
    print(stdout.readlines())

    if stdout.channel.recv_exit_status() != 0:
        print("command2 execution failed", command2)
        exit()

    print("Load vopt to VIOS successful")
    client.close()

def monitor_iso_installation(config):
    ip = util.get_ip_address(config)
    username = "fedora"
    keyfile = util.get_ssh_keyfile(config)
    command = "sudo journalctl -u getcontainer.service -g \"Installation complete\""

    for i in range(10):
        scp_port = 22
        client = get_ssh_client()
        try:
            client.connect(ip, scp_port, username, key_filename=keyfile)
        except (paramiko.BadHostKeyException, paramiko.AuthenticationException,
        paramiko.SSHException, paramiko.ssh_exception.NoValidConnectionsError) as e:
            if i == 9:
                print("failed to grep Installation complete message after 10 retries")
                exit()
            print("failed to SSH to partition, retrying..")
            time.sleep(30)

    for i in range(10):
        chan = client.get_transport().open_session()
        print("opned channel")
        chan.exec_command(command)
        if chan.recv_exit_status() == 0:
            break
        else:
            print("command %s execution failed: " % command)
            if i == 4:
                print("failed to grep Installation complete message after 5 retries.")
                exit(1)
            time.sleep(30)

    print("Installation of bootstrap iso complete")
    return

def authenticate_hmc(config):
    # Populate Authentication payload
    payload = auth.populate_payload(config)
    url = "https://" + util.get_host_address(config) + auth.URI
    headers = {"Content-Type": auth.CONTENT_TYPE, "Accept": auth.ACCEPT}
    response = requests.put(url, headers=headers, data=payload, verify=False)
    if response.status_code != 200:
        print("Failed to authenticate hmc ", response.text)
        exit()
    root = ET.fromstring(response.text)
    SESSION_KEY = ""
    for child in root.iter():
        if "X-API-Session" in child.tag:
            SESSION_KEY = child.text

    return SESSION_KEY, response.cookies

def get_system_uuid(config, cookies):
    uri = "/rest/api/uom/ManagedSystem/quick/All"
    url = "https://" + util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config)}
    print("headers ", headers)
    response = requests.get(url, headers=headers, cookies=cookies, verify=False)
    if response.status_code != 200:
        print("Failed to get system UUID ", response.text)
        exit()
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
        exit()
    else:
        print("UUID for the system %s: %s", sys_name, uuid)
    return uuid

def create_partition(config, cookies, system_uuid):
    uri = f"/rest/api/uom/ManagedSystem/{system_uuid}/LogicalPartition"
    url = "https://" +  util.get_host_address(config) + uri
    payload = partition.populate_payload(config)
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": partition.CONTENT_TYPE}
    response = requests.put(url, headers=headers, data=payload, cookies=cookies, verify=False)
    if response.status_code != 200:
        print("Failed to create partition ", response.text)
        exit()

    #partition response will be in XML
    partition_data = response.text
    root = ET.fromstring(partition_data)
    partition_uuid = ""
    for child in root.iter():
        if "PartitionUUID" in child.tag:
            partition_uuid = child.text

    return partition_uuid

def get_network_uuid(config, cookies, system_uuid):
    uri = f"/rest/api/uom/ManagedSystem/{system_uuid}/VirtualNetwork/quick/All"
    url = "https://" +  util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": "application/vnd.ibm.powervm.uom+xml, type=VirtualNetwork"}
    response = requests.get(url, headers=headers, cookies=cookies, verify=False)
    if response.status_code != 200:
        print("Failed to get vlan id")
        exit()
    uuid = ""
    network_name = util.get_vnetwork_name(config)
    for nw in response.json():
        if nw["NetworkName"] == network_name:
            uuid = nw["UUID"]
            break

    if "" == uuid:
        print("Failed to get UUID for the virtual network %s", network_name)
        exit()
    else:
        print("Network UUID for the virtual network %s: %s", network_name, uuid)
    return uuid

def get_vlan_details(config, cookies, system_uuid):
    nw_uuid = get_network_uuid(config, cookies, system_uuid)
    uri = f"/rest/api/uom/ManagedSystem/{system_uuid}/VirtualNetwork/{nw_uuid}"
    url = "https://" +  util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": "application/vnd.ibm.powervm.uom+xml, type=VirtualNetwork"}
    response = requests.get(url, headers=headers, cookies=cookies, verify=False)
    if response.status_code != 200:
        print("Failed to get vlan id")
        exit()

    # parse xml response to get vlan_id and vswitch_id
    root = ET.fromstring(response.text)
    for child in root.iter():
        if "NetworkVLANID" in child.tag:
            vlan_id = child.text
        elif "VswitchID" in child.tag:
            vswitch_id = child.text

    return vlan_id, vswitch_id

def attach_network(config, cookies, system_uuid, partition_uuid):
    # Get VLAN ID and VSWITCH ID
    vlan_id, vswitch_id = get_vlan_details(config, cookies, system_uuid)
    payload = virtual_network.populate_payload(vlan_id, vswitch_id, util.get_vswitch_name(config))

    uri = f"/rest/api/uom/LogicalPartition/{partition_uuid}/ClientNetworkAdapter"
    url =  "https://" +  util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": virtual_network.CONTENT_TYPE}
    response = requests.put(url, headers=headers, cookies=cookies, data=payload, verify=False)
    if response.status_code != 200:
        print("Failed to attach virtual network to the partition ", response.text)
        exit()
    return

def get_vios_uuid(config, cookies, system_uuid):
    uri = f"/rest/api/uom/ManagedSystem/{system_uuid}/VirtualIOServer/quick/All"
    url = "https://" +  util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": "application/vnd.ibm.powervm.uom+xml; Type=VirtualIOServer"}
    response = requests.get(url, headers=headers, cookies=cookies, verify=False)
    if response.status_code != 200:
        print("Failed to get VIOS id")
        exit()

    uuid = ""
    sys_name = util.get_system_name(config)
    for vios in response.json():
        if vios["SystemName"] == sys_name:
            uuid = vios["UUID"]
            break

    if "" == uuid:
        print("Failed to get VIOS uuid")
        exit()
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
        exit()
    soup = BeautifulSoup(response.text, 'xml')
    vios = str(soup.find("VirtualIOServer"))
    return vios

def get_virtual_slot_number(vios_payload, disk_name):
    soup = BeautifulSoup(vios_payload, 'xml')
    disk = soup.find(lambda tag: tag.name == "DiskName" and disk_name in tag.text)
    storage_scsi = disk.parent.parent.parent
    slot_num = storage_scsi.find("VirtualSlotNumber")
    return slot_num.text

def attach_storage(vios_payload, config, cookies, partition_uuid, system_uuid, vios_uuid):
    uri = f"/rest/api/uom/ManagedSystem/{system_uuid}/VirtualIOServer/{vios_uuid}"
    hmc_host = util.get_host_address(config)
    url =  "https://" +  hmc_host + uri
    physical_vol_name = util.get_physical_volume_name(config)
    payload = storage.populate_payload(vios_payload, hmc_host, partition_uuid, system_uuid, physical_vol_name)
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": storage.CONTENT_TYPE}
    response = requests.post(url, headers=headers, cookies=cookies, data=payload, verify=False)

    if response.status_code != 200:
        print("Failed to attach virtual storage to the partition ", response.text)
        exit()
    return

def attach_vopt(vios_payload, config, cookies, partition_uuid, sys_uuid, vios_uuid, vopt_name, slot):
    uri = f"/rest/api/uom/ManagedSystem/{sys_uuid}/VirtualIOServer/{vios_uuid}"
    hmc_host = util.get_host_address(config)
    url =  "https://" +  hmc_host + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": storage.CONTENT_TYPE}
    #vopt_name = util.get_vopt_name(config)
    payload = vopt.populate_payload(vios_payload, hmc_host, partition_uuid, sys_uuid, vopt_name, slot)
    response = requests.post(url, headers=headers, cookies=cookies, data=payload, verify=False)

    if response.status_code != 200:
        print("Failed to attach virtual storage to the partition ", response.text)
        exit()
    return

def get_lpar_profile_id(config, cookies, partition_uuid):
    uri = f"/rest/api/uom/LogicalPartition/{partition_uuid}/LogicalPartitionProfile"
    url =  "https://" +  util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": "application/vnd.ibm.powervm.uom+xml; Type=LogicalPartitionProfile"}
    response = requests.get(url, headers=headers, cookies=cookies, verify=False)
    if response.status_code != 200:
        print("Failed to get lpar profile id ", response.text)
        exit()
    soup = BeautifulSoup(response.text, 'xml')
    entry_node = soup.find('entry')
    lpar_profile_id = entry_node.find('id')
    return lpar_profile_id.text


def get_partition_details(config, cookies, system_uuid, partition_uuid):
    uri = f"/rest/api/uom/ManagedSystem/{system_uuid}/LogicalPartition/{partition_uuid}"
    url =  "https://" +  util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": "application/vnd.ibm.powervm.uom+xml; Type=LogicalPartition"}
    response = requests.get(url, headers=headers, cookies=cookies, verify=False)
    if response.status_code != 200:
        print("Failed to get partition details", response.text)
        exit()
    soup = BeautifulSoup(response.text, 'xml')
    lpar = str(soup.find('LogicalPartition'))
    return lpar

def update_partition(config, cookies, system_uuid, partition_uuid, partition_payload, lun):
    uri = f"/rest/api/uom/ManagedSystem/{system_uuid}/LogicalPartition/{partition_uuid}"
    url =  "https://" +  util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": "application/vnd.ibm.powervm.uom+xml; Type=LogicalPartition"}
    payload = partition.get_bootorder_payload(partition_payload, lun)
    response = requests.post(url, headers=headers, cookies=cookies, data=payload, verify=False)
    if response.status_code != 200:
        print("Failed to attach virtual storage to the partition ", response.text)
        exit()
    print("Updated the bootorder for the partition: ", partition_uuid)
    return

def check_app(config):
    ip_address = util.get_ip_address(config)
    url = "http://" + ip_address + ":8080/"
    response = requests.get(url, verify=False)
    if response.status_code != 200:
        print("AI application didn't respond ", response.text)
        return False
    print("AI application responded healthy..")
    return True

def poll_job_status(config, cookies, job_id):
    uri = f"/rest/api/uom/jobs/{job_id}"
    url =  "https://" +  util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": "application/vnd.ibm.powervm.web+xml; type=JobRequest"}
    response = requests.get(url, headers=headers, cookies=cookies, verify=False)
    if response.status_code != 200:
        print("Failed to get job completion ", response.text)
        exit()
    soup = BeautifulSoup(response.text, 'xml')
    if soup.find("Status").text == "COMPLETED_OK":
        return True
    else:
        return False

def check_job_status(config, cookies, response):
    # check job status for COMPLETED_OK
    soup = BeautifulSoup(response.text, 'xml')
    job_id = soup.find("JobID").text
    if soup.find("Status").text == "COMPLETED_OK":
        print("Partition activated successfully.")
        return
    else:
        # poll for job status to be COMPLETRED_OK 3 times.
        for i in range(10):
            status = poll_job_status(config, cookies, job_id)
            if status:
                return True
            else:
                time.sleep(10)
                continue
    return False

def activate_partititon(config, cookies, partition_uuid):
    uri = f"/rest/api/uom/LogicalPartition/{partition_uuid}/do/PowerOn"
    url =  "https://" +  util.get_host_address(config) + uri
    lpar_profile_id = get_lpar_profile_id(config, cookies, partition_uuid)
    payload = activation.populated_payload(lpar_profile_id)

    headers = {"x-api-key": util.get_session_key(config), "Content-Type": activation.CONTENT_TYPE}
    response = requests.put(url, headers=headers, cookies=cookies, data=payload, verify=False)
    if response.status_code != 200:
        print("Failed to activate partition %s", partition_uuid)
        exit()
    # check job status for COMPLETED_OK
    status = check_job_status(config, cookies, response)
    if not status:
        print("Failed to activate partition %s", partition_uuid)
        exit()
    print("Partition activated successfully.")
    return

def shutdown_paritition(config, cookies, partition_uuid):
    uri = f"/rest/api/uom/LogicalPartition/{partition_uuid}/do/PowerOff"
    url =  "https://" + util.get_host_address(config) + uri
    payload = activation.shutdown_payload()
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": activation.CONTENT_TYPE}
    response = requests.put(url, headers=headers, cookies=cookies, data=payload, verify=False)
    if response.status_code != 200:
        print("Failed to shutdown partition %s", partition_uuid)
        exit()
    # check job status for COMPLETED_OK
    status = check_job_status(config, cookies, response)
    if not status:
        print("Failed to shutdown partition%s", partition_uuid)
        exit()
    print("Partition shutdown successfully.")
    return

def get_bootorder_string(partition_str):
    soup = BeautifulSoup(partition_str, 'xml')
    boot_str_list = soup.find("BootDeviceList").text
    res = boot_str_list.split(" ")
    boot_str = res[0]
    print("boot string ", boot_str)

    if "/vdevice/v-scsi@" in boot_str:
        dev_id = re.search('/vdevice/v-scsi@(.*)/', boot_str)
        print("device boot id ", dev_id.group(0))
    else:
        print("failed to get device boot id from bootorder")
    return dev_id.group(0)

def start_manager():
    print("1. Initilaize and parse configuration")
    config = initialize()
    print("----------- Initialize done ----------------------")

    print("2. Copy ISO file to VIOS server")
    copy_iso_and_create_disk(config)
    print("----------- Copy ISO done -----------")

    print("3. Authenticate with HMC host")
    session_token, cookies = authenticate_hmc(config)
    print("----------- Authenticate to HMC done -----------")

    config.add_section("SESSION")
    config.set("SESSION", "x-api-key", session_token)

    print("4. Get System UUID for target host")
    sys_uuid = get_system_uuid(config, cookies)
    print("----------- Get System UUID done -----------")

    print("5. Create Partion on the target host")
    partition_uuid = create_partition(config, cookies, sys_uuid)

    print("partition creation success. partition UUID: %s", partition_uuid)
    print("----------- Create partition done -----------")

    print("6. Attach Network to the partition")
    attach_network(config, cookies, sys_uuid, partition_uuid)
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
                vg_id = "52dac546-6441-37ea-b0bd-431ca1940124"
            print("volume group id ", vg_id)
            vstorage.create_virtualdisk(config, cookies, vios_uuid, vg_id)
            vios_payload = get_vios_details(config, cookies, sys_uuid, vios_uuid)
            vstorage.attach_virtualdisk(vios_payload, config, cookies, partition_uuid, sys_uuid, vios_uuid)
            diskname = util.get_virtual_disk_name(config)
    else:
        attach_storage(vios_payload, config, cookies, partition_uuid, sys_uuid, vios_uuid)
        diskname = util.get_physical_volume_name(config)
    print("----------- Attach storage done -----------")

    print("8. Attach vOpt to the partition")
    updated_vios_payload = get_vios_details(config, cookies, sys_uuid, vios_uuid)
    # Get VirtualSlotNumber for the disk(physical/virtual)
    slot_num = get_virtual_slot_number(updated_vios_payload, diskname)

    # Attach boostrap vopt
    vopt_bootstrap = util.get_vopt_bootstrap_name(config)
    attach_vopt(updated_vios_payload, config, cookies, partition_uuid, sys_uuid, vios_uuid, vopt_bootstrap, slot_num)

    # Attach cloud-init vopt
    updated_vios_payload = get_vios_details(config, cookies, sys_uuid, vios_uuid)
    vopt_cloud_init = util.get_vopt_cloud_init_name(config)
    attach_vopt(updated_vios_payload, config, cookies, partition_uuid, sys_uuid, vios_uuid, vopt_cloud_init, slot_num)
    print("----------- Attach vOpt done -----------")

    print("9. Activate the partition")
    activate_partititon(config, cookies, partition_uuid)
    print("----------- Activate partition done -----------")
    time.sleep(30)

    # Get bootstring pattern
    partition_payload = get_partition_details(config, cookies, sys_uuid, partition_uuid)
    dev_boot_id = get_bootorder_string(partition_payload)
    print("device boot id ", dev_boot_id)

    # Shutdown partition and update boot order to boot from disk
    shutdown_paritition(config, cookies, partition_uuid)
    update_partition(config, cookies, sys_uuid, partition_uuid, partition_payload, dev_boot_id + "disk@" + BOOTSTRAP_LUN)
    activate_partititon(config, cookies, partition_uuid)

    time.sleep(120)
    # monitor ISO installation
    print("----------- Monitor ISO installation -----------")
    monitor_iso_installation(config)

    # Shutdown partition and update boot order to boot from disk
    print("----------- Shutdown partition and update boot order to boot from disk ----------- ")
    shutdown_paritition(config, cookies, partition_uuid)
    update_partition(config, cookies, sys_uuid, partition_uuid, partition_payload, dev_boot_id + "disk@" + DISK_LUN)

    print("9. Activate the partition")
    activate_partititon(config, cookies, partition_uuid)
    print("----------- Activate partition done -----------")

    # Poll for the 8080 AI application port
    time.sleep(200)
    print("Check for AI app to be running")
    for i in range(10):
        up = check_app(config)
        if up:
            print("AI application is up and running.. ASE workflow completed.")
            exit()
        time.sleep(30)

    print("AI application failed to load from bootc")


print("Starting ASE lifecycle manager")
start_manager()
