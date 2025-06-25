import os
import sys
# Import smolagents 
from smolagents import ToolCallingAgent, ToolCollection, LiteLLMModel
# Bring in MCP Client Side libraries
from mcp import StdioServerParameters

# Specify Ollama LLM via LiteLLM
model = LiteLLMModel(
        model_id=os.getenv("OLLAMA_MODEL"),
        num_ctx=8192) 

# Outline STDIO stuff to get to MCP Tools
server_parameters = StdioServerParameters(
    command="uv",
    args=["run", "server.py"],
    env={"HMC_IP": os.getenv("HMC_IP"), "HMC_USERNAME": os.getenv("HMC_USERNAME"), "HMC_PASSWORD": os.getenv("HMC_PASSWORD")},
)

# Run the agent using the MCP tools 
with ToolCollection.from_mcp(server_parameters, trust_remote_code=True) as tool_collection:
    agent = ToolCallingAgent(tools=[*tool_collection.tools], model=model)
    agent.run(sys.argv[1])
