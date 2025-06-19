import shutil

import network.virtual_network as virtual_network
import partition.activation as activation
import partition.partition as partition
import utils.monitor_util as monitor_util
import storage.vopt_storage as vopt
import utils.actions_util as action_util
import utils.common as common
import utils.iso_util as iso_util
import utils.string_util as util
import vios.vios as vios


logger = common.get_logger("pim-update-config")

def update_config():
    cookies = None
    try:
        logger.info("Updating PIM partition's config")
        config = common.initialize_config()
        # Invoking initialize_action to perform common actions like validation, authentication etc.
        is_config_valid, cookies, sys_uuid, vios_uuid_list = action_util.initialize_action(
            config)
        if is_config_valid:
            update_config_action(config, cookies, sys_uuid, vios_uuid_list)
    except Exception as e:
        logger.error(f"encountered an error: {e}")
    finally:
        if cookies:
            action_util.cleanup(config, cookies)
        logger.info("Updating PIM partition's config completed")

def update_config_action(config, cookies, sys_uuid, vios_uuid_list):
    try:
        logger.debug("Checking partition exists")
        exists, _, partition_uuid = partition.check_partition_exists(config, cookies, sys_uuid)
        if not exists:
            logger.info(f"Partition named '{util.get_partition_name(config)}' not found, nothing to update")
            return

        logger.debug("Partition exists, generating cloud init config")

        # Get VLAN ID and VSWITCH ID
        vlan_id, vswitch_id = virtual_network.get_vlan_details(config, cookies, sys_uuid)

        # Check if network adapter is already attached to lpar. If not, do attach
        _, slot_num = virtual_network.check_network_adapter(config, cookies, partition_uuid, vlan_id, vswitch_id)

        iso_util.generate_cloud_init_iso_config(config, slot_num, common.cloud_init_update_config_dir)
        if not common.compare_dir(common.cloud_init_config_dir, common.cloud_init_update_config_dir):
            logger.info("No change in config, skipping the update")
            shutil.rmtree(common.cloud_init_update_config_dir)
            return
        logger.info("Detected config change, updating")
        iso_util.generate_cloud_init_iso_file(common.cloud_init_update_config_dir, config, common.cloud_init_update_config_dir)

        logger.debug("Shutting down the partition")
        activation.shutdown_partition(config, cookies, partition_uuid)
        logger.info("Partition shut down to attach the new config")

        cloud_init_iso = util.get_cloud_init_iso(config)
        logger.debug("Uploading the cloud init")
        vios_cloudinit_media_uuid = iso_util.upload_iso_to_media_repository(config, cookies, common.cloud_init_update_config_dir, cloud_init_iso, sys_uuid, vios_uuid_list)
        logger.debug("Cloud init uploaded")
        
        logger.debug("Attaching the cloud init to the partiiton")
        vios_payload = vios.get_vios_details(config, cookies, sys_uuid, vios_cloudinit_media_uuid)
        vopt.attach_vopt(vios_payload, config, cookies, partition_uuid, sys_uuid, vios_cloudinit_media_uuid, cloud_init_iso)
        logger.info("New cloud init config attached to the partiiton")

        logger.debug("Activating the partition")
        activation.activate_partititon(config, cookies, partition_uuid)
        logger.info("Partition activated")

        logger.info("Monitoring boot process, this will take a while")
        monitor_util.monitor_pim(config)

        # Move used cloud init iso to iso dir
        shutil.move(f"{common.cloud_init_update_config_dir}/{cloud_init_iso}", f"{common.iso_dir}/{cloud_init_iso}")
        
        # Cleanup existing config and move updated config
        shutil.rmtree(common.cloud_init_config_dir)
        shutil.move(common.cloud_init_update_config_dir, common.cloud_init_config_dir)
    except Exception as e:
        raise e
