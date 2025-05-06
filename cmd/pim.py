import argparse
import hashlib
import logging
import os
import time
from bs4 import BeautifulSoup

from configobj import ConfigObj
import os
import paramiko.ssh_exception
import requests
import paramiko
import urllib3
import sys
import subprocess

import auth.auth as auth
from auth.auth_exception import AuthError
import app.ai_app as app
from app.ai_app_exception import AiAppError
import partition.activation as activation
import partition.partition as partition
from partition.partition_exception import PartitionError
from pim_exception import PimError
import network.virtual_network as virtual_network
from network.network_exception import NetworkError
import utils.string_util as util
import utils.common as common
import utils.validator as validator
import storage.storage as storage
import storage.vopt_storage as vopt
import storage.virtual_storage as vstorage
from storage.storage_exception import StorageError
from jinja2 import Environment, FileSystemLoader

iso_folder = os.getcwd() + "/iso"
keys_path = os.getcwd() + "/keys"

def initialize():
    config_file = "config.ini"
    config = ConfigObj(config_file)
    return config

def get_ssh_client():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    return client

def hash(file):
    sha256 = hashlib.sha256()
    with open(file, 'rb') as f:
        for chunk in iter(lambda: f.read(128 * sha256.block_size), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def create_iso_path(config, cookies, vios_uuid, filename, checksum, filesize):
    uri = "/rest/api/web/File/"
    url = "https://" + util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": "application/vnd.ibm.powervm.web+xml;type=File", "Accept": "application/atom+xml"}
    payload = f'''
    <web:File xmlns:web="http://www.ibm.com/xmlns/systems/power/firmware/web/mc/2012_10/" schemaVersion="V1_0">
        <web:Filename>{filename}</web:Filename>
        <web:InternetMediaType>application/octet-stream</web:InternetMediaType>
        <web:SHA256>{checksum}</web:SHA256>
        <web:ExpectedFileSizeInBytes>{filesize}</web:ExpectedFileSizeInBytes>
        <web:FileEnumType>BROKERED_MEDIA_ISO</web:FileEnumType>
        <web:TargetVirtualIOServerUUID>{vios_uuid}</web:TargetVirtualIOServerUUID>
    </web:File>
    '''
    response = None
    file_uuid = ""
    try:
        response = requests.put(url, headers=headers, data=payload, cookies=cookies, verify=False)
        if response.status_code != 200:
            logger.error(f"failed to create ISO path for file '{filename}', error: {response.text}")
            raise Exception(f"failed to create ISO path for file '{filename}', error: {response.text}")
        # extract file uuid from response
        soup = BeautifulSoup(response.text, "xml")
        file_uuid = soup.find("FileUUID").text
    except Exception as e:
        logger.error(f"failed to create ISO path, error: {e}")
        raise e
    logger.debug(f"{filename} ISO path created successfully")

    return file_uuid

def uploadfile(config, cookies, filehandle, file_uuid):
    uri = "/rest/api/web/File/contents/" + file_uuid
    url = "https://" + util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": "application/octet-stream", "Accept": "application/vnd.ibm.powervm.web+xml"}

    logger.debug(f"Uploading file '{filehandle}'")
    def readfile(f, chunksize):
        while True:
            d = f.read(chunksize)
            if not d:
                break
            yield d

    try:
        response = requests.put(url, headers=headers, data=readfile(filehandle, chunksize=65536) ,cookies=cookies, verify=False)
        if response.status_code != 204:
            logger.error(f"failed to upload ISO file '{filehandle}' to VIOS media repository, error: {response.text}")
            raise Exception(f"failed to upload ISO file '{filehandle}' to VIOS media repository, error: {response.text}")
    except Exception as e:
        logger.error(f"failed to upload ISO file '{filehandle}' to VIOS media repository, error: {e}")
        raise e
    return

def remove_iso_file(config, cookies, filename, file_uuid):
    uri = f"/rest/api/web/File/{file_uuid}"
    url = "https://" + util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": "application/vnd.ibm.powervm.web+xml;type=File"}
    try:
        response = requests.delete(url, headers=headers, cookies=cookies, verify=False)
        if response.status_code != 204:
            logger.error(f"failed to remove ISO file '{filename}' from VIOS after uploading to media repository, error: {response.text}")
            raise Exception(f"failed to remove ISO file '{filename}' from VIOS after uploading to media repository, error: {response.text}")
    except Exception as e:
        logger.error(f"Failed to remove ISO file '{filename}' from VIOS after uploading to media repository, error {e}")

    logger.debug(f"ISO file: '{filename}' removed from VIOS successfully")
    return

def upload_iso_to_media_repository(config, cookies, iso_file_name, vios_uuid_list):
    # Iterating over the vios_uuid_list to upload the ISO to the media repository for a VIOS
    # If upload operation fails for current VIOS, next available VIOS in the list will be used as a fallback.
    file_uuid = ""
    for index, vios_uuid in enumerate(vios_uuid_list):
        try:
            # Create ISO filepath for bootstrap iso
            iso_file = iso_folder + "/" + iso_file_name
            iso_checksum = hash(iso_file)
            iso_size = os.path.getsize(iso_file)
            file_uuid = create_iso_path(config, cookies, vios_uuid, iso_file_name, iso_checksum, iso_size)
            # transfer ISO file to VIOS media repository
            with open(iso_file, 'rb') as f:
                uploadfile(config, cookies, f, file_uuid)
                logger.info(f"'{iso_file_name}' ISO file upload completed!!")
            
            # remove iso files from VIOS
            remove_iso_file(config, cookies, iso_file, file_uuid)
            return vios_uuid
        except Exception as e:
            logger.error(f"failed to upload ISO to '{vios_uuid}' VIOS")
            if file_uuid != "":
                remove_iso_file(config, cookies, iso_file, file_uuid)
            if index == len(vios_uuid_list)-1:
                raise e
            else:
                logger.info("Upload of ISO file will be attempted on next available VIOS")
    return

def build_and_download_iso(config):
    iso_folder = "iso"
    create_dir(iso_folder)
    generate_cloud_init_iso_config(config)
    generate_cloud_init_iso_file(iso_folder, config)
    download_bootstrap_iso(iso_folder, config)
    
def generate_cloud_init_iso_config(config):
    file_loader = FileSystemLoader('cloud-init-iso/templates')
    env = Environment(loader=file_loader)
    pim_config_template = env.get_template('pim_config.json')
    pim_config_output = pim_config_template.render(config=config)
    
    network_config_template = env.get_template('99_custom_network.cfg')
    network_config_output = network_config_template.render(config=config)
    
    cloud_init_config_path = "cloud-init-iso/config"
    create_dir(cloud_init_config_path)

    pim_config_file = open(cloud_init_config_path + "/pim_config.json", "w")
    pim_config_file.write(pim_config_output)

    network_config_file = open(cloud_init_config_path + "/99_custom_network.cfg", "w")
    network_config_file.write(network_config_output)

    auth_json = config["ai"]["auth-json"]
    auth_config_file = open(cloud_init_config_path + "/auth.json", "w")
    auth_config_file.write(auth_json)
    logger.info("Generated config files for the cloud-init ISO")

def generate_cloud_init_iso_file(iso_folder, config):
    logger.info("Generating cloud-init ISO file")
    cloud_init_image_name = util.get_cloud_init_iso(config)
    generate_cmd = f"mkisofs -l -o {iso_folder}/{cloud_init_image_name} ./cloud-init-iso/config"
    
    try: subprocess.run(generate_cmd.split(), check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"failed to generate cloud-init ISO via mkisofs, error: {e.stderr}")
        raise

def download_bootstrap_iso(iso_folder, config):
    logger.info("Downloading bootstrap ISO file...")
    download_url = util.get_bootstrap_iso_download_url(config)
    iso_file_path = f"{iso_folder}/{util.get_bootstrap_iso(config)}"
    try:
        response = requests.get(download_url, stream=True)
        response.raise_for_status()

        with open(iso_file_path, "wb") as iso_file:
            for chunk in response.iter_content(chunk_size=8192):
                iso_file.write(chunk)
    except requests.exceptions.RequestException as e:
        logger.error(f"failed to download '{util.get_bootstrap_iso(config)}' file, error: {e}")
        raise
    
    logger.info("Download completed for bootstrap ISO file")

def create_dir(path):
    try:
        if not os.path.isdir(path):
            os.mkdir(path)
    except OSError as e:
        logger.error(f"failed to create '{path}' directory, error: {e}")
        raise

def monitor_iso_installation(config, cookies):
    ip = util.get_ip_address(config)
    username = util.get_ssh_username(config)
    ssh_key = util.get_ssh_priv_key(config)
    command = "sudo journalctl -u getcontainer.service -f 2>&1 | awk '{print} /Installation complete/ {print \"Match found: \" $0; exit 0}'"

    for i in range(10):
        scp_port = 22
        client = get_ssh_client()
        try:
            client.connect(ip, scp_port, username, key_filename=ssh_key)
        except (paramiko.BadHostKeyException, paramiko.AuthenticationException,
        paramiko.SSHException, paramiko.ssh_exception.NoValidConnectionsError) as e:
            if i == 9:
                logger.error(f"failed to establish SSH connection to partition after 10 retries, error: {e}")
                raise paramiko.SSHException
            logger.info("SSH to partition failed, retrying..")
            time.sleep(30)
    logger.info("SSH connection to partition is successful")

    stdin, stdout, stderr = client.exec_command(command, get_pty=True)
    while True:
        out = stdout.readline()
        logger.info(out)
        if stdout.channel.exit_status_ready():
            if stdout.channel.recv_exit_status() == 0:
                logger.info("Received ISO Installation complete message")
                break
            else:
                logger.error("failed to get ISO installation complete message. Please look at the errors if appear on the console and take appropriate resolution!!")
                raise PimError("failed to get ISO installation complete message")
    client.close()
    return

def get_system_uuid(config, cookies):
    uri = "/rest/api/uom/ManagedSystem/quick/All"
    url = "https://" + util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config)}
    response = requests.get(url, headers=headers, cookies=cookies, verify=False)
    if response.status_code != 200:
        logger.error(f"failed to get system UUID, error: {response.text}")
        raise PimError(f"failed to get system UUID, error: {response.text}")
    systems = []
    try: 
        systems = response.json()
    except requests.JSONDecodeError as e:
        logger.error(f"failed to parse json while getting UUID of the system, error: {e}")
        raise

    uuid = ""
    sys_name = util.get_system_name(config)
    for system in systems:
        if system["SystemName"] == sys_name:
            uuid = system["UUID"]
            break
    
    if "" == uuid:
        logger.error(f"no system available with name '{sys_name}'")
        raise PimError(f"no system available with name '{sys_name}'")
    else:
        logger.info(f"UUID for the system '{sys_name}': '{uuid}'")
    return uuid

