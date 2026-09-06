"""
AlfaazAI Backend (No API Key, No ffmpeg Version)
===================================================
Pipeline:
    audio (WAV, recorded in-browser) -> SpeechRecognition (Google Web Speech, free) -> text
                                      -> deep-translator (free)                       -> translated text
                                      -> gTTS (free)                                  -> spoken audio

No OpenAI key, no billing, no ffmpeg install required — the frontend records
audio as WAV directly using the Web Audio API, so the backend can read it as-is.

Run locally:
    pip install -r requirements.txt
    uvicorn main:app --reload --port 8000
"""

import uuid
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from deep_translator import GoogleTranslator
from gtts import gTTS
import speech_recognition as sr

app = FastAPI(title="AlfaazAI", description="Free, no-API-key voice translation layer for Urdu & regional languages")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

TMP_DIR = Path("tmp_audio")
TMP_DIR.mkdir(exist_ok=True)

RECOGNITION_LANGS = {
    "ur": "ur-PK",
    "en": "en-US",
    "hi": "hi-IN",
    "ar": "ar-SA",
}

SUPPORTED_TTS_LANGS = {"ur", "en", "hi", "ar"}

recognizer = sr.Recognizer()


class TranslateRequest(BaseModel):
    text: str
    source_lang: str = "auto"
    target_lang: str = "en"


class SpeakRequest(BaseModel):
    text: str
    lang: str = "ur"


def _transcribe_file(wav_path: Path, source_lang: str) -> str:
    lang_code = RECOGNITION_LANGS.get(source_lang, "ur-PK")
    with sr.AudioFile(str(wav_path)) as source:
        audio_data = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio_data, language=lang_code)
    except sr.UnknownValueError:
        raise HTTPException(400, "Could not understand the audio. Try speaking more clearly.")
    except sr.RequestError as e:
        raise HTTPException(503, f"Speech recognition service error: {e}")


@app.get("/")
def root():
    return {"status": "AlfaazAI backend is running (no API key, no ffmpeg needed)", "docs": "/docs"}


@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...), source_lang: str = Form("ur")):
    """Speech -> Text. Expects a WAV file (browser records WAV directly)."""
    tmp_in = TMP_DIR / f"{uuid.uuid4()}.wav"
    with open(tmp_in, "wb") as f:
        f.write(await audio.read())

    try:
        text = _transcribe_file(tmp_in, source_lang)
        return {"text": text}
    finally:
        tmp_in.unlink(missing_ok=True)


@app.post("/translate")
def translate(req: TranslateRequest):
    try:
        translated = GoogleTranslator(source=req.source_lang, target=req.target_lang).translate(req.text)
        return {"translated_text": translated}
    except Exception as e:
        raise HTTPException(400, f"Translation failed: {e}")


@app.post("/speak")
def speak(req: SpeakRequest):
    try:
        lang = req.lang if req.lang in SUPPORTED_TTS_LANGS else "en"
        tts = gTTS(text=req.text, lang=lang)
        out_path = TMP_DIR / f"{uuid.uuid4()}.mp3"
        tts.save(str(out_path))
        return FileResponse(out_path, media_type="audio/mpeg", filename="response.mp3")
    except Exception as e:
        raise HTTPException(400, f"Text-to-speech failed: {e}")


@app.post("/process")
async def process(
    audio: UploadFile = File(...),
    source_lang: str = Form("ur"),
    target_lang: str = Form("en"),
):
    """Full pipeline: WAV audio in -> transcribe -> translate -> speak -> audio out."""
    tmp_in = TMP_DIR / f"{uuid.uuid4()}.wav"
    with open(tmp_in, "wb") as f:
        f.write(await audio.read())

    out_path = None
    try:
        original_text = _transcribe_file(tmp_in, source_lang)

        translated_text = GoogleTranslator(source=source_lang, target=target_lang).translate(original_text)

        tts_lang = target_lang if target_lang in SUPPORTED_TTS_LANGS else "en"
        tts = gTTS(text=translated_text, lang=tts_lang)
        out_path = TMP_DIR / f"{uuid.uuid4()}.mp3"
        tts.save(str(out_path))

        return {
            "original_text": original_text,
            "translated_text": translated_text,
            "audio_url": f"/audio/{out_path.name}",
        }
    finally:
        tmp_in.unlink(missing_ok=True)


@app.get("/audio/{filename}")
def get_audio(filename: str):
    path = TMP_DIR / filename
    if not path.exists():
        raise HTTPException(404, "Audio file not found")
    return FileResponse(path, media_type="audio/mpeg")
