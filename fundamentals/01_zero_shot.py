"""
01 - ZERO-SHOT PROMPTING

Zero-shot = you ask the model to do a task WITHOUT giving it any worked
examples. You rely entirely on (a) the model's pretrained knowledge and
(b) how clearly you describe the task.

It is the baseline you should always try first. If zero-shot is good enough,
you don't need the extra tokens of few-shot examples.

KEY IDEAS
  - Be specific about the task, the input, and the desired output.
  - State the output FORMAT explicitly ("Reply with only the label").
  - Constrain the answer space ("one of: positive, negative, neutral").
  - Vague instructions are the #1 cause of bad zero-shot results.

Run:  secrun python fundamentals/01_zero_shot.py
"""

# --- make the repo-root 'common' package importable when run directly ---
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import chat, header, rule

REVIEW = "The screen is gorgeous but the battery dies in three hours and support never replied."


def vague_zero_shot() -> str:
    # Weak: no format, no label set -> the model rambles or guesses a scale.
    return chat(
        [{"role": "user", "content": f"What do you think of this review? {REVIEW}"}]
    )


def good_zero_shot() -> str:
    # Strong: task + constrained label set + exact output format.
    prompt = (
        "Classify the sentiment of the product review below.\n"
        "Respond with exactly one word: Positive, Negative, or Mixed.\n\n"
        f"Review: {REVIEW}\n"
        "Sentiment:"
    )
    return chat([{"role": "user", "content": prompt}], temperature=0)


if __name__ == "__main__":
    header("ZERO-SHOT PROMPTING")

    print("\n[Vague prompt] ->")
    print(vague_zero_shot())

    rule()
    print("\n[Specific, constrained prompt] ->")
    print(good_zero_shot())

    rule()
    print(
        "\nTakeaway: same model, same review. The constrained prompt returns a\n"
        "clean, parseable label; the vague one returns prose you'd have to\n"
        "post-process. Clarity > cleverness."
    )