def get_vios_uuid_list(config, cookies, system_uuid):
    uri = f"/rest/api/uom/ManagedSystem/{system_uuid}/VirtualIOServer/quick/All"
    url = "https://" +  util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": "application/vnd.ibm.powervm.uom+xml; Type=VirtualIOServer"}
    response = requests.get(url, headers=headers, cookies=cookies, verify=False)
    if response.status_code != 200:
        logger.error(f"failed to get VIOS list, error: {response.text}")
        raise PimError(f"failed to get VIOS list, error: {response.text}")

    uuids = []
    sys_name = util.get_system_name(config)
    for vios in response.json():
        if vios["SystemName"] == sys_name:
            uuids.append(vios["UUID"])

    if len(uuids) == 0:
        logger.error(f"no VIOS available for '{sys_name}'")
        raise PimError(f"no VIOS available for '{sys_name}'")
    else:
        logger.debug(f"VIOS UUID(s) for system {sys_name}: {uuids}")
    return uuids

def get_vios_details(config, cookies, system_uuid, vios_uuid):
    uri = f"/rest/api/uom/ManagedSystem/{system_uuid}/VirtualIOServer/{vios_uuid}"
    url = "https://" +  util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": "application/vnd.ibm.powervm.uom+xml; Type=VirtualIOServer"}
    response = requests.get(url, headers=headers, cookies=cookies, verify=False)
    if response.status_code != 200:
        logger.error(f"failed to get VIOS details for '{vios_uuid}', error")
        raise PimError(f"failed to get VIOS details for '{vios_uuid}', error")

    soup = BeautifulSoup(response.text, 'xml')
    vios = str(soup.find("VirtualIOServer"))
    return vios

