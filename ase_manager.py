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

    host_ip = config.get("VIOS_SERVER", "host_address").strip('"')
    username = config.get("VIOS_SERVER", "username").strip('"')
    password = config.get("VIOS_SERVER", "password").strip('"')
    iso = config.get("CUSTOM_ISO", "iso").strip('"')
    remote_path=config.get("CUSTOM_ISO", "target_path").strip('"')

    client.connect(host_ip, 22, username, password)
    scp = SCPClient(client.get_transport())
    scp.put(iso, remote_path=remote_path)
    print("ISO file copy success!!")

def authenticate_hmc(config):
    # Populate Authentication payload
    auth.populate_payload(config.get("HMC_HOST", "username").strip('"'), config.get("HMC_HOST", "password").strip('"'))
    url = "https://" + config.get("HMC_HOST", "host_address").strip('"') + auth.URI
    headers = {"Content-Type": auth.CONTENT_TYPE, "Accept": auth.ACCEPT}
    resp = requests.put(url, headers=headers, data=auth.PAYLOAD, verify=False)
    root = ET.fromstring(resp.text)
    SESSION_KEY = ""
    for child in root.iter():
        if "X-API-Session" in child.tag:
            SESSION_KEY = child.text

    return SESSION_KEY

def get_system_uuid(config):
    uri = "/rest/api/uom/ManagedSystem/quick/All"
    url = "https://" + config.get("HMC_HOST", "host_address") + uri
    headers = {"x-api-key": config.get("SESSION", "x-api-key")}
    response = requests.get(url, headers=headers, payload={})
    try: 
        systems = response.json()
    except requests.JSONDecodeError:
        print("response is not valid json")

    uuid = ""
    sys_name = config.get("SYSTEM", "name")
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

def create_partition(config, system_uuid):
    uri = f"rest/api/uom/ManagedSystem/{system_uuid}/LogicalPartition"
    url = "https://" +  config.get("HMC_HOST", "host_address") + uri
    headers = {"x-api-key": config.get("SESSION", "x-api-key"), "Content-Type": partition.CONTENT_TYPE}
    response = requests.put(url, headers=headers, payload=partition.PAYLOAD)
    if response.status != 200:
        print("Failed to create partition")
        exit()

    #partition response will be in XML
    partition_data = response.text
    print("response: ", partition_data)
    tree = ET.fromstring(partition_data)
    root = tree.getroot()
    return root.find("PartitionUUID").text

def attach_network(config, partition_uuid):
    uri = f"/rest/api/uom/LogicalPartition/{partition_uuid}/ClientNetworkAdapter"
    url =  "https://" +  config.get("HMC_HOST", "host_address") + uri
    headers = {"x-api-key": config.get("SESSION", "x-api-key"), "Content-Type": virtual_network.CONTENT_TYPE}
    response = requests.put(url, headers=headers, payload=virtual_network.PAYLOAD)
    if response.status != 200:
        print("Failed to attach virtual network to the partition")
        exit()
    return

def attach_storage(config, system_uuid, vios_uuid):
    uri = f"rest/api/uom/ManagedSystem/{system_uuid}/VirtualIOServer/{vios_uuid}"
    url =  "https://" +  config.get("HMC_HOST", "host_address") + uri
    headers = {"x-api-key": config.get("SESSION", "x-api-key"), "Content-Type": storage.CONTENT_TYPE}
    response = requests.put(url, headers=headers, payload=virtual_network.PAYLOAD)
    if response.status != 200:
        print("Failed to attach virtual network to the partition")
        exit()
    return

def activate_partititon(config, partition_uuid):
    uri = f"/rest/api/uom/LogicalPartition/{partition_uuid}/do/PowerOn"
    url =  "https://" +  config.get("HMC_HOST", "host_address") + uri
    headers = {"x-api-key": config.get("SESSION", "x-api-key"), "Content-Type": activation.CONTENT_TYPE}
    response = requests.put(url, headers=headers, payload=activation.PAYLOAD)
    if response.status != 200:
        print("Failed to activate partition %s", partition_uuid)
        exit()
    return

def start_manager():
    print("1. Initilaize and parse configuration")
    config = initialize()
    print("=========== Initialize done ========================")

    print("2. Copy ISO file to VIOS server")
    #copy_iso(config)
    print("=========== Copy ISO done ========================")

    print("3. Authenticate with HMC host")
    session_token = authenticate_hmc(config)
    print("token ", session_token)
    print("=========== Authenticate to HMC done ========================")

    config.add_section("SESSION")
    config.set("SESSION", "x-api-key", session_token)

    print("4. Get System UUID for target host")
    uuid = get_system_uuid(config)
    print("=========== Get System UUID done ========================")


    print("4. Create Partion on the target host")
    partition_uuid = create_partition(config)
    print("partition creation success. partition UUID: %s", partition_uuid)
    print("=========== Create partition done ========================")

    print("6. Attach Network to the partition")
    attach_network(config, partition_uuid)
    print("=========== Attach network done ========================")

    print("7. Attach VIOS storage to the partition")
    attach_storage(config, vios_uuid)

    print("8. Attach vOpt to the partition")

    print("9. Activate the partition")
    activate_partititon(config, partition_uuid)
    print("=========== Activate partition done ========================")

    
    #print("9. Reboot the system")
    #print("10. Shutdown partition")


print("Starting ASE lifecycle manager")
start_manager()

# xml_str = '''<?xml version="1.0" encoding="UTF-8"?>
# <library>
# <Metadata>
# <Atom>
# </Atom>
# </Metadata>
#  <book>
#    <title>The Great Gatsby</title>
#    <author>F. Scott Fitzgerald</author>
#    <year>1925</year>
#  </book>
# </library>'''

# xml_resp = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
# <LogonResponse xmlns="http://www.ibm.com/xmlns/systems/power/firmware/web/mc/2012_10/" xmlns:ns2="http://www.w3.org/XML/1998/namespace/k2" schemaVersion="V1_0">
#     <Metadata>
#         <Atom/>
#     </Metadata>
#     <X-API-Session kb="ROR" kxe="false">Ivq2wxwdH42qfYLSurUMgkaZZuRrYW4Rr8dN4WWufIQKGkdnETYv3RryYC9IpVGt4n62K2-Vs5VjaJ8c_36u3hy0IBPexlESu3vm9G0aKOr67pG9L0k4-6Us3ehGkMk_VmiTrkx3LCNl_Nk7nssBDEfSoEWL-S2yfNB4IzciWpXWveeIW5jOILzcFNXyoO7_AME0T4bKSU59_AL8eYR08Y-Hj6H3xoodLvMTiuhua4o=</X-API-Session>
# </LogonResponse>'''

# root = ET.fromstring(xml_resp)
# for child in root.iter():
#    print("tag ", child.tag)
#    if "X-API-Session" in child.tag:
#        print(child.text)


