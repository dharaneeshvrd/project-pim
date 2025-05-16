import argparse
import json
import logging
import os
import time
from bs4 import BeautifulSoup

from configobj import ConfigObj
import os
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
bootc_auth_json = "/etc/ostree/auth.json"


def initialize():
    config_file = "config.ini"
    try:
        config = ConfigObj(config_file)
    except Exception as e:
        logger.error(f"failed to parse config.ini, error: {e}")
        raise e
    return config

def get_ssh_client():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    return client

def check_if_keys_generated(config):
    priv_key = f"{keys_path}/{util.get_partition_name(config)}_pim"
    pub_key = f"{keys_path}/{util.get_partition_name(config)}_pim.pub"
    if os.path.isfile(priv_key) and os.path.isfile(pub_key):
        return True
    return False

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

def is_iso_uploaded(config, cookies, iso_file_name,  sys_uuid, vios_uuid_list):
    try:
        for _, vios_uuid in enumerate(vios_uuid_list):
            vios = get_vios_details(config, cookies, sys_uuid, vios_uuid)
            _, _, media_repos = get_media_repositories(config, cookies, vios)
            vopt_media = media_repos.find_all("VirtualOpticalMedia")
            for vopt in vopt_media:
                if  vopt.find(lambda tag: tag.name == "MediaName" and tag.text == iso_file_name):
                    logger.info(f"Found ISO file '{iso_file_name}' in media repositories")
                    return True, vios_uuid

    except Exception as e:
        raise e
    logger.info(f"ISO file '{iso_file_name}' was not found in the media repositories")
    return False, ""

def upload_iso_to_media_repository(config, cookies, iso_file_name, sys_uuid, vios_uuid_list):
    # Check if bootstrap ISO file is already uploaded to any of the available VIOS
    if "_pimb" in iso_file_name:
        uploaded, vios_uuid = is_iso_uploaded(config, cookies, iso_file_name, sys_uuid, vios_uuid_list)
        if uploaded:
            return vios_uuid

    logger.info(f"Uploading ISO file '{iso_file_name} to VIOS media repository")
    # Iterating over the vios_uuid_list to upload the ISO to the media repository for a VIOS
    # If upload operation fails for current VIOS, next available VIOS in the list will be used as a fallback.
    file_uuid = ""
    for index, vios_uuid in enumerate(vios_uuid_list):
        try:
            # Re-run scenario: If lpar is already activated but launch flow failed during monitoring or app_check stage in previous run. Skip reupload of cloudinit iso
            if "_pimc" in iso_file_name:
                exists, lpar_uuid = partition.check_partition_exists(config, cookies, sys_uuid)
                if exists:
                    lpar_state = activation.check_lpar_status(config, cookies, lpar_uuid)
                    if lpar_state == "running":
                        logger.info(f"Partition already in 'running' state, skipping reupload of cloud-init ISO '{iso_file_name}'")
                        return vios_uuid

                    vios = get_vios_details(config, cookies, sys_uuid, vios_uuid)

                    # remove SCSI mapping from VIOS
                    remove_scsi_mappings(config, cookies, sys_uuid, vios_uuid, vios, iso_file_name)

                    # Delete existing cloud-init vOPT with same name if already loaded in VIOS media repository
                    remove_vopt_device(config, cookies, vios, iso_file_name)

            # Create ISO filepath for bootstrap iso
            iso_file = iso_folder + "/" + iso_file_name
            iso_checksum = common.hash(iso_file)
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
    
    network_config_template = env.get_template('99_custom_network.cfg')
    network_config_output = network_config_template.render(config=config)
    
    cloud_init_config_path = "cloud-init-iso/config"
    create_dir(cloud_init_config_path)

    pim_config_json = config["ai"]["pim-config-json"] if config["ai"]["pim-config-json"] != "" else "{}"
    pim_config_json = json.loads(pim_config_json)

    # 'workloadImage' is being used inside the bootstrap iso to write the bootc image into disk, in case of modification of this field name, needs same modification in bootstrap.iso too.
    pim_config_json["workloadImage"] = util.get_workload_image(config)
    
    pim_config_file = open(cloud_init_config_path + "/pim_config.json", "w")
    pim_config_file.write(json.dumps(pim_config_json))

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

