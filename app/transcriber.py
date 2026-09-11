"""Transkription via OpenAI Whisper-API, inkl. Aufsplitten grosser Dateien."""
from dataclasses import dataclass
from pathlib import Path

from openai import OpenAI
from pydub import AudioSegment

from app.config import MAX_CHUNK_BYTES, TRANSCRIBE_MODEL


@dataclass
class TranscriptionResult:
    text: str
    language: str


def _split_into_chunks(audio_path: Path, workdir: Path) -> list[Path]:
    """Teilt eine Audiodatei in Stuecke unter MAX_CHUNK_BYTES auf."""
    size = audio_path.stat().st_size
    if size <= MAX_CHUNK_BYTES:
        return [audio_path]

    audio = AudioSegment.from_file(audio_path)
    total_ms = len(audio)
    # Anzahl Chunks anhand des Groessenverhaeltnisses schaetzen (mit Puffer).
    num_chunks = max(2, (size // MAX_CHUNK_BYTES) + 1)
    chunk_ms = total_ms // num_chunks + 1

    chunks = []
    for i, start in enumerate(range(0, total_ms, chunk_ms)):
        segment = audio[start : start + chunk_ms]
        chunk_path = workdir / f"{audio_path.stem}_chunk{i}.mp3"
        segment.export(chunk_path, format="mp3", bitrate="128k")
        chunks.append(chunk_path)
    return chunks


def transcribe(audio_path: Path, workdir: Path, client: OpenAI) -> TranscriptionResult:
    chunks = _split_into_chunks(audio_path, workdir)

    texts = []
    detected_language = ""
    try:
        for chunk_path in chunks:
            with open(chunk_path, "rb") as f:
                result = client.audio.transcriptions.create(
                    model=TRANSCRIBE_MODEL,
                    file=f,
                    response_format="verbose_json",
                )
            texts.append(result.text.strip())
            if not detected_language:
                detected_language = getattr(result, "language", "") or ""
    finally:
        if len(chunks) > 1:
            for chunk_path in chunks:
                chunk_path.unlink(missing_ok=True)

    return TranscriptionResult(text=" ".join(t for t in texts if t), language=detected_language)
