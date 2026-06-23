"""
06 - STRUCTURED OUTPUT (JSON)
=============================

When a program -- not a human -- consumes the model's reply, you want machine-
readable output (usually JSON) with a guaranteed shape. Free-form prose is hard
and brittle to parse.

Three escalating levels of reliability:
  1. ASK for JSON in the prompt          (works, but can leak prose/markdown).
  2. response_format={"type":"json_object"}  (forces valid JSON syntax).
  3. JSON SCHEMA / structured outputs     (forces your exact fields & types;
                                           OpenAI hosted models + some local).

KEY IDEAS
  - Describe each field and its type; give an example object.
  - Set temperature low (0) for deterministic, parseable output.
  - ALWAYS wrap json.loads in try/except -- never trust the bytes blindly.
  - Not every local model supports json_schema; json_object is more portable.

Run:  python fundamentals/06_structured_output.py
"""

import json

# --- make the repo-root 'common' package importable when run directly ---
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import chat, get_client, header, rule, DEFAULT_MODEL

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
    # Level 2: force valid JSON syntax with response_format.
    return chat(
        [
            {"role": "system", "content": "You output only valid JSON. No markdown, no prose."},
            {"role": "user", "content": PROMPT},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )


def with_json_schema() -> str:
    """Level 3: enforce the exact schema. Falls back gracefully if unsupported."""
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
            "contact_name", "email", "product", "quantity",
            "destination", "deadline", "budget_eur",
        ],
        "additionalProperties": False,
    }
    client = get_client()
    resp = client.chat.completions.create(
        model=DEFAULT_MODEL,
        temperature=0,
        messages=[{"role": "user", "content": PROMPT}],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "order", "schema": schema, "strict": True},
        },
    )
    return resp.choices[0].message.content or ""


if __name__ == "__main__":
    header("STRUCTURED OUTPUT (JSON)")
    print("\nSource email:\n", EMAIL)

    rule()
    print("\n[response_format=json_object] ->")
    raw = ask_for_json()
    print(raw)

    # Demonstrate that the output is actually usable as data.
    try:
        data = json.loads(raw)
        print(f"\nParsed OK. quantity={data.get('quantity')} "
              f"deadline={data.get('deadline')} budget={data.get('budget_eur')}")
    except json.JSONDecodeError as e:
        print("Failed to parse JSON:", e)

    rule()
    print("\n[json_schema strict mode] (may fall back on some local models) ->")
    try:
        print(with_json_schema())
    except Exception as e:  # noqa: BLE001 - educational fallback
        print(f"json_schema not supported by this endpoint ({type(e).__name__}). "
              "Use json_object instead.")

    rule()
    print(
        "\nTakeaway: when code reads the output, constrain the format at the API\n"
        "level and still defensively parse. Don't regex prose out of a paragraph."
    )
