"""
05 - SYSTEM PROMPTS
===================

The SYSTEM message sets durable, global behavior for the whole conversation:
the persona, rules, constraints, output format, and what to do at the edges.
User messages are the per-turn requests; the system prompt is the policy that
governs all of them.

Think of the system prompt as the model's "job description + standard operating
procedure." A strong one usually covers:
  - ROLE        : who the assistant is.
  - GOAL        : what it is optimizing for.
  - RULES       : hard constraints / things it must never do.
  - FORMAT      : exactly how to structure the output.
  - FALLBACK    : what to do when it can't comply or lacks info.

KEY IDEAS
  - Put STABLE instructions in system, VARIABLE content in user messages.
  - Be explicit about refusals & unknowns ("If unsure, say you don't know").
  - Constraints are more reliable as positive rules ("Use at most 3 sentences")
    than negatives ("Don't be too long").

Run:  python fundamentals/05_system_prompts.py
"""

# --- make the repo-root 'common' package importable when run directly ---
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import chat, header, rule

WEAK_SYSTEM = "You are a helpful assistant."

STRONG_SYSTEM = """\
ROLE: You are "Ledger", a support assistant for a personal-finance app.

GOAL: Help users understand the app's features accurately and safely.

RULES:
- Answer ONLY questions about the app. For tax/legal/investment advice, decline
  and suggest the user consult a licensed professional.
- Never invent features. If you don't know, say so.
- Keep a warm, plain-language tone. No financial jargon without a definition.

FORMAT:
- 1 short paragraph, then up to 3 bullet "Next steps" if relevant.

FALLBACK:
- If the request is out of scope, reply: "That's outside what I can help with,
  but here's who can..." and point them to the right resource.
"""

USER_TURNS = [
    "How do I set a monthly budget in the app?",
    "Which stocks should I buy to retire early?",  # out of scope -> should decline
]


def respond(system: str, user: str) -> str:
    return chat(
        [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.4,
    )


if __name__ == "__main__":
    header("SYSTEM PROMPTS")

    for user in USER_TURNS:
        rule("=")
        print(f"\nUser: {user}")

        print("\n[Weak system: 'helpful assistant'] ->")
        print(respond(WEAK_SYSTEM, user))

        print("\n[Strong system: role+rules+format+fallback] ->")
        print(respond(STRONG_SYSTEM, user))

    rule()
    print(
        "\nTakeaway: the strong system prompt enforces scope (declines the stock\n"
        "question), tone, and a consistent format across DIFFERENT user turns --\n"
        "behavior the weak prompt leaves to chance."
    )
