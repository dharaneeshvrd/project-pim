import argparse
import logging
import urllib3


from actions.destroy import destroy
from actions.launch import launch
from actions.rollback import rollback
from actions.update_compute import update_compute
from actions.upgrade import upgrade
import utils.common as common

parser = argparse.ArgumentParser(description="PIM lifecycle manager")
parser.add_argument("action", choices=["launch", "upgrade", "rollback", "update-compute", "destroy"],
                    help="Does launch, upgrade, rollback, update-compute and destroy PIM partition")
parser.add_argument("--debug", action='store_true',
                    help='Enable debug logging level')
args = parser.parse_args()

if args.debug:
    common.set_log_level(logging.DEBUG)
else:
    common.set_log_level(logging.INFO)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
action = "update_compute" if args.action == "update-compute" else args.action
globals()[action]()
