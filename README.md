# AI Assistant (Groq + Pinecone)

## Run on your computer
1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and add your keys
3. `streamlit run app.py`

## Pages (sidebar)
- app          chat with voice, modes, news, nearby places, auto-memory
- Memories     see, add and delete what the assistant remembers
- Daily Practice  topic -> answer by voice/text -> scores -> progress chart

## Optional .env / Secrets values
- DEFAULT_CITY   default city for /near
- APP_PASSWORD   asks for a password (use this when the app is online!)
- GROQ_MODEL / FAST_MODEL   change model names if Groq retires one

## Files
app.py, pages/1_Memories.py, pages/2_Daily_Practice.py,
assistant.py, auto_memory.py, practice.py, voice.py, memory.py,
common.py, llm.py, tools.py, prompts.py, config.py, main.py (terminal version)
