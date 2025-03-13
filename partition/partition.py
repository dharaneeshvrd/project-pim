import logging
import requests
from bs4 import BeautifulSoup

import utils.string_util as util
import utils.common as common

logger = common.get_logger("partition")

CONTENT_TYPE = "application/vnd.ibm.powervm.uom+xml; Type=LogicalPartition"

def populate_payload(config):
    partition_name = util.get_partition_name(config) + "-pim"
    return f'''
<LogicalPartition:LogicalPartition xmlns:LogicalPartition="http://www.ibm.com/xmlns/systems/power/firmware/uom/mc/2012_10/" xmlns="http://www.ibm.com/xmlns/systems/power/firmware/uom/mc/2012_10/" xmlns:ns2="http://www.w3.org/XML/1998/namespace/k2" schemaVersion="V1_8_0">
    <CurrentProfileSync>On</CurrentProfileSync>
    <PartitionMemoryConfiguration kb="CUD" kxe="false" schemaVersion="V1_8_0">
        <Metadata>
            <Atom/>
        </Metadata>
        <DesiredMemory kb="CUD" kxe="false">{util.get_desired_memory(config)}</DesiredMemory>
        <MaximumMemory kb="CUD" kxe="false">{util.get_max_memory(config)}</MaximumMemory>
        <MinimumMemory kb="CUD" kxe="false">{util.get_min_memory(config)}</MinimumMemory>
    </PartitionMemoryConfiguration>
    <PartitionName kxe="false" kb="CUR">{partition_name}</PartitionName>
    <PartitionProcessorConfiguration kb="CUD" kxe="false" schemaVersion="V1_8_0">
        <Metadata>
            <Atom/>
        </Metadata>
        <DedicatedProcessorConfiguration kb="CUD" kxe="false" schemaVersion="V1_8_0">
            <Metadata>
                <Atom/>
            </Metadata>
            <DesiredProcessors kb="CUD" kxe="false">{util.get_desired_proc(config)}</DesiredProcessors>
            <MaximumProcessors kxe="false" kb="CUD">{util.get_max_proc(config)}</MaximumProcessors>
            <MinimumProcessors kb="CUD" kxe="false">{util.get_min_proc(config)}</MinimumProcessors>
        </DedicatedProcessorConfiguration>
        <HasDedicatedProcessors kxe="false" kb="CUD">{util.has_dedicated_proc(config)}</HasDedicatedProcessors>
        <SharingMode kxe="false" kb="CUD">{util.get_sharing_mode(config)}</SharingMode>
    </PartitionProcessorConfiguration>
    <PartitionType kxe="false" kb="COD">{util.get_partition_type(config)}</PartitionType>
</LogicalPartition:LogicalPartition>
'''

def get_bootorder_payload(partition_payload, bootorder):
    lpar_bs =  BeautifulSoup(partition_payload, 'xml')
    pending_boot = lpar_bs.find("PendingBootString")
    pending_boot.append(bootorder)
    return str(lpar_bs)

def create_partition(config, cookies, system_uuid):
    uri = f"/rest/api/uom/ManagedSystem/{system_uuid}/LogicalPartition"
    url = "https://" +  util.get_host_address(config) + uri
    payload = populate_payload(config)
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": CONTENT_TYPE}
    response = requests.put(url, headers=headers, data=payload, cookies=cookies, verify=False)
    if response.status_code != 200:
        logger.error(f"Failed to create partition {response.text}")
        exit()

    soup = BeautifulSoup(response.text, 'xml')
    partition_uuid = soup.find("PartitionUUID")
    return partition_uuid.text

def get_partition_details(config, cookies, system_uuid, partition_uuid):
    uri = f"/rest/api/uom/ManagedSystem/{system_uuid}/LogicalPartition/{partition_uuid}"
    url =  "https://" +  util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": "application/vnd.ibm.powervm.uom+xml; Type=LogicalPartition"}
    response = requests.get(url, headers=headers, cookies=cookies, verify=False)
    if response.status_code != 200:
        logger.error(f"Failed to get partition details {response.text}")
        common.cleanup_and_exit(1)
    soup = BeautifulSoup(response.text, 'xml')
    lpar = str(soup.find('LogicalPartition'))
    return lpar

def update_partition(config, cookies, system_uuid, partition_uuid, partition_payload, lun):
    uri = f"/rest/api/uom/ManagedSystem/{system_uuid}/LogicalPartition/{partition_uuid}"
    url =  "https://" +  util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": "application/vnd.ibm.powervm.uom+xml; Type=LogicalPartition"}
    payload = get_bootorder_payload(partition_payload, lun)
    response = requests.post(url, headers=headers, cookies=cookies, data=payload, verify=False)
    if response.status_code != 200:
        logger.error(f"Failed to attach virtual storage to the partition {response.text}")
        common.cleanup_and_exit(1)
    logger.info(f"Updated the bootorder for the partition: {partition_uuid}")
    return
