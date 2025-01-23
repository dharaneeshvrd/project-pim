
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

def get_bootstrap_iso(config):
    return config.get("CUSTOM_ISO", "bootstrap_iso").strip('"')

def get_cloud_init_iso(config):
    return config.get("CUSTOM_ISO", "cloud_init_iso").strip('"')

def get_iso_target_path(config):
    return config.get("CUSTOM_ISO", "target_path").strip('"')

def get_disk_name(config):
    return config.get("CUSTOM_ISO", "disk_name").strip('"')

def get_system_name(config):
    return config.get("SERVER", "name").strip('"')


# partition related Getters
def get_desired_memory(config):
    return config.get("MEMORY_CONFIG", "desired_memory").strip('"')

def get_max_memory(config):
    return config.get("MEMORY_CONFIG", "max_memory").strip('"')

def get_min_memory(config):
    return config.get("MEMORY_CONFIG", "min_memory").strip('"')

def get_desired_proc(config):
    return config.get("PROCESSOR_CONFIG", "desired_vpu").strip('"')

def get_max_proc(config):
    return config.get("PROCESSOR_CONFIG", "max_vpu").strip('"')

def get_min_proc(config):
    return config.get("PROCESSOR_CONFIG", "min_vpu").strip('"')

def has_dedicated_proc(config):
    return config.get("PROCESSOR_CONFIG", "has_dedicated_proc")

def get_sharing_mode(config):
    return config.get("PROCESSOR_CONFIG", "sharing_mode").strip('"')

def get_partition_type(config):
    return config.get("PARTITION", "type").strip('"')

def get_partition_name(config):
    return config.get("PARTITION", "name").strip('"')

# Network config Getters
def get_vswitch_name(config):
    return config.get("NETWORK_CONFIG", "virtual_switch_name").strip('"')

def get_vnetwork_name(config):
    return config.get("NETWORK_CONFIG", "virtual_network_name").strip('"')

def get_ip_address(config):
    return config.get("NETWORK_CONFIG", "ip_address").strip('"')

def get_ssh_keyfile(config):
    return config.get("NETWORK_CONFIG", "ssh_key").strip('"')

# storage related Getters
def get_physical_volume_name(config):
    return config.get("STORAGE", "physical_volume_name").strip('"')

def get_vopt_name(config):
    return config.get("STORAGE", "vopt_name").strip('"')

def get_vopt_bootstrap_name(config):
    return config.get("STORAGE", "vopt_bootstrap_name").strip('"')

def get_vopt_cloud_init_name(config):
    return config.get("STORAGE", "vopt_cloud_init_name").strip('"')

def get_volume_group(config):
    return config.get("STORAGE", "vg_name").strip('"')

def get_virtual_disk_name(config):
    return config.get("STORAGE", "vdisk_name").strip('"')

def use_virtual_disk(config):
    return config.getboolean("STORAGE", "use_virtual_disk")

def use_existing_vd(config):
    return config.getboolean("STORAGE", "use_existing_vd")

def use_existing_vg(config):
    return config.getboolean("STORAGE", "use_existing_vg")

def get_virtual_disk_size(config):
    return config.get("STORAGE", "vdisk_size").strip('"')
