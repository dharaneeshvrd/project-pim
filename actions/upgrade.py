import time

import utils.common as common
import utils.monitor_util as monitor_util
import utils.string_util as util
import utils.validator as validator

logger = common.get_logger("pim-upgrade")
bootc_auth_json = "/etc/ostree/auth.json"


def upgrade():
    try:
        config = common.initialize_config()
        logger.info("Upgrading PIM partition")

        logger.debug("Validating configuration")
        validator.validate_upgrade_config(config)
        logger.debug("Configuration validated")

        logger.debug("Upgrade to the latest PIM image")
        if not upgrade_action(config):
            return

        logger.debug("Monitor booting")
        monitor_util.monitor_pim(config)
    except Exception as e:
        logger.error(f"encountered an error: {e}")
    finally:
        logger.info("End of PIM command!!!")


def upgrade_action(config):
    try:
        ssh_client = common.ssh_to_partition(config)

        logger.debug("Updating auth.json with the latest one provided")
        auth_json = util.get_auth_json(config)
        sftp_client = ssh_client.open_sftp()
        with sftp_client.open("/tmp/auth.json", 'w') as f:
            f.write(auth_json)
        sftp_client.close()

        move_command = f"sudo mv /tmp/auth.json {bootc_auth_json}"
        _, stdout, stderr = ssh_client.exec_command(move_command, get_pty=True)
        if stdout.channel.recv_exit_status() != 0:
            raise Exception(
                f"failed to load auth.json in {bootc_auth_json}, error: {stdout.readlines()}, {stderr.readlines()}")

        upgraded = False
        bootc_upgrade_cmd = "sudo bootc upgrade --apply"
        _, stdout, _ = ssh_client.exec_command(bootc_upgrade_cmd, get_pty=True)
        while True:
            out = stdout.readline()
            logger.debug(out)
            if "Rebooting system" in out:
                upgraded = True
            if stdout.channel.exit_status_ready():
                break
            time.sleep(1)

        if upgraded:
            logger.info("Successfully upgraded the PIM image to latest level")
        else:
            logger.info("No upgrade available, PIM image is at latest level.")
    except Exception as e:
        logger.error(f"failed to upgrade PIM partition, error: {e}")
        raise Exception(f"failed to upgrade PIM partition, error: {e}")

    return upgraded