def get_active_vios(config, cookies, sys_uuid, vios_uuids):
    # active_vios_servers: 
    #   KEY   -> vios_uuid 
    #   VALUE -> VIOS server details
    # This dictionary helps avoid multiple REST calls to fetch VIOS details.
    active_vios_servers = {}

    for vios_uuid in vios_uuids:
        vios_payload = get_vios_details(config, cookies, sys_uuid, vios_uuid)
        soup = BeautifulSoup(vios_payload, 'xml')
        state = soup.find("ResourceMonitoringControlState")
        if state.text == "active":
            active_vios_servers[vios_uuid] = vios_payload
    return active_vios_servers

def get_vios_with_mediarepo_tag(active_vios_servers):
    vios_uuid_list = []
    for vios_uuid, vios_payload in active_vios_servers.items():
        soup = BeautifulSoup(vios_payload, 'xml')
        if soup.find("MediaRepositories"):
            vios_uuid_list.append(vios_uuid)
    return vios_uuid_list

def get_vios_with_physical_storage(config, active_vios_servers):
    required_capacity = int(util.get_required_disk_size(config)) * 1024
    vios_list = []
    min_volume_capacity = sys.maxsize
    for vios_uuid, vios_payload in active_vios_servers.items():
        soup = BeautifulSoup(vios_payload, 'xml')
        pvs_soup = soup.find("PhysicalVolumes")  
        pv_list = pvs_soup.find_all("PhysicalVolume") 
        
        min_volume_capacity = sys.maxsize
        disk_name = ""
        
        for pv in pv_list:
            available_for_usage = pv.find("AvailableForUsage")
            volume_capacity = int(pv.find("VolumeCapacity").text)
            if available_for_usage.text == "true" and volume_capacity >= required_capacity:
                # Selecting the physical volume with disk capacity nearest to the required storage size
                if volume_capacity < min_volume_capacity:
                    min_volume_capacity = volume_capacity
                    disk_name = pv.find("VolumeName").text
        if disk_name != "":
            vios_list.append((vios_uuid, disk_name, min_volume_capacity))
    vios_list.sort(key=lambda vios: vios[2])
    return vios_list

