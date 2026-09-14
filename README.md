# Transcript Tool

Lokale Web-App: YouTube- oder Instagram-Reel-URL einfügen, Transkript wird
automatisch erzeugt und sowohl auf **Deutsch** als auch auf **Englisch**
ausgegeben.

Funktionsweise: [yt-dlp](https://github.com/yt-dlp/yt-dlp) lädt die Audiospur
herunter, die [OpenAI Whisper-API](https://platform.openai.com/docs/guides/speech-to-text)
transkribiert sie (inkl. Spracherkennung), und bei Bedarf übersetzt ein
GPT-Modell den Text in die jeweils fehlende Zielsprache.

## Nutzung am iPad / ohne eigenen Rechner (Render.com)

Am iPad kann das Tool nicht lokal laufen (kein Terminal, kein ffmpeg) –
stattdessen lässt es sich komplett im Browser bei [Render.com](https://render.com)
hosten. Das Repo enthält bereits `Dockerfile` und `render.yaml`, Render
braucht also keine manuelle Konfiguration.

1. Auf [render.com](https://render.com) einen Account anlegen (Login mit GitHub geht am schnellsten).
2. Im Dashboard auf **New +** → **Web Service** klicken.
3. Das GitHub-Repo `steffenruesch-debug/Claud-Code` auswählen (ggf. Render
   erst die Berechtigung für das Repo geben) und den Branch
   `claude/transcript-tool-instagram-youtube-mwj01z` (oder `main`, falls der
   PR gemerged wurde) auswählen.
4. Render erkennt automatisch das Dockerfile – bei "Environment" sollte
   **Docker** stehen, sonst manuell umstellen.
5. Unter **Environment Variables** den Wert für `OPENAI_API_KEY` eintragen
   (dein Key von https://platform.openai.com/api-keys). Die anderen
   Variablen aus `render.yaml` sind bereits vorbelegt/optional.
6. **Create Web Service** klicken. Der erste Build dauert ein paar Minuten.
7. Danach ist die App unter der von Render vergebenen URL erreichbar
   (z. B. `https://transcript-tool.onrender.com`) – funktioniert direkt in
   Safari auf dem iPad, kein Terminal nötig.

**Hinweis Free-Tier:** Der kostenlose Render-Plan schläft nach ca. 15 Minuten
Inaktivität ein; der erste Aufruf danach dauert dann ~30–60 Sekunden länger
(Cold Start). Für den persönlichen Gebrauch ist das in der Regel unproblematisch.

Da die App dann über eine echte URL erreichbar ist, solltest du sie nicht
öffentlich verlinken, solange kein Login/Zugriffsschutz eingebaut ist –
sonst könnte theoretisch jeder mit dem Link auf deine Kosten transkribieren.
Für den privaten Gebrauch (Link nicht teilen) reicht das erstmal.

## Alternative: lokal auf einem Rechner ausführen

### Voraussetzungen

- Python 3.10+
- [ffmpeg](https://ffmpeg.org/) installiert und im `PATH`
  (macOS: `brew install ffmpeg`, Ubuntu/Debian: `sudo apt install ffmpeg`)
- Ein OpenAI-API-Key mit Guthaben

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# .env öffnen und OPENAI_API_KEY eintragen
```

### Starten

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
Dockerfile        Container-Image inkl. ffmpeg, für Render/Railway/Fly.io
render.yaml       Render.com-Blueprint (Web Service, Env-Vars)
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
