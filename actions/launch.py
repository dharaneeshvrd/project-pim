
import paramiko

from app.ai_app_exception import AiAppError
from auth.auth_exception import AuthError
from network.network_exception import NetworkError
import network.virtual_network as virtual_network
from partition.partition_exception import PartitionError
import partition.activation as activation
import partition.partition as partition
from storage.storage_exception import StorageError
import storage.storage as storage
import storage.vopt_storage as vopt
import utils.actions_util as action_util
import utils.common as common
import utils.iso_util as iso_util
import utils.monitor_util as monitor_util
import utils.string_util as util
from vios.vios_exception import VIOSError
import vios.vios as vios_operation


logger = common.get_logger("pim-launch")


def launch():
    cookies = None
    try:
        logger.info("Launching PIM partition")
        config = common.initialize_config()
        # Invoking initialize_action to perform common actions like validation, authentication etc.
        is_config_valid, cookies, sys_uuid, vios_uuid_list = action_util.initialize_action(config)
        if is_config_valid:
            launch_action(config, cookies, sys_uuid, vios_uuid_list)
    except Exception as e:
        logger.error(f"encountered an error: {e}")
    finally:
        if cookies:
            action_util.cleanup(config, cookies)
        logger.info("End of PIM command!!!")


def launch_action(config, cookies, sys_uuid, vios_uuids):
    try:
        # Check if SSH key pair is configured, if empty generate key pair
        if not util.get_ssh_priv_key(config) or not util.get_ssh_pub_key(config):
            config = load_ssh_keys(config)

        # Populate configobj with public key content to get populated in cloud-init config
        config["ssh"]["pub-key"] = common.readfile(
            util.get_ssh_pub_key(config))

        active_vios_servers = vios_operation.get_active_vios(
            config, cookies, sys_uuid, vios_uuids)
        if len(active_vios_servers) == 0:
            logger.error("failed to find active VIOS server")
            raise VIOSError("failed to find active VIOS server")
        logger.debug(
            f"List of active VIOS '{list(active_vios_servers.keys())}'")

        vios_media_uuid_list = vios_operation.get_vios_with_mediarepo_tag(active_vios_servers)
        if len(vios_media_uuid_list) == 0:
            logger.error("failed to find VIOS server for the partition")
            raise StorageError("failed to find VIOS server for the partition")

        logger.debug("Setup Partition on the target host")
        partition_uuid = partition.create_partition(config, cookies, sys_uuid)
        logger.info("Partition setup completed")
        logger.debug(f"Partition's UUID: {partition_uuid}")

        logger.debug("Setup network to the partition")
        slot_num = virtual_network.attach_network(
            config, cookies, sys_uuid, partition_uuid)
        logger.info("Network setup completed")

        logger.debug(
            "Downloading(bootstrap) & building(cloud-init) installation ISOs")
        iso_util.build_and_download_iso(config, slot_num)
        logger.info("Downloaded & built installation ISOs")

        logger.debug("Loading installation ISOs to VIOS media repository")
        vios_bootstrap_media_uuid = iso_util.upload_iso_to_media_repository(
            config, cookies, util.get_bootstrap_iso(config), sys_uuid, vios_media_uuid_list)
        logger.debug(
            f"a. Selecting '{vios_bootstrap_media_uuid}' VIOS to mount bootstrap vOPT")
        vios_cloudinit_media_uuid = iso_util.upload_iso_to_media_repository(
            config, cookies, util.get_cloud_init_iso(config), sys_uuid, vios_media_uuid_list)
        logger.debug(
            f"b. Selecting '{vios_cloudinit_media_uuid}' VIOS to mount cloudinit vOPT")
        logger.info("Installation ISOs loaded to VIOS")

        logger.debug("Setup PIM installation ISOs")
        vios_payload = vios_operation.get_vios_details(
            config, cookies, sys_uuid, vios_bootstrap_media_uuid)

        # Attach bootstrap vOPT
        vopt_bootstrap = util.get_bootstrap_iso(config)
        vopt_cloud_init = util.get_cloud_init_iso(config)

        cloud_init_attached = False
        b_scsi_exists = vopt.check_if_scsi_mapping_exist(
            partition_uuid, vios_payload, vopt_bootstrap)
        if not b_scsi_exists:
            if vios_cloudinit_media_uuid == vios_bootstrap_media_uuid:
                vopt.attach_vopt(vios_payload, config, cookies,
                                 partition_uuid, sys_uuid, vios_bootstrap_media_uuid, "")
                cloud_init_attached = True
            else:
                vopt.attach_vopt(vios_payload, config, cookies, partition_uuid,
                                 sys_uuid, vios_bootstrap_media_uuid, vopt_bootstrap)
        if not cloud_init_attached:
            vios_cloudinit_payload = vios_operation.get_vios_details(
                config, cookies, sys_uuid, vios_cloudinit_media_uuid)
            c_scsi_exists = vopt.check_if_scsi_mapping_exist(
                partition_uuid, vios_cloudinit_payload, vopt_cloud_init)
            if not c_scsi_exists:
                vopt.attach_vopt(vios_cloudinit_payload, config, cookies, partition_uuid,
                                 sys_uuid, vios_cloudinit_media_uuid, vopt_cloud_init)

        logger.info("PIM installation ISOs setup completed")

        logger.debug("Setup storage")
        # Re-run scenario: Check if physical disk is already attached
        storage_attached = False
        for _, a_vios in active_vios_servers.items():
            logger.debug("Attach physical storage to the partition")
            physical_disk_found, _ = storage.check_if_storage_attached(
                a_vios, partition_uuid)
            vfc_disk_found, _ = storage.check_if_vfc_disk_attached(
                a_vios, partition_uuid)
            if physical_disk_found:
                logger.debug(
                    f"Physical disk is already attached to lpar '{partition_uuid}'")
                storage_attached = True
            if vfc_disk_found:
                logger.debug(
                    f"SAN storage(VFC) disk is already attached to lpar '{partition_uuid}'")
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
            vios_storage_list = vios_operation.get_vios_with_physical_storage(
                config, active_vios_servers)
            if len(vios_storage_list) == 0:
                logger.error(
                    "failed to find physical volume for the partition")
                raise StorageError(
                    "failed to find physical volume for the partition")
            storage.attach_physical_storage(
                config, cookies, sys_uuid, partition_uuid, vios_storage_list)
        logger.info("Storage setup completed")

        partition_payload = partition.get_partition_details(
            config, cookies, sys_uuid, partition_uuid)
        partition.set_partition_boot_string(
            config, cookies, sys_uuid, partition_uuid, partition_payload, "cd/dvd-all")

        logger.debug("Activate partition")
        activation.activate_partititon(config, cookies, partition_uuid)
        logger.info("Partition activated")

        logger.info("Monitoring boot process, this will take a while")
        monitor_util.monitor_bootstrap_boot(config)
        monitor_util.monitor_pim(config)
    except (AiAppError, AuthError, NetworkError, PartitionError, StorageError, VIOSError, paramiko.SSHException, Exception) as e:
        raise e


def load_ssh_keys(config):
    # Check if keys already exists in 'keys_path'
    if not common.check_if_keys_generated(config):
        common.generate_ssh_keys(config)
    config = common.load_ssh_config(config)
    return config
