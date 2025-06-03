from colorama import Fore
# Bring in MCP Server SDK
from mcp.server.fastmcp import FastMCP

import hmc

# Create server 
mcp = FastMCP("ibmhmcserver")

session_key = ""
cookies = None

# Add hmc version retriever tool
@mcp.tool()
def get_hmc_version(ip_addr: str) -> str:
    """This tool returns the HMC version of a given HMC.
    Args:
        ip_address: valid ip address with 4 octets separated by :
        Example payload: "10.0.0.22"

    Returns:
        str:"Major version: 1, minor version: 0, service pack version: 1110"
    """
    global session_key
    global cookies

    session_key, cookies = hmc.authenticate_hmc(ip_addr)
    major_ver, min_ver, serv_pack_name = hmc.get_hmc_version(ip_addr, session_key, cookies)
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

# Kick off MCP server
if __name__ == "__main__":
    mcp.run(transport="stdio")
