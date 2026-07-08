"""
EXAMPLE 4 - CONSTRAINED SUMMARIZATION
=====================================

USE CASE: summarize a long document for a SPECIFIC audience and purpose, under
hard constraints (length, focus, format) -- e.g. an exec TL;DR of a postmortem.

Optimizations applied: define the audience + purpose, hard length limits,
extraction focus ("only what changes a decision"), grounding ("only use the
text"), and a fixed output structure.

Run:  secrun python examples/04_summarization.py
"""

# --- make the repo-root 'common' package importable when run directly ---
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import chat, header, rule

DOCUMENT = """\
Incident report: On June 18, a deploy to the payments service introduced a
config change that lowered the database connection pool from 100 to 10. Under
normal load this was fine, but during the 6pm peak, requests queued and timed
out. Checkout error rate rose to 22% for 47 minutes. On-call was paged at 6:08pm,
identified the config diff at 6:31pm, and rolled back at 6:39pm; recovery was
complete by 6:55pm. Estimated revenue impact: ~$40k. Root cause: the pool value
was templated from a staging default that was never overridden for production.
Action items: add a pre-deploy check that flags pool-size drops, add a synthetic
peak-load test, and alert on connection-pool saturation.
"""


# --------------------------------------------------------------------------
# BEFORE: "summarize this" -> generic, unbounded length, no audience focus.
# --------------------------------------------------------------------------
def naive() -> str:
    return chat(
        [{"role": "user", "content": f"Summarize this:\n\n{DOCUMENT}"}],
        temperature=0.5,
    )


# --------------------------------------------------------------------------
# AFTER: audience + purpose + hard constraints + fixed structure + grounding.
# --------------------------------------------------------------------------
OPTIMIZED_PROMPT = f"""\
Summarize the incident report below FOR A BUSY EXECUTIVE who has 30 seconds.

CONSTRAINTS:
- Use ONLY information in the report; do not speculate.
- Total length: at most 80 words.
- Lead with business impact (money + duration), not technical detail.

OUTPUT FORMAT:
TL;DR: <one sentence: what happened + impact>
Cause: <one sentence>
Prevention: <one sentence naming the key action items>

Report:
\"\"\"{DOCUMENT}\"\"\"
"""


def optimized() -> str:
    return chat([{"role": "user", "content": OPTIMIZED_PROMPT}], temperature=0.2)


if __name__ == "__main__":
    header("EXAMPLE 4 - CONSTRAINED SUMMARIZATION")
    print("\nSource document:\n", DOCUMENT)

    rule()
    print("\n[BEFORE - 'summarize this'] ->")
    print(naive())

    rule()
    print("\n[AFTER - audience + length + focus + structure] ->")
    print(optimized())

    rule()
    print(
        "\nWHY IT'S BETTER:\n"
        "  - Naming the AUDIENCE (exec, 30s) sets the right altitude.\n"
        "  - The 80-word cap forces ruthless prioritization.\n"
        "  - 'Lead with business impact' reorders for the reader's needs.\n"
        "  - Grounding ('only the report') prevents invented details.\n"
        "  - The fixed 3-line structure is skimmable and consistent."
    )
