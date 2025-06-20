import partition.activation as activation
import partition.partition as partition
import utils.actions_util as action_util
import utils.common as common
import utils.string_util as util
import vios.vios as vios_operation


logger = common.get_logger("pim-destroy")


def destroy():
    cookies = None
    try:
        logger.info("Destroying PIM partition")
        config = common.initialize_config()
        # Invoking initialize_action to perform common actions like validation, authentication etc.
        is_config_valid, cookies, sys_uuid, vios_uuid_list = action_util.initialize_action(config)
        if is_config_valid:
            destroy_action(config, cookies, sys_uuid, vios_uuid_list)
    except (Exception) as e:
        logger.error(f"encountered an error: {e}")
    finally:
        if cookies:
            action_util.cleanup(config, cookies)
        logger.info("Destroying PIM partition completed")


# destroy partition
def destroy_action(config, cookies, sys_uuid, vios_uuid_list):
    try:
        exists, created_by_pim, partition_uuid = partition.check_partition_exists(
            config, cookies, sys_uuid)
        if not exists:
            logger.debug(
                f"Partition named '{util.get_partition_name(config).lower()}' not found, attempting VIOS cleanup")
            # in the absence of partition, partition_uuid will be empty
            vios_operation.cleanup_vios(
                config, cookies, sys_uuid, partition_uuid, vios_uuid_list)
            return
        logger.debug("Shutting down the partition")
        activation.shutdown_partition(config, cookies, partition_uuid)
        logger.info("Partition shut down")

        logger.debug(
            "Detaching installation medias and physical disk from the partition")
        vios_operation.cleanup_vios(
            config, cookies, sys_uuid, partition_uuid, vios_uuid_list)
        logger.info(
            "Detached installation medias and physical disk from the partition")

        if created_by_pim:
            logger.debug("Destroying the partition")
            partition.remove_partition(config, cookies, partition_uuid)
            logger.info("Partition destroyed")
    except Exception as e:
        raise e
    return
