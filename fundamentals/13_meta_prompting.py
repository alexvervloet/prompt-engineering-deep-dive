"""
13 - META-PROMPTING (USE THE MODEL TO IMPROVE THE PROMPT)

A surprisingly effective trick: when a prompt underperforms, don't hand-tune it for
an hour: ask the model to REWRITE it. The model knows the techniques in this repo
(clear instructions, output format, role, edge cases) and can apply them to your
draft. This is "meta-prompting": a prompt whose job is to produce a better prompt.

This file:
  1. Starts with a weak, vague prompt.
  2. Runs it, and you see a mediocre result.
  3. Asks the model to rewrite the prompt using prompt-engineering best practices.
  4. Runs the REWRITTEN prompt and compares.

KEY IDEAS
  - The meta-prompt should ask for a *reusable* prompt (with a slot for the input),
    not an answer to the specific example; otherwise you just get one output.
  - Give the meta-prompt a rubric: role, explicit steps, output format, how to
    handle missing info. You're telling the model what "good" looks like.
  - Great for bootstrapping: generate a strong first draft, then refine by hand.
    Also pairs with evals (repo #5): let the model propose variants, score them.

Run:  secrun python fundamentals/13_meta_prompting.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import chat, header, rule

# A deliberately weak prompt for a real task.
WEAK_PROMPT = "Summarize this."

SAMPLE_INPUT = (
    "Our Q3 outage lasted 47 minutes after a bad config push to the auth service. "
    "About 12% of users couldn't log in. We rolled back in 30 minutes, then spent 17 "
    "more restoring cache warmth. Root cause: a missing staging check. Action items: "
    "add a canary deploy, require staging sign-off, and alert on auth error-rate spikes."
)

META_PROMPT = f"""You are a prompt engineer. Rewrite the weak prompt below into a strong,
REUSABLE prompt template for the task, applying best practices:
  - assign a clear role and audience,
  - give explicit instructions and any needed steps,
  - specify the exact output format and length,
  - say how to handle missing or ambiguous information,
  - use a placeholder like {{input}} where the user's text goes.

Return ONLY the improved prompt template (no commentary).

Weak prompt:
\"\"\"{WEAK_PROMPT}\"\"\""""


def run_prompt(prompt_template: str, text: str) -> str:
    # Templates from the model may use {input} or literally include the text slot.
    filled = prompt_template.replace("{input}", text)
    if text not in filled:  # no placeholder -> append the input explicitly
        filled = f'{prompt_template}\n\nText:\n"""{text}"""'
    return chat([{"role": "user", "content": filled}], temperature=0.3)


if __name__ == "__main__":
    header("META-PROMPTING: LET THE MODEL IMPROVE THE PROMPT")

    print("\n[1] Weak prompt ->", repr(WEAK_PROMPT))
    print("\n[Result with the weak prompt] ->")
    print(run_prompt(WEAK_PROMPT, SAMPLE_INPUT))

    rule()
    print("\n[2] Asking the model to rewrite the prompt...\n")
    improved = chat([{"role": "user", "content": META_PROMPT}], temperature=0.4).strip()
    print(improved)

    rule()
    print("\n[Result with the IMPROVED prompt] ->")
    print(run_prompt(improved, SAMPLE_INPUT))

    rule()
    print(
        "\nTakeaway: the model can apply prompt-engineering principles to your own\n"
        "drafts. Use meta-prompting to bootstrap a strong template, then refine by\n"
        "hand and (ideally) score variants with an eval set."
    )
