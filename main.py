from fastapi import FastAPI, UploadFile, File
import whisper
import tempfile
import os
import glob

# Auto-detect ffmpeg from winget install path
FFMPEG_WINGET = glob.glob(
    os.path.expanduser("~/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_*/ffmpeg-*-full_build/bin")
)
if FFMPEG_WINGET and FFMPEG_WINGET[0] not in os.environ.get("PATH", ""):
    os.environ["PATH"] += os.pathsep + FFMPEG_WINGET[0]

app = FastAPI(title="Whisper Transcription API")
model = whisper.load_model("base")  # Options: tiny, base, small, medium, large


@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename)[1] if file.filename else ".mp3"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        result = model.transcribe(tmp_path)
    finally:
        os.unlink(tmp_path)

    return {
        "text": result["text"],
        "language": result["language"],
    }


@app.get("/")
def root():
    return {"status": "Whisper API running"}
