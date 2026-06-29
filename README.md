# Prompt Engineering — A Guided Deep Dive

A hands-on playground for learning prompt engineering **from the basics** —
zero/few-shot, chain-of-thought, roles, structured output — through to optimized
prompts for real use cases, and finally to the discipline that separates a guess
from a result: **measuring** that a prompt change actually helped. Every concept
is a small, runnable Python script you read, run, and tweak. No framework magic —
just enough code to *see* how each idea changes what the model does.

This is the third of eight core repos in the series. The first two teach the API
call ([OpenAI](https://github.com/Ailuue/openai-api-deep-dive),
[Claude](https://github.com/Ailuue/claude-api-deep-dive)); this one teaches you to
get more out of that same call by asking better.

Like its siblings, it's meant to be *walked through*, not just read. Each script
prints a **before/after** so you can see the effect, and [EXERCISES.md](EXERCISES.md)
has a predict-then-run prompt for each lesson.

---

## 0. The one big idea

> **The model is fixed; the prompt is the program. You don't touch the weights —
> you change what you ask and how, and that is most of the quality you'll ever
> get.**

Everything below is a variation on that. Zero/few-shot is *how many examples* you
show; chain-of-thought is *giving room to think*; roles and system prompts are
*who the model is and what the rules are*; structured output is *the exact shape of
the answer*. None of it changes the model — it changes the request. And the last
step, the capstone, is the habit that makes it real: **measure** the change instead
of trusting that the new prompt "reads better."

---

## 1. Setup (5 minutes)

```bash
# 1. Create an isolated Python environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Choose your provider and add your key
cp .env.example .env
#    ...then open .env. Set PROVIDER to "openai" or "claude" and paste the key.

# 4. Confirm everything is wired up (makes no API call, costs nothing)
python check_setup.py
```

Prompt engineering is provider-agnostic, so this repo is too — pick whichever stack
you set up in the sibling repos with `PROVIDER` in `.env`:

| `PROVIDER` | Chat model | Key needed |
|------------|-----------|------------|
| `openai` (default) | OpenAI `gpt-4o-mini` | `OPENAI_API_KEY` |
| `claude` | Claude `claude-haiku-4-5` | `ANTHROPIC_API_KEY` |

The only file that knows which provider you picked is
[common/providers.py](common/providers.py); every lesson is pure prompting. Because
the OpenAI stack uses the OpenAI SDK, it also reaches **any OpenAI-compatible local
server** (Ollama, LM Studio, llama.cpp, vLLM) — keep `PROVIDER=openai` and set
`OPENAI_BASE_URL` to the local endpoint. So the same lessons run against hosted
OpenAI, hosted Claude, or a model on your laptop, for free.

> 💡 **No offline mode here.** Unlike most sibling repos, every lesson makes a
> small, real call — the whole point is to *watch* a prompt change the output. The
> calls are cheap (a fraction of a cent each), or free against a local model.

---

## 2. The fundamentals — the core techniques

Each file is a self-contained before/after. Run them in order.

```bash
python fundamentals/01_zero_shot.py
```

| File | Technique | One-line idea |
|------|-----------|---------------|
| [01_zero_shot.py](fundamentals/01_zero_shot.py) | Zero-shot | Ask clearly, constrain the output — no examples. |
| [02_few_shot.py](fundamentals/02_few_shot.py) | Few-shot | Teach format & conventions with 2–5 examples. |
| [03_chain_of_thought.py](fundamentals/03_chain_of_thought.py) | Chain-of-thought | Let the model reason step by step before answering. |
| [04_role_prompting.py](fundamentals/04_role_prompting.py) | Role / persona | Assign expertise + audience to steer tone & depth. |
| [05_system_prompts.py](fundamentals/05_system_prompts.py) | System prompts | Set durable behavior: role, rules, format, fallback. |
| [06_structured_output.py](fundamentals/06_structured_output.py) | Structured output | Force machine-readable JSON (`json=True` / a schema). |
| [07_delimiters_and_context.py](fundamentals/07_delimiters_and_context.py) | Delimiters & grounding | Separate instructions from data; answer only from context. |
| [08_prompt_chaining.py](fundamentals/08_prompt_chaining.py) | Prompt chaining | Decompose into a pipeline; generate→critique→revise. |
| [09_self_consistency.py](fundamentals/09_self_consistency.py) | Self-consistency | Sample N times and majority-vote for accuracy. |
| [10_parameters.py](fundamentals/10_parameters.py) | Decoding params | temperature, top_p, max_tokens, seed, stop. |
| [11_react.py](fundamentals/11_react.py) | ReAct | Interleave Thought→Action→Observation; the pattern under "agents". |
| [12_reflexion.py](fundamentals/12_reflexion.py) | Reflexion | Attempt→verify→reflect→retry against a real check, not vibes. |
| [13_meta_prompting.py](fundamentals/13_meta_prompting.py) | Meta-prompting | Use the model to rewrite a weak prompt into a strong one. |
| [14_reasoning_models.py](fundamentals/14_reasoning_models.py) | Reasoning models | Drop the "think step by step" scaffolding; give goal + constraints. |

---

## 3. The use cases — optimizing prompts for real tasks

Each shows a **naïve prompt vs an optimized prompt** for a real job, and explains
*why* every change helps.

```bash
python examples/03_code_review.py
```

| File | Use case | Techniques combined |
|------|----------|---------------------|
| [01_customer_support_reply.py](examples/01_customer_support_reply.py) | Support email responder | system prompt · policy constraints · tone · fallback |
| [02_data_extraction.py](examples/02_data_extraction.py) | Unstructured text → typed JSON | schema · normalization · null policy · `json=True` |
| [03_code_review.py](examples/03_code_review.py) | Security-aware code review | persona · rubric · severity · fixed format |
| [04_summarization.py](examples/04_summarization.py) | Audience-targeted TL;DR | audience · length limits · focus · grounding |
| [05_text_to_sql.py](examples/05_text_to_sql.py) | Natural language → SQL | schema grounding · dialect · safety · few-shot |
| [06_classification.py](examples/06_classification.py) | Ticket routing / classification | closed label set · 'other' escape hatch · confidence · few-shot edges |

---

## 4. The mental model (cheat sheet)

A reliable prompt usually answers these questions for the model:

1. **Role** — who are you? (persona / expertise)
2. **Task** — what exactly should you do?
3. **Context** — what information do you have? (clearly delimited)
4. **Constraints** — what are the hard rules / what must you not do?
5. **Format** — exactly how should the output be structured?
6. **Examples** — what does a good answer look like? (if needed)
7. **Fallback** — what to do when you can't comply or don't know?

General heuristics:

- **Be specific.** Vagueness is the #1 cause of bad output.
- **Show, don't just tell.** Examples lock in format and conventions cheaply.
- **Give room to think** on hard problems; **hide the reasoning** if the end user
  doesn't need it.
- **Constrain the output** when code will parse it, and still parse defensively.
- **Match temperature to the task:** `0` for extraction/classification/code,
  higher for creative work.
- **Iterate.** Prompt engineering is empirical — change one thing, observe, repeat.

---

## 5. The capstone: `optimize.py`

Everything points here. Every lesson *argues* a tuned prompt beats a naive one;
the capstone stops arguing and **measures it** — it runs both prompts over a small
labeled set, scores each, and tells you which won and by how much. That's the whole
discipline in one tool, and the bridge to the [Evals deep dive](https://github.com/Ailuue/evals-deep-dive).

```bash
# Compare the built-in naive vs tuned prompt on a sentiment task:
python hands_on/optimize.py

# A different built-in task (support-ticket priority), showing the misses:
python hands_on/optimize.py --task priority --show-misses

# Bring your own: two prompt files + a JSONL of {"text","expected"} rows:
python hands_on/optimize.py --prompt-a naive.txt --prompt-b tuned.txt --data cases.jsonl
```

Read [hands_on/optimize.py](hands_on/optimize.py): `evaluate()` is the whole loop
(run a prompt over the cases, score each, average) and `compare()` prints the
verdict. **Suggested exercise:** add two hard cases (a sarcastic review, a
backhanded compliment) and rerun — watch which prompt cracks. The first time it
tells you your "better" prompt was actually *worse*, prompt engineering has clicked.

---

## Notes & costs

- Running a script makes real API calls. Against a hosted API this costs a fraction
  of a cent each; against a local model it's free.
- `09_self_consistency.py`, `10_parameters.py`, and the capstone make several calls
  each by design (they sample or score multiple times).
- Never commit your `.env` — it's already in `.gitignore`.

---

## Where to go next

You've learned to shape a single call. The series builds outward from here:

- **Ground it in your data** — when the model needs facts it doesn't have, retrieve
  the right text and put it in the context. → [RAG](https://github.com/Ailuue/rag-deep-dive)
- **Measure it at scale** — the capstone is a tiny eval; the real discipline (judges,
  metrics, significance, CI gates) is its own dive. → [Evals](https://github.com/Ailuue/evals-deep-dive)
- **Let it act** — ReAct (lesson 11) by hand is the seed of an agent loop with real
  tools. → [Agents](https://github.com/Ailuue/agents-deep-dive)
- **Harden it** — delimiters (lesson 07) are the first, weakest injection defense;
  the real defense-in-depth is its own dive. → [Prompt Injection & Guardrails](https://github.com/Ailuue/prompt-injection-deep-dive)
- **Reasoning models** — lesson 14 is the start; prompting o-series / extended
  thinking well is a growing skill.

---

## From teaching code to production

Every lesson here optimizes one prompt in isolation. Production is about operating
prompts like the code they are:

| This repo's teaching shortcut | In production |
|-------------------------------|---------------|
| The prompt is a string literal in the script | A **versioned prompt** behind config, promoted only past an **eval gate** |
| You eyeball the before/after | The capstone's compare, run as a **CI gate** that blocks a quality regression |
| `chat()` is called bare | The call wrapped in **retries + backoff**, a **budget**, and a **response cache** |
| You trust the model's output shape | **Schema validation** (`structured()`) + **guardrails** on every request |
| One prompt, one model, by hand | A **prompt registry** with staged rollouts, A/B tested on live traffic |

These shortcuts are right for learning and wrong for production. All of those
concerns — observability, cost, reliability, caching, guardrails, prompt
versioning, and eval gates — are built from scratch and wired into one running app
in **[Production](https://github.com/Ailuue/ai-in-production-deep-dive)** (#8 in the
series). It runs **offline on a mock provider**, so you can see the whole ops
machinery with no key and no cost.

---

## File map

```
check_setup.py              ← run first: verifies Python, packages, provider, key
README.md                   ← this guide
EXERCISES.md                ← predict-then-run prompts, one per lesson
common/                     ← shared plumbing (read providers.py!)
  providers.py              ← the ONLY provider-specific file: chat / chat_stream / structured
  display.py                ← tiny terminal helpers (header, rule)
fundamentals/               ← the core techniques (run in order)
  01_zero_shot.py … 14_reasoning_models.py
examples/                   ← naïve-vs-optimized prompts for 6 real use cases
  01_customer_support_reply.py … 06_classification.py
hands_on/
  optimize.py               ← capstone: A/B-compare two prompts on a labeled set
```

---

## Troubleshooting

Run `python check_setup.py` first — it catches most problems. Then, by symptom:

| What you see | What it means / the fix |
|--------------|-------------------------|
| `PROVIDER=... needs ... in .env` | The active stack is missing its key. Set `PROVIDER` and the matching key in `.env`. |
| `ModuleNotFoundError` (openai / anthropic / rich) | Dependencies aren't installed or the venv isn't active. `source .venv/bin/activate` then `pip install -r requirements.txt`. |
| `AuthenticationError` / 401 | The key is present but wrong — check it matches the `PROVIDER` you set. |
| A JSON lesson prints prose, not JSON | A weaker (often local) model ignored the format. `json=True` / `structured()` help; the lessons also parse defensively. |
| Running against a local model and it's flaky on JSON/ReAct | Small models follow strict formats less reliably — try a more capable one (qwen2.5, llama3.1) or the hosted stack. |
| `SyntaxError` / odd type errors on startup | You're likely on Python 3.9 or older; this repo needs 3.10+. `check_setup.py` confirms your version. |

Still stuck? Every file is small and self-contained — open it, read the docstring
at the top, and run it directly.

---

## The series

This is one of thirteen standalone, hands-on deep dives into building with LLM APIs — eight core, plus five bonus dives.
Each one stands on its own — its own setup, examples, and capstone — and they all
share the same house style: provider-agnostic, built from scratch (no
frameworks), offline-first examples, and a real capstone. Do them in any order;
this sequence builds naturally:

1. [OpenAI API](https://github.com/Ailuue/openai-api-deep-dive) — the API from zero
2. [Claude API](https://github.com/Ailuue/claude-api-deep-dive) — the same ideas, the Anthropic way
3. [Prompt Engineering](https://github.com/Ailuue/prompt-engineering-deep-dive) — shape model behavior with better prompts (zero/few-shot, chain-of-thought, roles)
4. [RAG](https://github.com/Ailuue/rag-deep-dive) — answer questions over your own documents
5. [Evals](https://github.com/Ailuue/evals-deep-dive) — measure whether a change actually helps
6. [Agents](https://github.com/Ailuue/agents-deep-dive) — give a model tools and a loop so it can act
7. [Prompt Injection & Guardrails](https://github.com/Ailuue/prompt-injection-deep-dive) — attack and defend all of the above
8. [Production](https://github.com/Ailuue/ai-in-production-deep-dive) — operate one app end to end: observability, cost, reliability, caching, guardrails, prompt versioning, eval gates

**Bonus dives** — standalone, slotting in where they're most useful:

- [Context Engineering](https://github.com/Ailuue/context-engineering-deep-dive) — manage what's in the window: memory, compaction, assembly
- [Multimodal](https://github.com/Ailuue/multimodal-deep-dive) — images & audio, not just text
- [Fine-tuning](https://github.com/Ailuue/fine-tuning-deep-dive) — teach a model new behavior by example
- [MCP](https://github.com/Ailuue/mcp-deep-dive) — serve tools, data & prompts to any LLM over a standard protocol
- [Local Models](https://github.com/Ailuue/local-models-deep-dive) — run open-weight models on your own machine

**You are here: #3 — Prompt Engineering.**
