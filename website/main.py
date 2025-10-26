# main.py
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import os
import shutil
from fastapi.middleware.cors import CORSMiddleware
from transcriptutil import generate_transcription
from audiogeneration import generateAudio
from instruction import placeholder
import radar_sim  # headless background radar (no Streamlit/Tk)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Start background radar simulation/rendering on server startup
@app.on_event("startup")
def _start_bg():
    try:
        radar_sim.start_background()
    except Exception as e:
        # Don't crash the API if background fails to start
        print(f"[startup] Failed to start radar background: {e}")

FILE_DIR = "data/"  # where to store files
os.makedirs(FILE_DIR, exist_ok=True)  # make sure the directory exists

def process_file(file_path: str):
    return f"the file read is {file_path}"

# read and process file from directory
@app.get("/process/{filename}")
async def process_existing_file(filename: str):
    file_path = os.path.join(FILE_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="file not found")
    result = process_file(file_path)
    return {"filename": filename, "result": result}

# allow uploads from frontend
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(FILE_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"detail": f"File '{file.filename}' uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

@app.post("/generate/")
async def generate_endpoint():
    text = generate_transcription("./data/front_end_pilotCommand.wav")
    return text

@app.post("/generate-audio/")
async def generate_audio_endpoint():
    try:
        text = placeholder()
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        generateAudio(text)
        if not os.path.exists("output.wav"):
            raise HTTPException(status_code=500, detail="Audio generation failed")
        return FileResponse("output.wav", media_type="audio/wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/plot/")
async def plot_endpoint():
    # Serve the plot image using an absolute path to avoid CWD issues
    image_path = os.path.join(os.path.dirname(__file__), "current_plot.png")
    
    # Check if the image file exists
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Plot image not found")
    
    return FileResponse(image_path, media_type="image/png")


# --- Optional control endpoints to mirror send_commands & state queries ---
class CommandRequest(BaseModel):
    instruction: str


@app.post("/command")
async def command_endpoint(body: CommandRequest):
    try:
        ok, msg = radar_sim.submit_instruction(body.instruction)
        if not ok:
            raise HTTPException(status_code=400, detail=msg)
        # force a fresh render immediately (optional)
        try:
            radar_sim.generate_plot()
        except Exception:
            pass
        return {"detail": msg}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/flights")
async def flights_endpoint():
    try:
        return {"flights": radar_sim.list_flights()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/log")
async def log_endpoint(tail: int = 50):
    try:
        return {"log": radar_sim.get_log(tail)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))