"""
04 - ROLE / PERSONA PROMPTING
=============================

Role prompting = you assign the model a PERSONA or expertise ("You are a senior
security engineer...") to steer its vocabulary, depth, priorities, and tone.

A good role does three things:
  - Sets the LENS (what the model pays attention to).
  - Sets the AUDIENCE (how technical / simple to be).
  - Sets the TONE (formal, friendly, terse, encouraging).

KEY IDEAS
  - The role usually lives in the SYSTEM message (see 05_system_prompts.py).
  - Specific roles beat generic ones: "kind kindergarten teacher" > "teacher".
  - Pair the persona with the audience: who is the answer FOR?
  - Personas are steering, not magic credentials -- they don't make facts true.

Run:  python fundamentals/04_role_prompting.py
"""

# --- make the repo-root 'common' package importable when run directly ---
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import chat, header, rule

QUESTION = "What is a database index and why would I use one?"

ROLES = {
    "No role (baseline)": None,
    "Patient teacher for a 12-year-old": (
        "You are a patient teacher explaining tech to a curious 12-year-old. "
        "Use a simple everyday analogy and avoid jargon."
    ),
    "Senior database engineer in a design review": (
        "You are a senior database engineer reviewing a schema. Be precise and "
        "technical, mention trade-offs (write cost, storage), and assume the "
        "reader is a professional developer."
    ),
}


def ask_with_role(role: str | None) -> str:
    messages = []
    if role:
        messages.append({"role": "system", "content": role})
    messages.append({"role": "user", "content": QUESTION})
    return chat(messages, temperature=0.5)


if __name__ == "__main__":
    header("ROLE / PERSONA PROMPTING")
    print("\nSame question, three personas:", QUESTION)

    for label, role in ROLES.items():
        rule()
        print(f"\n[{label}] ->")
        print(ask_with_role(role))

    rule()
    print(
        "\nTakeaway: the persona changes the altitude and vocabulary of the\n"
        "answer without changing the question. Match the role to your audience."
    )
