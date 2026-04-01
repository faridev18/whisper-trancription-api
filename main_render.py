from fastapi import FastAPI, UploadFile, File
import whisper
import tempfile
import os

# Injecte ffmpeg dans le PATH depuis plusieurs sources possibles
def _setup_ffmpeg():
    # 1. Essai via imageio-ffmpeg
    # Le binaire s'appelle "ffmpeg-linux-x86_64-vX.Y.Z", pas "ffmpeg"
    # On crée un symlink "ffmpeg" dans le même dossier pour que whisper le trouve
    try:
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        ffmpeg_dir = os.path.dirname(ffmpeg_exe)
        ffmpeg_link = os.path.join(ffmpeg_dir, "ffmpeg")
        if not os.path.exists(ffmpeg_link):
            os.symlink(ffmpeg_exe, ffmpeg_link)
        if ffmpeg_dir not in os.environ.get("PATH", ""):
            os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
        return
    except Exception:
        pass
    # 2. Chemins système Linux courants
    for path in ["/usr/bin", "/usr/local/bin", "/bin"]:
        if os.path.isfile(os.path.join(path, "ffmpeg")):
            if path not in os.environ.get("PATH", ""):
                os.environ["PATH"] = path + os.pathsep + os.environ.get("PATH", "")
            return

_setup_ffmpeg()

# Sur Render free tier, utilise "tiny" pour éviter les OOM (512MB RAM)
# Modifiable via la variable d'env WHISPER_MODEL
MODEL_SIZE = os.environ.get("WHISPER_MODEL", "base")

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
