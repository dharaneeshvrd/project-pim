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

def copy_iso(config):
    scp_port = 22
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    host_ip = util.get_host_address(config)
    username = util.get_host_username(config)
    password = util.get_host_password(config)
    iso = util.get_iso(config)
    remote_path=util.get_iso_target_path(config)

    client.connect(host_ip, 22, username, password)
    scp = SCPClient(client.get_transport())
    scp.put(iso, remote_path=remote_path)
    print("ISO file copy success!!")

def authenticate_hmc(config):
    # Populate Authentication payload
    auth.populate_payload(util.get_host_username(config), util.get_host_password(config))
    url = "https://" + util.get_host_address(config) + auth.URI
    headers = {"Content-Type": auth.CONTENT_TYPE, "Accept": auth.ACCEPT}
    resp = requests.put(url, headers=headers, data=auth.PAYLOAD, verify=False)
    root = ET.fromstring(resp.text)
    SESSION_KEY = ""
    for child in root.iter():
        if "X-API-Session" in child.tag:
            SESSION_KEY = child.text

    return SESSION_KEY, resp.cookies

def get_system_uuid(config, cookies):
    uri = "/rest/api/uom/ManagedSystem/quick/All"
    url = "https://" + util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config)}
    session = requests.Session()
    response = session.get(url, headers=headers, cookies=cookies, verify=False)

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
    print("url: ", url)
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": partition.CONTENT_TYPE}
    response = requests.put(url, headers=headers, data=partition.PAYLOAD, cookies=cookies, verify=False)
    if response.status_code != 200:
        print("Failed to create partition")
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

def attach_network(config, cookies, partition_uuid):
    uri = f"/rest/api/uom/LogicalPartition/{partition_uuid}/ClientNetworkAdapter"
    url =  "https://" +  util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": virtual_network.CONTENT_TYPE}
    response = requests.put(url, headers=headers, cookies=cookies, data=virtual_network.PAYLOAD, verify=False)
    if response.status_code != 200:
        print("Failed to attach virtual network to the partition")
        exit()
    return

def attach_storage(config, cookies, system_uuid, vios_uuid):
    uri = f"/rest/api/uom/ManagedSystem/{system_uuid}/VirtualIOServer/{vios_uuid}"
    url =  "https://" +  util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": storage.CONTENT_TYPE}
    response = requests.put(url, headers=headers, data=virtual_network.PAYLOAD, verify=False)
    if response.status_code != 200:
        print("Failed to attach virtual network to the partition")
        exit()
    return

def activate_partititon(config, cookies, partition_uuid):
    uri = f"/rest/api/uom/LogicalPartition/{partition_uuid}/do/PowerOn"
    url =  "https://" +  util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": activation.CONTENT_TYPE}
    response = requests.put(url, headers=headers, cookies=cookies, data=activation.PAYLOAD, verify=False)
    if response.status_code != 200:
        print("Failed to activate partition %s", partition_uuid)
        exit()
    return

def start_manager():
    print("1. Initilaize and parse configuration")
    config = initialize()
    print("----------- Initialize done ----------------------")

    print("2. Copy ISO file to VIOS server")
    #copy_iso(config)
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
    #partition_uuid = create_partition(config, cookies, sys_uuid)
    partition_uuid = "77F1CA69-7751-46A4-A766-C941A7DD6C06"
    print("partition creation success. partition UUID: %s", partition_uuid)
    print("----------- Create partition done -----------")

    print("6. Attach Network to the partition")
    #attach_network(config, cookies, partition_uuid)
    print("----------- Attach network done -----------")

    print("7. Attach VIOS storage to the partition")
    #attach_storage(config, cookies, vios_uuid)

    print("8. Attach vOpt to the partition")

    print("9. Activate the partition")
    activate_partititon(config, cookies, partition_uuid)
    print("----------- Activate partition done -----------")

    
    #print("9. Reboot the system")
    #print("10. Shutdown partition")


print("Starting ASE lifecycle manager")
start_manager()
