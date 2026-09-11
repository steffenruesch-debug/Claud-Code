import os

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
YTDLP_COOKIES_FILE = os.getenv("YTDLP_COOKIES_FILE") or None
MAX_DURATION_SECONDS = int(os.getenv("MAX_DURATION_SECONDS", "7200"))

# OpenAI-Modelle
TRANSCRIBE_MODEL = os.getenv("TRANSCRIBE_MODEL", "whisper-1")
TRANSLATE_MODEL = os.getenv("TRANSLATE_MODEL", "gpt-4o-mini")

# Whisper-API akzeptiert Dateien bis 25 MB. Wir bleiben etwas darunter,
# um Verpackungs-Overhead beim Aufsplitten abzufedern.
MAX_CHUNK_BYTES = 24 * 1024 * 1024
