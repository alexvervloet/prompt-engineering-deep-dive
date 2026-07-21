"""
optimize.py: the capstone: prove a prompt change actually helped.

Every lesson in this repo shows a *naive* prompt next to a *tuned* one and argues
the tuned version is better. This capstone stops arguing and **measures it**: it
runs both prompts over a small labeled set, scores each output, and tells you
which prompt won, and by how much. That's the whole discipline of prompt
engineering in one tool: change the prompt, run the numbers, keep the change only
if the number goes up. (It's also the bridge to the Evals deep dive, which is this
idea at full scale.)

Run it (uses your configured PROVIDER, making small, real API calls):

    # Compare the built-in naive vs tuned prompt on the support-ticket priority task:
    secrun python hands_on/optimize.py

    # A different built-in task (sentiment classification):
    secrun python hands_on/optimize.py --task sentiment

    # Show the cases each prompt got wrong:
    secrun python hands_on/optimize.py --show-misses

    # Bring your own: two prompt files + a JSONL of {"text","expected"} rows:
    secrun python hands_on/optimize.py --prompt-a naive.txt --prompt-b tuned.txt --data cases.jsonl

The one idea: a prompt isn't "better" because it reads better. It's better
because it *scores* better on cases you care about. Read the source: `evaluate()`
is the whole loop (run a prompt over the cases, score each, average), and
`compare()` prints the verdict.
"""

import argparse
import json
import os
import sys
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rich.console import Console
from rich.table import Table

from common import chat, describe, ensure_ready

console = Console()


# --------------------------------------------------------------------------
# A task = an instruction, two prompts to compare, and a labeled set of cases.
# The score is a tolerant label match: we win if the expected label appears as
# a word in the model's reply (so "Positive." or "positive sentiment" still pass).
# --------------------------------------------------------------------------
@dataclass
class Case:
    text: str
    expected: str


@dataclass
class Task:
    name: str
    naive: str
    tuned: str
    cases: list[Case]


def score(output: str, expected: str) -> bool:
    """Tolerant exact-ish match: is the expected label a word in the output?

    Markdown decoration (*, #, `) is stripped before matching; it's chrome,
    not signal, and shouldn't count for or against either prompt. A compound
    hedge like "Mixed/Negative" still fails to match "Mixed": refusing to
    commit to one label is a real failure, not a formatting artifact.
    """
    cleaned = output.replace("*", " ").replace("#", " ").replace("`", " ")
    words = {w.strip(".,!?:;\"'()").lower() for w in cleaned.split()}
    return expected.lower() in words


# --- Built-in task 1: sentiment (the running example from fundamentals/01) ---
SENTIMENT = Task(
    name="sentiment",
    naive="Classify the sentiment of the review.",
    tuned=(
        "You classify product-review sentiment.\n"
        "Reply with EXACTLY one word: Positive, Negative, or Mixed.\n"
        "Use Mixed when the review has both clear praise and clear complaints.\n"
        "No explanation, no punctuation, just the label."
    ),
    cases=[
        Case("This laptop is fast, light, and the screen is stunning. Love it.", "Positive"),
        Case("Stopped charging after two weeks and support ghosted me.", "Negative"),
        Case("Great camera but the battery is genuinely terrible.", "Mixed"),
        Case("Exactly what I needed and it arrived a day early.", "Positive"),
        Case("It works, I guess, but it's wildly overpriced for what it does.", "Negative"),
        Case("Beautiful design, though the app crashes constantly.", "Mixed"),
    ],
)

# --- Built-in task 2: support-ticket priority (mirrors examples/06) ---
PRIORITY = Task(
    name="priority",
    naive="What priority is this support ticket?",
    tuned=(
        "You triage support tickets into a priority for routing.\n"
        "Reply with EXACTLY one word: Low, Medium, High, or Urgent.\n"
        "  Urgent  - the product is down or data is at risk, RIGHT NOW.\n"
        "  High    - a paying customer is blocked but has a workaround.\n"
        "  Medium  - a real problem that isn't blocking work.\n"
        "  Low     - a question, suggestion, or cosmetic nit.\n"
        "Output only the label."
    ),
    cases=[
        Case("The whole site is down and none of our team can log in.", "Urgent"),
        Case("Billing charged me twice; I need a refund but can still work.", "High"),
        Case("The export button is misaligned on the settings page.", "Low"),
        Case("Reports load, but they're missing last week's data.", "Medium"),
        Case("How do I invite a teammate to my workspace?", "Low"),
        Case("Production API has been returning 500s for an hour.", "Urgent"),
    ],
)

