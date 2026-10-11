"""Page: daily English speaking practice with scores."""
import hashlib
import pandas as pd
import streamlit as st
import common

common.setup("Daily Practice", "🎯")
import practice
import voice

st.title("🎯 Daily English Practice")
st.caption("Get a topic, answer by voice or text, and get a score. "
           "Scores cover grammar, vocabulary and clarity (not pronunciation).")

for key, default in {"question": None, "result": None, "result_audio": None,
                     "answer": "", "last_audio": None}.items():
    st.session_state.setdefault(key, default)


@st.cache_data(ttl=30, show_spinner="Loading your progress...")
def load_history():
    return practice.history()


col1, col2 = st.columns(2)
level = col1.selectbox("Level", ["Beginner", "Intermediate", "Advanced"], index=1)
category = col2.selectbox("Topic type", practice.CATEGORIES)
read_aloud = st.checkbox("🔊 Read the feedback aloud")

if st.button("🎲 Get a new topic", type="primary"):
    try:
        with st.spinner("Thinking of a topic..."):
            st.session_state.question = practice.new_topic(level, category)
        st.session_state.result = None
        st.session_state.result_audio = None
        st.session_state.answer = ""
    except Exception as error:
        st.error(f"Could not get a topic: {error}")

if not st.session_state.question:
    st.info("Press **Get a new topic** to start.")
else:
    st.subheader(st.session_state.question)

    recording = st.audio_input("🎤 Record your answer (press stop when done)")
    if recording is not None:
        data = recording.getvalue()
        digest = hashlib.md5(data).hexdigest()
        if digest != st.session_state.last_audio:      # only handle NEW recordings
            st.session_state.last_audio = digest
            try:
                with st.spinner("Listening..."):
                    st.session_state.answer = voice.speech_to_text(data)
            except Exception as error:
                st.error(f"Could not read the audio: {error}")

    answer = st.text_area("Your answer (speak above, or type here)", key="answer", height=120)

    if st.button("✅ Check my answer", disabled=not answer.strip()):
        try:
            with st.spinner("Checking your answer..."):
                result = practice.evaluate(st.session_state.question, answer, level)
                st.session_state.result = result
                st.session_state.result_audio = None
                if read_aloud:
                    spoken = (f"Your score is {result['overall']} out of 10. "
                              f"{result['encouragement']} A better way to say it: "
                              f"{result['corrected']}")
                    st.session_state.result_audio = voice.text_to_speech(spoken)
                try:
                    practice.save_result(st.session_state.question, level, result)
                    load_history.clear()
                except Exception as error:
                    st.warning(f"Feedback is ready, but I could not save your score: {error}")
        except Exception as error:
            st.error(str(error))

result = st.session_state.result
if result:
    st.divider()
    a, b, c, d = st.columns(4)
    a.metric("Overall", f"{result['overall']}/10")
    b.metric("Grammar", f"{result['grammar']}/10")
    c.metric("Vocabulary", f"{result['vocabulary']}/10")
    d.metric("Clarity", f"{result['clarity']}/10")
    if result["encouragement"]:
        st.success(result["encouragement"])
    if st.session_state.result_audio:
        st.audio(st.session_state.result_audio, format="audio/mp3")
    st.markdown("**Corrected answer**")
    st.write(result["corrected"])
    if result["mistakes"]:
        st.markdown("**What to improve**")
        for mistake in result["mistakes"]:
            st.markdown(f"- {mistake}")
    st.markdown("**A model answer**")
    st.write(result["better_answer"])

st.divider()
if st.checkbox("📈 Show my progress"):
    try:
        rows = load_history()
    except Exception as error:
        rows = []
        st.error(f"Could not load progress: {error}")
    if not rows:
        st.info("No scores yet. Finish one practice and it will appear here.")
    else:
        recent = [r["overall"] for r in rows[-7:]]
        m1, m2, m3 = st.columns(3)
        m1.metric("Practices", len(rows))
        m2.metric("Days practised", len({r.get("date") for r in rows}))
        m3.metric("Average (last 7)", f"{sum(recent) / len(recent):.1f}/10")
        st.line_chart(pd.DataFrame({
            "Overall": [r["overall"] for r in rows],
            "Grammar": [r["grammar"] for r in rows],
            "Vocabulary": [r["vocabulary"] for r in rows],
            "Clarity": [r["clarity"] for r in rows],
        }))
