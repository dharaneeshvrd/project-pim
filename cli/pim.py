import argparse
import logging
import urllib3

import cli.utils.common as common

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

common_parser = argparse.ArgumentParser(add_help=False)
common_parser.add_argument("--debug", action="store_true", help="Enable debug logging")

parser = argparse.ArgumentParser(description="PIM Partition Lifecycle Manager\n" \
    "All the commands acts upon configuration provided in config.ini file\n" \
    "All the commands supports re-run which means if user tries to rerun a particular command involving creating a new resource" \
    "it picks up from where it left during last run or it picks the already created resource and proceed with the command execution", 
    parents=[common_parser], formatter_class=argparse.RawTextHelpFormatter)

command_parser = parser.add_subparsers(dest="command", required=True)
launch_parser = command_parser.add_parser(
    "launch", help="Setup PIM partition", parents=[common_parser], description="Setup PIM partition\n " \
    "If user specified a partition name and if it does not exist already, it sets up the PIM partition E2E(Creating a new partition, attach network, storage and installation medias and activates it)\n " \
    "If user specified an existing partition name on which the storage already attached, it only attaches network and installation medias and activates it", formatter_class=argparse.RawTextHelpFormatter)

destroy_parser = command_parser.add_parser(
    "destroy", help="Destroy PIM partition and cleanup installation devices", parents=[common_parser], 
    description="Destroy PIM partition and cleanup installation devices. It ensures only resources created by this script will get cleaned up", formatter_class=argparse.RawTextHelpFormatter)

upgrade_parser = command_parser.add_parser(
    "upgrade", help="Upgrade PIM partition's AI image to the latest version", parents=[common_parser], description="Upgrade PIM partition's AI image to the latest version", formatter_class=argparse.RawTextHelpFormatter)

rollback_parser = command_parser.add_parser(
    "rollback", help="Rollback PIM partition's AI image to its previous version", parents=[common_parser], description="Rollback PIM partition's AI image to its previous version", formatter_class=argparse.RawTextHelpFormatter)

update_compute_parser = command_parser.add_parser(
    "update-compute", help="Updates the cpu and memory configuration of the PIM partition", parents=[common_parser], description="Updates the cpu and memory configuration of the PIM partition", formatter_class=argparse.RawTextHelpFormatter)

update_config_parser = command_parser.add_parser(
    "update-config", help="Updates PIM partition's AI related configuration", parents=[common_parser], description="Updates PIM partition's AI related configuration", formatter_class=argparse.RawTextHelpFormatter)

status_parser = command_parser.add_parser(
    "status", help="Status of PIM partition", parents=[common_parser], description="Status of PIM partition(Overall partition status from HMC, AI application validation if enabled)", formatter_class=argparse.RawTextHelpFormatter)

command_args = parser.parse_args()
if command_args.debug:
    common.set_log_level(logging.DEBUG)
else:
    common.set_log_level(logging.INFO)

from cli.cmd.launch import launch
from cli.cmd.destroy import destroy
from cli.cmd.upgrade import upgrade
from cli.cmd.rollback import rollback
from cli.cmd.update_compute import update_compute
from cli.cmd.update_config import update_config
from cli.cmd.status import status

launch_parser.set_defaults(func=launch)
destroy_parser.set_defaults(func=destroy)
upgrade_parser.set_defaults(func=upgrade)
rollback_parser.set_defaults(func=rollback)
update_compute_parser.set_defaults(func=update_compute)
update_config_parser.set_defaults(func=update_config)
status_parser.set_defaults(func=status)

command_args = parser.parse_args()
command_args.func()
