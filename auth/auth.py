import requests
from bs4 import BeautifulSoup

import utils.string_util as util

CONTENT_TYPE = "application/vnd.ibm.powervm.web+xml; type=LogonRequest"
ACCEPT = "application/vnd.ibm.powervm.web+xml; type=LogonResponse"
URI = "/rest/api/web/Logon"

def populate_payload(config):
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<LogonRequest xmlns="http://www.ibm.com/xmlns/systems/power/firmware/web/mc/2012_10/" schemaVersion="V1_1_0">
    <Metadata>
        <Atom/>
    </Metadata>
    <UserID kb="CUR" kxe="false">{util.get_host_username(config)}</UserID>
    <Password kb="CUR" kxe="false">{util.get_host_password(config)}</Password>
</LogonRequest>
'''

def authenticate_hmc(config):
    # Populate Authentication payload
    payload = populate_payload(config)
    url = "https://" + util.get_host_address(config) + URI
    headers = {"Content-Type": CONTENT_TYPE, "Accept": ACCEPT}
    response = requests.put(url, headers=headers, data=payload, verify=False)
    if response.status_code != 200:
        print("Failed to authenticate hmc ", response.text)
        exit()

    soup = BeautifulSoup(response.text, 'xml')
    session_key = soup.find("X-API-Session")
    return session_key.text, response.cookies

def delete_session(config, cookies):
    url = "https://" + util.get_host_address(config) + URI
    headers = {"x-api-key": util.get_session_key(config)}
    response = requests.delete(url, cookies=cookies, headers=headers, verify=False)
    if response.status_code != 204:
        print("Failed to delete session on hmc ", response.text)
        exit(1)
    print("Loged off HMC session successfully")
    return