def get_virtual_slot_number(vios_payload, disk_name):
    soup = BeautifulSoup(vios_payload, 'xml')
    scsi_mappings = soup.find("VirtualSCSIMappings")

    # Below double XMl parsing (convert xml -> str and str -> xml) is done as workaround for the XML parsing issue seen on IBMi partititon
    # TODO: Identify root cause and remove the workaround later
    scsi_mappings = BeautifulSoup(str(scsi_mappings), 'xml')

    disk = scsi_mappings.find(lambda tag: tag.name == "MediaName" and tag.text == disk_name)
    storage_scsi = disk.parent.parent.parent
    slot_num = storage_scsi.find("VirtualSlotNumber")
    return slot_num.text

def get_volume_group(config, cookies, vios_uuid, vg_name):
    uri = f"/rest/api/uom/VirtualIOServer/{vios_uuid}/VolumeGroup"
    url =  "https://" + util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": "application/vnd.ibm.powervm.uom+xml; type=VolumeGroup"}
    response = requests.get(url, headers=headers, cookies=cookies, verify=False)
    if response.status_code != 200:
        logger.error(f"failed to get volume group, error: {response.text}")
        raise PimError(f"failed to get volume group, error: {response.text}")

    soup = BeautifulSoup(response.text, 'xml')
    group = soup.find("GroupName", string=vg_name)
    vol_group = group.parent
    vg_id = vol_group.find("AtomID").text
    return vg_id

def get_partition_id(config, cookies, system_uuid):
    uri = f"/rest/api/uom/ManagedSystem/{system_uuid}/LogicalPartition/quick/All"
    url = "https://" +  util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config)}
    response = requests.get(url, headers=headers, cookies=cookies, verify=False)
    if response.status_code != 200:
        logger.error(f"failed to get partition list, error: {response.text}")
        raise PimError(f"failed to get partition list, error: {response.text}")

    uuid = ""
    partition_name = util.get_partition_name(config) + "-pim"
    for partition in response.json():
        if partition["PartitionName"] == partition_name:
            uuid = partition["UUID"]
            break

    if "" == uuid:
        logger.error(f"no partition available with name '{partition_name}'")
        raise PimError(f"no partition available with name '{partition_name}'")
    else:
        logger.info(f"UUID of partition '{partition_name}': {uuid}")
    return uuid

