"""
06 - STRUCTURED OUTPUT (JSON)
=============================

When a program -- not a human -- consumes the model's reply, you want machine-
readable output (usually JSON) with a guaranteed shape. Free-form prose is hard
and brittle to parse.

Three escalating levels of reliability:
  1. ASK for JSON in the prompt          (works, but can leak prose/markdown).
  2. json=True  (forces valid JSON syntax: response_format on OpenAI, an
                 assistant prefill on Claude -- `common.chat` picks the right one).
  3. JSON SCHEMA / structured outputs     (forces your exact fields & types:
                 OpenAI's strict `json_schema`, or Claude's forced tool call --
                 `common.structured` picks the right one).

KEY IDEAS
  - Describe each field and its type; give an example object.
  - Set temperature low (0) for deterministic, parseable output.
  - ALWAYS wrap json.loads in try/except -- never trust the bytes blindly.
  - Level 2 is the portable workhorse; level 3 is the strongest guarantee.

Run:  secrun python fundamentals/06_structured_output.py
"""

import json

# --- make the repo-root 'common' package importable when run directly ---
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import chat, header, rule, structured

EMAIL = (
    "Hi, this is Dana Lopez. We'd like 250 units of the X200 sensor shipped to "
    "our Berlin warehouse by August 3rd. Budget is around 9,000 EUR. You can "
    "reach me at dana.lopez@acme.io."
)

PROMPT = f"""\
Extract the order details from the email below as JSON with EXACTLY these keys:
  - contact_name (string)
  - email (string)
  - product (string)
  - quantity (integer)
  - destination (string)
  - deadline (string, ISO date YYYY-MM-DD if possible, else null)
  - budget_eur (number or null)

Email:
\"\"\"{EMAIL}\"\"\"
"""


def ask_for_json() -> str:
    # Level 2: force valid JSON syntax with json=True (provider-appropriate).
    return chat(
        [
            {
                "role": "system",
                "content": "You output only valid JSON. No markdown, no prose.",
            },
            {"role": "user", "content": PROMPT},
        ],
        temperature=0,
        json=True,
    )


def with_json_schema() -> str:
    """Level 3: enforce the exact fields & types via `common.structured`."""
    schema = {
        "type": "object",
        "properties": {
            "contact_name": {"type": "string"},
            "email": {"type": "string"},
            "product": {"type": "string"},
            "quantity": {"type": "integer"},
            "destination": {"type": "string"},
            "deadline": {"type": ["string", "null"]},
            "budget_eur": {"type": ["number", "null"]},
        },
        "required": [
            "contact_name",
            "email",
            "product",
            "quantity",
            "destination",
            "deadline",
            "budget_eur",
        ],
        "additionalProperties": False,
    }
    return structured(
        [{"role": "user", "content": PROMPT}],
        schema,
        name="order",
        temperature=0,
    )


if __name__ == "__main__":
    header("STRUCTURED OUTPUT (JSON)")
    print("\nSource email:\n", EMAIL)

    rule()
    print("\n[json=True — forced JSON object] ->")
    raw = ask_for_json()
    print(raw)

    # Demonstrate that the output is actually usable as data.
    try:
        data = json.loads(raw)
        print(
            f"\nParsed OK. quantity={data.get('quantity')} "
            f"deadline={data.get('deadline')} budget={data.get('budget_eur')}"
        )
    except json.JSONDecodeError as e:
        print("Failed to parse JSON:", e)

    rule()
    print("\n[schema-enforced output] (strict json_schema / forced tool call) ->")
    try:
        print(with_json_schema())
    except Exception as e:  # noqa: BLE001 - educational fallback
        print(
            f"Schema enforcement unsupported by this endpoint ({type(e).__name__}). "
            "Fall back to json=True."
        )

    rule()
    print(
        "\nTakeaway: when code reads the output, constrain the format at the API\n"
        "level and still defensively parse. Don't regex prose out of a paragraph."
    )
