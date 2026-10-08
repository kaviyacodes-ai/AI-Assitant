"""Talks to Groq."""
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL

client = Groq(api_key=GROQ_API_KEY)


def chat(messages, temperature=0.6, model=None):
    """Send messages to Groq and return the reply text."""
    response = client.chat.completions.create(
        model=model or GROQ_MODEL,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content
