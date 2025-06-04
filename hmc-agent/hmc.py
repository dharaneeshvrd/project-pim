import requests
from bs4 import BeautifulSoup

CONTENT_TYPE = "application/vnd.ibm.powervm.web+xml; type=LogonRequest"
ACCEPT = "application/vnd.ibm.powervm.web+xml; type=LogonResponse"
URI = "/rest/api/web/Logon"

def populate_payload(username, password):
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<LogonRequest xmlns="http://www.ibm.com/xmlns/systems/power/firmware/web/mc/2012_10/" schemaVersion="V1_1_0">
    <Metadata>
        <Atom/>
    </Metadata>
    <UserID kb="CUR" kxe="false">{username}</UserID>
    <Password kb="CUR" kxe="false">{password}</Password>
</LogonRequest>
'''

def authenticate_hmc(hmc_creds: dict):
    # Populate Authentication payload
    payload = populate_payload(hmc_creds["hmc_username"], hmc_creds["hmc_password"])
    url = "https://" + hmc_creds["hmc_ip"] + URI
    headers = {"Content-Type": CONTENT_TYPE, "Accept": ACCEPT}
    response = requests.put(url, headers=headers, data=payload, verify=False)
    if response.status_code != 200:
        raise Exception(f"failed to authenticate HMC, error: {response.text}")

    soup = BeautifulSoup(response.text, 'xml')
    session_key = soup.find("X-API-Session")
    return session_key.text, response.cookies

def get_hmc_version(ip, session_key, cookies):
    uri = f"/rest/api/uom/ManagementConsole"
    url =  "https://" + ip + uri
    headers = {"x-api-key": session_key}
    response = requests.get(url, headers=headers, cookies=cookies, verify=False)
    print(f"status: {response.status_code}")
    if response.status_code != 200:
        print("failed to get hmc version")
        return
    soup = BeautifulSoup(response.text, 'xml')
    version_info = soup.find("VersionInfo")
    major_ver = version_info.find("Version").text
    min_ver = version_info.find("Minor").text
    serv_pack_name = version_info.find("ServicePackName").text
    return major_ver, min_ver, serv_pack_name

def list_all_systems(ip, session_key, cookies):
    uri = f"rest/api/uom/ManagedSystem/quick/All"
    url =  "https://" + ip + uri
    headers = {"x-api-key": session_key}
    response = requests.get(url, headers=headers, cookies=cookies, verify=False)
    if response.status_code != 200:
        print("failed to get hmc version")
        return
    list_of_systems = response.json()
    list_of_sys_names = []
    for system in list_of_systems:
        list_of_sys_names.append(system["SystemName"])
    return list_of_sys_names

def get_logical_partitions(ip, session_key, cookies):
    uri = f"/rest/api/uom/LogicalPartition/quick/All"
    url = f"https://{ip}{uri}"
    headers = {"x-api-key": session_key}
    response = requests.get(url, headers=headers, cookies=cookies, verify=False)
    print(f"status: {response.status_code}")
    if response.status_code != 200:
        print("failed to get logical partitions")
        return []
    partitions = response.json()
    vm_list = []
    for lpar in partitions:
        name = lpar["PartitionName"] 
        lpar_id = lpar["PartitionID"]
        state = lpar["PartitionState"]
        vm_list.append({
            "name": name,
            "id": lpar_id,
            "state": state
        })

    return vm_list