import streamlit as st
import requests
import os

BASE_URL = "http://127.0.0.1:8000"

st.title("yippie hackathon boson higgssssss")

# upload a file
st.header("Upload file")
uploaded_file = st.file_uploader("choose an audio file")
if uploaded_file is not None:
    st.write(f"selected file: {uploaded_file.name}")
    if st.button("upload file"):
        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
        response = requests.post(f"{BASE_URL}/upload/", files=files)
        if response.status_code == 200:
            st.success(response.json()["detail"])
        else:
            st.error(f"Error: {response.text}")

st.header("processing existing file")
filename = st.text_input("enter filename")
if st.button("process file"): # create a button that toggles an if block
    response = requests.get(f"{BASE_URL}/process/{filename}") # call backend endpoint
    # endpoint - backend application that can be accessed by client applications
    if response.status_code == 200: # evaluate if a http request was sucessful

        result = response.json() # response from backend is json.
        st.subheader(f"Results for {result['filename']}") # convert it to python dictionary
        st.json(result["result"]) # display the result

    else:
        st.error(f"Error: {response.text}")
