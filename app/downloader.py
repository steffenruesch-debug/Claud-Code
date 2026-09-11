"""Audio-Download von YouTube- und Instagram-URLs via yt-dlp."""
import re
import uuid
from dataclasses import dataclass
from pathlib import Path

import yt_dlp

from app.config import MAX_DURATION_SECONDS, YTDLP_COOKIES_FILE

YOUTUBE_RE = re.compile(r"(youtube\.com|youtu\.be)", re.IGNORECASE)
INSTAGRAM_RE = re.compile(r"instagram\.com", re.IGNORECASE)


class UnsupportedUrlError(ValueError):
    pass


class DownloadError(RuntimeError):
    pass


class VideoTooLongError(ValueError):
    def __init__(self, duration: int):
        self.duration = duration
        super().__init__(
            f"Video ist {duration}s lang und ueberschreitet das Limit von "
            f"{MAX_DURATION_SECONDS}s."
        )


@dataclass
class AudioInfo:
    path: Path
    title: str
    duration: float
    platform: str
    source_url: str


def detect_platform(url: str) -> str:
    if YOUTUBE_RE.search(url):
        return "youtube"
    if INSTAGRAM_RE.search(url):
        return "instagram"
    raise UnsupportedUrlError(
        "Nur YouTube- und Instagram-URLs werden unterstuetzt."
    )


def download_audio(url: str, workdir: Path) -> AudioInfo:
    platform = detect_platform(url)
    workdir.mkdir(parents=True, exist_ok=True)
    job_id = uuid.uuid4().hex
    out_template = str(workdir / f"{job_id}.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": out_template,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "128",
            }
        ],
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
    }
    if YTDLP_COOKIES_FILE:
        ydl_opts["cookiefile"] = YTDLP_COOKIES_FILE

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            duration = info.get("duration") or 0
            if duration and duration > MAX_DURATION_SECONDS:
                raise VideoTooLongError(int(duration))
            ydl.download([url])
    except VideoTooLongError:
        raise
    except yt_dlp.utils.DownloadError as exc:
        raise DownloadError(str(exc)) from exc

    audio_path = workdir / f"{job_id}.mp3"
    if not audio_path.exists():
        raise DownloadError("Audio-Datei konnte nicht erzeugt werden.")

    return AudioInfo(
        path=audio_path,
        title=info.get("title") or "Unbenannt",
        duration=duration,
        platform=platform,
        source_url=url,
    )
