import os
# Import smolagents 
from smolagents import ToolCallingAgent, ToolCollection, LiteLLMModel, LogLevel

# Specify Ollama LLM via LiteLLM
model = LiteLLMModel(
        model_id=os.getenv("OLLAMA_MODEL"),
        num_ctx=8192)

while True:
    user_input = input("\nYou: ")
    if user_input.lower() == "exit":
        print("Ending chat session...")
        break

    sse_params = {
    "transport": "sse",
    "url": "http://127.0.0.1:8000/sse"
    }

    with ToolCollection.from_mcp(sse_params, trust_remote_code=True) as tool_collection:
        agent = ToolCallingAgent(tools=[*tool_collection.tools], model=model,verbosity_level=LogLevel.OFF)
        response = agent.run(user_input, stream=False, max_steps=1)
        print(f"\nAgent: {response}")
