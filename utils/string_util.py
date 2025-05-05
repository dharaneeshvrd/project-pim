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
    # Use below return while handling the rerun scenario for bootstrap ISO
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

def get_shared_desired_proc(config):
    return config["custom-flavor"]["cpu"]["shared"]["desired-proc-unit"]

def get_shared_max_proc(config):
    return config["custom-flavor"]["cpu"]["shared"]["max-proc-unit"]

def get_shared_min_proc(config):
    return config["custom-flavor"]["cpu"]["shared"]["min-proc-unit"]

def get_shared_desired_virt_proc(config):
    return config["custom-flavor"]["cpu"]["shared"]["desired-virt-proc"]

def get_shared_max_virt_proc(config):
    return config["custom-flavor"]["cpu"]["shared"]["max-virt-proc"]

def get_shared_min_virt_proc(config):
    return config["custom-flavor"]["cpu"]["shared"]["min-virt-proc"]

def has_dedicated_proc(config):
    return  "true" if config["custom-flavor"]["cpu"]["mode"] == "dedicated" else "false"

def get_cpu_mode(config):
    return config["custom-flavor"]["cpu"]["mode"]

def get_sharing_mode(config):
    return config["custom-flavor"]["cpu"]["sharing-mode"]

def get_partition_type(config):
    return "AIX/Linux"

def get_partition_name(config):
    return config["partition"]["name"]

def get_partition_flavor(config):
    return config["partition"]["flavor"]

# Network config Getters
def get_vswitch_name(config):
    return config["partition"]["network"]["connection"]["virtual-switch-name"]

def get_vnetwork_name(config):
    return config["partition"]["network"]["connection"]["virtual-network-name"]

def get_ip_address(config):
    return config["partition"]["network"]["ip"]["address"]

def get_network_prefix_length(config):
    return config["partition"]["network"]["ip"]["prefix-length"]

def get_network_gateway(config):
    return config["partition"]["network"]["ip"]["gateway"]

def get_network_nameserver(config):
    return config["partition"]["network"]["ip"]["nameserver"]

def get_ssh_username(config):
    return config["ssh"]["user-name"]

def get_ssh_priv_key(config):
    return config["ssh"]["priv-key-file"]

def get_ssh_pub_key(config):
    return config["ssh"]["pub-key-file"]

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

def get_workload_image(config):
    return config["ai"]["workload-image"]

def get_llm_args(config):
    return config["ai"]["llm-args"]

def get_llm_image(config):
    return config["ai"]["llm-image"]

def get_auth_json(config):
    return config["ai"]["auth-json"]

def get_model(config):
    llm_args = get_llm_args(config)
    llm_args_s = llm_args.split(" ")
    model = ""
    for i, arg in enumerate(llm_args_s):
        if "--model=" in arg:
            model = arg.split("=")[-1]
            return model
        elif "--model" == arg and len(llm_args_s) > i+1:
            model = llm_args_s[i+1]
            return model

    raise Exception("Not able to retrieve model from input config, check your llm_args. llm_args: {}".format(llm_args))
