import partition.activation as activation
import partition.partition as partition
import utils.actions_util as action_util
import utils.common as common
import utils.string_util as util

logger = common.get_logger("pim-update-compute")


def update_compute():
    cookies = None
    try:
        logger.info("Updating PIM partition's compute")
        config = common.initialize_config()
        # Invoking initialize_action to perform common actions like validation, authentication etc.
        is_config_valid, cookies, sys_uuid, _ = action_util.initialize_action(
            config)
        if is_config_valid:
            update_compute_action(config, cookies, sys_uuid)
    except Exception as e:
        logger.error(f"encountered an error: {e}")
    finally:
        if cookies:
            action_util.cleanup(config, cookies)
        logger.info("End of PIM command!!!")


def update_compute_action(config, cookies, sys_uuid):
    try:
        logger.debug("Checking if partition exists")
        exists, _, partition_uuid = partition.check_partition_exists(
            config, cookies, sys_uuid)
        if not exists:
            logger.info(
                f"Partition named '{util.get_partition_name(config)}' not found, nothing to update")
            return
        logger.debug("Shutting down the partition")
        activation.shutdown_partition(config, cookies, partition_uuid)
        logger.info("Partition shut down to update compute")
        partition.edit_lpar_compute(config, cookies, sys_uuid, partition_uuid)
        logger.info(
            f"Modified the partition: '{util.get_partition_name(config)}' with updated compute")
        logger.debug("Activate the partition after updating compute")
        activation.activate_partititon(config, cookies, partition_uuid)
        logger.info("Partition activated after updating compute")
        logger.info(
            f"Update compute for partition: '{util.get_partition_name(config)}' is complete")
    except Exception as e:
        raise e
