import partition.activation as activation
import partition.partition as partition
import utils.command_util as command_util
import utils.common as common
import utils.string_util as util

logger = common.get_logger("pim-update-compute")


def update_compute():
    cookies = None
    try:
        logger.info("Updating PIM partition's compute")
        config = common.initialize_config()
        # Invoking initialize_command to perform common actions like validation, authentication etc.
        is_config_valid, cookies, sys_uuid, _ = command_util.initialize_command(
            config)
        if is_config_valid:
            _update_compute(config, cookies, sys_uuid)
            logger.info("PIM partition's compute successfully updated")
    except Exception as e:
        logger.error(f"encountered an error: {e}")
    finally:
        if cookies:
            command_util.cleanup(config, cookies)


def _update_compute(config, cookies, sys_uuid):
    try:
        logger.debug("Checking if partition exists")
        exists, _, partition_uuid = partition.check_partition_exists(
            config, cookies, sys_uuid)
        if not exists:
            logger.info(
                f"Partition named '{util.get_partition_name(config)}' not found, nothing to update")
            return
        logger.info("Shutting down the partition")
        activation.shutdown_partition(config, cookies, partition_uuid)
        logger.info("Partition shut down to update compute")
        partition.edit_lpar_compute(config, cookies, sys_uuid, partition_uuid)
        logger.info(
            f"Modified the partition: '{util.get_partition_name(config)}' with updated compute")
        logger.info("Activate the partition after updating compute")
        activation.activate_partition(config, cookies, partition_uuid)
        logger.info("Partition activated after updating compute")
        logger.info(
            f"Update compute for partition: '{util.get_partition_name(config)}' is complete")
    except Exception as e:
        raise e
