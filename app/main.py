import shutil
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI

from app.config import OPENAI_API_KEY
from app.downloader import (
    DownloadError,
    UnsupportedUrlError,
    VideoTooLongError,
    download_audio,
)
from app.models import TranscribeRequest, TranscribeResponse
from app.transcriber import transcribe
from app.translator import translate

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
TMP_DIR = BASE_DIR / "tmp"

app = FastAPI(title="Transcript Tool")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok", "openai_configured": bool(OPENAI_API_KEY)}


def _language_bucket(detected_language: str) -> str:
    """Ordnet die von Whisper erkannte Sprache 'de', 'en' oder 'other' zu."""
    lang = (detected_language or "").strip().lower()
    if lang in ("de", "german", "deutsch"):
        return "de"
    if lang in ("en", "english", "englisch"):
        return "en"
    return "other"


@app.post("/api/transcribe", response_model=TranscribeResponse)
def transcribe_endpoint(payload: TranscribeRequest):
    if not OPENAI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY ist nicht konfiguriert. Siehe .env.example.",
        )

    client = OpenAI(api_key=OPENAI_API_KEY)
    job_dir = TMP_DIR / uuid.uuid4().hex

    try:
        try:
            audio_info = download_audio(payload.url, job_dir)
        except UnsupportedUrlError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except VideoTooLongError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except DownloadError as exc:
            raise HTTPException(
                status_code=502, detail=f"Download fehlgeschlagen: {exc}"
            ) from exc

        try:
            result = transcribe(audio_info.path, job_dir, client)
        except Exception as exc:  # OpenAI-Fehler, Netzwerk etc.
            raise HTTPException(
                status_code=502, detail=f"Transkription fehlgeschlagen: {exc}"
            ) from exc

        bucket = _language_bucket(result.language)
        try:
            if bucket == "de":
                transcript_de = result.text
                transcript_en = translate(result.text, "en", client)
            elif bucket == "en":
                transcript_en = result.text
                transcript_de = translate(result.text, "de", client)
            else:
                transcript_de = translate(result.text, "de", client)
                transcript_en = translate(result.text, "en", client)
        except Exception as exc:
            raise HTTPException(
                status_code=502, detail=f"Uebersetzung fehlgeschlagen: {exc}"
            ) from exc

        return TranscribeResponse(
            platform=audio_info.platform,
            title=audio_info.title,
            duration=audio_info.duration,
            detected_language=result.language,
            transcript_original=result.text,
            transcript_de=transcript_de,
            transcript_en=transcript_en,
        )
    finally:
        shutil.rmtree(job_dir, ignore_errors=True)
