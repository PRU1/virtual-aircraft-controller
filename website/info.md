# HOW TO USE THIS CODE 
(for when I inevitably forget)

## Prereqs
Create a virtual environment and install: 
```
pip install streamlit fastapi torch uvicorn streamlit-audiorecorder
```
Also install ffmpeg (if Mac, run `brew install ffmpeg`. If on Windows, run the installer). There may be dependencies I'm missing, so install them if they come up please.

## Start the backend
In the directory `./website/`, run:
```
uvicorn main:app --reload
```

## Run the streamlit app 
Make sure you are in the directory of `app.py`. Run:
```
streamlit run app.py
```


