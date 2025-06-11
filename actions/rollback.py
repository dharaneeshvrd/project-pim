import utils.common as common
import utils.validator as validator
import utils.monitor_util as monitor_util

logger = common.get_logger("pim-rollback")


def rollback():
    try:
        config = common.initialize_config()
        logger.info("Rollback PIM partition")

        logger.debug("Validate configuration")
        validator.validate_rollback_config(config)
        logger.debug("Configuration validated")

        logger.debug("Rollback to the previous PIM image")
        rollback_action(config)

        logger.debug("Monitor booting")
        monitor_util.monitor_pim(config)
    except Exception as e:
        logger.error(f"encountered an error: {e}")
    finally:
        logger.info("End of PIM command!!!")


def rollback_action(config):
    try:
        ssh_client = common.ssh_to_partition(config)

        bootc_rollback_cmd = "sudo bootc rollback"
        _, stdout, stderr = ssh_client.exec_command(
            bootc_rollback_cmd, get_pty=True)
        if stdout.channel.recv_exit_status() != 0:
            logger.error(
                f"failed to rollback, error: {stdout.readlines()}, {stderr.readlines()}")
        else:
            logger.info("Rollback succeeded")

        logger.debug("Reboot to apply the rollback")
        _, stdout, stderr = ssh_client.exec_command(
            "sudo reboot", get_pty=True)
        if stdout.channel.recv_exit_status() != 0:
            logger.error(
                f"failed to reboot, error: {stdout.readlines()}, {stderr.readlines()}")
    except Exception as e:
        logger.error(f"failed to rollback PIM partition, error: {e}")
        raise Exception(f"failed to rollback PIM partition, error: {e}")
