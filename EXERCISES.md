# Exercises: make the learning stick

Reading code teaches you less than *predicting* what it will do and then checking.
This file turns each lesson of the [README](README.md) into a few quick
active-recall prompts.

How to use it: work the lesson first, then come back. **Commit to an answer before
you run or reveal.** The prediction is where the learning happens, even
(especially) when you're wrong. Answers are hidden behind ▸ toggles.

> Every lesson here makes a small, real API call (against your `PROVIDER`, or a
> free local model). There's no offline mode; the point is to *watch* prompts
> change behavior.

---

## Fundamentals

### 01: Zero-shot

**Predict.** Same model, same review. The vague prompt asks "what do you think of
this review?"; the tuned one says "Respond with exactly one word: Positive,
Negative, or Mixed." Which output can your code branch on without post-processing,
and why?

<details><summary>▸ Answer</summary>

The tuned one. Constraining the label set *and* the format turns the reply into a
single token you can compare; the vague prompt returns prose you'd have to parse.
Clarity beats cleverness, and "state the output format" is the cheapest win in the
whole repo.
</details>

### 02: Few-shot

**Recall.** You want the model to emit `billing|high` (a format it would never
produce on its own). Cheaper to write a paragraph of rules, or show three
examples? What two things do the examples teach at once?

<details><summary>▸ Answer</summary>

Show examples. 2–5 demonstrations teach the *format* (`category|priority`) **and**
your *conventions* (what counts as "high") far more cheaply than a rulebook. Keep
the formatting identical across examples; the model copies what it sees.
</details>

### 03: Chain-of-thought

**Predict.** On a multi-step word problem, does "think step by step" help more on
an easy arithmetic question or a multi-constraint one? What's the cost you pay for
the accuracy?

<details><summary>▸ Answer</summary>

It helps most on multi-step problems, where one-shot answers skip a step. The cost
is tokens (and latency) for the reasoning, and on a *reasoning* model it can even
hurt (lesson 14). Give room to think where the task needs it, not everywhere.
</details>

### 04: Role prompting

**Recall.** "You are a patient kindergarten teacher" vs. "You are a terse senior
SRE." Name two things the role changes about the answer beyond vocabulary.

<details><summary>▸ Answer</summary>

Depth/assumed background (what it explains vs. takes for granted) and tone/length.
A role is a compact way to set audience + expertise without spelling out a dozen
style rules.
</details>

### 05: System prompts

**Recall.** What belongs in the system prompt vs. the user message, and why is the
system prompt called "your most powerful lever"?

<details><summary>▸ Answer</summary>

Durable behavior (role, rules, output format, fallback) goes in the system prompt;
the specific input goes in the user turn. It's set once and steers every turn, so a
single good system prompt fixes a whole class of outputs.
</details>

### 06: Structured output

**Predict.** Three levels: ask for JSON, `json=True`, and `structured(schema=...)`.
Which guarantees valid JSON *syntax*, and which guarantees your exact *fields and
types*? Why still wrap `json.loads` in try/except?

<details><summary>▸ Answer</summary>

`json=True` forces valid JSON syntax (response_format on OpenAI, an assistant
prefill on Claude); `structured()` forces the schema (strict `json_schema` on
OpenAI, a forced tool call on Claude). You still parse defensively because a local
model: or any future change, can surprise you; never trust bytes blindly.
</details>

### 07: Delimiters & grounding

**Recall.** Why wrap the document in triple quotes and say "answer only from the
text between them"? What attack does this start to defend against?

<details><summary>▸ Answer</summary>

