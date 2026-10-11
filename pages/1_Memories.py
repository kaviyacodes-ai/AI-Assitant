"""Page: see, add and delete what the assistant remembers."""
import datetime
import streamlit as st
import common

common.setup("Memories", "🧠")
import memory

st.title("🧠 My Memories")
st.caption("Facts the assistant remembers about you. Delete anything you do not want kept.")

if "hidden" not in st.session_state:
    st.session_state.hidden = set()   # deleted ids (Pinecone can take a few seconds to update)

new_fact = st.text_input("Add a memory", placeholder="I am preparing for the IELTS exam")
if st.button("Save memory") and new_fact.strip():
    memory.remember(new_fact.strip())
    st.success("Saved! It may take a few seconds to appear below.")

if st.button("🔄 Refresh"):
    st.rerun()

st.divider()
try:
    records = [r for r in memory.list_records() if r["id"] not in st.session_state.hidden]
except Exception as error:
    st.error(f"Could not load memories: {error}")
    st.stop()

if not records:
    st.info("No memories yet. Chat with the assistant and tell it about yourself.")

for record in records:
    left, right = st.columns([9, 1])
    left.write(record.get("text", ""))
    saved = int(record.get("saved_at", 0))
    if saved:
        left.caption(datetime.datetime.fromtimestamp(saved).strftime("%d %b %Y"))
    if right.button("🗑️", key=record["id"], help="Delete this memory"):
        memory.forget(record["id"])
        st.session_state.hidden.add(record["id"])
        st.rerun()
