"""Terminal version.   Run:  python main.py
(For the web version with voice, run:  streamlit run app.py)"""
import config
config.check_keys()

import assistant
from prompts import MODES

HELP = """
Commands:
  /mode <name>             general, english, grammar, coding, learning, productivity
  /news <topic>            latest headlines, summarised
  /near <thing> | <city>   e.g.  /near pharmacy | Chennai
  /remember <fact>         save something to memory (important facts are also saved automatically)
  /help                    show this message
  /quit                    exit
Anything else is a normal chat message.
"""


def main():
    mode, history = "general", []
    print("AI Assistant ready. Type /help for commands.")

    while True:
        text = input(f"\n[{mode}] You: ").strip()
        if not text:
            continue

        try:
            if text == "/quit":
                print("Goodbye!")
                break
            elif text == "/help":
                print(HELP)
            elif text.startswith("/mode"):
                name = text[5:].strip()
                if name in MODES:
                    mode = name
                    print(f"Switched to {mode} mode.")
                else:
                    print("Modes:", ", ".join(MODES))
            else:
                reply, saved = assistant.respond(text, mode, history)
                print("\nAssistant:", reply)
                if saved:
                    print(f"\n(remembered: {saved})")
        except Exception as error:   # keep the app alive on network/API errors
            print("Something went wrong:", error)


if __name__ == "__main__":
    main()
