from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import shutil
from fastapi.middleware.cors import CORSMiddleware # something about letting you do something something across backend and frontend when hosted on different ports
from transcriptutil import generate_transcription
from audiogeneration import generateAudio
from instruction import placeholder
from infoscraper import scrapeinfo

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


FILE_DIR = "data/" # where to store files
os.makedirs(FILE_DIR, exist_ok = True) # make sure the directory exists

def process_file(file_path : str):
    return f"the file read is {file_path}"

# read and process file from directory
@app.get("/process/{file_name}")
async def process_existing_file(filename : str):
    file_path = os.path.join(FILE_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="file not found")
    result = process_file(file_path)
    return {"filename": filename, "result": result}

# allow uploads from frontend
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)): # async load means if the server is bogged down, it can handle other requests first.
    file_path = os.path.join(FILE_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"detail": f"File '{file.filename}' uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
    

from pydantic import BaseModel
import os

app = FastAPI()

FILE_DIR = "data/" # where to store files

def process_file(file_path : str):
    return f"the file read is {file_path}"

# read and process file from directory
@app.get("/process/{file_name}")
async def process_existing_file(filename : str):
    file_path = os.path.join(FILE_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="file not found")
    result = process_file(file_path)
    return {"filename": filename, "result": result}

# allow uploads from frontend
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)): # async load means if the server is bogged down, it can handle other requests first.
    file_path = os.path.join(FILE_DIR, file.filename)
    return {"detail": f"file {file.filename} uploaded yippiee"}

@app.post("/generate/")
async def generate_endpoint():
    # payload is a dictionary that contains the request data
    text = generate_transcription("./data/front_end_pilotCommand.wav") # dummy text
    return text

@app.post("/generate-audio/")
async def generate_audio_endpoint():
    # infoscraper
    scraped = scrapeinfo("./data/front_end_pilotCommand.wav")
    try:
        text = placeholder(scraped)  
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        # Generate audio file
        generateAudio(text)
        
        # Check if file was created
        if not os.path.exists("output.wav"):
            raise HTTPException(status_code=500, detail="Audio generation failed")
            
        return FileResponse("output.wav", media_type="audio/wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

