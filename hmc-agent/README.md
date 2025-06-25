# AI agent to manage Power Infra using MCP Server built for HMC 

# Setup
1. Clone this repository `git clone https://github.ibm.com/project-pim/infra-agents` and go into it `cd infra-agents`
2. Create a virtual environment `uv venv` and activate it `source .venv/bin/activate`
3. Install the dependencies `uv sync`
Note: Make sure npm/nodejs dependency is installed to use `uv` functionalities 

# Usage

Run ollama in local wherever you are going to run your agent application

**Set env**
```
# HMC details
export HMC_IP=""
export HMC_USERNAME=""
export HMC_PASSWORD=""

# Model to use
export OLLAMA_MODEL="ollama_chat/granite3.2:8b"
```
**Run the agent**
```
uv run agent.py "<< query >>"

ex:
uv run agent.py "List the partitions that are in running state"
```

Other sample queries:
```
- Get HMC version
- List the systems managed by HMC
- List the partitions
```

Optionally you can run the inspector `uv run mcp dev server.py` to interact with the tools directly without LLM