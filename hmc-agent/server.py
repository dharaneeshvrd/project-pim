import logging

# Bring in MCP Server SDK
from mcp.server.fastmcp import FastMCP
from tabulate import tabulate

import hmc

logger = logging.getLogger("mcp_server")

# Create server 
mcp = FastMCP("ibmhmcserver")

session_key = ""
cookies = None

# Add hmc version retriever tool
@mcp.tool()
def get_hmc_version() -> str:
    """This tool returns the HMC version.
    Returns:
        str:"Major version: 1, minor version: 0, service pack version: 1110"
    """
    hmc.authenticate_hmc()
    major_ver, min_ver, serv_pack_name = hmc.get_hmc_version()
    hmc.delete_session()
    return str(f"HMC Version info \n major version: {major_ver}\n minor version: {min_ver}\n service pack name: {serv_pack_name}")

@mcp.tool()
def list_all_systems() -> str:
    """This tool returns all power systems managed by HMC.
    Returns:
        str:"list of power system names"
    """
    hmc.authenticate_hmc()
    systems = hmc.list_all_systems()
    res = '\n'.join(systems)
    hmc.delete_session()
    return str(f"list of power systems managed by HMC: {res}")

@mcp.tool()
def get_logical_partitions() -> str:
    """This tool returns the logical partitions created in HMC.
    Returns:
        str: "Logical Partition Name: <name>, ID: <id>, State: <state>"
    """
    hmc.authenticate_hmc()
    partitions_json = hmc.get_logical_partitions()
    partitions = hmc.compose_parititon_data(partitions_json)

    if not partitions:
        return "No logical partitions found."

    result = []
    # Iterate through the partitions and format the output
    for partition in partitions:
        name = partition["name"]
        lpar_id = partition["id"]
        state = partition["state"]
        result.append([name, lpar_id, state])
    
    headers = ["Logical Partition Name", "ID", "State"]
    hmc.delete_session()
    return tabulate(result, headers=headers, tablefmt="grid")
    
@mcp.tool()
def partition_stats(partition_name) -> str:
    """
    This tool returns the status of given parititon
    Returns:
        str: PartitionState: <current parititon's status>
    """
    # Get lpar UUID from partition name
    hmc.authenticate_hmc()
    stats = hmc.paritition_stats(partition_name)
    hmc.delete_session()
    parititon_stats = {"partition_stats": stats}
    return str(f"Current status of partition: \n{parititon_stats}")

@mcp.tool()
def get_compute_usage(system_name) -> str:
    """
    This tool returns current usage of given system's cpu and memory.
    """
    hmc.authenticate_hmc()
    sys_uuid = hmc.get_system_uuid(system_name)
    logger.info(f"system UUID: {sys_uuid}")
    compute_details = hmc.get_compute_usage(sys_uuid)
    hmc.delete_session()
    compute_usage = {"compute_usage": compute_details}
    return str(f"Compute usage details: \n{compute_usage}")

# Kick off MCP server
if __name__ == "__main__":
    mcp.run(transport="stdio")