It separates *instructions* from *data* so the model doesn't treat the document's
contents as commands, the first and weakest line of defense against prompt injection
(see the Prompt Injection deep dive for why it's necessary but not sufficient).
</details>

### 08: Prompt chaining

**Predict.** One prompt does "summarize, critique, and rewrite" in a single shot;
a chain does each as its own call. Which produces a better final draft, and what
do you gain operationally by splitting it?

<details><summary>▸ Answer</summary>

The chain usually wins: each step is simpler, so the model does it better, and you
can inspect/validate between steps. The cost is more calls (more tokens, more
latency). Decompose when one mega-prompt is juggling too much.
</details>

### 09: Self-consistency

**Predict.** You sample the same problem five times at temperature 0.8 and take the
majority vote. Why must temperature be > 0, and on what kind of task does voting
help most?

<details><summary>▸ Answer</summary>

At temperature 0 the samples are (near) identical, so there's nothing to vote
over. Voting helps on problems with one correct answer but many reasoning paths
(math, a single extracted fact): the wrong paths scatter, the right one clusters.
It costs N× the tokens, so spend it where correctness matters.
</details>

### 10: Decoding parameters

**Recall.** Match the task to temperature: extraction, brainstorming, code edits.
Which knob bounds cost and which is OpenAI-only?

<details><summary>▸ Answer</summary>

Extraction/code → temperature 0; brainstorming → 0.7–1.0. `max_tokens` bounds
cost/latency. `seed` (reproducible sampling) is OpenAI-only; Claude's temperature
range is 0–1 (not 0–2). Tune temperature *or* top_p, not both.
</details>

### 11: ReAct

**Predict.** The loop sets `stop=["Observation:"]`. What breaks if you remove that
stop sequence? Who actually runs the tool, the model or your code?

<details><summary>▸ Answer</summary>

Without the stop, the model writes its *own* fake `Observation:` and reasons over
hallucinated data. The stop hands control back to your code at the right moment;
*you* run the tool and feed the real result back. That control split is exactly how
real tool use / agents work.
</details>

### 12: Reflexion

**Recall.** How is Reflexion stronger than plain "critique your answer"? What makes
the feedback trustworthy?

<details><summary>▸ Answer</summary>

Reflexion grounds the retry in a *real check* (run the code, test the result), not
the model's opinion of its own work. Attempt → verify → reflect on the actual
failure → retry. Feedback grounded in reality beats self-graded vibes.
</details>

### 13: Meta-prompting

**Do.** Take your weakest prompt from a real project, paste it into the
meta-prompting lesson's pattern, and ask the model to rewrite it. Did it add a
role, a format, or a fallback you'd omitted?

<details><summary>▸ Answer</summary>

Usually all three. The model is good at spotting the missing "what does good look
like?" scaffolding. Meta-prompting is a fast first draft; you still measure the
result (the capstone) rather than assume the rewrite is better.
</details>

### 14: Reasoning models

**Predict.** On a reasoning model (o-series, Claude thinking), does adding "think
step by step" and worked examples help or hurt? How do you control depth instead?

<details><summary>▸ Answer</summary>

It often *hurts*. The model already reasons internally, so the scaffolding is
redundant and can box in its process. Give the goal + constraints + "what good
looks like," then control depth with the model's effort/reasoning setting, not a
longer prompt.
</details>

---

## Use-case examples: naive vs optimized

Each `examples/*.py` shows a weak prompt next to a tuned one for a real task. The
recall prompt is the same every time, because the *method* is: **name the specific
change and why it helps.**

**Recall (support reply, `01`).** Name two things the optimized prompt adds that
keep the reply on-policy and on-brand.

<details><summary>▸ Answer</summary>

A system prompt with policy constraints + tone, and an explicit fallback for "I
can't do that" cases, so the model refuses gracefully instead of improvising a
promise the business can't keep.
</details>

**Predict (extraction `02`, classification `06`).** Both force JSON with
`json=True` and a closed schema/label set. What does the `null`/`other` escape
hatch buy you that "just guess" doesn't?

<details><summary>▸ Answer</summary>

It separates *absent* from *guessed*. A `null` field or an `other` label (plus a
confidence score) routes the uncertain cases to a human instead of silently
emitting a confident-looking wrong answer your code then trusts.
</details>

**Recall (summarization `04`, code review `03`, text-to-SQL `05`).** Pick one.
Which single prompt ingredient most changes its output quality: audience, rubric,
or schema grounding?

<details><summary>▸ Answer</summary>

Summarization → **audience** (a TL;DR for an exec vs. an engineer differ entirely).
Code review → **rubric + severity** (so it flags what matters, consistently).
Text-to-SQL → **schema grounding** (the model can't query tables it can't see).
Each is the "context/constraints" rung of the mental model doing the heavy lifting.
</details>

---

## Capstone: `optimize.py`

**Predict.** You run `secrun python hands_on/optimize.py`. The tuned sentiment prompt
*reads* far better than the naive one. Does that guarantee it scores higher? What
would make you *not* ship it?

<details><summary>▸ Answer</summary>

No. A nicer-reading prompt can score the same or worse on real cases. You ship it
only if its accuracy actually beats the baseline on the labeled set; a tie or a
regression means keep iterating. "Reads better" is a hypothesis; the score is the
test.
</details>

**Do.** Add two hard cases to a built-in task (edit `SENTIMENT.cases`), say a
sarcastic review and a backhanded compliment, then rerun with `--show-misses`.
Which prompt cracks under the harder set?

<details><summary>▸ Answer</summary>

Often the naive prompt's accuracy falls fastest, because the tuned prompt's "use
Mixed when there's both praise and complaint" rule was written for exactly those
edge cases. Hard cases are where prompt quality separates, which is why a good
test set is mostly edge cases.
</details>

**Stretch.** Write your own task: a `cases.jsonl` of `{"text","expected"}` rows and
two prompt files, then run `optimize.py --prompt-a naive.txt --prompt-b tuned.txt
--data cases.jsonl`. The first time it tells you your "better" prompt was actually
worse, the discipline has clicked, and you're ready for the
[Evals deep dive](https://github.com/alexvervloet/evals-deep-dive), which is this idea at
full scale.

---

### Where to take it next

Invent your own. Take a prompt you actually use, write ten honest labeled cases,
and measure a change instead of eyeballing it. Prompt engineering is empirical:
change one thing, run the number, keep it only if it went up.
