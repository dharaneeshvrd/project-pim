import argparse
import logging
import urllib3

from actions.destroy import destroy
from actions.launch import launch
from actions.rollback import rollback
from actions.upgrade import upgrade
import utils.common as common


parser = argparse.ArgumentParser(description="PIM lifecycle manager")
parser.add_argument("action", choices=["launch", "upgrade", "rollback", "destroy"],
                    help="Does launch, upgrade, rollback and destroy PIM partition")
parser.add_argument("--debug", action='store_true',
                    help='Enable debug logging level')
args = parser.parse_args()

if args.debug:
    common.set_log_level(logging.DEBUG)
else:
    common.set_log_level(logging.INFO)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
globals()[args.action]()
