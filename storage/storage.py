import requests
from bs4 import BeautifulSoup

import utils.string_util as util
import utils.common as common

CONTENT_TYPE = "application/vnd.ibm.powervm.uom+xml; Type=VirtualIOServer"

def populate_payload(vios_payload, hmc_host, partition_uuid, system_uuid, physical_volume_name, slot):
    physical_vol = f'''
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

def attach_storage(vios_payload, config, cookies, partition_uuid, system_uuid, vios_uuid, slot):
    uri = f"/rest/api/uom/ManagedSystem/{system_uuid}/VirtualIOServer/{vios_uuid}"
    hmc_host = util.get_host_address(config)
    url =  "https://" +  hmc_host + uri
    physical_vol_name = util.get_physical_volume_name(config)
    payload = populate_payload(vios_payload, hmc_host, partition_uuid, system_uuid, physical_vol_name, slot)
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": CONTENT_TYPE}
    response = requests.post(url, headers=headers, cookies=cookies, data=payload, verify=False)

    if response.status_code != 200:
        print("Failed to attach virtual storage to the partition ", response.text)
        common.cleanup_and_exit(config, cookies, 1)
    return