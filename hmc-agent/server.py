from colorama import Fore
# Bring in MCP Server SDK
from mcp.server.fastmcp import FastMCP
from tabulate import tabulate

import hmc

# Create server 
mcp = FastMCP("ibmhmcserver")

session_key = ""
cookies = None

# Add hmc version retriever tool
@mcp.tool()
def get_hmc_version(hmc_creds: dict) -> str:
    """This tool returns the HMC version of a given HMC.
    Args:
        hmc_creds:  A dictionary containing the HMC connection credentials.
        Example:
            {
                "HMC_IP": "10.0.0.22",
                "HMC_USERNAME": "xyz",
                "HMC_PASSWORD": "abc"
            }

    Returns:
        str:"Major version: 1, minor version: 0, service pack version: 1110"
    """
    global session_key
    global cookies

    hmc_creds =  {k.lower(): v for k, v in hmc_creds.items()}
    session_key, cookies = hmc.authenticate_hmc(hmc_creds)
    major_ver, min_ver, serv_pack_name = hmc.get_hmc_version(hmc_creds["hmc_ip"], session_key, cookies)
    print(f"HMC Version info \n major version: {major_ver}\n minor version: {min_ver}\n service pack name: {serv_pack_name}")
    return str(f"HMC Version info \n major version: {major_ver}\n minor version: {min_ver}\n service pack name: {serv_pack_name}")

@mcp.tool()
def list_all_systems(ip_addr: str) -> str:
    """This tool returns all power systems managed by the given HMC.
    Args:
        ip_address: valid ip address with 4 octets separated by :
        Example payload: "10.0.0.22"

    Returns:
        str:"list of power systems"
    """

    global session_key
    global cookies

    if len(session_key) == 0 and cookies is None:
        # Authenticate with HMC
        session_key, cookies = hmc.authenticate_hmc(ip_addr)

    systems = hmc.list_all_systems(ip_addr, session_key, cookies)
    res = ' '.join(systems)
    return str(f"list of power systems managed by HMC: {res}")

@mcp.tool()
def get_logical_partitions(ip_addr: str) -> str:
    """This tool returns the logical partitions of a given HMC.
    Args:
        ip_address: valid ip address with 4 octets separated by :
        Example payload: "10.0.0.22"
    Returns:
        str: "Logical Partition Name: <name>, ID: <id>, State: <state>"
    """
    session_key, cookies = hmc.authenticate_hmc(ip_addr)
    
    partitions = hmc.get_logical_partitions(ip_addr, session_key, cookies)

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
    return tabulate(result, headers=headers, tablefmt="grid")
    

# Kick off MCP server
if __name__ == "__main__":
    mcp.run(transport="stdio")