BUILTIN = {t.name: t for t in (SENTIMENT, PRIORITY)}


def evaluate(system: str, cases: list[Case]) -> tuple[float, list[tuple[Case, str, bool]]]:
    """Run one prompt over every case; return its accuracy and per-case results."""
    results = []
    for case in cases:
        output = chat(
            [{"role": "system", "content": system}, {"role": "user", "content": case.text}],
            temperature=0,
            max_tokens=16,
        ).strip()
        results.append((case, output, score(output, case.expected)))
    accuracy = sum(1 for _, _, passed in results if passed) / len(results) if results else 0.0
    return accuracy, results


def compare(task: Task, show_misses: bool) -> None:
    console.print(f"\n[bold]Task:[/bold] {task.name}   [dim]({describe()})[/dim]\n")

    acc_a, results_a = evaluate(task.naive, task.cases)
    acc_b, results_b = evaluate(task.tuned, task.cases)

    table = Table(title=f"Naive vs tuned prompt over {len(task.cases)} labeled cases")
    table.add_column("Prompt")
    table.add_column("Accuracy", justify="right")
    table.add_column("Correct", justify="right")
    table.add_row("A · naive", f"{acc_a:.0%}", f"{sum(p for *_, p in results_a)}/{len(task.cases)}")
    table.add_row("B · tuned", f"{acc_b:.0%}", f"{sum(p for *_, p in results_b)}/{len(task.cases)}")
    console.print(table)

    delta = acc_b - acc_a
    if delta > 0:
        console.print(f"\n[bold green]Prompt B (tuned) wins[/bold green] by {delta:+.0%}.")
    elif delta < 0:
        console.print(f"\n[bold red]Prompt B (tuned) is worse[/bold red] by {delta:+.0%}. Don't ship it.")
    else:
        console.print("\n[bold yellow]A tie[/bold yellow] on this set; try harder cases before deciding.")

    if show_misses:
        for label, results in (("A · naive", results_a), ("B · tuned", results_b)):
            misses = [(c, out) for c, out, passed in results if not passed]
            if misses:
                console.print(f"\n[dim]{label} missed:[/dim]")
                for case, out in misses:
                    console.print(f"  expected [green]{case.expected}[/green], got "
                                  f"[red]{out!r}[/red]  ←  {case.text[:60]}")

    console.print(
        "\n[dim]The lesson: the tuned prompt isn't better because it reads better, "
        "it's better because it scored better. Measure, don't argue.[/dim]"
    )


def load_custom(prompt_a: str, prompt_b: str, data: str) -> Task:
    """Bring-your-own: two prompt files and a JSONL of {'text','expected'} rows."""
    with open(prompt_a, encoding="utf-8") as f:
        naive = f.read().strip()
    with open(prompt_b, encoding="utf-8") as f:
        tuned = f.read().strip()
    cases = []
    with open(data, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            cases.append(Case(row["text"], str(row["expected"])))
    if not cases:
        sys.exit(f"No cases found in {data} (expected JSONL with 'text' and 'expected').")
    return Task(name=os.path.basename(data), naive=naive, tuned=tuned, cases=cases)


def main() -> int:
    parser = argparse.ArgumentParser(description="A/B-compare two prompts on a labeled set.")
    parser.add_argument("--task", choices=sorted(BUILTIN), default="priority",
                        help="which built-in task to run (default: priority)")
    parser.add_argument("--show-misses", action="store_true", help="print the cases each prompt got wrong")
    parser.add_argument("--prompt-a", help="a prompt file (the baseline) for a custom task")
    parser.add_argument("--prompt-b", help="a prompt file (the candidate) for a custom task")
    parser.add_argument("--data", help="a JSONL file of {'text','expected'} rows for a custom task")
    args = parser.parse_args()

    ensure_ready()

    custom = (args.prompt_a, args.prompt_b, args.data)
    if any(custom):
        if not all(custom):
            sys.exit("Custom mode needs all of --prompt-a, --prompt-b, and --data.")
        task = load_custom(*custom)
    else:
        task = BUILTIN[args.task]

    compare(task, show_misses=args.show_misses)
    return 0


if __name__ == "__main__":
    sys.exit(main())