def remove_partition(config, cookies, partition_uuid):
    uri = f"/rest/api/uom/LogicalPartition/{partition_uuid}"
    url = "https://" +  util.get_host_address(config) + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": "application/vnd.ibm.powervm.uom+xml; Type=LogicalPartition"}
    response = requests.delete(url, headers=headers, cookies=cookies, verify=False)
    if response.status_code != 204:
        logger.error(f"failed to delete partition, error: {response.text}")
        raise PimError(f"failed to delete partition, error: {response.text}")
    logger.info("Partition deleted successfully")

def remove_scsi_mappings(config, cookies, sys_uuid, vios_uuid, vios, disk_name):
    logger.info("Removing SCSI mappings..")
    soup = BeautifulSoup(vios, "xml")
    scsi_mappings = soup.find("VirtualSCSIMappings")
    b_devs = scsi_mappings.find_all("BackingDeviceName")
    disk = None
    for b_dev in b_devs:
        if b_dev.text == disk_name:
            disk = b_dev
            break
    
    if disk == None:
        logger.error(f"no SCSI mapping available for '{disk_name}'")
        raise PimError(f"no SCSI mapping available for '{disk_name}'")
    scsi1 = disk.parent.parent
    scsi1.decompose()

    logger.debug("Removed SCSI mappings from VIOS payload")

    uri = f"/rest/api/uom/ManagedSystem/{sys_uuid}/VirtualIOServer/{vios_uuid}"
    hmc_host = util.get_host_address(config)
    url =  "https://" +  hmc_host + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": storage.CONTENT_TYPE}
    response = requests.post(url, headers=headers, cookies=cookies, data=str(soup), verify=False)

    if response.status_code != 200:
        logger.error(f"failed to update VIOS with removed storage mappings, error: {response.text}")
        raise PimError(f"failed to update VIOS with removed storage mappings, error: {response.text}")

    logger.info("Successfully removed SCSI mappings and vOPT media repositories and updated VIOS..")
    return

def remove_vopt_device(config, cookies, vios, vopt_name):
    # find volume group URL associated with StoragePool
    soup = BeautifulSoup(vios, 'xml')
    storage_pool = soup.find("StoragePools")
    if storage_pool.find("link") is not None:
        vg_url = storage_pool.find("link").attrs['href']
    else:
        logger.error("failed to get volume group hyperlink from VIOS")
        raise PimError("failed to get volume group hyperlink from VIOS")

    # make REST call to volume group URL(vg_url) to get list of media repositories
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": "application/vnd.ibm.powervm.uom+xml; type=VolumeGroup"}
    response = requests.get(vg_url, headers=headers, cookies=cookies, verify=False)
    try:
        if response.status_code != 200:
            logger.error(f"failed to get volume group details, error: {response.text}")
            raise PimError(f"failed to get volume group details, error: {response.text}")
        soup = BeautifulSoup(response.text, 'xml')
        vol_group = soup.find("VolumeGroup")

        # remove vopt_name from media repositoy
        vopt_media = vol_group.find_all("VirtualOpticalMedia")
        for v_media in vopt_media:
            if v_media.find("MediaName") is not None and v_media.find("MediaName").text == vopt_name:
                v_media.decompose()
                break

        logger.info("Updated volume group after removing vOPT from media repositories")
        # Now update the modified media repositoy list after delete
        response = requests.post(vg_url, data=str(vol_group), headers=headers, cookies=cookies, verify=False)
        if response.status_code != 200:
            logger.error(f"failed to update volume group after deleting vOPT device from media repository, error: {response.text}")
            raise PimError(f"failed to update volume group after deleting vOPT device from media repository, error: {response.text}")

        logger.info(f"Virtual optical media '{vopt_name}' has been deleted successfully")
    except Exception as e:
        raise e

