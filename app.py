"""Web version with voice.   Run:  streamlit run app.py"""
import hashlib
import streamlit as st
import common
import config

# Page setup + key check + optional password (see common.py)
common.setup("AI Assistant", "🤖")

# Imported only after the key check (these connect to Groq / Pinecone)
import assistant
import memory
import voice
from prompts import MODES

ACCENTS = {"American": "com", "British": "co.uk",
           "Indian": "co.in", "Australian": "com.au"}

# ---------- remember things between button clicks ----------
if "chat" not in st.session_state:
    st.session_state.chat = []         # messages shown on screen
    st.session_state.history = []      # messages sent to the AI
    st.session_state.last_audio = None # stops one recording being processed twice

# ---------- sidebar: settings and quick tools ----------
pending = None   # a message created by a sidebar button
with st.sidebar:
    st.header("Settings")
    mode = st.selectbox("Mode", list(MODES), format_func=str.title)
    speak = st.checkbox("🔊 Read replies aloud")
    accent = ACCENTS[st.selectbox("Voice accent", list(ACCENTS))]
    auto_save = st.checkbox("🧠 Auto-save memories", value=True)

    st.divider()
    st.subheader("📰 News")
    topic = st.text_input("Topic", placeholder="cricket, technology...")
    if st.button("Get headlines"):
        pending = f"/news {topic}"

    st.subheader("📍 Nearby")
    thing = st.text_input("Looking for", placeholder="pharmacy, cafe...")
    city = st.text_input("City", value=config.DEFAULT_CITY)
    if st.button("Find places") and thing:
        pending = f"/near {thing} | {city}"

    st.divider()
    fact = st.text_input("🧠 Remember this", placeholder="I am preparing for IELTS")
    if st.button("Save memory") and fact:
        memory.remember(fact)
        st.success("Saved!")

    if st.button("🗑️ Clear chat"):
        st.session_state.chat = []
        st.session_state.history = []
        st.rerun()

# ---------- main page ----------
st.title("🤖 AI Assistant")
st.caption(f"Mode: {mode.title()}  •  Tip: choose English mode and speak to practise")

with st.expander("🎤 Speak instead of typing", expanded=True):
    recording = st.audio_input("Record your message, then press stop")

spoken = None
if recording is not None:
    data = recording.getvalue()
    digest = hashlib.md5(data).hexdigest()
    if digest != st.session_state.last_audio:      # only handle NEW recordings
        st.session_state.last_audio = digest
        try:
            with st.spinner("Listening..."):
                spoken = voice.speech_to_text(data)
        except Exception as error:
            st.error(f"Could not read the audio: {error}")

typed = st.chat_input("Type a message, or /news, /near, /remember")
user_text = pending or typed or spoken

# Show the conversation so far
for m in st.session_state.chat:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m.get("audio"):
            st.audio(m["audio"], format="audio/mp3")
        if m.get("saved"):
            st.caption(f"🧠 Remembered: {m['saved']}")

# Handle a new message
if user_text:
    st.session_state.chat.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                reply, saved = assistant.respond(
                    user_text, mode, st.session_state.history, auto_save)
            except Exception as error:
                reply, saved = f"⚠️ Something went wrong: {error}", None
        st.markdown(reply)

        audio_bytes = None
        if speak:
            try:
                audio_bytes = voice.text_to_speech(reply, accent)
            except Exception as error:
                st.warning(f"Voice failed: {error}")
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3", autoplay=True)
        if saved:
            st.caption(f"🧠 Remembered: {saved}")

    st.session_state.chat.append(
        {"role": "assistant", "content": reply, "audio": audio_bytes, "saved": saved})
