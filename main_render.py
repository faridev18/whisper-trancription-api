from fastapi import FastAPI, UploadFile, File
import whisper
import tempfile
import os
import imageio_ffmpeg

# Injecte ffmpeg (fourni par imageio-ffmpeg) dans le PATH
ffmpeg_bin = os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe())
if ffmpeg_bin not in os.environ.get("PATH", ""):
    os.environ["PATH"] = ffmpeg_bin + os.pathsep + os.environ.get("PATH", "")

# Sur Render free tier, utilise "tiny" pour éviter les OOM (512MB RAM)
# Modifiable via la variable d'env WHISPER_MODEL
MODEL_SIZE = os.environ.get("WHISPER_MODEL", "tiny")

app = FastAPI(title="Whisper Transcription API")
model = whisper.load_model(MODEL_SIZE)


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
    return {"status": "Whisper API running", "model": MODEL_SIZE}
