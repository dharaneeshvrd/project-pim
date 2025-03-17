import logging

import auth.auth as auth

def get_logger(name):
    logger = logging.getLogger(name)
    logging.basicConfig()
    logger.setLevel(logging.INFO)
    return logger

def cleanup_and_exit(config, cookies, status):
    print("deleting user HMC session")
    auth.delete_session(config, cookies)
    exit(status)
