import requests
from bs4 import BeautifulSoup

from .activation import check_lpar_status
from .partition_exception import PartitionError
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
        <DesiredMemory kb="CUD" kxe="false">{convert_gb_to_mb(util.get_desired_memory(config))}</DesiredMemory>
        <MaximumMemory kb="CUD" kxe="false">{convert_gb_to_mb(util.get_max_memory(config))}</MaximumMemory>
        <MinimumMemory kb="CUD" kxe="false">{convert_gb_to_mb(util.get_min_memory(config))}</MinimumMemory>
    </PartitionMemoryConfiguration>
    <PartitionName kxe="false" kb="CUR">{partition_name}</PartitionName>
    <PartitionProcessorConfiguration kb="CUD" kxe="false" schemaVersion="V1_8_0">
        <Metadata>
            <Atom/>
        </Metadata>
        {get_processor_config(config)}
        <SharingMode kxe="false" kb="CUD">{util.get_sharing_mode(config)}</SharingMode>
    </PartitionProcessorConfiguration>
    <PartitionType kxe="false" kb="COD">{util.get_partition_type(config)}</PartitionType>
</LogicalPartition:LogicalPartition>
'''

def get_processor_config(config):
    if util.has_dedicated_proc(config) == "true":
        return f'''<DedicatedProcessorConfiguration kb="CUD" kxe="false" schemaVersion="V1_8_0">
            <Metadata>
                <Atom/>
            </Metadata>
            <DesiredProcessors kb="CUD" kxe="false">{util.get_desired_proc(config)}</DesiredProcessors>
            <MaximumProcessors kxe="false" kb="CUD">{util.get_max_proc(config)}</MaximumProcessors>
            <MinimumProcessors kb="CUD" kxe="false">{util.get_min_proc(config)}</MinimumProcessors>
        </DedicatedProcessorConfiguration>
        <HasDedicatedProcessors kxe="false" kb="CUD">{util.has_dedicated_proc(config)}</HasDedicatedProcessors>'''

    return f'''<HasDedicatedProcessors kxe="false" kb="CUD">{util.has_dedicated_proc(config)}</HasDedicatedProcessors>
        <SharedProcessorConfiguration kb="CUD" kxe="false" schemaVersion="V1_0">
            <Metadata>
                <Atom />
            </Metadata>
            <DesiredProcessingUnits kb="CUD" kxe="false">{util.get_shared_desired_proc(config)}</DesiredProcessingUnits>
            <DesiredVirtualProcessors kb="CUD" kxe="false">{util.get_shared_desired_virt_proc(config)}</DesiredVirtualProcessors>
            <MaximumProcessingUnits kb="CUD" kxe="false">{util.get_shared_max_proc(config)}</MaximumProcessingUnits>
            <MaximumVirtualProcessors kb="CUD" kxe="false">{util.get_shared_max_virt_proc(config)}</MaximumVirtualProcessors>
            <MinimumProcessingUnits kb="CUD" kxe="false">{util.get_shared_min_proc(config)}</MinimumProcessingUnits>
            <MinimumVirtualProcessors kb="CUD" kxe="false">{util.get_shared_min_virt_proc(config)}</MinimumVirtualProcessors>
        </SharedProcessorConfiguration>''' 

def get_bootorder_payload(partition_payload, bootorder):
    lpar_bs =  BeautifulSoup(partition_payload, 'xml')
    pending_boot = lpar_bs.find("PendingBootString")
    pending_boot.append(bootorder)
    return str(lpar_bs)

def convert_gb_to_mb(value):
    return int(value) * 1024

def create_partition(config, cookies, system_uuid):
    uri = f"/rest/api/uom/ManagedSystem/{system_uuid}/LogicalPartition"
    url = "https://" +  util.get_host_address(config) + uri
    payload = populate_payload(config)
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": CONTENT_TYPE}
    response = requests.put(url, headers=headers, data=payload, cookies=cookies, verify=False)
    if response.status_code != 200:
        logger.error(f"failed to create partition, error: {response.text}")
        raise PartitionError(f"failed to create partition, error: {response.text}")

    soup = BeautifulSoup(response.text, 'xml')
    partition_uuid = soup.find("PartitionUUID")
    return partition_uuid.text

def get_partition_details(config, cookies, system_uuid, partition_uuid):
    uri = f"/rest/api/uom/ManagedSystem/{system_uuid}/LogicalPartition/{partition_uuid}"
    url =  "https://" +  util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": "application/vnd.ibm.powervm.uom+xml; Type=LogicalPartition"}
    response = requests.get(url, headers=headers, cookies=cookies, verify=False)
    if response.status_code != 200:
        logger.error(f"failed to get partition details, error: {response.text}")
        raise PartitionError(f"failed to get partition details, error: {response.text}")
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
        logger.error(f"failed to attach virtual storage to the partition, error: {response.text}")
        raise PartitionError(f"failed to attach virtual storage to the partition, error: {response.text}")
    logger.info(f"Updated the bootorder for the partition: {partition_uuid}")
    return

def remove_partition(config, cookies, partition_uuid):
    uri = f"/rest/api/uom/LogicalPartition/{partition_uuid}"
    url = "https://" +  util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": "application/vnd.ibm.powervm.uom+xml; Type=LogicalPartition"}
    response = requests.delete(url, headers=headers, cookies=cookies, verify=False)
    if response.status_code != 204:
        logger.error(f"failed to delete partition, error: {response.text}")
        return
    logger.info("Partition deleted successfully")
