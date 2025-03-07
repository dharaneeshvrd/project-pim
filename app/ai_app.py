import json
import requests

from bs4 import BeautifulSoup

import utils.string_util as util
import utils.common as common

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

def check_app(config):
    ip_address = util.get_ip_address(config)
    url = "http://" + ip_address + ":" + APP_PORT
    response = requests.get(url, verify=False)
    if response.status_code != 200:
        print("AI application didn't respond ", response.text)
        return False
    print("AI application responded healthy..")
    return True

def check_bot_service(config):
    ip_address = util.get_ip_address(config)
    url = "http://" + ip_address + ":" + APP_PORT + "/completion"
    payload = get_prompt_payload()
    prompt = json.loads(payload)["prompt"]
    print("Prompt: \n%s" % prompt)
    response = requests.post(url,  data=payload, verify=False)
    if response.status_code != 200:
        print("Failed to get response for a prompt from bot service ", response.text)
        common.cleanup_and_exit(1)
    resp_json = response.json()
    return resp_json["content"]
