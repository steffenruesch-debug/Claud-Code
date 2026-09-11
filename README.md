# Transcript Tool

Lokale Web-App: YouTube- oder Instagram-Reel-URL einfügen, Transkript wird
automatisch erzeugt und sowohl auf **Deutsch** als auch auf **Englisch**
ausgegeben.

Funktionsweise: [yt-dlp](https://github.com/yt-dlp/yt-dlp) lädt die Audiospur
herunter, die [OpenAI Whisper-API](https://platform.openai.com/docs/guides/speech-to-text)
transkribiert sie (inkl. Spracherkennung), und bei Bedarf übersetzt ein
GPT-Modell den Text in die jeweils fehlende Zielsprache.

## Voraussetzungen

- Python 3.10+
- [ffmpeg](https://ffmpeg.org/) installiert und im `PATH`
  (macOS: `brew install ffmpeg`, Ubuntu/Debian: `sudo apt install ffmpeg`)
- Ein OpenAI-API-Key mit Guthaben

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# .env öffnen und OPENAI_API_KEY eintragen
```

## Starten

```bash
uvicorn app.main:app --reload
```

Danach im Browser öffnen: http://localhost:8000

## Instagram-Hinweis

Instagram blockiert anonyme Downloads teils oder verlangt einen Login.
Falls der Download fehlschlägt, kannst du eine `cookies.txt` (Netscape-
Format, z. B. per Browser-Extension "Get cookies.txt LOCALLY" exportiert)
angeben und den Pfad in `.env` unter `YTDLP_COOKIES_FILE` eintragen.

## Kosten

Die Nutzung verursacht laufende Kosten über deinen OpenAI-API-Key
(Transkription + ggf. Übersetzung), abhängig von der Videolänge. Über
`MAX_DURATION_SECONDS` in `.env` lässt sich eine Obergrenze setzen, um
versehentlich hohe Kosten bei sehr langen Videos zu vermeiden.

## Struktur

```
app/
  main.py         FastAPI-App & Endpunkte
  downloader.py   yt-dlp-Wrapper (YouTube/Instagram → Audiodatei)
  transcriber.py  OpenAI Whisper-Transkription inkl. Aufsplitten großer Dateien
  translator.py   GPT-Übersetzung ins jeweils fehlende DE/EN
  models.py       Request-/Response-Schemas
static/           Frontend (HTML/CSS/JS, keine Build-Tools nötig)
```

## Später: öffentliche, kostenpflichtige Version

Das Tool ist bewusst so strukturiert, dass Kern-Logik (Download,
Transkription, Übersetzung) von der API-Schicht getrennt ist. Für eine
öffentliche Version mit zahlenden Nutzern kämen u. a. noch dazu:

- Nutzer-Accounts & Login
- Bezahlmodell/Kontingente (z. B. Stripe + Guthaben oder Abo)
- Rate-Limiting pro Nutzer
- Asynchrone Verarbeitung/Warteschlange für lange Videos statt synchronem Request
- Hosting mit eigenem Server statt `localhost`

Das ist bewusst noch nicht gebaut, damit das Tool jetzt schnell für dich
nutzbar ist.
