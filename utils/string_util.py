import hashlib

def get_system_name(config):
    return config["system"]["name"]

def get_host_address(config):
    return config["system"]["hmc"]["host-address"]

def get_host_username(config):
    return config["system"]["hmc"]["user-name"]

def get_host_password(config):
    return config["system"]["hmc"]["password"]

def get_vios_address(config):
    return config["system"]["vios-server"]["host-address"]

def get_session_key(config):
    return  config["session"]["x-api-key"]

def get_bootstrap_iso(config):
    # Use below return while handling the rerun scenario for bootstrap iso
    #return hashlib.sha256(get_bootstrap_iso_download_url(config).encode()).hexdigest()[:32] + "_pimb"
    return get_partition_name(config) + "_pimb" 

def get_cloud_init_iso(config):
    return get_partition_name(config) + "_pimc"

# partition related Getters
def get_desired_memory(config):
    return config["custom-flavor"]["memory"]["desired-memory"]

def get_max_memory(config):
    return config["custom-flavor"]["memory"]["max-memory"]

def get_min_memory(config):
    return config["custom-flavor"]["memory"]["min-memory"]

def get_desired_proc(config):
    return config["custom-flavor"]["cpu"]["dedicated"]["desired-proc-unit"]

def get_max_proc(config):
    return config["custom-flavor"]["cpu"]["dedicated"]["max-proc-unit"]

def get_min_proc(config):
    return config["custom-flavor"]["cpu"]["dedicated"]["min-proc-unit"]

def has_dedicated_proc(config):
    return  "true" if config["custom-flavor"]["cpu"]["mode"] == "deicated" else "false"

def get_sharing_mode(config):
    return config["custom-flavor"]["cpu"]["sharing-mode"]

def get_partition_type(config):
    return "AIX/Linux"

def get_partition_name(config):
    return config["partition"]["name"]

# Network config Getters
def get_vswitch_name(config):
    return config["partition"]["network"]["connection"]["virtual-switch-name"]

def get_vnetwork_name(config):
    return config["partition"]["network"]["connection"]["virtual-network-name"]

def get_ip_address(config):
    return config["partition"]["network"]["ip"]["address"]

def get_ssh_username(config):
    return config["partition"]["ssh"]["user-name"]

def get_ssh_password(config):
    return "PIMForPowerSpyre"

# storage related Getters
def get_physical_volume_name(config):
    return config.get("STORAGE", "physical_volume_name").strip('"')

def get_volume_group(config):
    return config.get("STORAGE", "vg_name").strip('"')

def get_virtual_disk_name(config):
    return config.get("STORAGE", "vdisk_name").strip('"')

def use_virtual_disk(config):
    return False

def use_existing_vd(config):
    return config.getboolean("STORAGE", "use_existing_vd")

def use_existing_vg(config):
    return config.getboolean("STORAGE", "use_existing_vg")

def get_required_disk_size(config):
    return config["partition"]["storage"]["size"]

def get_bootstrap_iso_download_url(config):
    return config["ai"]["bootstrap-iso-url"]

def get_llm_args(config):
    return config["ai"]["llm-args"]

def get_model(config):
    llm_args = get_llm_args(config)
    llm_args_s = llm_args.split(" ")
    model = ""
    for i, arg in enumerate(llm_args_s):
     if "--model=" in arg:
             model = arg.split("=")[-1]
             break
     elif "--model" == arg and len(llm_args_s) > i+1:
             model = llm_args_s[i+1]
             break
     if model == "":
         raise Exception("Not able to retrieve model from input config, check your llm_args. llm_args: {}".format(llm_args))
     
     return model
