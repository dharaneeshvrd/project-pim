import hashlib
import logging
import os

from urllib.parse import urlparse
from configobj import ConfigObj

import auth.auth as auth
import utils.string_util as util

LOG_LEVEL = logging.INFO
PARTITION_FLAVOR_DIR = f"{os.getcwd()}/partition-flavor"

def set_log_level(level):
    global LOG_LEVEL
    LOG_LEVEL = level

def setup_logging(level):
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=level
    )

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    logger.propagate = False

    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)-8s - %(message)s')
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)

    return logger

def cleanup(config, cookies):
    auth.delete_session(config, cookies)

def create_dir(path):
    try:
        if not os.path.isdir(path):
            os.mkdir(path)
    except OSError as e:
        logger.error(f"failed to create '{path}' directory, error: {e}")
        raise


def file_checksum(file):
    sha256 = hashlib.sha256()
    with open(file, 'rb') as f:
        for chunk in iter(lambda: f.read(128 * sha256.block_size), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def string_hash(str):
    return hashlib.sha256(str.encode('utf-8')).hexdigest()

def readfile(filename):
    f = open(filename, "r")
    data = f.read()
    return data

def verify_checksum(file, checksum_file):
    file_sha256 = file_checksum(file)
    data = readfile(checksum_file)
    csum = data.split(' ')[0]
    if csum == file_sha256:
        return True
    return False

def get_iso_url_and_checksum_path(config, iso_folder):
    iso_url = util.get_bootstrap_iso_download_url(config)
    iso_file_path = f"{iso_folder}/{util.get_bootstrap_iso(config)}"
    url_path = urlparse(iso_url).path
    iso_file = url_path.split('/')[-1]
    checksum_file = iso_file.replace('.iso', '.checksum')
    checksum_url = iso_url.replace(iso_file, checksum_file)
    checksum_file_path = f"{iso_folder}/{checksum_file}"
    return iso_url, iso_file_path, checksum_url, checksum_file_path

def load_partition_flavor(flavor_name):
    try:
        flavor_list = list_defined_partition_flavor()
        file_name = f"{flavor_name}.ini"
        if flavor_name in flavor_list:
            config = ConfigObj(f"{PARTITION_FLAVOR_DIR}/{file_name}")
            return config
        raise Exception(f"partition flavor with name '{flavor_name}' is undefined")
    except Exception as e:
        raise e

def list_defined_partition_flavor():
    flavor_list = []
    try:
        config_list = os.listdir(PARTITION_FLAVOR_DIR)
        for file in config_list:
            name = file.split(".")[0]
            flavor_list.append(name)
    except Exception as e:
        raise e
    return flavor_list

logger = get_logger("common-utils")