def download_bootstrap_checksum(checksum_url, checksum_file_path):
    logger.info("Downloading bootstrap ISO's checksum file...")

    logger.debug(f"bootstrap iso checksum url: {checksum_url}")
    try:
        response = requests.get(checksum_url, stream=True)
        response.raise_for_status()

        with open(checksum_file_path, "wb") as csum_file:
            for chunk in response.iter_content(chunk_size=8192):
                csum_file.write(chunk)
    except requests.exceptions.RequestException as e:
        logger.error(f"failed to download '{checksum_file_path}' file, error: {e}")
        raise
    return

def download_bootstrap_iso(iso_folder, config):
    iso_url, iso_file_path, checksum_url, checksum_file_path = common.get_iso_url_and_checksum_path(config, iso_folder)

    try:
        # Check if bootstrap iso is already downloaded locally(on IBMi)
        if os.path.isfile(iso_file_path):
            logger.info(f"Bootstrap iso '{iso_file_path}' found, checking integrity of the file")
            # Check if iso checksum file exists
            if not os.path.exists(checksum_file_path):
                # Download checksum file for bootstrap iso
                download_bootstrap_checksum(checksum_url, checksum_file_path)
            if not common.verify_checksum(iso_file_path, checksum_file_path):
                logger.info("Checksum of found boostrap iso did not match, cleaning up iso..")
                cleanup_iso_artifacts(iso_file_path, checksum_file_path)
            else:
                logger.info(f"Bootstrap iso '{iso_file_path}' found, skipping download..")
                return

        logger.info("Downloading bootstrap ISO file...")

        response = requests.get(iso_url, stream=True)
        response.raise_for_status()

        with open(iso_file_path, "wb") as iso_file:
            for chunk in response.iter_content(chunk_size=8192):
                iso_file.write(chunk)

        # Download checksum file for bootstrap iso
        download_bootstrap_checksum(checksum_url, checksum_file_path)
        # Verify bootstrap iso file's checksum
        if not common.verify_checksum(iso_file_path, checksum_file_path):
            # re-try attempt
            logger.error("Checksum of bootstrap iso is not matching against checksumfile download from repository")
            return
        logger.info("Integrity of downloaded bootstrap iso has been successfully verified..")
    except requests.exceptions.RequestException as e:
        logger.error(f"failed to download '{util.get_bootstrap_iso(config)}' file, error: {e}")
        raise
    logger.info("Download completed for bootstrap ISO file")
    return

def create_dir(path):
    try:
        if not os.path.isdir(path):
            os.mkdir(path)
    except OSError as e:
        logger.error(f"failed to create '{path}' directory, error: {e}")
        raise

def ssh_to_partition(config):
    ip = util.get_ip_address(config)
    username = util.get_ssh_username(config)
    ssh_key = util.get_ssh_priv_key(config)

    for i in range(10):
        scp_port = 22
        client = get_ssh_client()
        try:
            client.connect(ip, scp_port, username, key_filename=ssh_key, timeout=10)
            break
        except Exception as e:
            if i == 9:
                logger.error(f"failed to establish SSH connection to partition after 10 retries, error: {e}")
                raise paramiko.SSHException(f"failed to establish SSH connection to partition after 10 retries, error: {e}")
            logger.info("SSH to partition failed, retrying..")
            time.sleep(30)
    logger.info("SSH connection to partition is successful")
    return client

def monitor_bootstrap_boot(config):
    logger.debug("Bootstrap boot: Checking getcontainer.service")
    try:
        ssh_client = ssh_to_partition(config) 

        get_container_svc_exists = "ls /usr/lib/systemd/system/getcontainer.service"
        _, stdout, _ = ssh_client.exec_command(get_container_svc_exists, get_pty=True)
        if stdout.channel.recv_exit_status() == 0:
            logger.info("getcontainer.service exists") 

            get_container_svc_cmd = "sudo journalctl -u getcontainer.service -f 2>&1 | awk '{print} /Installation complete/ {print \"Match found: \" $0; exit 0}'"
            _, stdout, stderr = ssh_client.exec_command(get_container_svc_cmd, get_pty=True)
            while True:
                out = stdout.readline()
                logger.info(out)
                if stdout.channel.exit_status_ready():
                    if stdout.channel.recv_exit_status() == 0:
                        logger.info("Received ISO Installation complete message")
                        # Sleep is required to give time for reboot to happen to boot from the disk
                        time.sleep(10)
                        break
                    else:
                        logger.info("Could not find bootstrap ISO installation complete message\n. \
                        In case logs from bootstrap boot appears, please look at the errors if appear on the console and take appropriate resolution!!\n")
        else:
            logger.info("Could not find 'getcontainer.service', will look for 'base_config.service' in PIM boot since it could be a re-run and bootstrap might have already finished")
            ssh_client.close()
    except Exception as e:
        logger.error(f"failed to monitor bootstrap boot, error: {e}")
        raise Exception(f"failed to monitor bootstrap boot, error: {e}")

    return

