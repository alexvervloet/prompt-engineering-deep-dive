"""
11 - ReAct (REASON + ACT)
=========================

ReAct interleaves *reasoning* and *acting*: instead of answering in one shot, the
model alternates Thought -> Action -> Observation until it has enough to answer.
It's the prompting pattern under most "agents" — and you can do it with nothing but
a prompt and a parse loop, which is exactly what this file shows.

The loop, driven entirely by prompting:
  1. You describe the available ACTIONS (tools) and the strict output format.
  2. The model writes a `Thought:` then an `Action: tool[input]`.
  3. YOU stop generation at that point, run the tool, and feed back `Observation:`.
  4. Repeat until the model writes `Answer:` instead of an Action.

KEY IDEAS
  - The model can't actually *do* anything — it emits a request to act, you act,
    you hand back the result. Same control split as real tool use.
  - A `stop` sequence ("Observation:") is what hands control back to your code at
    the right moment — without it the model hallucinates its own observations.
  - Grounding each step in a real Observation is what stops the model from making
    up facts: it reasons over data it actually fetched, not its memory.
  - The `tool[input]` regex only enforces the outer syntax — it does NOT validate
    that `input` is in a format the tool understands (e.g. `lookup[height of the
    Eiffel Tower]` parses fine but won't match the FACTS dict key below). Real
    tool-calling systems fix this with schema-validated structured arguments
    instead of free-text regex parsing.

Run:  secrun python fundamentals/11_react.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re

from common import chat, header, rule

# --- The "tools" the model may ask us to run. Real apps hit APIs/DBs; we fake
# them so the example is self-contained and free of dependencies. ---
FACTS = {
    "eiffel tower height": "330 meters",
    "speed of light": "299,792,458 meters per second",
    "great wall length": "21,196 kilometers",
}


def tool_lookup(query: str) -> str:
    return FACTS.get(query.strip().lower(), "no entry found")


def tool_calc(expr: str) -> str:
    # eval is fine here ONLY because we restrict to arithmetic chars.
    if not re.fullmatch(r"[\d\s+\-*/().]+", expr):
        return "error: only arithmetic allowed"
    try:
        return str(eval(expr))  # noqa: S307 - sandboxed by the regex above
    except Exception as e:
        return f"error: {e}"


TOOLS = {"lookup": tool_lookup, "calc": tool_calc}

SYSTEM = """You answer questions using a strict ReAct loop. On each turn, output EITHER:

  Thought: <your reasoning>
  Action: <tool>[<input>]

...where <tool> is one of: lookup (look up a fact), calc (evaluate arithmetic).
OR, when you have enough information, output:

  Thought: <your reasoning>
  Answer: <final answer>

Use exactly one Action per turn and then STOP. Do not write 'Observation:' yourself."""


def react(question: str, max_steps: int = 5) -> str:
    transcript = f"Question: {question}\n"
    for step in range(max_steps):
        # Stop at "Observation:" so the model can't invent the tool's result.
        reply = chat(
            [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": transcript},
            ],
            temperature=0,
            stop=["Observation:"],
        ).strip()
        print(reply)
        transcript += reply + "\n"

        if "Answer:" in reply:
            return reply.split("Answer:", 1)[1].strip()

        # Parse the requested action: tool[input]
        m = re.search(r"Action:\s*(\w+)\[(.*?)\]", reply, re.DOTALL)
        if not m:
            return "(stopped: no valid Action and no Answer)"
        tool, arg = m.group(1).lower(), m.group(2)
        observation = TOOLS.get(tool, lambda _: "error: unknown tool")(arg)
        print(f"Observation: {observation}\n")
        transcript += f"Observation: {observation}\n"

    return "(stopped: hit the step limit)"


if __name__ == "__main__":
    header("ReAct — REASON + ACT")
    question = (
        "How many meters taller is the Eiffel Tower than a 100-meter building, doubled?"
    )
    print(f"\nQuestion: {question}\n")
    rule()
    answer = react(question)
    rule()
    print(f"\nFinal answer -> {answer}")
    print(
        "\nTakeaway: 'agents' are mostly this loop. The model proposes an action,\n"
        "your code runs it and returns the result, and a stop sequence hands control\n"
        "back at the right moment. Reasoning grounded in real observations beats\n"
        "reasoning from memory."
    )
