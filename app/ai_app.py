import json
import requests

import utils.string_util as util
import utils.common as common
from .ai_app_exception import AiAppError

logger = common.get_logger("AI-app")

APP_PORT = "8000"
PROMPT_PAYLOAD = '''
{{
    "model": "{model}",
    "messages": [[
        {{
            "role": "user",
            "content": "What is the capital of France?"
        }}
    ]]
}}
'''

def get_prompt_payload():
    return PROMPT_PAYLOAD.format(model=util.get_model())

def check_app(config):
    ip_address = util.get_ip_address(config)
    url = "http://" + ip_address + ":" + APP_PORT + "/v1/models"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            logger.error(f"AI application didn't respond {response.text}, will retry...")
            return False
    except Exception as e:
        logger.info(f"AI application not responding yet, err: {e}")
        return False

    logger.info("AI application responded healthy..")
    return True

def check_bot_service(config):
    ip_address = util.get_ip_address(config)
    url = "http://" + ip_address + ":" + APP_PORT + "/v1/chat/completions"
    try:
        payload = get_prompt_payload()
        prompt = json.loads(payload)
        logger.info(f"Prompt: \n{prompt}")
        response = requests.post(url,  data=payload, headers={"Content-Type": "application/json"})
        if response.status_code != 200:
            logger.error(f"Failed to get response for a prompt from OpenAI API server: {response.text}")
            raise AiAppError(f"Failed to get response for a prompt from OpenAI API server: {response.text}")
        resp_json = response.json()
    except Exception as e:
        logger.info(f"Failed to get response for a prompt from OpenAI API server: {e}")
        raise AiAppError(f"Failed to get response for a prompt from OpenAI API server: {e}")
    
    return resp_json