def monitor_pim_boot(config):
    # Re-run scenario: If lpar is in 2nd boot stage, check base_config service logs
    logger.info("PIM boot: Checking base_config.service")
    try:
        ssh_client = ssh_to_partition(config)    

        base_config_svc_exists = "ls /etc/systemd/system/base_config.service"
        _, stdout, _ = ssh_client.exec_command(base_config_svc_exists, get_pty=True)
        if stdout.channel.recv_exit_status() == 0:
            logger.info("base_config.service exists")

            logger.info("Checking base_config.service logs")
            base_cfg_svc_cmd = "sudo journalctl -u base_config.service -f 2>&1 | awk '{print} /base_config.sh run successfully/ {print \"Match found: \" $0; exit 0}'"
            _, stdout, _ = ssh_client.exec_command(base_cfg_svc_cmd, get_pty=True)
            while True:
                out = stdout.readline()
                logger.info(out)
                if stdout.channel.exit_status_ready():
                    if stdout.channel.recv_exit_status() == 0:
                        logger.info("Found 'base_config.sh run successfully' message")
                        ssh_client.close()
                        return
        else:
            logger.error("failed to find '/etc/systemd/system/base_config.service', please check console for more possible errors")
            raise Exception("failed to  find '/etc/systemd/system/base_config.service', please check console for more possible errors")
    except Exception as e:
        logger.error(f"failed to monitor PIM boot, error: {e}")
        raise Exception(f"failed to monitor PIM boot, error: {e}")

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
        media_repos = soup.find("MediaRepositories")
        if media_repos:
            free_memory = calculate_free_space(vios_uuid, media_repos)
            logger.debug(f"Media repositories has {free_memory} GB free memory in '{vios_uuid}' VIOS.")
            if free_memory > 3.0:
                vios_uuid_list.append(vios_uuid)
            else:
                logger.error("sufficient memory not available in '{vios_uuid}' VIOS for media repositories.")
    return vios_uuid_list

def calculate_free_space(vios_uuid, media_repos):
    used_memory = 0.0
    free_memory = 0.0
    try:
        size_list = media_repos.find_all("Size")
        capacity = float(media_repos.find("RepositorySize").text)
        for size in size_list:
            used_memory += float(size.text)
        free_memory = capacity - used_memory
    except Exception as e:
        logger.error(f"failed to calculate free memory in '{vios_uuid}' VIOS for media repositories. error: {e}")
    return free_memory

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

def remove_scsi_mappings(config, cookies, sys_uuid, vios_uuid, vios, disk_name):
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
        return
    scsi1 = disk.parent.parent
    scsi1.decompose()

    logger.debug(f"Payload prepared to remove '{disk_name}' SCSI mappings from VIOS payload")

    uri = f"/rest/api/uom/ManagedSystem/{sys_uuid}/VirtualIOServer/{vios_uuid}"
    hmc_host = util.get_host_address(config)
    url =  "https://" +  hmc_host + uri
    headers = {"x-api-key": util.get_session_key(config), "Content-Type": storage.CONTENT_TYPE}
    response = requests.post(url, headers=headers, cookies=cookies, data=str(soup), verify=False)

    if response.status_code != 200:
        logger.error(f"failed to update VIOS with removed '{disk_name}' mappings, error: {response.text}")
        return

    logger.info(f"Successfully removed SCSI mappings for '{disk_name}'")
    return

def get_media_repositories(config, cookies, vios):
    vg_url = ""
    vol_group = None
    media_repos = None
    try:
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
        if response.status_code != 200:
            logger.error(f"failed to get media repositories, error: {response.text}")
            raise PimError(f"failed to get media repositories, error: {response.text}")
        soup = BeautifulSoup(response.text, 'xml')
        media_repos = soup.find("MediaRepositories")
        vol_group = soup.find("VolumeGroup")
    except Exception as e:
        logger.error(f"failed to get media repositories, error: {e}")
        raise e
    logger.info("Obtained media repositories from VIOS successfully")
    return vg_url, vol_group, media_repos

