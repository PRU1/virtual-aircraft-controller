from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil

from transcriptutil import generate_transcription
from audiogeneration import generateAudio
from instruction import placeholder
import radar_sim
import aircraftcreator

from audioparser import parse_audio
from pydantic import BaseModel


class CommandModel(BaseModel):
    callsign: str
    command: str
    value: int


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Kick off radar simulation threads when the API boots."""
    print("[main] Starting radar simulation...")
    radar_sim.start_background()
    aircraftcreator.start_background(start_gui=False)


FILE_DIR = "data"
os.makedirs(FILE_DIR, exist_ok=True)


def process_file(file_path: str) -> str:
    return f"the file read is {file_path}"


@app.get("/process/{file_name}")
async def process_existing_file(file_name: str):
    file_path = os.path.join(FILE_DIR, file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="file not found")
    result = process_file(file_path)
    return {"filename": file_name, "result": result}


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """Save uploaded audio, parse for instructions, and apply them.

    This saves the upload first (so parsing/reading doesn't consume the UploadFile
    stream unexpectedly), then opens the saved file and passes the file-object to
    `parse_audio`. The parsed result is then fed into the helper functions in
    `aircraftcreator`.
    """
    file_path = os.path.join(FILE_DIR, file.filename)

    # Save uploaded file first
    try:
        with open(file_path, "wb") as buffer:
            # ensure we're at start
            try:
                file.file.seek(0)
            except Exception:
                pass
            shutil.copyfileobj(file.file, buffer)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"File upload failed: {exc}")

    # Parse the saved file for instructions
    parse_results = []
    try:
        with open(file_path, "rb") as f:
            parsed = parse_audio(f)

        # Normalize parsed output and apply commands.
        # parse_audio may return a single string, a list of strings, or a list of tokens.
        if isinstance(parsed, str):
            ok, msg = aircraftcreator.process_command_string(parsed)
            parse_results.append({"instruction": parsed, "ok": ok, "msg": msg})
        elif isinstance(parsed, list):
            # If the parser returned a list of tokens (e.g. ['ABC123','alt','5000'])
            # join them into a single instruction string.
            if parsed and all(isinstance(x, str) for x in parsed):
                # Heuristic: if the list looks like a single instruction tokens, join once
                # If it appears to be multiple instruction strings, attempt to process each.
                # Detect nested lists by checking types of elements.
                if any(" " in x for x in parsed):
                    # elements already contain spaces -> treat each element as an instruction
                    for item in parsed:
                        ok, msg = aircraftcreator.process_command_string(item)
                        parse_results.append({"instruction": item, "ok": ok, "msg": msg})
                else:
                    # treat as token list for a single instruction
                    instr = " ".join(parsed)
                    ok, msg = aircraftcreator.process_command_string(instr)
                    parse_results.append({"instruction": instr, "ok": ok, "msg": msg})
            else:
                # Unknown structure: represent as string
                instr = str(parsed)
                ok, msg = False, "Unrecognized parse format"
                parse_results.append({"instruction": instr, "ok": ok, "msg": msg})
        else:
            parse_results.append({"parsed": str(parsed), "ok": False, "msg": "Unsupported parse result type"})
    except Exception as exc:
        # Parsing/applying commands failed, but file was saved successfully.
        parse_results.append({"error": str(exc)})

    return {"detail": f"File '{file.filename}' uploaded successfully", "parse_results": parse_results}
    


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
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/plot/")
async def plot_endpoint():
    """Serve the latest radar image, forcing a fresh render first."""
    image_path = os.path.join(os.path.dirname(__file__), "current_plot.png")
    try:
        radar_sim.generate_plot_once(image_path)
    except Exception as exc:
        print(f"[plot] Error generating plot: {exc}")

    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Plot image not found")

    return FileResponse(image_path, media_type="image/png")


@app.get("/test-plot")
async def test_plot():
    try:
        image_path = os.path.join(os.path.dirname(__file__), "current_plot.png")
        radar_sim.generate_plot_once(image_path)
        return {
            "detail": f"Plot generated at {image_path}",
            "flights": radar_sim.list_flights(),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/command/")
async def command_endpoint(cmd: CommandModel):
    """Send a single command to a flight.

    Body: {"callsign":"ABC123", "command":"alt", "value":5000}
    """
    try:
        ok, msg = aircraftcreator.send_command(cmd.callsign, cmd.command, cmd.value)
        if not ok:
            raise HTTPException(status_code=400, detail=msg)
        return {"detail": "command applied"}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

