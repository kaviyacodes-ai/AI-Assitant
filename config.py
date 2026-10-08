"""Loads settings from the .env file."""
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
DEFAULT_CITY = os.getenv("DEFAULT_CITY", "")
APP_PASSWORD = os.getenv("APP_PASSWORD", "")   # optional: asks for a password in the web app

GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")   # main chat model
FAST_MODEL = os.getenv("FAST_MODEL", "openai/gpt-oss-20b")      # small, fast model for memory checks
STT_MODEL = "whisper-large-v3-turbo"     # speech -> text (Whisper on Groq)
PINECONE_INDEX = "my-assistant-memory"   # Pinecone index name
EMBED_MODEL = "multilingual-e5-large"    # Pinecone's built-in embedding model
EMBED_DIMENSION = 1024                   # must match EMBED_MODEL


def missing_keys():
    """Returns the names of any API keys that are not set."""
    keys = {"GROQ_API_KEY": GROQ_API_KEY, "PINECONE_API_KEY": PINECONE_API_KEY}
    return [name for name, value in keys.items() if not value]


def check_keys():
    """Stop early with a friendly message if keys are missing."""
    missing = missing_keys()
    if missing:
        raise SystemExit(f"Missing in .env: {', '.join(missing)}")
