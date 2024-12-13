import os
import xml.etree.ElementTree as ET 

import configparser
import requests
import paramiko

import auth
import activation
import partition
import virtual_network
import storage
import string_util as util

from scp import SCPClient

def initialize():
    config_file = "config.ini"
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

def copy_iso_and_create_disk(config):
    scp_port = 22
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    host_ip = util.get_host_address(config)
    username = util.get_host_username(config)
    password = util.get_host_password(config)
    iso = util.get_iso(config)
    remote_path=util.get_iso_target_path(config)

    client.connect(host_ip, scp_port, username, password)
    scp = SCPClient(client.get_transport())
    scp.put(iso, remote_path=remote_path)
    print("ISO file copy success!!")

    # create virtual optical disk
    disk_name = util.get_disk_name(config)
    try:
        command = f"mkvopt -name {disk_name} -file {iso}"
        client.exec_command(command)
    except paramiko.ssh_exception:
        print("Failed to create disk from ISO image")
    print("Create disk using ISO is successful")

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
    print("response: ", partition_data)
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
    #vswitch_id = get_vswitch_id(config, cookies, system_uuid)
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

def attach_storage(config, cookies, partition_uuid, system_uuid, vios_uuid):
    uri = f"/rest/api/uom/ManagedSystem/{system_uuid}/VirtualIOServer/{vios_uuid}"
    hmc_host = util.get_host_address(config)
    url =  "https://" +  hmc_host + uri
    physical_vol_name = util.get_physical_volume_name(config)
    payload = storage.populate_payload(hmc_host, partition_uuid, system_uuid, physical_vol_name)
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": storage.CONTENT_TYPE}
    response = requests.post(url, headers=headers, cookies=cookies, data=payload, verify=False)
    print("response ", response.text)
    print("response status ", response.status_code)

    if response.status_code != 200:
        print("Failed to attach virtual storage to the partition ", response.text)
        exit()
    return

def attach_vopt(config, cookies, partition_uuid, sys_uuid, vios_uuid):
    uri = f"/rest/api/uom/ManagedSystem/{sys_uuid}/VirtualIOServer/{vios_uuid}"
    hmc_host = util.get_host_address(config)
    url =  "https://" +  hmc_host + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": storage.CONTENT_TYPE}
    vopt_name = util.get_vopt_name(config)
    payload = storage.populate_payload(hmc_host, partition_uuid, sys_uuid, vopt_name)
    response = requests.post(url, headers=headers, cookies=cookies, data=payload, verify=False)

    if response.status_code != 200:
        print("Failed to attach virtual storage to the partition ", response.text)
        exit()
    return

def activate_partititon(config, cookies, partition_uuid):
    uri = f"/rest/api/uom/LogicalPartition/{partition_uuid}/do/PowerOn"
    url =  "https://" +  util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": activation.CONTENT_TYPE}
    response = requests.put(url, headers=headers, cookies=cookies, data=activation.PAYLOAD, verify=False)
    print("response ", response.text)
    if response.status_code != 200:
        print("Failed to activate partition %s", partition_uuid)
        exit()
    return

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

    print("7. Attach virtual storage to the partition")
    vios_uuid = get_vios_uuid(config, cookies, sys_uuid)
    attach_storage(config, cookies, partition_uuid, sys_uuid, vios_uuid)
    print("----------- Attach virtual storage done -----------")

    print("8. Attach vOpt to the partition")
    attach_vopt(config, cookies, partition_uuid, sys_uuid, vios_uuid)
    print("----------- Attach vOpt storage done -----------")

    print("9. Activate the partition")
    activate_partititon(config, cookies, partition_uuid)
    print("----------- Activate partition done -----------")

    
    #print("9. Reboot the system")
    #print("10. Shutdown partition")


print("Starting ASE lifecycle manager")
start_manager()
