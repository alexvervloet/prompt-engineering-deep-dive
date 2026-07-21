"""
02 - FEW-SHOT PROMPTING

Few-shot = you include a handful of input->output EXAMPLES in the prompt before
the real input. The model infers the pattern (the task, the format, the tone,
the edge-case handling) from your demonstrations.

Use it when:
  - The desired OUTPUT FORMAT is specific/unusual.
  - The task is subjective and you want to pin down YOUR definition.
  - Zero-shot is close but inconsistent.

KEY IDEAS
  - 2-5 examples is usually plenty; more isn't always better.
  - Make examples DIVERSE and cover edge cases (e.g. an ambiguous one).
  - Keep formatting IDENTICAL across examples -- the model copies it.
  - Balance your label distribution; don't make every example "Positive".

Run:  secrun python fundamentals/02_few_shot.py
"""

# --- make the repo-root 'common' package importable when run directly ---
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import chat, header, rule

# We want a very specific output shape: a JSON-ish tag the model would not
# produce on its own. The examples teach both the labels AND the format.
SYSTEM = "You label support tickets. Reply with only: <category>|<priority>."

FEW_SHOT_EXAMPLES = [
    {"role": "user", "content": "My invoice charged me twice this month."},
    {"role": "assistant", "content": "billing|high"},
    {"role": "user", "content": "How do I change my profile picture?"},
    {"role": "assistant", "content": "how-to|low"},
    {
        "role": "user",
        "content": "The whole site has been down for an hour, we can't work.",
    },
    {"role": "assistant", "content": "outage|urgent"},
]

NEW_TICKET = "I was promised a refund last week and still haven't received it."


def zero_shot_baseline() -> str:
    return chat(
        [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": NEW_TICKET},
        ],
        temperature=0,
    )


def few_shot() -> str:
    messages = [{"role": "system", "content": SYSTEM}]
    messages.extend(FEW_SHOT_EXAMPLES)  # the demonstrations
    messages.append({"role": "user", "content": NEW_TICKET})  # the real task
    return chat(messages, temperature=0)


if __name__ == "__main__":
    header("FEW-SHOT PROMPTING")

    print("\nNew ticket:", NEW_TICKET)

    rule()
    print("\n[Zero-shot] (model has only the terse system rule) ->")
    print(zero_shot_baseline())

    rule()
    print("\n[Few-shot] (3 examples teach the exact format + priority sense) ->")
    print(few_shot())

    rule()
    print(
        "\nTakeaway: examples are the cheapest way to lock in an exact output\n"
        "format and your own labeling conventions without a long rulebook."
    )
