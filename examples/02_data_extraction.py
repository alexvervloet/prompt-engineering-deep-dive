"""
EXAMPLE 2 - STRUCTURED DATA EXTRACTION
======================================

USE CASE: pull clean, typed records out of messy unstructured text (here, a
job posting) so downstream code can store/filter them.

Optimizations applied: explicit schema with types, normalization rules,
null handling, few-shot-style field descriptions, forced-JSON output, and
defensive parsing.

Run:  secrun python examples/02_data_extraction.py
"""

import json

# --- make the repo-root 'common' package importable when run directly ---
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import chat, header, rule

JOB_POST = """\
We're hiring a Senior Backend Engineer (Remote, EU timezones). Comp: 80-95k EUR
plus equity. You'll work in Python and Go on our payments platform. 5+ yrs exp.
Nice to have: Kubernetes. Apply by 2026-07-15. Contact jobs@fintechco.eu.
"""


# --------------------------------------------------------------------------
# BEFORE: "extract the info" with no schema -> inconsistent keys, salary as a
# free-text string, no way to know if a field was simply absent.
# --------------------------------------------------------------------------
def naive() -> str:
    return chat(
        [{"role": "user", "content": f"Extract the job info as JSON:\n\n{JOB_POST}"}],
        temperature=0.3,
    )


# --------------------------------------------------------------------------
# AFTER: pin the exact schema, types, normalization, and null policy.
# --------------------------------------------------------------------------
OPTIMIZED_PROMPT = f"""\
Extract structured data from the job posting. Return ONLY JSON with these keys:

  title          (string)
  seniority      (one of: "junior", "mid", "senior", "lead", or null)
  remote         (boolean)
  location_note  (string or null)   # e.g. timezone/region constraints
  salary_min     (integer or null)  # annual, in the currency below
  salary_max     (integer or null)
  currency       (3-letter ISO code, e.g. "EUR", or null)
  skills         (array of strings; required + nice-to-have, deduplicated)
  min_years_exp  (integer or null)
  apply_by       (ISO date "YYYY-MM-DD" or null)
  contact_email  (string or null)

NORMALIZATION RULES:
- "80-95k EUR" -> salary_min 80000, salary_max 95000, currency "EUR".
- If a field is not stated, use null (do NOT guess).
- skills should be lowercase single words/phrases.

Job posting:
\"\"\"{JOB_POST}\"\"\"
"""


def optimized() -> str:
    return chat(
        [
            {
                "role": "system",
                "content": "You are a precise extraction engine. Output only valid JSON.",
            },
            {"role": "user", "content": OPTIMIZED_PROMPT},
        ],
        temperature=0,
        json=True,
    )


if __name__ == "__main__":
    header("EXAMPLE 2 - DATA EXTRACTION")
    print("\nSource posting:\n", JOB_POST)

    rule()
    print("\n[BEFORE - no schema] ->")
    print(naive())

    rule()
    print("\n[AFTER - typed schema + normalization + null policy] ->")
    raw = optimized()
    print(raw)

    try:
        data = json.loads(raw)
        print(
            f"\nParsed OK -> salary_min={data.get('salary_min')} "
            f"({type(data.get('salary_min')).__name__}), "
            f"skills={data.get('skills')}"
        )
    except json.JSONDecodeError as e:
        print("Parse error:", e)

    rule()
    print(
        "\nWHY IT'S BETTER:\n"
        "  - Typed fields (int salary, bool remote) are query-ready, not prose.\n"
        "  - Explicit null policy distinguishes 'absent' from 'guessed'.\n"
        "  - Normalization rules make '80-95k' a structured range every time.\n"
        "  - json=True + try/except = robust, machine-readable pipeline."
    )
