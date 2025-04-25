import requests
from bs4 import BeautifulSoup

import utils.string_util as util
import utils.common as common
from .storage_exception import StorageError

logger = common.get_logger("storage")

CONTENT_TYPE = "application/vnd.ibm.powervm.uom+xml; Type=VirtualIOServer"

def populate_payload(vios_payload, hmc_host, partition_uuid, system_uuid, vopt_name, slot):
    vopt_vol_no_slot = f'''
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

    vopt_vol_slot = f'''
    <VirtualSCSIMapping schemaVersion="V1_0">
        <Metadata>
            <Atom/>
        </Metadata>
        <AssociatedLogicalPartition kb="CUR" kxe="false" href="https://{hmc_host}/rest/api/uom/ManagedSystem/{system_uuid}/LogicalPartition/{partition_uuid}" rel="related"/>
        <ClientAdapter kb="CUR" kxe="false" schemaVersion="V1_0">
            <Metadata>
                <Atom/>
            </Metadata>
            <AdapterType kxe="false" kb="ROR">Client</AdapterType>
            <VirtualSlotNumber kxe="false" kb="COD">{slot}</VirtualSlotNumber>
        </ClientAdapter>
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
    
    if slot == -1:
        vopt_vol = vopt_vol_no_slot
    else:
        vopt_vol = vopt_vol_slot

    vopt_bs = BeautifulSoup(vopt_vol, 'xml')
    vios_bs = BeautifulSoup(vios_payload, 'xml')
    scsi_mappings = vios_bs.find('VirtualSCSIMappings')
    scsi_mappings.append(vopt_bs)
    payload = str(vios_bs)
    return payload

def attach_vopt(vios_payload, config, cookies, partition_uuid, sys_uuid, vios_uuid, vopt_name, slot):
    uri = f"/rest/api/uom/ManagedSystem/{sys_uuid}/VirtualIOServer/{vios_uuid}"
    hmc_host = util.get_host_address(config)
    url =  "https://" +  hmc_host + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": "application/vnd.ibm.powervm.uom+xml; Type=VirtualIOServer"}
    #vopt_name = util.get_vopt_name(config)
    payload = populate_payload(vios_payload, hmc_host, partition_uuid, sys_uuid, vopt_name, slot)
    response = requests.post(url, headers=headers, cookies=cookies, data=payload, verify=False)

    if response.status_code != 200:
        logger.error(f"failed to attach virtual storage to the partition, error: {response.text}")
        raise StorageError(f"failed to attach virtual storage to the partition, error: {response.text}")
    return
