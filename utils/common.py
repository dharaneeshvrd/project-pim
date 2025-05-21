import logging
import hashlib
from urllib.parse import urlparse

import auth.auth as auth
import utils.string_util as util

LOG_LEVEL = logging.INFO

def set_log_level(level):
    global LOG_LEVEL
    LOG_LEVEL = level

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

def hash(file):
    sha256 = hashlib.sha256()
    with open(file, 'rb') as f:
        for chunk in iter(lambda: f.read(128 * sha256.block_size), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def readfile(filename):
    f = open(filename, "r")
    data = f.read()
    return data

def verify_checksum(file, checksum_file):
    file_sha256 = hash(file)
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