def remove_vopt_device(config, cookies, vios, vopt_name):
    try:
        vg_url, vol_group, media_repos = get_media_repositories(config, cookies, vios)
        if media_repos is None:
            logger.error("failed to get media repositories")
            raise Exception("failed to get media repositories")

        found = False
        # remove vopt_name from media repositoy
        vopt_media = media_repos.find_all("VirtualOpticalMedia")
        for v_media in vopt_media:
            if v_media.find("MediaName") is not None and v_media.find("MediaName").text == vopt_name:
                found = True
                v_media.decompose()
                break
        
        if not found:
            logger.info("vOPT device '{vopt_name}' is not present in media repository")
            return

        headers = {"x-api-key": util.get_session_key(config), "Content-Type": "application/vnd.ibm.powervm.uom+xml; type=VolumeGroup"}
        # Now update the modified media repositoy list after delete
        response = requests.post(vg_url, data=str(vol_group), headers=headers, cookies=cookies, verify=False)
        if response.status_code != 200:
            logger.error(f"failed to update volume group after deleting vOPT device from media repository, error: {response.text}")
            return

        logger.info(f"Virtual optical media '{vopt_name}' has been deleted successfully")
    except Exception as e:
        raise e
    return

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
    return ""

def cleanup_vios(config, cookies, sys_uuid, partition_uuid, vios_uuid_list):
    vopt_list = [util.get_bootstrap_iso(config), util.get_cloud_init_iso(config)]
    storage_cleaned = False
    processed_vios_list = []
    try:
        for vopt in vopt_list:
            vios_uuid = find_vios_with_vopt_mounted(config, cookies, sys_uuid, vios_uuid_list, vopt)
            if not vios_uuid:
                logger.error(f"no matching VIOS found where {vopt} vOPTs mounted")
                continue
            vios = get_vios_details(config, cookies, sys_uuid, vios_uuid)

            # remove SCSI mappings from VIOS
            found, phys_disk = storage.check_if_storage_attached(vios, partition_uuid)
            if found and not storage_cleaned:
                logger.debug(f"Removing SCSI mapping for physical disk '{phys_disk}'")
                remove_scsi_mappings(config, cookies, sys_uuid, vios_uuid, vios, phys_disk)
                storage_cleaned = True

            vios = get_vios_details(config, cookies, sys_uuid, vios_uuid)
            logger.debug(f"Removing SCSI mapping for vOPT device '{vopt}'")
            remove_scsi_mappings(config, cookies, sys_uuid, vios_uuid, vios, vopt)
            # TODO: delete virtual disk, volumegroup if created by the script during launch

            vios = get_vios_details(config, cookies, sys_uuid, vios_uuid)

            # remove mounted cloud-init vOPT from media repositoy.
            if vopt == util.get_cloud_init_iso(config):
                logger.debug(f"Removing vOPT device '{vopt}'")
                remove_vopt_device(config, cookies, vios, vopt)
            processed_vios_list.append(vios_uuid)
    
        # If storage and any of the vOPT not using same VIOS, need to cleanup with a different VIOS
        if not storage_cleaned:
            for vios_uuid in vios_uuid_list:
                if vios_uuid not in processed_vios_list:
                    vios = get_vios_details(config, cookies, sys_uuid, vios_uuid)
                    found, phys_disk = storage.check_if_storage_attached(vios, partition_uuid)
                    if found:
                        logger.debug(f"Removing SCSI mapping for physical disk '{phys_disk}'")
                        remove_scsi_mappings(config, cookies, sys_uuid, vios_uuid, vios, phys_disk)
    except Exception as e:
        logger.error(f"failed to clean up vios, error: {e}")
        
def cleanup_iso_artifacts(iso_path, checksum_path):
    if os.path.exists(iso_path):
        os.remove(iso_path)
    if os.path.exists(checksum_path):
        os.remove(checksum_path)
    logger.debug("ISO artifacts have been deleted successfully")
    return

def destroy_partition(config, cookies, partition_uuid):
    try:
        activation.shutdown_partition(config, cookies, partition_uuid)
        partition.remove_partition(config, cookies, partition_uuid)
    except (PartitionError, PimError) as e:
        logger.error(f"failed to destroy partition. error: {e}")
    logger.info("Destroy partition done")

