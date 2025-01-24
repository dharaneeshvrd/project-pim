APP_PORT = "8080"
PROMPT_PAYLOAD = '''
{
    "stream":false,
    "n_predict":400,
    "temperature":0.7,
    "stop":["</s>",
    "Llama:","User:"],
    "repeat_last_n":256,
    "repeat_penalty":1.18,
    "top_k":40,
    "top_p":0.5,
    "min_p":0.05,
    "tfs_z":1,
    "typical_p":1,
    "presence_penalty":0,
    "frequency_penalty":0,
    "mirostat":0,
    "mirostat_tau":5,
    "mirostat_eta":0.1,
    "grammar":"",
    "n_probs":0,
    "image_data":[],
    "cache_prompt":true,
    "slot_id":-1,
    "prompt":"This is a conversation between User and Llama, a friendly chatbot. Llama is helpful, kind, honest, good at writing, and never fails to answer any requests immediately and with precision.\\n\\nUser: Write me an SQL query to join two tables\\nLlama:"
}
'''

def get_prompt_payload():
    return PROMPT_PAYLOAD
