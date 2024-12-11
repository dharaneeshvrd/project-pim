CONTENT_TYPE = "application/vnd.ibm.powervm.uom+xml; Type=LogicalPartition"
PAYLOAD = '''
<LogicalPartition:LogicalPartition xmlns:LogicalPartition="http://www.ibm.com/xmlns/systems/power/firmware/uom/mc/2012_10/" xmlns="http://www.ibm.com/xmlns/systems/power/firmware/uom/mc/2012_10/" xmlns:ns2="http://www.w3.org/XML/1998/namespace/k2" schemaVersion="V1_8_0">
    <PartitionMemoryConfiguration kb="CUD" kxe="false" schemaVersion="V1_8_0">
        <Metadata>
            <Atom/>
        </Metadata>
        <DesiredMemory kb="CUD" kxe="false">{desired_memory}</DesiredMemory>
        <MaximumMemory kb="CUD" kxe="false">{max_memory}</MaximumMemory>
        <MinimumMemory kb="CUD" kxe="false">{min_memory}</MinimumMemory>
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
            <DesiredProcessors kb="CUD" kxe="false">{desired_proc}</DesiredProcessors>
            <MaximumProcessors kxe="false" kb="CUD">{max_proc}</MaximumProcessors>
            <MinimumProcessors kb="CUD" kxe="false">{min_proc}</MinimumProcessors>
        </DedicatedProcessorConfiguration>
        <HasDedicatedProcessors kxe="false" kb="CUD">{has_dedicated_proc}</HasDedicatedProcessors>
        <SharingMode kxe="false" kb="CUD">{sharing_mode}</SharingMode>
    </PartitionProcessorConfiguration>
    <PartitionType kxe="false" kb="COD">{partition_type}</PartitionType>
</LogicalPartition:LogicalPartition>
'''