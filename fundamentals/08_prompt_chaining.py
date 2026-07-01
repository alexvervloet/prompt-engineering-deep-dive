"""
08 - PROMPT CHAINING / TASK DECOMPOSITION
=========================================

Hard tasks get more reliable when you BREAK them into a pipeline of smaller
prompts, each doing one job and feeding the next. Each step is easy to test,
debug, and swap out -- far better than one giant "do everything" prompt.

Example pipeline (turn a messy idea into a polished tweet):
  Step 1  EXTRACT  -> pull the key points from raw notes.
  Step 2  DRAFT    -> write a tweet from those points.
  Step 3  CRITIQUE -> score & critique the draft against rules.
  Step 4  REVISE   -> rewrite using the critique.

KEY IDEAS
  - One responsibility per step = easier debugging and cheaper iteration.
  - The output of step N becomes (part of) the input to step N+1.
  - A "generate -> critique -> revise" loop (self-refinement) reliably raises
    quality. The critic step is where most of the gains come from.

Run:  python fundamentals/08_prompt_chaining.py
"""

# --- make the repo-root 'common' package importable when run directly ---
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import chat, header, rule

RAW_NOTES = """\
ok so we shipped the new offline mode finally. works on mobile + desktop.
syncs automatically when you reconnect. took the team 3 months. people kept
asking for it. also fixed the battery drain bug from before.
"""


def step_extract(notes: str) -> str:
    return chat(
        [
            {
                "role": "user",
                "content": f"Extract the 3 most important points from these notes as a short "
                f"bullet list:\n\n{notes}",
            }
        ],
        temperature=0,
    )


def step_draft(points: str) -> str:
    return chat(
        [
            {
                "role": "user",
                "content": f"Write a single tweet (<=280 chars) announcing this, upbeat but not "
                f"hypey, no hashtags:\n\n{points}",
            }
        ],
        temperature=0.7,
    )


def step_critique(draft: str) -> str:
    return chat(
        [
            {
                "role": "user",
                "content": f"Critique this tweet against: clarity, length<=280, no hashtags, "
                f"concrete benefit. List concrete fixes only.\n\nTweet:\n{draft}",
            }
        ],
        temperature=0,
    )


def step_revise(draft: str, critique: str) -> str:
    return chat(
        [
            {
                "role": "user",
                "content": f"Rewrite the tweet applying every fix. Output only the final tweet.\n\n"
                f"Original:\n{draft}\n\nFixes:\n{critique}",
            }
        ],
        temperature=0.7,
    )


if __name__ == "__main__":
    header("PROMPT CHAINING / DECOMPOSITION")

    rule()
    print("\nStep 1 - EXTRACT key points ->")
    points = step_extract(RAW_NOTES)
    print(points)

    rule()
    print("\nStep 2 - DRAFT a tweet ->")
    draft = step_draft(points)
    print(draft)

    rule()
    print("\nStep 3 - CRITIQUE the draft ->")
    critique = step_critique(draft)
    print(critique)

    rule()
    print("\nStep 4 - REVISE using the critique ->")
    final = step_revise(draft, critique)
    print(final)

    rule()
    print(
        "\nTakeaway: a chain of small, single-purpose prompts -- especially a\n"
        "generate->critique->revise loop -- beats one monolithic prompt on both\n"
        "quality and debuggability."
    )
