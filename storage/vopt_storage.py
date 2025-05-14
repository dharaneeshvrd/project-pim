import requests
from bs4 import BeautifulSoup

import utils.string_util as util
import utils.common as common
from .storage_exception import StorageError

logger = common.get_logger("storage")

CONTENT_TYPE = "application/vnd.ibm.powervm.uom+xml; Type=VirtualIOServer"

def get_vopt_scsi_mapping(hmc_host, partition_uuid, system_uuid, vopt_name):
    scsi_mapping = f'''
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
            </VirtualOpticalMedia>
        </Storage>
    </VirtualSCSIMapping>
    '''
    return BeautifulSoup(scsi_mapping, 'xml')

def populate_payload(config, vios_payload, hmc_host, partition_uuid, system_uuid, vopt_name):
    vios_bs = BeautifulSoup(vios_payload, 'xml')
    scsi_mappings = vios_bs.find('VirtualSCSIMappings')

    if vopt_name:
        bc_scsi = get_vopt_scsi_mapping(hmc_host, partition_uuid, system_uuid, vopt_name)
        scsi_mappings.append(bc_scsi)
    else:
        bootstrap_scsi = get_vopt_scsi_mapping(hmc_host, partition_uuid, system_uuid, util.get_bootstrap_iso(config))
        cloudinit_scsi = get_vopt_scsi_mapping(hmc_host, partition_uuid, system_uuid, util.get_cloud_init_iso(config))
        scsi_mappings.append(bootstrap_scsi)
        scsi_mappings.append(cloudinit_scsi)

    return str(vios_bs)

def check_if_scsi_mapping_exist(vios, media_dev_name):
    soup = BeautifulSoup(vios, 'xml')
    scsi_mappings = soup.find('VirtualSCSIMappings')
    b_devs = scsi_mappings.find_all("BackingDeviceName")
    disk = None
    for b_dev in b_devs:
        if b_dev.text == media_dev_name:
            disk = b_dev
            break

    if disk != None:
        logger.info(f"SCSI mapping for media device '{media_dev_name}' found in the VIOS")
        return True
    return False

def attach_vopt(vios_payload, config, cookies, partition_uuid, sys_uuid, vios_uuid, vopt_name):
    uri = f"/rest/api/uom/ManagedSystem/{sys_uuid}/VirtualIOServer/{vios_uuid}"
    hmc_host = util.get_host_address(config)
    url =  "https://" +  hmc_host + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": "application/vnd.ibm.powervm.uom+xml; Type=VirtualIOServer"}
    payload = populate_payload(config, vios_payload, hmc_host, partition_uuid, sys_uuid, vopt_name)
    response = requests.post(url, headers=headers, cookies=cookies, data=payload, verify=False)

    if response.status_code != 200:
        logger.error(f"failed to attach virtual storage to the partition, error: {response.text}")
        raise StorageError(f"failed to attach virtual storage to the partition, error: {response.text}")
    return
