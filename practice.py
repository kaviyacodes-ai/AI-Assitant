"""Daily English practice: get a topic -> answer -> scored feedback -> progress."""
import json
import time
import llm
import memory

NAMESPACE = "practice"
CATEGORIES = ["Surprise me", "Daily life", "Work and career", "Travel",
              "Food", "Technology", "Hobbies", "Opinions"]

EVAL_PROMPT = """You are a kind, honest English speaking examiner. A {level} learner answered a question.
The answer may have been spoken and auto-transcribed, so ignore capital letters and punctuation.

Reply with JSON only, no other text:
{"grammar": 0-10, "vocabulary": 0-10, "clarity": 0-10, "overall": 0-10,
 "corrected": "the learner's answer, corrected",
 "mistakes": ["up to 3 short explanations, most important first"],
 "better_answer": "a natural model answer in 2-3 sentences at the learner's level",
 "encouragement": "one short encouraging sentence"}
Scores are whole numbers. "clarity" means how clear and well organised the answer is."""


def new_topic(level, category):
    focus = "any everyday topic" if category == "Surprise me" else category
    prompt = (f"Give ONE speaking practice question for a {level.lower()} English "
              f"learner about {focus}. Maximum 25 words. Output only the question.")
    reply = llm.chat([{"role": "user", "content": prompt}], temperature=0.9)
    return reply.strip().strip('"')


def _score(value):
    try:
        return max(0, min(10, int(round(float(value)))))
    except (TypeError, ValueError):
        return 0


def evaluate(question, answer, level):
    """Returns a dict with scores and feedback."""
    reply = llm.chat(
        [{"role": "system", "content": EVAL_PROMPT.replace("{level}", level.lower())},
         {"role": "user", "content": f"Question: {question}\n\nLearner's answer: {answer}"}],
        temperature=0.2,
    )
    try:
        data = json.loads(reply[reply.index("{"): reply.rindex("}") + 1])
    except ValueError:
        raise ValueError("I could not read the feedback. Please press Check again.")

    return {
        "grammar": _score(data.get("grammar")),
        "vocabulary": _score(data.get("vocabulary")),
        "clarity": _score(data.get("clarity")),
        "overall": _score(data.get("overall")),
        "corrected": str(data.get("corrected", "")),
        "mistakes": [str(m) for m in (data.get("mistakes") or [])][:3],
        "better_answer": str(data.get("better_answer", "")),
        "encouragement": str(data.get("encouragement", "")),
    }


def save_result(question, level, result):
    """Store the scores in Pinecone so progress is kept between days."""
    memory.remember(
        f"English practice ({level}): {question}",
        namespace=NAMESPACE,
        extra={
            "overall": result["overall"], "grammar": result["grammar"],
            "vocabulary": result["vocabulary"], "clarity": result["clarity"],
            "level": level, "date": time.strftime("%Y-%m-%d"),
        },
    )


def history():
    """All past practice sessions, oldest first."""
    rows = [r for r in memory.list_records(NAMESPACE) if "overall" in r]
    return sorted(rows, key=lambda r: r.get("saved_at", 0))
