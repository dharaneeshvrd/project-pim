import argparse
import logging
import urllib3

import utils.common as common
from actions.destroy import destroy
from actions.launch import launch
from actions.rollback import rollback
from actions.update_compute import update_compute
from actions.upgrade import upgrade


def main():
    parser = argparse.ArgumentParser(description="PIM lifecycle manager")
    parser.add_argument("--debug", action='store_true',
                        help='Enable debug logging level')

    action_parsers = parser.add_subparsers(dest="action", required=True)
    launch_parser = action_parsers.add_parser(
        "launch", help="Create a new partition with the given configuration")
    launch_parser.set_defaults(func=launch)

    destroy_parser = action_parsers.add_parser(
        "destroy", help="Delete the partition and clean up the VIOS")
    destroy_parser.set_defaults(func=destroy)

    upgrade_parser = action_parsers.add_parser(
        "upgrade", help="Update the partition AI image to the latest version")
    upgrade_parser.set_defaults(func=upgrade)

    rollback_parser = action_parsers.add_parser(
        "rollback", help="Rollback the partition AI image to its previous version")
    rollback_parser.set_defaults(func=rollback)

    update_compute_parser = action_parsers.add_parser(
        "update-compute", help="Updates the cpu and memory configuration for the partition.")
    update_compute_parser.set_defaults(func=update_compute)

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    action_args = parser.parse_args()
    if action_args.debug:
        common.set_log_level(logging.DEBUG)
    else:
        common.set_log_level(logging.INFO)

    action_args.func()


if __name__ == "__main__":
    main()
