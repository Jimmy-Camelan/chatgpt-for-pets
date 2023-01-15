import streamlit as st
from streamlit_chat import message

import openai
from config import open_api_key
openai.api_key = open_api_key
import urllib
import requests
import json


def generate_response(prompt):
    before_prompt = st.secrets['OPENAPI_PREPEND']
    after_prompt = st.secrets['OPENAPI_APPEND']
    prompt = "{}{}{}".format(before_prompt, prompt, after_prompt)
    completions = openai.Completion.create(
        engine = "text-davinci-003",
        prompt = prompt,
        max_tokens = st.secrets['OPENAPI_MAX_TOKENS'],
        n = 1,
        stop=[" Human:", " AI:"],
        temperature=st.secrets['OPENAPI_TEMP'],
    )
    message = completions.choices[0].text
    return message


def chatgpt_clone(input, history):
    history = history or []
    output = generate_response(input)
    history.append((input, output))
    return history, history

# Streamlit App
st.set_page_config(
    page_title="Camlist Pet Assistant",
    page_icon=":dog:"
)

st.header("Talk to the AI Pet Assistant by Camlist")

history_input = []

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []


def get_text():
    input_text = st.text_input("Ask me anything related to pets:", key="input")
    return input_text 


user_input = get_text()

def get_ultra_real_sound(message):
    url = "https://play.ht/api/v1/convert"
    payload = json.dumps({
    "voice": "Larry",
    "content": [
     "Hello My friends",
     "It's a beautiful day, isn't it ?"
    ],
    "speed": "1.0",
    "preset": "balanced"
  })
    headers = {
    'Authorization': "L8WNM2KVUYMdW8lZGyqidl5wZBE2",
    'X-User-ID': "92331bfc99da4105b3ef4cb87a5f221c",
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return respons.json()['payload']


if user_input:
    output = generate_response(user_input)
    TTS_file = get_ultra_real_sound(user_input)

    history_input.append([user_input, output])
    st.session_state.past.append(user_input)
    st.session_state.generated.append(output)
    html_string = """
            <audio id='audio' controls autoplay>
""" + "<source src=\"{}\" type=\"audio/mpeg\">".format(TTS_file) + """
              Your browser does not support the audio element.
            </audio>
            <script type="application/javascript">
            const myTimeout = setTimeout(playAudio, 5000);
            function playAudio() {
              console.log("helloooooo");
              document.getElementById('audio').play();
            }
            </script>
"""
    sound = st.empty()
    sound.markdown(html_string, unsafe_allow_html=True)

if st.session_state['generated']:

    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state["generated"][i], key=str(i))
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
