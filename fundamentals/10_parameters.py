"""
10 - DECODING PARAMETERS (temperature, top_p, max_tokens, seed, stop)
=====================================================================

The prompt is only half the story -- the SAMPLING parameters control how the
model turns its probabilities into text. Same prompt + different params =
different behavior.

THE KNOBS
  - temperature (0-2): randomness. 0 = (near) deterministic, pick the most
    likely token. Higher = more diverse/creative (and more error-prone).
  - top_p (0-1): nucleus sampling -- only consider the smallest set of tokens
    whose probabilities sum to top_p. Usually tune temperature OR top_p, not both.
  - max_tokens: hard cap on reply length (controls cost + runaway output).
  - seed: with temperature 0 + a fixed seed, many backends give reproducible
    output -- invaluable for tests/evals.
  - stop: strings that end generation early (e.g. stop at "\n\n").

RULES OF THUMB
  - Extraction / classification / code edits  -> temperature 0.
  - Brainstorming / copywriting / variety      -> temperature 0.7-1.0.
  - Always set max_tokens in production to bound cost & latency.

PROVIDER NOTE
  - temperature range is 0-2 on OpenAI but 0-1 on Claude; `common.chat` clamps
    for you, so the calls below behave on either stack.
  - `seed` is an OpenAI feature (reproducible sampling); Claude has no seed. The
    runnable calls here use only temperature + max_tokens, so they work on both.

Run:  secrun python fundamentals/10_parameters.py
"""

# --- make the repo-root 'common' package importable when run directly ---
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import chat, header, rule

PROMPT = "Give me a name for a cozy neighborhood coffee shop. Reply with just the name."


def sample_at(temperature: float, n: int = 3) -> list[str]:
    return [
        chat(
            [{"role": "user", "content": PROMPT}],
            temperature=temperature,
            max_tokens=20,
        ).strip()
        for _ in range(n)
    ]


if __name__ == "__main__":
    header("DECODING PARAMETERS")

    rule()
    print("\ntemperature = 0  (deterministic -> expect repeats):")
    for name in sample_at(0.0):
        print("  -", name)

    rule()
    print("\ntemperature = 1.0  (diverse -> expect variety):")
    for name in sample_at(1.0):
        print("  -", name)

    rule()
    print("\nmax_tokens demo (cap length to ~12 tokens):")
    capped = chat(
        [{"role": "user", "content": "Explain photosynthesis."}],
        temperature=0.3,
        max_tokens=12,
    )
    print("  ", capped, "  <-- cut off by the token budget")

    rule()
    print(
        "\nTakeaway: pick temperature by task -- 0 for correctness/parsing,\n"
        "higher for creativity -- and always bound length with max_tokens."
    )
