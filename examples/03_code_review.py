"""
EXAMPLE 3 - CODE REVIEW ASSISTANT

USE CASE: review a code snippet and return actionable, prioritized findings --
not a vague "looks fine" or a wall of nitpicks.

Optimizations applied: expert persona, a review RUBRIC (what to look for),
severity levels, a strict output format, and an instruction to cite line-ish
locations and propose concrete fixes.

Run:  secrun python examples/03_code_review.py
"""

# --- make the repo-root 'common' package importable when run directly ---
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import chat, header, rule

CODE = """\
def get_user_orders(db, user_id):
    query = "SELECT * FROM orders WHERE user_id = " + user_id
    results = db.execute(query)
    orders = []
    for r in results:
        orders.append(r)
    return orders
"""


# --------------------------------------------------------------------------
# BEFORE: "review this code" -> typically a friendly but shallow summary that
# may miss the SQL injection and gives no priorities or fixes.
# --------------------------------------------------------------------------
def naive() -> str:
    return chat(
        [{"role": "user", "content": f"Review this code:\n\n{CODE}"}],
        temperature=0.5,
    )


# --------------------------------------------------------------------------
# AFTER: expert persona + explicit rubric + severity + fix-oriented format.
# --------------------------------------------------------------------------
OPTIMIZED_SYSTEM = """\
You are a meticulous senior software engineer doing a security-aware code review.

REVIEW RUBRIC (check each, in this order of importance):
  1. Security    (injection, secrets, unsafe deserialization, authz)
  2. Correctness (bugs, edge cases, error handling)
  3. Performance (needless work, N+1, allocations)
  4. Clarity     (naming, dead code, idioms)

FOR EACH finding output exactly:
  [SEVERITY] <one-line problem>
    - Why it matters: <short>
    - Fix: <concrete change, with a code snippet if useful>

SEVERITY is one of: CRITICAL, HIGH, MEDIUM, LOW.
Order findings by severity (CRITICAL first). If there are no issues in a
category, don't mention it. End with a one-line overall verdict.
"""


def optimized() -> str:
    return chat(
        [
            {"role": "system", "content": OPTIMIZED_SYSTEM},
            {
                "role": "user",
                "content": f"Review this Python function:\n\n```python\n{CODE}```",
            },
        ],
        temperature=0.2,
    )


if __name__ == "__main__":
    header("EXAMPLE 3 - CODE REVIEW")
    print("\nCode under review:\n", CODE)

    rule()
    print("\n[BEFORE - 'review this code'] ->")
    print(naive())

    rule()
    print("\n[AFTER - persona + rubric + severity + fixes] ->")
    print(optimized())

    rule()
    print(
        "\nWHY IT'S BETTER:\n"
        "  - The rubric forces a SECURITY pass first (catches the SQL injection).\n"
        "  - Severity labels make the output triage-able.\n"
        "  - 'Fix:' requires actionable changes, not just complaints.\n"
        "  - The fixed format is consistent and easy to scan or post as comments."
    )
