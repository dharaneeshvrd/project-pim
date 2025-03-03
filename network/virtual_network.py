import requests
from bs4 import BeautifulSoup

import utils.string_util as util

CONTENT_TYPE = "application/vnd.ibm.powervm.uom+xml; Type=ClientNetworkAdapter"
PAYLOAD = '''
<ClientNetworkAdapter:ClientNetworkAdapter xmlns:ClientNetworkAdapter="http://www.ibm.com/xmlns/systems/power/firmware/uom/mc/2012_10/" xmlns="http://www.ibm.com/xmlns/systems/power/firmware/uom/mc/2012_10/" xmlns:ns2="http://www.w3.org/XML/1998/namespace/k2" schemaVersion="V1_0">
    <Metadata>
        <Atom>
        </Atom>
    </Metadata>
    <PortVLANID kb="CUR" kxe="false">2133</PortVLANID>
    <VirtualSwitchID kxe="false" kb="ROR">0</VirtualSwitchID>
    <VirtualSwitchName ksv="V1_12_0" kb="ROR" kxe="false">ETHERNET0</VirtualSwitchName>
</ClientNetworkAdapter:ClientNetworkAdapter>
'''

def populate_payload(vlanid, vswitchid, vswitchname):
    return f'''
<ClientNetworkAdapter:ClientNetworkAdapter xmlns:ClientNetworkAdapter="http://www.ibm.com/xmlns/systems/power/firmware/uom/mc/2012_10/" xmlns="http://www.ibm.com/xmlns/systems/power/firmware/uom/mc/2012_10/" xmlns:ns2="http://www.w3.org/XML/1998/namespace/k2" schemaVersion="V1_0">
    <Metadata>
        <Atom>
        </Atom>
    </Metadata>
    <PortVLANID kb="CUR" kxe="false">{vlanid}</PortVLANID>
    <VirtualSwitchID kxe="false" kb="ROR">{vswitchid}</VirtualSwitchID>
    <VirtualSwitchName ksv="V1_12_0" kb="ROR" kxe="false">{vswitchname}</VirtualSwitchName>
</ClientNetworkAdapter:ClientNetworkAdapter>
'''

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
    
    soup = BeautifulSoup(response.text, 'xml')
    vlan_id = soup.find("NetworkVLANID")
    vswitch_id = soup.find("VswitchID")

    return vlan_id.text, vswitch_id.text

def attach_network(config, cookies, system_uuid, partition_uuid):
    # Get VLAN ID and VSWITCH ID
    vlan_id, vswitch_id = get_vlan_details(config, cookies, system_uuid)
    payload = populate_payload(vlan_id, vswitch_id, util.get_vswitch_name(config))

    uri = f"/rest/api/uom/LogicalPartition/{partition_uuid}/ClientNetworkAdapter"
    url =  "https://" +  util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": CONTENT_TYPE}
    response = requests.put(url, headers=headers, cookies=cookies, data=payload, verify=False)
    if response.status_code != 200:
        print("Failed to attach virtual network to the partition ", response.text)
        exit()
    return