def find_vios_with_vopt_mounted(config, cookies, sys_uuid, vios_uuid_list, vopt_name):
    for uuid in vios_uuid_list:
        vios = get_vios_details(config, cookies, sys_uuid, uuid)
        soup = BeautifulSoup(vios, "xml")
        media_repo_tag = soup.find("MediaRepositories")
        vopts = media_repo_tag.find_all("VirtualOpticalMedia")

        for vopt in vopts:
            media_name = vopt.find("MediaName")
            if media_name.text == vopt_name:
                return uuid
    raise PimError("no matching VIOS found where vOPTs mounted")

# destroy partition
def destroy(config, cookies, sys_uuid, vios_uuid_list):
    logger.info("PIM destroy flow")
    try:
        partition_uuid = get_partition_id(config, cookies, sys_uuid)

        # shutdown partition
        activation.shutdown_partition(config, cookies, partition_uuid)

        vopt_list = [util.get_bootstrap_iso(config), util.get_cloud_init_iso(config)]
        for vopt in vopt_list:
            vios_uuid = find_vios_with_vopt_mounted(config, cookies, sys_uuid, vios_uuid_list, vopt)
            vios = get_vios_details(config, cookies, sys_uuid, vios_uuid)

            # remove SCSI mapping from VIOS
            remove_scsi_mappings(config, cookies, sys_uuid, vios_uuid, vios, vopt)

             # TODO: delete virtual disk, volumegroup if created by the script during launch

            vios_updated = get_vios_details(config, cookies, sys_uuid, vios_uuid)

            # remove mounted virtual optical devices from media repositoy.
            remove_vopt_device(config, cookies, vios_updated, vopt)

        remove_partition(config, cookies, partition_uuid)
    except (PartitionError, PimError) as e:
        raise e

    logger.info("Delete partition done")
    return

def generate_ssh_keys(config):
    create_dir(keys_path)
    key_name = f"{keys_path}/{util.get_partition_name(config)}_pim"
    cmd = f"ssh-keygen -b 4096 -t rsa -m PEM -f {key_name} -q -N \"\""
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    if result.returncode != 0:
        logger.error(f"failed to run ssh-keygen command to generate keypair, error: {result.stderr}")
        raise Exception(f"failed to run ssh-keygen command to generate keypair, error: {result.stderr}")

    logger.info("SSH keypair generated successfully")
    config["ssh"]["user-name"] = "pim"
    config["ssh"]["priv-key-file"] = keys_path + "/" + util.get_partition_name(config) + "_pim"
    config["ssh"]["pub-key-file"] = keys_path+ "/" + util.get_partition_name(config) + "_pim.pub"
    return config

def attach_physical_storage(config, cookies, sys_uuid, partition_uuid, vios_bootstrap_media_uuid, vios_cloudinit_media_uuid, vios_storage_list):
    # Iterating over the vios_storage_list to attach physical volume from VIOS to a partition.
    # If attachment operation fails for current VIOS, next available VIOS in the list will be used as a fallback.
    for index, vios_storage in enumerate(vios_storage_list):
        try:
            vios_storage_uuid, physical_volume_name, _ = vios_storage
            updated_vios_payload = get_vios_details(config, cookies, sys_uuid, vios_storage_uuid)
            logger.debug("Attach physical storage to the partition")
            storage_slot_num = -1
            if vios_storage_uuid == vios_bootstrap_media_uuid:
                storage_slot_num = get_virtual_slot_number(updated_vios_payload, util.get_bootstrap_iso(config))
            elif vios_storage_uuid == vios_cloudinit_media_uuid:
                storage_slot_num = get_virtual_slot_number(updated_vios_payload, util.get_cloud_init_iso(config))
            
            storage.attach_storage(updated_vios_payload, config, cookies, partition_uuid, sys_uuid, vios_storage_uuid, storage_slot_num, physical_volume_name)
            logger.info(f"Attached '{physical_volume_name}' physical volume to the partition from VIOS '{vios_storage_uuid}'")
            break
        except (PimError, StorageError) as e:
            logger.error(f"failed to attach '{physical_volume_name}' physical storage in VIOS '{vios_storage_uuid}'")
            if index == len(vios_storage_list) - 1:
                raise e
            else:
                logger.info("Attempting to attach physical storage present in next available VIOS")

