import string_util as util
from bs4 import BeautifulSoup


CONTENT_TYPE = "application/vnd.ibm.powervm.uom+xml; Type=VirtualIOServer"

def populate_payload(vios_payload, hmc_host, partition_uuid, system_uuid, physical_volume_name):
    physical_vol = f'''
    <VirtualSCSIMapping schemaVersion="V1_0">
            <Metadata>
                <Atom/>
            </Metadata>
            <AssociatedLogicalPartition kb="CUR" kxe="false" href="https://{hmc_host}/rest/api/uom/ManagedSystem/{system_uuid}/LogicalPartition/{partition_uuid}" rel="related"/>
            <Storage kxe="false" kb="CUR">
                <PhysicalVolume schemaVersion="V1_0">
                    <Metadata>
                        <Atom/>
                    </Metadata>
                    <Description kxe="false" kb="CUD">SAS RAID 0 Disk Array</Description>
                    <LocationCode kxe="false" kb="ROR">U78D3.001.WZS069F-P1-C49-L40771AFE00-L0</LocationCode>
                    <ReservePolicy kb="CUD" kxe="false">NoReserve</ReservePolicy>
                    <ReservePolicyAlgorithm kb="CUD" kxe="false">Failover</ReservePolicyAlgorithm>
                    <AvailableForUsage kb="CUD" kxe="false">true</AvailableForUsage>
                    <VolumeCapacity kxe="false" kb="CUR">544792</VolumeCapacity>
                    <VolumeName kb="CUR" kxe="false">{physical_volume_name}</VolumeName>
                    <VolumeState kb="ROR" kxe="false">active</VolumeState>
                    <IsFibreChannelBacked kb="ROR" kxe="false">false</IsFibreChannelBacked>
                    <IsISCSIBacked ksv="V1_8_0" kb="ROR" kxe="false">false</IsISCSIBacked>
                    <StorageLabel ksv="V1_3_0" kxe="false" kb="ROR">VU5LTk9XTg==</StorageLabel>
                    <DescriptorPage83 ksv="V1_5_0" kb="ROR" kxe="false">SUJNICAgICBJUFItMCAgIDc3MUFGRTAwMDAwMDAwNDA=</DescriptorPage83>
                </PhysicalVolume>
            </Storage>
        </VirtualSCSIMapping>
'''
    phys_bs = BeautifulSoup(physical_vol, 'xml')
    vios_bs = BeautifulSoup(vios_payload, 'xml')
    scsi_mappings = vios_bs.find('VirtualSCSIMappings')
    scsi_mappings.append(phys_bs)
    payload = str(vios_bs)
    return payload