# destroy partition
def destroy(config, cookies, sys_uuid, vios_uuid_list):
    try:
        exists, partition_uuid = partition.check_partition_exists(config, cookies, sys_uuid)
        if not exists:
            logger.info(f"Partition named '{util.get_partition_name(config)}-pim' not found, attempting VIOS cleanup")
            # in the absence of partition, partition_uuid will be empty
            cleanup_vios(config, cookies, sys_uuid, partition_uuid, vios_uuid_list)
            return
        activation.shutdown_partition(config, cookies, partition_uuid)
        cleanup_vios(config, cookies, sys_uuid, partition_uuid, vios_uuid_list)
        partition.remove_partition(config, cookies, partition_uuid)
    except Exception as e:
        raise e
    logger.info("destroy flow completed successfully")
    return

def generate_ssh_keys(config):
    # Check if keys already exists in 'keys_path'
    if not check_if_keys_generated(config):
        create_dir(keys_path)
        key_name = f"{keys_path}/{util.get_partition_name(config)}_pim"
        cmd = f"ssh-keygen -b 4096 -t rsa -m PEM -f {key_name} -q -N \"\""
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        if result.returncode != 0:
            logger.error(f"failed to run ssh-keygen command to generate keypair, error: {result.stderr} \n {result.stdout}")
            raise Exception(f"failed to run ssh-keygen command to generate keypair, error: {result.stderr}")
        logger.info("SSH keypair generated successfully")

    config["ssh"]["user-name"] = "pim"
    config["ssh"]["priv-key-file"] = keys_path + "/" + util.get_partition_name(config) + "_pim"
    config["ssh"]["pub-key-file"] = keys_path+ "/" + util.get_partition_name(config) + "_pim.pub"
    return config

def attach_physical_storage(config, cookies, sys_uuid, partition_uuid, vios_storage_list):
    physical_volume_name = ""
    vios_uuid = ""
    try:
        for index, a_vios in enumerate(vios_storage_list):
            vios_uuid, physical_volume_name, _ = a_vios
            vios = get_vios_details(config, cookies, sys_uuid, vios_uuid)
            logger.debug("Attach physical storage to the partition")
            found, _ = storage.check_if_storage_attached(vios, partition_uuid)
            if found:
                logger.info(f"Physical volume is already attached to lpar, skipping storage attachment to lpar")
                return
    except (PimError, StorageError) as e:
        logger.error(f"failed to attach '{physical_volume_name}' physical storage in VIOS '{vios_uuid}'")
        raise e

    # Iterating over the vios_storage_list to attach physical volume from VIOS to a partition.
    # If attachment operation fails for current VIOS, next available VIOS in the list will be used as a fallback.
    for index, vios_storage in enumerate(vios_storage_list):
        try:
            vios_storage_uuid, physical_volume_name, _ = vios_storage
            updated_vios_payload = get_vios_details(config, cookies, sys_uuid, vios_storage_uuid)
            logger.debug("Attach physical storage to the partition")
            
            found, _ = storage.check_if_storage_attached(updated_vios_payload, partition_uuid)
            if found:
                logger.info(f"Physical volume '{physical_volume_name}' is already attached to lpar")
                return

            storage.attach_storage(updated_vios_payload, config, cookies, partition_uuid, sys_uuid, vios_storage_uuid, physical_volume_name)
            logger.info(f"Attached '{physical_volume_name}' physical volume to the partition from VIOS '{vios_storage_uuid}'")
            break
        except (PimError, StorageError) as e:
            logger.error(f"failed to attach '{physical_volume_name}' physical storage in VIOS '{vios_storage_uuid}'")
            if index == len(vios_storage_list) - 1:
                raise e
            else:
                logger.info("Attempting to attach physical storage present in next available VIOS")
    return