def launch(config, cookies, sys_uuid, vios_uuids):
    try:
        # Check if SSH key pair is configured, if empty generate key pair
        if not util.get_ssh_priv_key(config) or not util.get_ssh_pub_key(config):
            config = generate_ssh_keys(config)

        # Populate configobj with public key content to get populated in cloud-init config
        config["ssh"]["pub-key"] = common.readfile(util.get_ssh_pub_key(config))

        active_vios_servers = get_active_vios(config, cookies, sys_uuid, vios_uuids)
        if len(active_vios_servers) == 0:
            logger.error("failed to find active VIOS server")
            raise PimError("failed to find active VIOS server")
        logger.debug(f"List of active VIOS '{list(active_vios_servers.keys())}'")

        vios_media_uuid_list = get_vios_with_mediarepo_tag(active_vios_servers)
        if len(vios_media_uuid_list) == 0:
            logger.error("failed to find VIOS server for the partition")
            raise StorageError("failed to find VIOS server for the partition")

        vios_storage_list = get_vios_with_physical_storage(config, active_vios_servers)
        if len(vios_storage_list) == 0:
            logger.error("failed to find physical volume for the partition")
            raise StorageError("failed to find physical volume for the partition")

        logger.info("5. Setup installation ISOs")
        build_and_download_iso(config)
        logger.info("---------------------- Setup installation ISOs done ----------------------")
        
        logger.info("6. Transfer ISO files to VIOS media repository")
        vios_bootstrap_media_uuid = upload_iso_to_media_repository(config, cookies, util.get_bootstrap_iso(config),vios_media_uuid_list)
        logger.info(f"a. Selecting '{vios_bootstrap_media_uuid}' VIOS to mount bootstrap vOPT")
        vios_cloudinit_media_uuid = upload_iso_to_media_repository(config, cookies, util.get_cloud_init_iso(config),vios_media_uuid_list)
        logger.info(f"b. Selecting '{vios_cloudinit_media_uuid}' VIOS to mount cloudinit vOPT")
        
        logger.info("---------------------- Transfer ISOs done ----------------------")

        logger.info("7. Create Partition on the target host")
        partition_uuid = partition.create_partition(config, cookies, sys_uuid)

        logger.debug(f"Partition created successfully. partition UUID: {partition_uuid}")
        logger.info("---------------------- Create partition done ----------------------")

        logger.info("8. Attach Network to the partition")
        virtual_network.attach_network(config, cookies, sys_uuid, partition_uuid)
        logger.info("---------------------- Attach network done ----------------------")

        logger.info("9. Attach installation medias to the partition")
        vios_payload = get_vios_details(config, cookies, sys_uuid, vios_bootstrap_media_uuid)

        # Attach bootstrap vOPT
        vopt_bootstrap = util.get_bootstrap_iso(config)
        vopt.attach_vopt(vios_payload, config, cookies, partition_uuid, sys_uuid, vios_bootstrap_media_uuid, vopt_bootstrap, -1)
        logger.info("a. Bootstrap virtual optical device attached")

        updated_vios_payload = get_vios_details(config, cookies, sys_uuid, vios_cloudinit_media_uuid)
        # Get VirtualSlotNumber for the disk(physical/virtual)
        slot_num = -1
        if vios_bootstrap_media_uuid == vios_cloudinit_media_uuid:
            slot_num = get_virtual_slot_number(updated_vios_payload, vopt_bootstrap)
        vopt_cloud_init = util.get_cloud_init_iso(config)
        vopt.attach_vopt(updated_vios_payload, config, cookies, partition_uuid, sys_uuid, vios_cloudinit_media_uuid, vopt_cloud_init, slot_num)
        logger.info("b. Cloudinit virtual optical device attached")
        logger.info("---------------------- Attach installation medias done ----------------------")

        logger.info("10. Attach storage")
        use_vdisk = util.use_virtual_disk(config)
        if use_vdisk:
            vios_storage_uuid = vios_storage_list[0][0]
            updated_vios_payload = get_vios_details(config, cookies, sys_uuid, vios_storage_uuid)
            use_existing_vd = util.use_existing_vd(config)
            if use_existing_vd:
                vstorage.attach_virtualdisk(updated_vios_payload, config, cookies, partition_uuid, sys_uuid, vios_storage_uuid)
            else:
                # Create volume group, virtual disk and attach storage
                use_existing_vg = util.use_existing_vg(config)
                if not use_existing_vg:
                    # Create volume group
                    vg_id = vstorage.create_volumegroup(config, cookies, vios_storage_uuid)
                else:
                    vg_id = get_volume_group(config, cookies, vios_storage_uuid, util.get_volume_group(config))
                    vstorage.create_virtualdisk(config, cookies, vios_storage_uuid, vg_id)
                    time.sleep(60)
                    updated_vios_payload = get_vios_details(config, cookies, sys_uuid, vios_storage_uuid)
                    vstorage.attach_virtualdisk(updated_vios_payload, config, cookies, partition_uuid, sys_uuid, vios_storage_uuid)
                    diskname = util.get_virtual_disk_name(config)
        else:
            attach_physical_storage(config, cookies, sys_uuid, partition_uuid, vios_bootstrap_media_uuid, vios_cloudinit_media_uuid, vios_storage_list)
        logger.info("---------------------- Attach storage done ----------------------")

        logger.info("11. Activate partition")
        activation.activate_partititon(config, cookies, partition_uuid)
        logger.info("---------------------- Partition activation done ----------------------")

        time.sleep(120)
        # monitor ISO installation
        logger.info("12. Monitor ISO installation")
        monitor_iso_installation(config, cookies)
        logger.info("---------------------- Monitor ISO installation done ----------------------")

        logger.info("13. Wait for lpar to boot from the disk")
        # Poll for the 8000 AI application port
        time.sleep(300)
        logger.info("14. Check for AI app to be running")
        for i in range(10):
            up = app.check_app(config)
            if not up:
                logger.info("AI application is still not up and running, retrying..")
                time.sleep(10)
                continue
            else:
                logger.info("AI application is up and running. Now checking response for prompt from OpenAI API server")
                resp = app.check_bot_service(config)
                logger.info(f"Response from bot service: \n{resp}")
                logger.info("---------------------- PIM workflow complete ----------------------")
                return
        logger.error("failed to bring up AI application from bootc")
        raise AiAppError("failed to bring up AI application from bootc")
    except (AiAppError, AuthError, NetworkError, PartitionError, StorageError, PimError, paramiko.SSHException, Exception) as e:
        raise e

