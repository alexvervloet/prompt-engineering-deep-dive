"""
12 - REFLEXION (SELF-CORRECTION FROM A FEEDBACK SIGNAL)
=======================================================

Prompt chaining (file 08) does generate -> critique -> revise *once*. Reflexion
goes further: the model attempts, you RUN A CHECK that produces a concrete signal
(pass/fail + why), and on failure the model REFLECTS on that signal and tries
again — looping until it passes or you give up.

The difference that matters: the feedback is *grounded* in a real verifier, not the
model's own opinion. A model grading itself is unreliable; a model reacting to "your
output failed this specific check" is much stronger.

The loop:
  1. Attempt the task.
  2. Verify with code (or a test, a linter, a schema validator...).
  3. If it fails, feed the failure back and ask the model to reflect + retry.
  4. Repeat until pass or max attempts.

KEY IDEAS
  - The verifier is the whole game. A cheap, objective check (does it parse? does
    it satisfy the constraints? does the test pass?) turns vague "try harder" into
    a precise error the model can actually fix.
  - Carry the history forward: the model should see its previous attempt AND why it
    failed, so it doesn't repeat the mistake.
  - This is how coding agents self-heal: write code -> run tests -> read the failure
    -> fix -> rerun.

Run:  secrun python fundamentals/12_reflexion.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import chat, header, rule

# The task has hard, machine-checkable constraints — perfect for a verifier.
TASK = (
    "Write a single sentence that:\n"
    "  (a) is about the ocean,\n"
    "  (b) contains exactly 12 words,\n"
    "  (c) contains the word 'silent',\n"
    "  (d) ends with an exclamation mark."
)


def verify(sentence: str) -> tuple[bool, str]:
    """Return (passed, feedback). This is the grounded signal the model reacts to."""
    s = sentence.strip()
    words = s.split()
    problems = []
    if len(words) != 12:
        problems.append(f"has {len(words)} words, needs exactly 12")
    if "silent" not in s.lower():
        problems.append("missing the word 'silent'")
    if not s.endswith("!"):
        problems.append("does not end with '!'")
    if not problems:
        return True, "all constraints satisfied"
    return False, "; ".join(problems)


def reflexion(max_attempts: int = 4) -> str:
    history = ""
    candidate = ""
    for attempt in range(1, max_attempts + 1):
        prompt = f"Task:\n{TASK}\n"
        if history:
            prompt += (
                f"\nYour previous attempt FAILED. Reflect on why, then write a corrected "
                f"sentence.\n{history}\nReturn ONLY the corrected sentence."
            )
        else:
            prompt += "\nReturn ONLY the sentence."

        candidate = chat([{"role": "user", "content": prompt}], temperature=0.4).strip()
        passed, feedback = verify(candidate)
        print(f"Attempt {attempt}: {candidate!r}")
        print(f"           verifier -> {'PASS' if passed else 'FAIL'} ({feedback})\n")
        if passed:
            return candidate
        history = f"Attempt: {candidate!r}\nVerifier feedback: {feedback}"
    return candidate  # best effort after the last attempt


if __name__ == "__main__":
    header("REFLEXION — SELF-CORRECTION FROM A FEEDBACK SIGNAL")
    print(f"\n{TASK}\n")
    rule()
    final = reflexion()
    rule()
    passed, _ = verify(final)
    print(f"\nFinal ({'passed' if passed else 'gave up'}): {final!r}")
    print(
        "\nTakeaway: a model correcting itself against a REAL check (code, a test, a\n"
        "schema) is far more reliable than one critiquing itself by vibes. Build the\n"
        "verifier first; the loop is the easy part."
    )
