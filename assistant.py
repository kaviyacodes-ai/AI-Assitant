"""The 'brain'. Used by both main.py (terminal) and app.py (web)."""
import config
import llm
import memory
import tools
import auto_memory
from prompts import MODES


def build_messages(mode, history, user_text):
    """System prompt + remembered facts + recent chat + new message."""
    system = MODES[mode]
    facts = memory.recall(user_text)
    if facts:
        system += "\n\nThings you remember about the user:\n- " + "\n- ".join(facts)
    return ([{"role": "system", "content": system}]
            + history[-10:]
            + [{"role": "user", "content": user_text}])


def ask(mode, history, user_text):
    reply = llm.chat(build_messages(mode, history, user_text))
    history.append({"role": "user", "content": user_text})
    history.append({"role": "assistant", "content": reply})
    return reply


def handle_news(topic, history):
    headlines = tools.get_news(topic or "top stories")
    if not headlines:
        return "I couldn't find any news right now."
    prompt = ("Summarise these headlines in simple English, one line each. "
              "Use only this information:\n" + "\n".join(headlines))
    return ask("general", history, prompt)


def handle_near(text, history):
    thing, _, city = text.partition("|")
    city = city.strip() or config.DEFAULT_CITY
    if not thing.strip() or not city:
        return "Try: /near cafe | Chennai  (or set DEFAULT_CITY in .env)"
    places = tools.find_places(thing.strip(), city)
    if not places:
        return "I couldn't find anything nearby."
    prompt = (f"The user wants '{thing.strip()}' in {city}. Present these results "
              "as a short helpful list:\n" + "\n".join(places))
    return ask("general", history, prompt)


def respond(text, mode, history, auto_save=True):
    """Handle one user message. Returns (reply, fact_saved_or_None)."""
    if text.startswith("/remember"):
        fact = text[9:].strip()
        if not fact:
            return "Usage: /remember <something to remember>", None
        memory.remember(fact)
        return "Saved to memory.", None
    if text.startswith("/news"):
        return handle_news(text[5:].strip(), history), None
    if text.startswith("/near"):
        return handle_near(text[5:], history), None

    reply = ask(mode, history, text)
    saved = None
    if auto_save and mode != "grammar":   # grammar mode = pasted text, not facts
        saved = auto_memory.maybe_save(text)
    return reply, saved