def start_manager():
    try:
        cookies = None
        parser = argparse.ArgumentParser(description="PIM lifecycle manager")
        parser.add_argument("action", choices=["launch", "destroy"] , help="Launch and destroy flow of bootc partition.")
        parser.add_argument("--debug", action='store_true', help='Enable debug logging level')
        args = parser.parse_args()

        if args.debug:
            common.setup_logging(logging.DEBUG)
        else:
            common.setup_logging(logging.INFO)
        
        logger.info("Starting PIM lifecycle manager")
        logger.info("1. Parse and Validate configuration")
        config = initialize()
        
        if not validator.validate_config(config):
            return

        logger.info("2. Authenticate with HMC host")
        session_token, cookies = auth.authenticate_hmc(config)
        logger.info("---------------------- Authenticate to HMC done ----------------------")

        config["session"] = {"x-api-key": session_token}

        logger.info("3. Get System UUID for target host")
        sys_uuid = get_system_uuid(config, cookies)
        logger.info("---------------------- Get System UUID done ----------------------")

        logger.info("4. Select VIOS for target host")
        if not validator.validate_networks(config, cookies, sys_uuid):
            return

        vios_uuid_list = get_vios_uuid_list(config, cookies, sys_uuid)

        if args.action == "launch":
            launch(config, cookies, sys_uuid, vios_uuid_list)
        elif args.action == "destroy":
            destroy(config, cookies, sys_uuid, vios_uuid_list)
    except (AiAppError, AuthError, NetworkError, PartitionError, StorageError, PimError, Exception) as e:
        logger.error(f"encountered an error: {e}")
    finally:
        if cookies:
            common.cleanup_and_exit(config, cookies, 0)

logger = common.get_logger("pim-manager")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
start_manager()
