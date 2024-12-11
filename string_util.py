
def get_host_address(config):
    return config.get("HMC_HOST", "host_address").strip('"')

def get_host_username(config):
    return config.get("HMC_HOST", "username").strip('"')

def get_host_password(config):
    return config.get("HMC_HOST", "password").strip('"')


def get_vios_address(config):
    return config.get("VIOS_SERVER", "host_address").strip('"')

def get_vios_username(config):
    return config.get("VIOS_SERVER", "username").strip('"')

def get_vios_password(config):
    return config.get("VIOS_SERVER", "password").strip('"')

def get_session_key(config):
    return config.get("SESSION", "x-api-key").strip('"')

def get_iso(config):
    return config.get("CUSTOM_ISO", "iso").strip('"')

def get_iso_target_path(config):
    return config.get("CUSTOM_ISO", "target_path").strip('"')

def get_system_name(config):
    return config.get("SERVER", "name").strip('"')