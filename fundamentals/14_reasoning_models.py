"""
14 - PROMPTING REASONING MODELS (LESS IS MORE)
==============================================

Most of this repo teaches you to *add* structure: "think step by step", worked
examples, explicit reasoning scaffolds. Reasoning models (OpenAI's o-series, the
thinking modes of recent Claude/Gemini, and many local "thinking" models) flip that
advice: they already reason internally, so the scaffolding you'd add for a normal
model can *hurt* — it's redundant and can box in their own process.

The shift in how you prompt:
  - DON'T say "think step by step" / "show your reasoning" — they do that already.
  - DO state the GOAL and the CONSTRAINTS, then get out of the way.
  - Prefer "what good looks like" (success criteria) over "here's the procedure".
  - Few-shot examples help LESS, and over-specified steps can lower quality.
  - Control depth with the model's effort/reasoning setting, not with prompt verbosity.

This file runs the SAME hard problem two ways against your configured model and
prints both, so you can compare. (You don't need an actual reasoning model to see
the contrast in *prompting style*; set MODEL/REASONING_MODEL in .env to try a real
one. On a normal model the verbose version often wins; on a reasoning model the
minimal version usually matches or beats it with fewer tokens.)

Run:  secrun python fundamentals/14_reasoning_models.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import chat, chat_model, header, rule

# A model may have a dedicated reasoning model configured; fall back to the default.
REASONING_MODEL = os.getenv("REASONING_MODEL", chat_model())

PROBLEM = (
    "Five houses in a row, each a different color, owner, and pet. "
    "The red house is immediately left of the blue house. "
    "The dog owner lives in the green house. "
    "The green house is somewhere right of the blue house. "
    "The cat owner lives at one end. "
    "Where (1-5, left to right) is the dog owner, and what is the order of house colors? "
    "Assume colors are red, blue, green, plus two others you may place freely."
)

# Style A: heavy scaffolding — the right call for a NON-reasoning model.
VERBOSE = (
    f"{PROBLEM}\n\n"
    "Let's think step by step. Enumerate the constraints, try placements, check each "
    "against every clue, backtrack when something fails, and only then give the final "
    "arrangement. Show your reasoning, then write FINAL: <answer>."
)

# Style B: goal + constraints only — the right call for a REASONING model.
MINIMAL = (
    f"{PROBLEM}\n\n"
    "Give the correct arrangement. Be certain it satisfies every clue. "
    "Answer on one line as FINAL: <answer>."
)


if __name__ == "__main__":
    header("PROMPTING REASONING MODELS — LESS IS MORE")
    print(f"\nModel in use: {REASONING_MODEL}")
    print(f"\nProblem:\n{PROBLEM}\n")

    rule()
    print("\n[Style A — verbose 'think step by step' scaffolding] ->")
    print(
        chat(
            [{"role": "user", "content": VERBOSE}], model=REASONING_MODEL, temperature=0
        )
    )

    rule()
    print("\n[Style B — goal + constraints only, no scaffolding] ->")
    print(
        chat(
            [{"role": "user", "content": MINIMAL}], model=REASONING_MODEL, temperature=0
        )
    )

    rule()
    print(
        "\nTakeaway: match the prompt to the model. Normal models need you to elicit\n"
        "reasoning ('step by step', examples). Reasoning models already think — give\n"
        "them the goal and constraints, drop the scaffolding, and control depth with\n"
        "the model's effort/reasoning setting instead of a longer prompt."
    )
