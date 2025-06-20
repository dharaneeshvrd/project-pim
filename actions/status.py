import json

import app.ai_app as app
import partition.activation as activation
import partition.partition as partition
import utils.actions_util as action_util
import utils.common as common
import utils.string_util as util

logger = common.get_logger("pim-status")

def status():
    cookies = None
    try:
        logger.info("PIM partition's status")
        config = common.initialize_config()
        # Invoking initialize_action to perform common actions like validation, authentication etc.
        is_config_valid, cookies, sys_uuid, _ = action_util.initialize_action(
            config)
        if is_config_valid:
            status_action(config, cookies, sys_uuid)
    except Exception as e:
        logger.error(f"encountered an error: {e}")
    finally:
        if cookies:
            action_util.cleanup(config, cookies)

def status_action(config, cookies, sys_uuid):
    try:
        logger.debug("Checking partition exists")
        exists, _, partition_uuid = partition.check_partition_exists(config, cookies, sys_uuid)
        if not exists:
            logger.error(f"Partition named '{util.get_partition_name(config)}' not found")
            return

        lpar_state = activation.check_lpar_status(config, cookies, partition_uuid)
        if lpar_state != "running":
            logger.error(f"Partition '{util.get_partition_name(config)}' not in running state")
            return
        logger.info("PIM partition is in running state")  

        if not util.get_ssh_priv_key(config) or not util.get_ssh_pub_key(config):
            config = common.load_ssh_keys(config)

        ssh_client = common.ssh_to_partition(config)

        bootc_status_command = f"sudo bootc status"
        _, stdout, stderr = ssh_client.exec_command(bootc_status_command, get_pty=True)
        if stdout.channel.recv_exit_status() != 0:
            raise Exception(f"failed to get status error: {stdout.readlines()}, {stderr.readlines()}")
        status_output = "\n".join(stdout.readlines())
        logger.info(f"Partition's bootc status:\n {status_output}")

        if util.get_ai_app_request(config) == "no":
            logger.info("Skipping AI application validation since 'ai.validation.request' set to False")
            return

        logger.info("Validate AI application launched via PIM")
        logger.debug(f"Validation request details\n Method: {util.get_ai_app_method(config)}\n URL: {util.get_ai_app_url(config)}\n Payload: {util.get_ai_app_payload(config)}")
        up, msg = app.check_app(config)
        if not up:
            logger.error(f"AI application is not responding, message: {msg}")
        else:
            logger.info("AI application is responding properly")
            logger.debug(f"Response: {json.dumps(json.loads(msg), indent=4)}")
    except Exception as e:
        raise e
