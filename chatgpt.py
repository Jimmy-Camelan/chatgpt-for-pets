import streamlit as st
from streamlit_chat import message

import openai
from google.cloud import texttospeech
from google.oauth2 import service_account
import json
import os
from config import open_api_key
import base64
openai.api_key = open_api_key

def google_auth(sa, sa_private_key):
    SA_str = sa
    info = json.loads(SA_str)
    info['private_key'] = sa_private_key
    credentials = service_account.Credentials.from_service_account_info(info)
    client = texttospeech.TextToSpeechClient(credentials=credentials)
    return client

def text_to_speech(text_to_convert):
    sa = os.environ.get('SERVICE_ACCOUNT')
    sa_private_key = os.environ.get('SA_PRIVATE_KEY')
    client = google_auth(sa, sa_private_key)


    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=text_to_convert)

    # Build the voice request, select the language code ("en-US") and the ssml
    # voice gender ("neutral")
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Neural2-F",
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
    )

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config)
    with open("output.mp3", "wb") as out:
        out.write(response.audio_content)
        print('Audio content written to file "output.mp3"')
    
    return response



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

def get_audio_str(file_name):
    aud_file= open(file_name,"rb")
    aud_data_binary = aud_file.read()
    aud_data = (base64.b64encode(aud_data_binary)).decode('ascii')
    return aud_data

if user_input:
    output = generate_response(user_input)
    text_to_speech(output)
    TTS_file = get_audio_str("./output.mp3")

    history_input.append([user_input, output])
    st.session_state.past.append(user_input)
    st.session_state.generated.append(output)
#     html_string = """
#             <audio id='audio' controls autoplay>
# """ + "<source src=\"data:audio/mpeg;base64,{}\">".format(TTS_file) + """
#               Your browser does not support the audio element.
#             </audio>
#             <script type="application/javascript">
#             const myTimeout = setTimeout(playAudio, 5000);
#             function playAudio() {
#               console.log("helloooooo");
#               document.getElementById('audio').play();
#             }
#             </script>
# """
#     sound = st.empty()
#     sound.markdown(html_string, unsafe_allow_html=True)

if st.session_state['generated']:
    html_string = """
      <audio id='audio' controls autoplay>
""" + "<source src=\"data:audio/mpeg;base64,{}\">".format(TTS_file) + """
        Your browser does not support the audio element.
      </audio>
      <script type='application/javascript'>
      document.getElementById('audio').play();
      </script>
"""
    sound = st.empty()
    sound.markdown(html_string, unsafe_allow_html=True)
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state["generated"][i], key=str(i))
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
    else:
        html_string = """
        <hr/>
<script type='application/javascript'>
          audio_src = document.getElementById('audio_src')
          audio_src = """ + "\"data:audio/mpeg;base64,{}\">".format(TTS_file) + """
          audio_player.load();
          audio_player = document.getElementById('audio').play();
</script>
"""
        player = st.empty()
        player.markdown(html_string, unsafe_allow_html=True)
