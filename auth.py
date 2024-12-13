import string_util as util

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
</LogonRequest>'''

