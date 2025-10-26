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
import base64
import time
import os

from PIL import Image

BASE_URL = "http://127.0.0.1:8000"
placeholder = st.empty()
interval = 1



# load the CSS
def load_css():
    with open('styles.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def display_transcript():
    st.subheader("Pilot Command Transcription")

    with st.spinner("Generating..."):
        # POST JSON to the backend /generate/ endpoint
        resp = requests.post(f"{BASE_URL}/generate/", timeout=60)
    if resp.status_code == 200:
        data = resp.json()
        st.subheader("Generated text")
        st.write(data.get("text"))
    else:
        st.error(f"API error: {resp.status_code} — {resp.text}")

load_css()


st.title("Pilot Speaking")

# record audio in browser
audio = audiorecorder("Record", "Stop recording")

if len(audio) > 0:
    # Convert audio to bytes and play it
    audio_bytes = audio.export().read()
    st.audio(audio_bytes, format="audio/wav")
    
    if st.button("Upload Recorded Audio"):
        # Pause any auto-refresh loops while uploading
        st.session_state.busy = True
        with st.spinner("Uploading..."):
            try:
                files = {"file": ("pilotCommand.wav", io.BytesIO(audio_bytes), "audio/wav")}
                # Slightly longer timeout in case local disk is slow
                response = requests.post(f"{BASE_URL}/upload/", files=files, timeout=20)
                if response.status_code == 200:
                    os.makedirs("./data", exist_ok=True)
                    with open("./data/front_end_pilotCommand.wav", "wb") as f:
                        f.write(audio_bytes)
                    st.success(response.json().get("detail"))
                else:
                    st.error(f"Upload failed ({response.status_code}): {response.text}")
            except requests.exceptions.ConnectionError:
                st.error(f"❌ Cannot connect to backend at {BASE_URL}. Is the server running?")
            except requests.exceptions.Timeout:
                st.error("❌ Upload timed out. Backend may be overloaded.")
            except Exception as e:
                st.error(f"❌ Upload error: {str(e)}")
            finally:
                st.session_state.busy = False



## Add this after your display_transcript() call
#if "generated_audio" not in st.session_state:
    #st.session_state.generated_audio = None
    
# Initialize flags used for auto-refresh control
if "busy" not in st.session_state:
    st.session_state.busy = False
if "refresh_enabled" not in st.session_state:
    st.session_state.refresh_enabled = True

#if st.button("Generate Audio"):
    #with st.spinner("Generating audio..."):
        #try:
            #response = requests.post(
                #f"{BASE_URL}/generate-audio/",
                #json={},
                #timeout=90
            #)
            #if response.status_code == 200:
                ## Store audio bytes in session state
                #st.session_state.generated_audio = response.content
                
                ## Create autoplay audio element
                #b64_audio = base64.b64encode(response.content).decode()
                #audio_html = f'''
                    #<audio autoplay controls>
                        #<source src="data:audio/wav;base64,{b64_audio}" type="audio/wav">
                    #</audio>
                #'''
                ##st.markdown(audio_html, unsafe_allow_html=True)
                #st.success("Audio generated successfully!")
            #else:
                #st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
        #except Exception as e:
            #st.error(f"Failed to generate audio: {str(e)}")

## Show regular audio player if we have generated audio
#if st.session_state.generated_audio is not None:
    #st.audio(st.session_state.generated_audio, format="audio/wav")

#st.image("./current_plot.png", use_column_width=True)


st.image("./current_plot.png", use_container_width=True)
# Auto-refresh only when not busy with another task
if st.session_state.refresh_enabled and not st.session_state.busy:
    time.sleep(interval)
    st.rerun()