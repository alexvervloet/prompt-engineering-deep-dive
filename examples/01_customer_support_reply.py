"""
EXAMPLE 1 - CUSTOMER SUPPORT REPLY
==================================

USE CASE: turn an angry customer email into an on-brand, helpful reply.

This file shows a NAIVE prompt vs an OPTIMIZED one and explains every change.
The optimized version combines: system prompt (role + tone + policy),
explicit constraints, structured output, and a fallback rule.

Run:  secrun python examples/01_customer_support_reply.py
"""

# --- make the repo-root 'common' package importable when run directly ---
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import chat, header, rule

CUSTOMER_EMAIL = """\
This is the SECOND time my order (#48213) arrived broken. I paid for express
shipping and waited two weeks. I want my money back and I'm done with you guys.
"""

# --------------------------------------------------------------------------
# BEFORE: vague, no persona, no policy, no format. You get an unpredictable,
# possibly off-brand reply that may over-promise a refund you can't authorize.
# --------------------------------------------------------------------------
NAIVE_PROMPT = f"Reply to this customer:\n\n{CUSTOMER_EMAIL}"


def naive() -> str:
    return chat([{"role": "user", "content": NAIVE_PROMPT}], temperature=0.7)


# --------------------------------------------------------------------------
# AFTER: a system prompt encodes WHO the agent is, the TONE, the POLICY (what
# it may and may not promise), the FORMAT, and a FALLBACK for missing info.
# --------------------------------------------------------------------------
OPTIMIZED_SYSTEM = """\
ROLE: You are a senior customer-support specialist for "Northwind Goods".

TONE: Warm, genuinely apologetic, calm, and concise. Never defensive.

POLICY (hard rules):
- You MAY offer: a free replacement, a prepaid return label, and a 20% discount
  on a future order.
- You MAY NOT promise refunds, free upgrades, or compensation beyond the above;
  for those, say a human agent will follow up within 24 hours.
- Acknowledge repeat issues explicitly and take ownership.

FORMAT:
- Greeting using the customer's order number.
- 1-2 sentence empathetic acknowledgement.
- A clear list of the concrete options you ARE authorized to offer.
- A single, specific next step / call to action.
- Sign off as "The Northwind Support Team".

FALLBACK: If key info is missing (e.g. no order number), ask for exactly that
one thing before offering remedies.
"""


def optimized() -> str:
    return chat(
        [
            {"role": "system", "content": OPTIMIZED_SYSTEM},
            {"role": "user", "content": CUSTOMER_EMAIL},
        ],
        temperature=0.5,
    )


if __name__ == "__main__":
    header("EXAMPLE 1 - CUSTOMER SUPPORT REPLY")
    print("\nIncoming email:\n", CUSTOMER_EMAIL)

    rule()
    print("\n[BEFORE - naive prompt] ->")
    print(naive())

    rule()
    print("\n[AFTER - role + policy + format + fallback] ->")
    print(optimized())

    rule()
    print(
        "\nWHY IT'S BETTER:\n"
        "  - Policy constraints stop the model over-promising a refund.\n"
        "  - The persona + tone keep replies on-brand and empathetic.\n"
        "  - The fixed format is consistent across every ticket.\n"
        "  - The fallback handles missing data instead of guessing."
    )
