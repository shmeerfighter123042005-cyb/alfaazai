# AlfaazAI 🗣️

A voice-first AI translation layer that lets Urdu and regional-language speakers
interact with any digital service by speaking — no typing, no English required.

**This version uses no API keys and costs nothing to run.**

## How it works

```
User's voice  →  Google Web Speech (free speech-to-text)
              →  Google Translate (free translation)
              →  gTTS (free text-to-speech)
              →  Spoken response back to the user
```

## Project structure

```
alfaazai/
├── backend/
│   ├── main.py            # FastAPI app: /transcribe, /translate, /speak, /process
│   └── requirements.txt
├── frontend/
│   └── index.html         # simple mic-based demo UI
└── .gitignore
```

## Prerequisites

- **Python 3.10–3.12** (avoid 3.13/3.14 — some packages don't have pre-built wheels yet)
- No ffmpeg needed — the frontend records WAV audio directly in the browser.

## Setup

### Option A — One click (Windows)

Just double-click **`start.bat`** in the project root. It automatically creates
the virtual environment, installs everything, and starts the server. Once you
see "Application startup complete", open `frontend/index.html` in your browser.

### Option B — Manual

1. **Backend**
   ```bash
   cd backend
   python -m venv venv && source venv/bin/activate   # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   uvicorn main:app --reload --port 8000
   ```
   No `.env` file or API key needed — everything runs on free services.

2. **Frontend**
   Just open `frontend/index.html` in a browser (or serve it with any static
   server). Make sure the backend is running on `localhost:8000`.

3. **Try it**
   Click "Start Speaking", say something in Urdu, click stop — you'll get the
   transcription, the translation, and a spoken-back audio response.

## API endpoints

| Endpoint      | Method | Purpose                                   |
|---------------|--------|--------------------------------------------|
| `/transcribe` | POST   | audio → text (Whisper)                    |
| `/translate`  | POST   | text → translated text                    |
| `/speak`      | POST   | text → spoken audio (mp3)                 |
| `/process`    | POST   | full pipeline: audio → translated audio   |

## Note on the free speech recognition

`speech_recognition`'s Google Web Speech backend is unofficial, free, and
rate-limited — great for hackathon demos, but not meant for production scale.
For a production version, swap `_transcribe_file()` in `main.py` for a paid
or self-hosted model (OpenAI Whisper API, or a locally-run Whisper model).

## Roadmap / what's left after the hackathon

- Add Punjabi, Sindhi, Pashto TTS support (gTTS coverage is limited for these —
  may need Coqui TTS or MMS-TTS)
- Move to a self-hosted or fine-tuned speech model for better accuracy and no rate limits
- Package as an installable SDK so third-party apps can integrate in a few lines
- Offline/low-bandwidth mode for rural connectivity
