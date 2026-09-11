from pydantic import BaseModel, Field


class TranscribeRequest(BaseModel):
    url: str = Field(..., description="YouTube- oder Instagram-Reel-URL")


class TranscribeResponse(BaseModel):
    platform: str
    title: str
    duration: float
    detected_language: str
    transcript_original: str
    transcript_de: str
    transcript_en: str
