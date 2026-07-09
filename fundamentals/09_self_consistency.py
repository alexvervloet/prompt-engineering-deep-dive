"""
09 - SELF-CONSISTENCY (SAMPLING + VOTING)
=========================================

For problems with one correct answer but many reasoning paths, a single CoT run
can land on a wrong path. SELF-CONSISTENCY samples the SAME prompt several times
at a non-zero temperature, then takes a MAJORITY VOTE over the final answers.
The most common answer is usually the right one.

KEY IDEAS
  - Requires temperature > 0 so the samples actually differ.
  - Parse out the final answer from each sample, then vote.
  - Costs N x the tokens -> use it where correctness matters (math, extraction
    of a single fact, classification near a decision boundary).
  - It's a cheap, model-agnostic accuracy boost with no fine-tuning.

Run:  secrun python fundamentals/09_self_consistency.py
"""

# --- make the repo-root 'common' package importable when run directly ---
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import chat, header, rule

# A 4-color combinatorics/probability problem with an "at least" condition.
# Counting-based reasoning is a well-known weak spot for LLMs -- much more so
# than straight arithmetic -- and this version needs the solver to enumerate
# every (color, count) case on their own (3/4/5 of red, 3/4 of blue, 3/4/5 of
# green, 3 of yellow) and sum C(n, k) * C(others, 5-k) for each, with no
# overlap to worry about since two colors can't each reach 3 within a 5-draw
# hand. That's a lot of cases to track without dropping or double-counting
# one, which is a much better source of genuine, independent per-sample
# slips than a problem a strong model just carries out correctly every time.
PROBLEM = (
    "A bag contains 6 red, 4 blue, 5 green, and 3 yellow marbles. You draw five "
    "marbles at random, without replacement. What is the probability that you "
    "get at least 3 marbles of the same color? Give your answer as a "
    "percentage, rounded to the nearest whole number."
)

PROMPT = (
    f"{PROBLEM}\n\n"
    "Reason step by step, then end with a line exactly like: ANSWER: <number>"
)


def sample_answer() -> tuple[str, int | None]:
    text = chat([{"role": "user", "content": PROMPT}], temperature=0.8)
    match = re.search(r"ANSWER:\s*(-?\d+)", text)
    return text, (int(match.group(1)) if match else None)


def self_consistency(n: int = 5) -> None:
    answers: list[int] = []
    for i in range(n):
        _, ans = sample_answer()
        print(f"  sample {i + 1}: ANSWER = {ans}")
        if ans is not None:
            answers.append(ans)

    if not answers:
        print("No parseable answers.")
        return

    winner, count = Counter(answers).most_common(1)[0]
    print(f"\nMajority vote -> {winner}  ({count}/{len(answers)} samples agreed)")


if __name__ == "__main__":
    header("SELF-CONSISTENCY")
    print("\nProblem:", PROBLEM)

    rule()
    print("\nSingle sample (temperature 0.8) -- could be the unlucky wrong path:")
    text, ans = sample_answer()
    print(text)

    rule()
    print("\nSelf-consistency over 5 samples + majority vote:")
    self_consistency(5)

    rule()
    print(
        "\nTakeaway: when an answer is verifiable-by-agreement, sampling several\n"
        "reasoning paths and voting is a simple, reliable accuracy upgrade."
    )
