import logging

import auth.auth as auth

def setup_logging(level):
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=level
    )

def get_logger(name):
    return logging.getLogger(name)

def cleanup_and_exit(config, cookies, status):
    auth.delete_session(config, cookies)
    exit(status)
