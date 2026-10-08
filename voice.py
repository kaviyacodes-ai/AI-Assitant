"""Voice features.

- speech_to_text: your recorded voice -> text (Whisper, running on Groq)
- text_to_speech: assistant's reply -> mp3 audio (Google's gTTS, needs internet)
"""
import io
import re
from gtts import gTTS
from config import STT_MODEL
from llm import client   # reuse the same Groq client


def speech_to_text(audio_bytes, filename="audio.wav"):
    result = client.audio.transcriptions.create(
        file=(filename, audio_bytes),
        model=STT_MODEL,
        language="en",
    )
    return result.text.strip()


def clean_for_speech(text):
    """Remove code, links and symbols so the voice sounds natural."""
    text = re.sub(r"```.*?```", " (code example) ", text, flags=re.S)
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"[*_#`>|]", "", text)
    return text.strip()


def text_to_speech(text, accent="com"):
    """accent: 'com' US, 'co.uk' British, 'co.in' Indian, 'com.au' Australian"""
    text = clean_for_speech(text)[:1500]   # keep it short and fast
    if not text:
        return None
    buffer = io.BytesIO()
    gTTS(text=text, lang="en", tld=accent).write_to_fp(buffer)
    return buffer.getvalue()