def rollback(config):
    try:
        ssh_client = ssh_to_partition(config)

        bootc_upgrade_cmd = "sudo bootc rollback"
        _, stdout, stderr = ssh_client.exec_command(bootc_upgrade_cmd, get_pty=True)
        if stdout.channel.recv_exit_status() != 0:
            logger.error(f"failed to rollback, error: {stdout.readlines()}, {stderr.readlines()}")
        else:
            logger.info("Rollback succeeded")

        logger.info("Reboot to apply the rollback")
        _, stdout, stderr = ssh_client.exec_command("sudo reboot", get_pty=True)
        if stdout.channel.recv_exit_status() != 0:
            logger.error(f"failed to reboot, error: {stdout.readlines()}, {stderr.readlines()}")         
    except Exception as e:
        logger.error(f"failed to rollback PIM partition, error: {e}")
        raise Exception(f"failed to rollback PIM partition, error: {e}")

def upgrade(config):
    try:
        ssh_client = ssh_to_partition(config)

        logger.info("Updating auth.json with the latest one provided")
        auth_json = util.get_auth_json(config)
        sftp_client = ssh_client.open_sftp()
        with sftp_client.open("/tmp/auth.json", 'w')  as f:
            f.write(auth_json)
        sftp_client.close()

        move_command = f"sudo mv /tmp/auth.json {bootc_auth_json}"
        _, stdout, stderr = ssh_client.exec_command(move_command, get_pty=True)
        if stdout.channel.recv_exit_status() != 0:
            raise Exception(f"failed to load auth.json in {bootc_auth_json}, error: {stdout.readlines()}, {stderr.readlines()}")
        
        upgraded = False
        logger.info("Upgrading to the latest image")
        bootc_upgrade_cmd = "sudo bootc upgrade --apply"
        _, stdout, _ = ssh_client.exec_command(bootc_upgrade_cmd, get_pty=True)
        while True:
            out = stdout.readline()
            logger.info(out)
            if "Rebooting system" in out:
                upgraded = True
            if stdout.channel.exit_status_ready():
                break
        if upgraded:
            logger.info("Upgrade available and successfully applied the latest PIM image")
        else:
            logger.info("Seems no upgrade available to apply")
    except Exception as e:
        logger.error(f"failed to upgrade PIM partition, error: {e}")
        raise Exception(f"failed to upgrade PIM partition, error: {e}")

    return upgraded

def monitor_pim(config):
    monitor_pim_boot(config)

    # No need to validate the AI application deployed via PIM flow if 'ai.validation.request' set to no, can complete the workflow
    if util.get_ai_app_request(config) == "no":
        logger.info("PIM image installed onto disk and rebooted, application should be available in few mins")
        logger.info("---------------------- PIM workflow complete ----------------------")

    # Validate the AI application deployed via PIM partition with the request details provided in 'ai.validation'
    logger.info("13. Check for AI app to be running")
    for i in range(50):
        up = app.check_app(config)
        if not up:
            logger.info("AI application is still not up and running, retrying..")
            time.sleep(10)
            continue
        else:
            logger.info("AI application is up and running")
            logger.info("---------------------- PIM workflow complete ----------------------")
            return
    logger.error("failed to bring up AI application from PIM image")
    raise AiAppError("failed to bring up AI application from PIM image")

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

        logger.info("5. Setup installation ISOs")
        build_and_download_iso(config)
        logger.info("---------------------- Setup installation ISOs done ----------------------")
        
        logger.info("6. Transfer ISO files to VIOS media repository")
        vios_bootstrap_media_uuid = upload_iso_to_media_repository(config, cookies, util.get_bootstrap_iso(config), sys_uuid, vios_media_uuid_list)
        logger.info(f"a. Selecting '{vios_bootstrap_media_uuid}' VIOS to mount bootstrap vOPT")
        vios_cloudinit_media_uuid = upload_iso_to_media_repository(config, cookies, util.get_cloud_init_iso(config), sys_uuid, vios_media_uuid_list)
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
        vopt_cloud_init = util.get_cloud_init_iso(config)

        cloud_init_attached = False
        b_scsi_exists = vopt.check_if_scsi_mapping_exist(vios_payload, vopt_bootstrap)
        if not b_scsi_exists:
            if vios_cloudinit_media_uuid == vios_bootstrap_media_uuid:
                vopt.attach_vopt(vios_payload, config, cookies, partition_uuid, sys_uuid, vios_bootstrap_media_uuid, "")
                cloud_init_attached = True
            else:
                vopt.attach_vopt(vios_payload, config, cookies, partition_uuid, sys_uuid, vios_bootstrap_media_uuid, vopt_bootstrap)
        if not cloud_init_attached:
            vios_cloudinit_payload = get_vios_details(config, cookies, sys_uuid, vios_cloudinit_media_uuid)
            c_scsi_exists = vopt.check_if_scsi_mapping_exist(vios_cloudinit_payload, vopt_cloud_init)
            if not c_scsi_exists:
                vopt.attach_vopt(vios_payload, config, cookies, partition_uuid, sys_uuid, vios_cloudinit_media_uuid, vopt_cloud_init)

        logger.info("Bootstrap and cloudinit virtual optical device attached")
        logger.info("---------------------- Attach installation medias done ----------------------")

        logger.info("10. Attach storage")
        # Re-run scenario: Check if physical disk is already attached
        storage_attached = False
        for vios_id in active_vios_servers:
            logger.debug("Attach physical storage to the partition")
            found, _ = storage.check_if_storage_attached(active_vios_servers[vios_id], partition_uuid)
            if found:
                logger.info(f"Physical disk is already attached to lpar '{partition_uuid}'")
                storage_attached = True

        # Enable below code block when virtual disk support is added
        '''
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
        '''

        if not storage_attached:
            vios_storage_list = get_vios_with_physical_storage(config, active_vios_servers)
            if len(vios_storage_list) == 0:
                logger.error("failed to find physical volume for the partition")
                raise StorageError("failed to find physical volume for the partition")
            attach_physical_storage(config, cookies, sys_uuid, partition_uuid, vios_storage_list)
        logger.info("---------------------- Attach storage done ----------------------")

        partition_payload = partition.get_partition_details(config, cookies, sys_uuid, partition_uuid)
        partition.set_partition_boot_string(config, cookies, sys_uuid, partition_uuid, partition_payload, "cd/dvd-all")

        logger.info("11. Activate partition")
        activation.activate_partititon(config, cookies, partition_uuid)
        logger.info("---------------------- Partition activation done ----------------------")

        monitor_bootstrap_boot(config)
        monitor_pim(config)
    except (AiAppError, AuthError, NetworkError, PartitionError, StorageError, PimError, paramiko.SSHException, Exception) as e:
        raise e

