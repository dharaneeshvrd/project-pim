import streamlit as st
import requests

def extract_entities(prompt, fields, text):
    messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Extract the following entities: {fields} from this text: {text}. Your output should strictly be in a json format, which only contains the key and value. The key here is the entity to be extracted and the value is the entity which you extracted."}
        ]
    payload = {
        "model": "ibm-granite/granite-3.2-2b-instruct",
        "messages": messages
    }

    # Send request to vLLM API
    try:
        response = requests.post("http://localhost:8000/v1/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()
        ai_message = data["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        ai_message = f"Error: {e}"

    return ai_message

st.title("Entity Extraction using OpenAI")

prompt = st.text_area("Enter the system prompt", "You are an AI trained to extract specific entities and return the output in JSON format.")
fields = st.text_input("Enter entities to extract (comma-separated)", "Person, Organization")
text = st.text_area("Enter text for entity extraction", "Barack Obama was the 44th President of the United States.")

if st.button("Extract Entities"):
    entities = extract_entities(prompt, fields, text)
    st.json(entities)
