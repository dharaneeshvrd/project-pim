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
                    <VolumeName kb="CUR" kxe="false">{physical_volume_name}</VolumeName>
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