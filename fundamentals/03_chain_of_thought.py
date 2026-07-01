"""
03 - CHAIN-OF-THOUGHT (CoT) PROMPTING
=====================================

Chain-of-thought = you ask the model to REASON STEP BY STEP before committing
to a final answer. Giving the model room to "think out loud" dramatically
improves accuracy on multi-step problems: math, logic, planning, debugging.

Two flavors:
  1. Zero-shot CoT  -> just add "Let's think step by step." / "Reason first."
  2. Few-shot CoT   -> show examples that include the reasoning, not just the
                       answer, so the model imitates the reasoning style.

KEY IDEAS
  - Reasoning helps most on problems with multiple dependent steps.
  - Ask for the FINAL ANSWER on its own line so it stays easy to parse.
  - Trade-off: more tokens + latency. For trivial tasks it's wasted cost.
  - For user-facing apps you often want the reasoning HIDDEN from the user.
    The GOTCHA: for a normal chat-completion model, "reasoning" only happens
    in the tokens it emits -- there's no silent scratchpad. So telling the
    model to "think silently, output only the final number" doesn't hide
    reasoning, it PREVENTS it, and accuracy collapses back to the no-CoT
    case (see `reason_then_hide` below). What actually works: let the model
    emit the full step-by-step reasoning, then strip it before showing the
    user (parse out the final line) -- or use a model with a real hidden
    reasoning channel (e.g. extended thinking / o1-style models), where
    reasoning tokens exist but are withheld from the visible output. See
    `reason_then_hide_correctly` for the working version.
  - "Think silently" can still LOOK reliable on an easy problem with a strong
    model -- a big model can pack a 3-step calculation into one forward pass
    without externalizing it. That's not a hidden scratchpad, it's spare
    capacity, and it runs out as the problem gets harder. See TOUGH_PROBLEM
    below: same "think silently" prompt, more dependent steps, and the
    silent version starts missing while visible CoT keeps landing exactly.

Run:  python fundamentals/03_chain_of_thought.py
"""

# --- make the repo-root 'common' package importable when run directly ---
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import chat, header, rule

PROBLEM = (
    "A store had 120 apples. It sold 35% of them in the morning and 18 more in "
    "the afternoon. A delivery then added half of what was left. How many apples "
    "does the store have now?"
)

# A deliberately harder problem: 6 dependent steps (vs. 3 above) with a rounding
# rule the model has to track across steps. Correct answer: 763. Easy enough for
# a strong model to nail with visible CoT every time -- hard enough that "think
# silently" (no externalized steps) starts missing it, even on a strong model.
TOUGH_PROBLEM = (
    "A warehouse starts with 1,000 crates. On day 1, 23% of the crates are "
    "shipped out, and then 17 more are damaged and removed. On day 2, a "
    "supplier delivers a new batch equal to one-quarter of what remains, and "
    "then 8% of the new total is found defective and discarded. On day 3, 31 "
    "crates are returned by customers, and finally 15% of the total is set "
    "aside for a clearance sale. Round down to the nearest whole crate after "
    "every percentage calculation. How many crates are left in the regular "
    "inventory after the clearance crates are set aside?"
)


def no_cot(problem: str = PROBLEM) -> str:
    # Demanding an instant answer encourages a fast (often wrong) guess.
    return chat(
        [{"role": "user", "content": f"{problem}\nAnswer with just the number."}],
        temperature=0,
    )


def zero_shot_cot(problem: str = PROBLEM) -> str:
    prompt = (
        f"{problem}\n\n"
        "Work through this step by step, showing each calculation. "
        "Then on a final line write: ANSWER: <number>."
    )
    return chat([{"role": "user", "content": prompt}], temperature=0)


def reason_then_hide(problem: str = PROBLEM) -> str:
    """Tempting but unreliable: asking the model to "think silently" doesn't
    give it a hidden scratchpad -- it just suppresses the reasoning tokens
    it needs to get the answer right. On an easy problem a strong model can
    sometimes get away with it (it has spare capacity to do the arithmetic
    in one forward pass); on TOUGH_PROBLEM that capacity runs out and it
    starts missing, the same way `no_cot` does. The fix that actually hides
    reasoning from the user without losing accuracy: run `zero_shot_cot`-style
    prompting (model emits full reasoning), then parse out just the
    "ANSWER:" line before displaying it -- the hiding happens in your code,
    not in the model's head."""
    prompt = (
        f"{problem}\n\n"
        "Think through the steps silently. Do NOT show your work. "
        "Output only the final number."
    )
    return chat([{"role": "user", "content": prompt}], temperature=0)


def reason_then_hide_correctly(problem: str = PROBLEM) -> str:
    """What actually works in production: let the model reason in full
    (same prompt shape as `zero_shot_cot`), then hide that reasoning
    YOURSELF in code by parsing out just the "ANSWER:" line before it
    ever reaches the user. The model gets the accuracy benefit of CoT;
    the user only sees the final number. This is the real version of
    what `reason_then_hide` was trying (and failing) to do."""
    prompt = (
        f"{problem}\n\n"
        "Work through this step by step, showing each calculation. "
        "Then on a final line write: ANSWER: <number>."
    )
    full_response = chat([{"role": "user", "content": prompt}], temperature=0)

    match = re.search(r"ANSWER:\s*(.+)", full_response)
    return match.group(1).strip() if match else full_response


if __name__ == "__main__":
    header("CHAIN-OF-THOUGHT PROMPTING")
    print("\nProblem:", PROBLEM)

    rule()
    print("\n[No reasoning, answer only] ->")
    print(no_cot())

    rule()
    print("\n[Zero-shot CoT: 'step by step'] ->")
    print(zero_shot_cot())

    rule()
    print('\n["Think silently", answer only -- likely broken, see docstring] ->')
    print(reason_then_hide())

    rule()
    print("\n[Reason in full, hide it in code -- the version that actually works] ->")
    print(reason_then_hide_correctly())

    rule()
    print("\n--- Now with a tougher, 6-step problem (correct answer: 763) ---")
    print("Problem:", TOUGH_PROBLEM)

    rule()
    print('\n[Tough problem, "think silently" -- watch this get less reliable] ->')
    print(reason_then_hide(TOUGH_PROBLEM))

    rule()
    print("\n[Tough problem, reason in full + hide in code -- stays reliable] ->")
    print(reason_then_hide_correctly(TOUGH_PROBLEM))

    rule()
    print(
        "\nTakeaway: letting the model reason before answering is one of the\n"
        "highest-leverage techniques for accuracy. To hide that reasoning from\n"
        "the end user, do it in your code (generate CoT, then strip it before\n"
        "displaying, as in `reason_then_hide_correctly`) -- don't ask the model\n"
        "to reason 'silently'. A strong model can sometimes fake silent reasoning\n"
        "on an easy problem by doing the arithmetic in one forward pass, but that\n"
        "spare capacity runs out as the problem gets harder -- visible CoT (hidden\n"
        "in your code, not in the prompt) is the version that keeps working."
    )
