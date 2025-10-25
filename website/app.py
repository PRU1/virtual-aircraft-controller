# chatgpt patch
# if pyaudioop is not found, use audioop instead
# run pip install audioop !!

# app.py (very top, before other imports)
import sys

# Fix for pydub trying to import 'pyaudioop' instead of 'audioop'
if 'pyaudioop' not in sys.modules:
    import audioop
    sys.modules['pyaudioop'] = audioop

# Now your normal imports
from audiorecorder import audiorecorder

import streamlit as st
import requests
import io

BASE_URL = "http://127.0.0.1:8000"

# load the CSS
def load_css():
    with open('styles.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()


st.title("Pilot Speaking")

# record audio in browser
audio = audiorecorder("Record", "Stop recording")

if len(audio) > 0:
    # Convert audio to bytes and play it
    audio_bytes = audio.export().read()
    st.audio(audio_bytes, format="audio/wav")
    
    if st.button("Upload Recorded Audio"):
        files = {"file": ("pilotCommand.wav", io.BytesIO(audio_bytes), "audio/wav")}
        response = requests.post(f"{BASE_URL}/upload/", files=files)
        if response.status_code == 200:
            with open("TESTINGTESTING.wav", "wb") as f:
                f.write(audio_bytes)
            st.success(response.json().get("detail"))
        else:
            st.error(f"Upload failed: {response.text}")
