import argparse
import logging
import urllib3

import utils.common as common

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

common_parser = argparse.ArgumentParser(add_help=False)
common_parser.add_argument("--debug", action="store_true", help="Enable debug logging")

parser = argparse.ArgumentParser(description="PIM lifecycle manager", parents=[common_parser])

action_parsers = parser.add_subparsers(dest="action", required=True)
launch_parser = action_parsers.add_parser(
    "launch", help="Create a new partition with the given configuration", parents=[common_parser])

destroy_parser = action_parsers.add_parser(
    "destroy", help="Delete the partition and clean up the VIOS", parents=[common_parser])

upgrade_parser = action_parsers.add_parser(
    "upgrade", help="Update the partition AI image to the latest version", parents=[common_parser])

rollback_parser = action_parsers.add_parser(
    "rollback", help="Rollback the partition AI image to its previous version", parents=[common_parser])

update_compute_parser = action_parsers.add_parser(
    "update-compute", help="Updates the cpu and memory configuration for the partition", parents=[common_parser])

update_config_parser = action_parsers.add_parser(
    "update-config", help="Updates PIM partition's AI related configuration", parents=[common_parser])

status_parser = action_parsers.add_parser(
    "status", help="Status of PIM partition(Overall partition status from HMC, AI application validation if enabled)", parents=[common_parser])

action_args = parser.parse_args()
if action_args.debug:
    common.set_log_level(logging.DEBUG)
else:
    common.set_log_level(logging.INFO)

from actions.destroy import destroy
from actions.launch import launch
from actions.rollback import rollback
from actions.update_compute import update_compute
from actions.upgrade import upgrade
from actions.update_config import update_config
from actions.status import status

launch_parser.set_defaults(func=launch)
destroy_parser.set_defaults(func=destroy)
upgrade_parser.set_defaults(func=upgrade)
rollback_parser.set_defaults(func=rollback)
update_compute_parser.set_defaults(func=update_compute)
update_config_parser.set_defaults(func=update_config)
status_parser.set_defaults(func=status)

action_args = parser.parse_args()
action_args.func()