def start_manager():
    try:
        cookies = None
        parser = argparse.ArgumentParser(description="PIM lifecycle manager")
        parser.add_argument("action", choices=["launch", "upgrade", "rollback", "destroy"] , help="Does launch, upgrade, rollback and destroy PIM partition.")
        parser.add_argument("--debug", action='store_true', help='Enable debug logging level')
        args = parser.parse_args()

        if args.debug:
            common.setup_logging(logging.DEBUG)
        else:
            common.setup_logging(logging.INFO)
        
        logger.info("Starting PIM lifecycle manager")
        config = initialize()

        command = None
        if args.action == "launch":
            logger.info("Launch PIM partition")
            command = launch
        elif args.action == "destroy":
            logger.info("Destroy PIM partition")
            command = destroy
   
        if args.action == "upgrade":
            logger.info("Upgrade PIM partition")
            
            logger.info("1. Validate configuration")
            validator.validate_upgrade_config(config)
            logger.info("---------------------- Validate configuration Done ----------------------")

            logger.info("2. Upgrade to the latest PIM image")
            if not upgrade(config):
                return
            logger.info("---------------------- Upgrade Done ----------------------")
            
            logger.info("3. Check for AI app to be running")
            monitor_pim(config)
            logger.info("---------------------- PIM workflow complete ----------------------")

            return

        if args.action == "rollback":
            logger.info("Rollback PIM partition")

            logger.info("1. Validate configuration")
            validator.validate_rollback_config(config)
            logger.info("---------------------- Validate configuration Done ----------------------")

            logger.info("2. Rollback to the previous PIM image")
            rollback(config)
            logger.info("---------------------- Rollback Done ----------------------")

            logger.info("3. Check for AI app to be running")
            monitor_pim(config)
            logger.info("---------------------- PIM workflow complete ----------------------")
            return

        logger.info("1. Validate configuration")
        if not validator.validate_config(config):
            return
        logger.info("---------------------- Validate configuration Done ----------------------")

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

        command(config, cookies, sys_uuid, vios_uuid_list)
    except (AiAppError, AuthError, NetworkError, PartitionError, StorageError, PimError, Exception) as e:
        logger.error(f"encountered an error: {e}")
    finally:
        if cookies:
            common.cleanup_and_exit(config, cookies, 0)

logger = common.get_logger("pim-manager")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
start_manager()
