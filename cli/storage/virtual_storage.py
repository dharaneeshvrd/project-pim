import requests
from bs4 import BeautifulSoup

import cli.utils.string_util as util
import cli.storage.storage as storage

def get_vg_payload(physical_vol_name, volume_group):
    return f'''
    <VolumeGroup:VolumeGroup xmlns:VolumeGroup="http://www.ibm.com/xmlns/systems/power/firmware/uom/mc/2012_10/" xmlns="http://www.ibm.com/xmlns/systems/power/firmware/uom/mc/2012_10/" xmlns:ns2="http://www.w3.org/XML/1998/namespace/k2" schemaVersion="V1_0">
        <GroupName kb="CUR" kxe="false">{volume_group}</GroupName>
        <PhysicalVolumes kb="CUD" kxe="false" schemaVersion="V1_0">
            <Metadata>
                <Atom/>
            </Metadata>
            <PhysicalVolume schemaVersion="V1_0">
                <Metadata>
                    <Atom/>
                </Metadata>
                <VolumeName kb="CUR" kxe="false">{physical_vol_name}</VolumeName>
            </PhysicalVolume>
        </PhysicalVolumes>
    </VolumeGroup:VolumeGroup>
    '''

def get_vdisk_payload(config, vg_payload):
    vg_soup = BeautifulSoup(vg_payload, 'xml')
    vdisk_payload_str = f'''
    <VirtualDisk schemaVersion="V1_0">
        <Metadata>
            <Atom/>
        </Metadata>
        <DiskCapacity kxe="false" kb="CUR">{util.get_virtual_disk_size(config)}</DiskCapacity>
        <DiskLabel kb="CUR" kxe="false">None</DiskLabel>
        <DiskName kxe="false" kb="CUR">{util.get_virtual_disk_name(config)}</DiskName>
    </VirtualDisk>
    '''
    vdisk_bs = BeautifulSoup(vdisk_payload_str, 'xml')
    vdisks = vg_soup.find("VirtualDisks")
    vdisks.append(vdisk_bs)
    payload = str(vg_soup)
    return payload

def get_vdisk_vios_payload(vios_payload, config, hmc_host, partition_uuid, system_uuid):
    vdisk_mapping = f'''
    <VirtualSCSIMapping schemaVersion="V1_0">
        <Metadata>
            <Atom/>
        </Metadata>
        <AssociatedLogicalPartition kb="CUR" kxe="false" href="https://{hmc_host}/rest/api/uom/ManagedSystem/{system_uuid}/LogicalPartition/{partition_uuid}" rel="related"/>
        <Storage kxe="false" kb="CUR">
            <VirtualDisk schemaVersion="V1_0">
                <Metadata>
                    <Atom/>
                </Metadata>
                <DiskCapacity kxe="false" kb="CUR">{util.get_virtual_disk_size(config)}</DiskCapacity>
                <DiskLabel kb="CUR" kxe="false">None</DiskLabel>
                <DiskName kxe="false" kb="CUR">{util.get_virtual_disk_name(config)}</DiskName>
            </VirtualDisk>
        </Storage>
    </VirtualSCSIMapping>
    '''
    vios_bs = BeautifulSoup(vios_payload, 'xml')
    vdisk_bs = BeautifulSoup(vdisk_mapping, 'xml')
    scsi_mappings = vios_bs.find('VirtualSCSIMappings')
    scsi_mappings.append(vdisk_bs)
    payload = str(vios_bs)
    return payload

def create_volumegroup(config, cookies, vios_uuid):
    uri = f"/rest/api/uom/VirtualIOServer/{vios_uuid}/VolumeGroup"
    hmc_host = util.get_host_address(config)
    url =  "https://" +  hmc_host + uri
    physical_vol_name = util.get_physical_volume_name(config)
    vg_name = util.get_volume_group(config)
    payload = get_vg_payload(physical_vol_name, vg_name)
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": "application/vnd.ibm.powervm.uom+xml; type=VolumeGroup"}
    response = requests.put(url, headers=headers, cookies=cookies, data=payload, verify=False)

    if response.status_code != 200:
        print("Failed to create volume group", response.text)
        exit()

    soup = BeautifulSoup(response.text, 'xml')
    vg_id = soup.find('id').text
    return vg_id

def get_volume_group_details(config, cookies, vios_uuid, vg_id):
    uri = f"/rest/api/uom/VirtualIOServer/{vios_uuid}/VolumeGroup/{vg_id}"
    hmc_host = util.get_host_address(config)
    url =  "https://" +  hmc_host + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": "application/vnd.ibm.powervm.uom+xml; type=VolumeGroup"}
    response = requests.get(url, headers=headers, cookies=cookies, verify=False)

    if response.status_code != 200:
        print("Failed to create volume group", response.text)
        exit()
    soup = BeautifulSoup(response.text, 'xml')
    vol_group_details = str(soup.find("VolumeGroup"))
    return vol_group_details

def create_virtualdisk(config, cookies, vios_uuid, vg_id):
    # Get Volume group details
    vg_details = get_volume_group_details(config, cookies, vios_uuid, vg_id)

    uri = f"/rest/api/uom/VirtualIOServer/{vios_uuid}/VolumeGroup/{vg_id}"
    hmc_host = util.get_host_address(config)
    url =  "https://" +  hmc_host + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": "application/vnd.ibm.powervm.uom+xml; type=VolumeGroup"}
    payload = get_vdisk_payload(config, vg_details)
    response = requests.post(url, headers=headers, cookies=cookies, data=payload, verify=False)
    if response.status_code != 200:
        print("Failed to create virtual disk", response.text)
        exit()

    print("Successfully created virtual disk")

def attach_virtualdisk(vios_payload, config, cookies, partition_uuid, system_uuid, vios_uuid):
    uri = f"/rest/api/uom/ManagedSystem/{system_uuid}/VirtualIOServer/{vios_uuid}"
    hmc_host = util.get_host_address(config)
    url =  "https://" +  hmc_host + uri
    payload = get_vdisk_vios_payload(vios_payload, config, hmc_host, partition_uuid, system_uuid)
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": storage.CONTENT_TYPE}
    response = requests.post(url, headers=headers, cookies=cookies, data=payload, verify=False)

    if response.status_code != 200:
        print("Failed to attach virtual storage to the partition ", response.text)
        exit()

    print("Successfully attached virtual disk")
