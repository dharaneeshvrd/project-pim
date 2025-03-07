import requests
import time
from bs4 import BeautifulSoup

import utils.string_util as util

CONTENT_TYPE = "application/vnd.ibm.powervm.web+xml; Type=JobRequest"

def populated_payload(lpar_profile_id):
    return f'''
<JobRequest xmlns="http://www.ibm.com/xmlns/systems/power/firmware/web/mc/2012_10/"  xmlns:ns2="http://www.w3.org/XML/1998/namespace/k2" schemaVersion="V1_0">
    <Metadata>
        <Atom/>
    </Metadata>
    <RequestedOperation kxe="false" kb="CUR" schemaVersion="V1_0">
    <Metadata>
    <Atom/>
    </Metadata>
    <OperationName kxe="false" kb="ROR">PowerOn</OperationName>
    <GroupName kxe="false" kb="ROR">LogicalPartition</GroupName>
    </RequestedOperation>
    <JobParameters kb="CUR" kxe="false" schemaVersion="V1_0">
        <Metadata>
            <Atom/>
        </Metadata>
	<JobParameter schemaVersion="V1_0">
        <Metadata>
            <Atom/>
        </Metadata>
        <ParameterName kxe="false" kb="ROR">force</ParameterName>
       <ParameterValue kxe="false" kb="CUR">false</ParameterValue>
    </JobParameter>
    <JobParameter schemaVersion="V1_0">
        <Metadata>
            <Atom/>
        </Metadata>
        <ParameterName kxe="false" kb="ROR">LogicalPartitionProfile</ParameterName>
        <ParameterValue kxe="false" kb="CUR">{lpar_profile_id}</ParameterValue>
    </JobParameter>
    <JobParameter schemaVersion="V1_0">
        <Metadata>
            <Atom/>
        </Metadata>
        <ParameterName kxe="false" kb="ROR">novsi</ParameterName>
        <ParameterValue kxe="false" kb="CUR">true</ParameterValue>
    </JobParameter>
    <JobParameter schemaVersion="V1_0">
        <Metadata>
            <Atom/>
        </Metadata>
        <ParameterName kxe="false" kb="ROR">bootmode</ParameterName>
        <ParameterValue kxe="false" kb="CUR">norm</ParameterValue>
    </JobParameter>
    <JobParameter schemaVersion="V1_0">
        <Metadata>
            <Atom/>
        </Metadata>
        <ParameterName kxe="false" kb="ROR">keylock</ParameterName>
        <ParameterValue kxe="false" kb="CUR">manual</ParameterValue>
    </JobParameter>
   </JobParameters>
</JobRequest>
'''

def shutdown_payload():
    return f"""
    <JobRequest xmlns="http://www.ibm.com/xmlns/systems/power/firmware/web/mc/2012_10/"  xmlns:ns2="http://www.w3.org/XML/1998/namespace/k2" schemaVersion="V1_0">
        <Metadata>
        <Atom/>
        </Metadata>
    <RequestedOperation kxe="false" kb="CUR" schemaVersion="V1_0">
        <Metadata>
        <Atom/>
        </Metadata>
        <OperationName kxe="false" kb="ROR">PowerOff</OperationName>
        <GroupName kxe="false" kb="ROR">LogicalPartition</GroupName>
    </RequestedOperation>
    <JobParameters kxe="false" kb="CUR" schemaVersion="V1_0">
        <Metadata>
        <Atom/>
        </Metadata>
        <JobParameter schemaVersion="V1_0">
        <Metadata>
            <Atom/>
        </Metadata>
        <ParameterName kb="ROR" kxe="false">immediate</ParameterName>
        <ParameterValue kxe="false" kb="CUR">true</ParameterValue>
    </JobParameter>
    <JobParameter schemaVersion="V1_0">
        <Metadata>
            <Atom/>
        </Metadata>
        <ParameterName kb="ROR" kxe="false">restart</ParameterName>
        <ParameterValue kxe="false" kb="CUR">false</ParameterValue>
    </JobParameter>
    <JobParameter schemaVersion="V1_0">
        <Metadata>
            <Atom/>
        </Metadata>
        <ParameterName kb="ROR" kxe="false">operation</ParameterName>
        <ParameterValue kxe="false" kb="CUR">shutdown</ParameterValue>
        </JobParameter>
    </JobParameters>
</JobRequest>
"""

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
    soup = BeautifulSoup(response, 'xml')
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
    payload = populated_payload(lpar_profile_id)

    headers = {"x-api-key": util.get_session_key(config), "Content-Type": CONTENT_TYPE}
    response = requests.put(url, headers=headers, cookies=cookies, data=payload, verify=False)
    if response.status_code != 200:
        print(f"Failed to activate partition {partition_uuid}")
        exit()
    # check job status for COMPLETED_OK
    status = check_job_status(config, cookies, response.text)
    if not status:
        print(f"Failed to activate partition {partition_uuid}")
        exit()
    print("Partition activated successfully.")
    return

def shutdown_paritition(config, cookies, partition_uuid):
    uri = f"/rest/api/uom/LogicalPartition/{partition_uuid}/do/PowerOff"
    url =  "https://" + util.get_host_address(config) + uri
    payload = shutdown_payload()
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": CONTENT_TYPE}
    response = requests.put(url, headers=headers, cookies=cookies, data=payload, verify=False)
    if response.status_code != 200:
        print(f"Failed to shutdown partition {partition_uuid}")
        exit()
    # check job status for COMPLETED_OK
    status = check_job_status(config, cookies, response)
    if not status:
        print(f"Failed to shutdown partition {partition_uuid}")
        exit()
    print("Partition shutdown successfully.")
    return
