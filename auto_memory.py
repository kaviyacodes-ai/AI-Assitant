"""Automatic memory: saves lasting facts the user mentions (name, goals, etc.).

A small, fast model reads each message and decides: is there something worth
remembering? If yes, the fact is saved to Pinecone (unless we already have it).
"""
import json
import llm
import memory
from config import FAST_MODEL

EXTRACT_PROMPT = """You read ONE message from a user and decide if it contains a \
LASTING personal fact worth remembering for future chats.

Worth saving: name, job or studies, goals, exams, hometown, preferences, \
skill level, ongoing projects.
NOT worth saving: questions, small talk, one-time events, requests, or text \
the user wants checked, corrected or translated.

Reply with JSON only, no other text:
{"save": true, "fact": "one short sentence starting with 'The user'"}
or
{"save": false, "fact": ""}"""


def _parse(text):
    """Pull the JSON object out of the model's reply. Returns a dict or None."""
    try:
        start, end = text.index("{"), text.rindex("}") + 1
        data = json.loads(text[start:end])
        return data if isinstance(data, dict) else None
    except ValueError:   # also covers invalid JSON
        return None


def maybe_save(user_text):
    """Returns the fact that was saved, or None."""
    # Skip commands, very short messages and long pasted text
    if user_text.startswith("/") or len(user_text.split()) < 4 or len(user_text) > 500:
        return None
    try:
        reply = llm.chat(
            [{"role": "system", "content": EXTRACT_PROMPT},
             {"role": "user", "content": user_text}],
            temperature=0,
            model=FAST_MODEL,
        )
        data = _parse(reply)
        if not data or not data.get("save") or not data.get("fact"):
            return None

        fact = data["fact"].strip()
        if memory.recall(fact, top_k=1, min_score=0.93):   # already known
            return None
        memory.remember(fact)
        return fact
    except Exception:
        return None   # auto-memory must never break the chat
