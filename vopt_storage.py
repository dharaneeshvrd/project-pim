import string_util as util
from bs4 import BeautifulSoup

CONTENT_TYPE = "application/vnd.ibm.powervm.uom+xml; Type=VirtualIOServer"

def populate_payload(vios_payload, hmc_host, partition_uuid, system_uuid, vopt_name):
    vopt_vol = f'''
    <VirtualSCSIMapping schemaVersion="V1_0">
        <Metadata>
            <Atom/>
        </Metadata>
        <AssociatedLogicalPartition kb="CUR" kxe="false" href="https://{hmc_host}/rest/api/uom/ManagedSystem/{system_uuid}/LogicalPartition/{partition_uuid}" rel="related"/>
        <Storage kxe="false" kb="CUR">
            <VirtualOpticalMedia schemaVersion="V1_0">
                <Metadata>
                    <Atom/>
                </Metadata>
                <MediaName kxe="false" kb="CUR">{vopt_name}</MediaName>
                <MountType kxe="false" kb="CUD">r</MountType>
                <Size kb="CUR" kxe="false">0.1221</Size>
            </VirtualOpticalMedia>
        </Storage>
    </VirtualSCSIMapping>
'''
    vopt_bs = BeautifulSoup(vopt_vol, 'xml')
    vios_bs = BeautifulSoup(vios_payload, 'xml')
    scsi_mappings = vios_bs.find('VirtualSCSIMappings')
    scsi_mappings.append(vopt_bs)
    payload = str(vios_bs)
    return payload
