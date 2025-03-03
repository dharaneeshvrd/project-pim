import string_util as util
from bs4 import BeautifulSoup
import random, string

CONTENT_TYPE = "application/vnd.ibm.powervm.uom+xml; Type=LogicalPartition"

def populate_payload(config):
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
    <PartitionName kxe="false" kb="CUR">{generate_partition_name()}</PartitionName>
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

def generate_partition_name():
    random_hexa_str = ''.join(random.choices("abcdef" + string.digits, k=8))
    return "lpar-bootc-{}".format(random_hexa_str)
