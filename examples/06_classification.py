"""
EXAMPLE 6 - TEXT CLASSIFICATION (TICKET ROUTING)
================================================

USE CASE: route incoming support tickets into a fixed set of categories so they
reach the right team automatically. Classification is the workhorse of LLM apps —
moderation, intent detection, triage, tagging — and a few prompt choices make the
difference between flaky labels and a reliable router.

Optimizations applied: a CLOSED label set with definitions, a forced single label
via forced JSON, an explicit 'other' escape hatch, a confidence score for routing
to humans, and a couple of few-shot edge cases for the tricky boundaries.

Run:  secrun python examples/06_classification.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import chat, header, rule

TICKETS = [
    "I was charged twice for my subscription this month, please refund one.",
    "The export button does nothing when I click it on Safari.",
    "How do I add a teammate to my workspace?",
    "You people are useless and I want to speak to a manager NOW.",
    "Is there a way to get the dInosaur plan? saw it mentioned somewhere",  # ambiguous/unknown
]

LABELS = ["billing", "bug", "how_to", "complaint", "other"]


# --------------------------------------------------------------------------
# BEFORE: open-ended "what category" -> invented labels, inconsistent casing,
# no escape hatch, nothing to route low-confidence cases to a human.
# --------------------------------------------------------------------------
def naive(ticket: str) -> str:
    return chat(
        [
            {
                "role": "user",
                "content": f"What category is this support ticket?\n\n{ticket}",
            }
        ],
        temperature=0,
    ).strip()


# --------------------------------------------------------------------------
# AFTER: closed label set + definitions + 'other' + confidence + few-shot
# edge cases, returned as JSON so your router can branch on it directly.
# --------------------------------------------------------------------------
SYSTEM = """You are a support-ticket router. Classify each ticket into EXACTLY ONE label:

  billing   - payments, charges, refunds, invoices, subscription cost
  bug        - something is broken or not working as expected
  how_to     - a question about how to use the product
  complaint  - an expression of frustration with no specific actionable request
  other      - none of the above, or the request is unclear/unknown

Rules:
  - Choose the SINGLE best label. If a ticket both complains AND reports a bug,
    prefer the actionable one (bug).
  - Use 'other' when unsure rather than guessing a category.
  - Output JSON only: {"label": <one of the labels>, "confidence": <0.0-1.0>}.

Examples:
  Ticket: "I can't believe this broke again, fix your app" -> {"label": "bug", "confidence": 0.7}
  Ticket: "where do I change my password" -> {"label": "how_to", "confidence": 0.95}
  Ticket: "do you offer the platinum tier??" -> {"label": "other", "confidence": 0.5}"""


def optimized(ticket: str) -> dict:
    raw = chat(
        [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"Ticket: {ticket}"},
        ],
        temperature=0,
        json=True,
    )
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {"label": "other", "confidence": 0.0}
    # Defensive: reject any label outside the closed set.
    if data.get("label") not in LABELS:
        data["label"] = "other"
    return data


if __name__ == "__main__":
    header("EXAMPLE 6 - CLASSIFICATION (TICKET ROUTING)")

    rule()
    print("\n[BEFORE - open-ended 'what category'] ->")
    for t in TICKETS:
        print(f"  {naive(t):<22} <- {t[:55]}")

    rule()
    print("\n[AFTER - closed labels + confidence + 'other' escape hatch] ->")
    for t in TICKETS:
        result = optimized(t)
        route = (
            "→ human review"
            if result["confidence"] < 0.6
            else f"→ {result['label']} team"
        )
        print(f"  {result['label']:<10} conf={result['confidence']:.2f}  {route}")
        print(f"             {t[:60]}")

    rule()
    print(
        "\nWHY IT'S BETTER:\n"
        "  - A CLOSED label set + definitions stops invented/inconsistent categories.\n"
        "  - An 'other' escape hatch + confidence score route the unsure cases to a\n"
        "    human instead of silently mislabeling them.\n"
        "  - json=True + a label whitelist make the output safe to branch on in code.\n"
        "  - Few-shot edge cases pin down the tricky boundaries (complaint vs bug)."
    )
