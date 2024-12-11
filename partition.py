CONTENT_TYPE = "application/vnd.ibm.powervm.uom+xml; Type=LogicalPartition"
PAYLOAD = '''
<LogicalPartition:LogicalPartition xmlns:LogicalPartition="http://www.ibm.com/xmlns/systems/power/firmware/uom/mc/2012_10/" xmlns="http://www.ibm.com/xmlns/systems/power/firmware/uom/mc/2012_10/" xmlns:ns2="http://www.w3.org/XML/1998/namespace/k2" schemaVersion="V1_8_0">
    <PartitionMemoryConfiguration kb="CUD" kxe="false" schemaVersion="V1_8_0">
        <Metadata>
            <Atom/>
        </Metadata>
        <DesiredMemory kb="CUD" kxe="false">16384</DesiredMemory>
        <MaximumMemory kb="CUD" kxe="false">16384</MaximumMemory>
        <MinimumMemory kb="CUD" kxe="false">4096</MinimumMemory>
    </PartitionMemoryConfiguration>
    <PartitionName kxe="false" kb="CUR">maac-ase-poc-lpar</PartitionName>
    <PartitionProcessorConfiguration kb="CUD" kxe="false" schemaVersion="V1_8_0">
        <Metadata>
            <Atom/>
        </Metadata>
        <DedicatedProcessorConfiguration kb="CUD" kxe="false" schemaVersion="V1_8_0">
            <Metadata>
                <Atom/>
            </Metadata>
            <DesiredProcessors kb="CUD" kxe="false">1</DesiredProcessors>
            <MaximumProcessors kxe="false" kb="CUD">1</MaximumProcessors>
            <MinimumProcessors kb="CUD" kxe="false">1</MinimumProcessors>
        </DedicatedProcessorConfiguration>
        <HasDedicatedProcessors kxe="false" kb="CUD">true</HasDedicatedProcessors>
        <SharingMode kxe="false" kb="CUD">sre idle proces</SharingMode>
    </PartitionProcessorConfiguration>
    <PartitionType kxe="false" kb="COD">AIX/Linux</PartitionType>
</LogicalPartition:LogicalPartition>
'''