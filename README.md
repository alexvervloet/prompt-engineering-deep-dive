# Prompt Engineering: A Guided Deep Dive

A hands-on playground for learning prompt engineering from the basics. Zero-shot and
few-shot, chain-of-thought, roles, structured output, then optimized prompts for real
use cases, and finally the discipline that separates a guess from a result: measuring
that a prompt change actually helped. Every concept is a small runnable Python script
you read, run, and tweak. No framework magic, just enough code to see how each idea
changes what the model does.

This is the third of eight core repos in the series. The first two teach the API call
([OpenAI](https://github.com/alexvervloet/openai-api-deep-dive),
[Claude](https://github.com/alexvervloet/claude-api-deep-dive)). This one teaches you to
get more out of that same call by asking better.

Like its siblings, walk through it rather than reading it. Each script prints a before
and after so you can see the effect, and [EXERCISES.md](EXERCISES.md) has a
predict-then-run prompt for each lesson.

---

## 0. The one big idea

> **The model is fixed. The prompt is the program. You never touch the weights. You
> change what you ask and how you ask it, and that is most of the quality you will ever
> get.**

Everything below is a variation on that. Zero-shot and few-shot are about how many
examples you show. Chain-of-thought is about giving room to think. Roles and system
prompts set who the model is and what the rules are. Structured output pins the exact
shape of the answer. None of it changes the model. It changes the request. And the last
step, the capstone, is the habit that makes it real: measure the change instead of
trusting that the new prompt reads better.

---

## 1. Setup (5 minutes)

```bash
# 1. Create an isolated Python environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Choose your provider (set PROVIDER in .env); your key loads separately
cp .env.example .env
#    Your API key does NOT go in .env. Store it in your OS keychain and run
#    lessons with `secrun`: 2-minute setup in ../docs/SECRETS.md.

# 4. Confirm everything is wired up (makes no API call, costs nothing)
secrun python check_setup.py       # secrun injects your key so the check can see it
```

Prompt engineering is provider-agnostic, so this repo is too. Pick whichever stack you
set up in the sibling repos with `PROVIDER` in `.env`.

| `PROVIDER` | Chat model | Key needed |
|------------|-----------|------------|
| `openai` (default) | OpenAI `gpt-5.4-nano` | `OPENAI_API_KEY` |
| `claude` | Claude `claude-haiku-4-5` | `ANTHROPIC_API_KEY` |

The only file that knows which provider you picked is
[common/providers.py](common/providers.py). Every lesson is pure prompting. Because the
OpenAI stack uses the OpenAI SDK, it also reaches any OpenAI-compatible local server:
Ollama, LM Studio, llama.cpp, vLLM. Keep `PROVIDER=openai` and set `OPENAI_BASE_URL` to
the local endpoint. So the same lessons run against hosted OpenAI, hosted Claude, or a
model on your laptop, for free.

> **No offline mode here.** Unlike most sibling repos, every lesson makes a small real
> call, because the whole point is to watch a prompt change the output. The calls are
> cheap, a fraction of a cent each, or free against a local model.

---

## 2. The core techniques

Each file is a self-contained before and after. Run them in order.

```bash
secrun python fundamentals/01_zero_shot.py
```

| File | Technique | One-line idea |
|------|-----------|---------------|
| [01_zero_shot.py](fundamentals/01_zero_shot.py) | Zero-shot | Ask clearly, constrain the output, no examples. |
| [02_few_shot.py](fundamentals/02_few_shot.py) | Few-shot | Teach format and conventions with two to five examples. |
| [03_chain_of_thought.py](fundamentals/03_chain_of_thought.py) | Chain-of-thought | Let the model reason step by step before answering. |
| [04_role_prompting.py](fundamentals/04_role_prompting.py) | Role / persona | Assign expertise + audience to steer tone & depth. |
| [05_system_prompts.py](fundamentals/05_system_prompts.py) | System prompts | Set durable behavior, meaning role, rules, format, and fallback. |
| [06_structured_output.py](fundamentals/06_structured_output.py) | Structured output | Force machine-readable JSON (`json=True` / a schema). |
| [07_delimiters_and_context.py](fundamentals/07_delimiters_and_context.py) | Delimiters and grounding | Separate instructions from data, and answer only from context. |
| [08_prompt_chaining.py](fundamentals/08_prompt_chaining.py) | Prompt chaining | Break the task into a pipeline: generate, critique, revise. |
| [09_self_consistency.py](fundamentals/09_self_consistency.py) | Self-consistency | Sample N times and majority-vote for accuracy. |
| [10_parameters.py](fundamentals/10_parameters.py) | Decoding params | Sampling-model controls. GPT-5.6 uses reasoning effort instead. |
| [11_react.py](fundamentals/11_react.py) | Classic text ReAct | Thought, action, observation with a stop-compatible model. Prefer native tools in production. |
| [12_reflexion.py](fundamentals/12_reflexion.py) | Reflexion | Attempt, verify, reflect, retry, against a real check rather than vibes. |
| [13_meta_prompting.py](fundamentals/13_meta_prompting.py) | Meta-prompting | Use the model to rewrite a weak prompt into a strong one. |
| [14_reasoning_models.py](fundamentals/14_reasoning_models.py) | Reasoning models | Drop the "think step by step" wrapper and give the goal plus the constraints. |

---

## 3. Optimizing prompts for real tasks

Each one shows a naive prompt against an optimized prompt for a real job, and explains
why every change helps.

```bash
secrun python examples/03_code_review.py
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

A reliable prompt usually answers seven questions for the model.

1. **Role.** Who are you? Persona and expertise.
2. **Task.** What exactly should you do?
3. **Context.** What information do you have, clearly delimited?
4. **Constraints.** What are the hard rules, and what must you not do?
5. **Format.** Exactly how should the output be structured?
6. **Examples.** What does a good answer look like, if examples are needed?
7. **Fallback.** What to do when you can't comply or don't know?

And some general heuristics.

- **Be specific.** Vagueness is the number one cause of bad output.
- **Show rather than tell.** Examples lock in format and conventions cheaply.
- **Give room to think** on hard problems, and hide the reasoning when the end user
  doesn't need it.
- **Constrain the output** when code will parse it, and still parse defensively.
- **Match temperature to the task** on models that support sampling controls. Use `0`
  for extraction, classification, and code, and go higher for creative work. On GPT-5.6,
  omit temperature and set reasoning effort on purpose.
- **Iterate.** Prompt engineering is empirical. Change one thing, observe, repeat.

---

## 5. The capstone: `optimize.py`

Everything points here. Every lesson argues that a tuned prompt beats a naive one. The
capstone stops arguing and measures it. It runs both prompts over a small labeled set,
scores each one, and tells you which won and by how much. That is the whole discipline
in one tool, and the bridge to the
[Evals deep dive](https://github.com/alexvervloet/evals-deep-dive).

```bash
# Compare the built-in naive vs tuned prompt on a sentiment task:
secrun python hands_on/optimize.py

# A different built-in task (support-ticket priority), showing the misses:
secrun python hands_on/optimize.py --task priority --show-misses

# Bring your own: two prompt files + a JSONL of {"text","expected"} rows:
secrun python hands_on/optimize.py --prompt-a naive.txt --prompt-b tuned.txt --data cases.jsonl
```

Read [hands_on/optimize.py](hands_on/optimize.py). `evaluate()` is the whole loop: run
a prompt over the cases, score each, average. `compare()` prints the verdict.
**Suggested exercise:** add two hard cases, a sarcastic review and a backhanded
compliment, then rerun and watch which prompt cracks. The first time it tells you your
"better" prompt was actually worse, prompt engineering has clicked.

---

## Notes & costs

- Running a script makes real API calls. Against a hosted API that costs a fraction of
  a cent each. Against a local model it's free.
- `09_self_consistency.py`, `10_parameters.py`, and the capstone each make several calls
  by design, because they sample or score multiple times.
- Never commit your `.env`. It's already in `.gitignore`.

---

## Where to go next

You've learned to shape a single call. The series builds outward from here.

- **Ground it in your data.** When the model needs facts it doesn't have, retrieve the
  right text and put it in the context.
  → [RAG](https://github.com/alexvervloet/rag-deep-dive)
- **Measure it at scale.** The capstone is a tiny eval. The real discipline, with
  judges, metrics, significance, and CI gates, is its own dive.
  → [Evals](https://github.com/alexvervloet/evals-deep-dive)
- **Let it act.** Classic text ReAct in lesson 11 exposes the loop. Production agents
  use native, schema-validated tools.
  → [Agents](https://github.com/alexvervloet/agents-deep-dive)
- **Harden it.** Delimiters in lesson 07 are the first and weakest injection defense.
  Real defense in depth is its own dive.
  → [Prompt Injection & Guardrails](https://github.com/alexvervloet/prompt-injection-deep-dive)
- **Reasoning models.** Lesson 14 is the start. Prompting the o-series and extended
  thinking well is a growing skill.

---

## From teaching code to production

Every lesson here optimizes one prompt in isolation. Production is about operating
prompts like the code they are.

| This repo's teaching shortcut | In production |
|-------------------------------|---------------|
| The prompt is a string literal in the script | A **versioned prompt** behind config, promoted only past an **eval gate** |
| You eyeball the before/after | The capstone's compare, run as a **CI gate** that blocks a quality regression |
| `chat()` is called bare | The call wrapped in **retries + backoff**, a **budget**, and a **response cache** |
| You trust the model's output shape | **Schema validation** (`structured()`) + **guardrails** on every request |
| One prompt, one model, by hand | A **prompt registry** with staged rollouts, A/B tested on live traffic |

All seven concerns (observability, cost, reliability, caching, guardrails, prompt
versioning, and eval gates) get built from scratch and wired into one running app in
[Production](https://github.com/alexvervloet/ai-in-production-deep-dive), which is #8 in
the series. It runs offline on a mock provider, so you can see the whole ops machinery
with no key and no cost.

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
  01_zero_shot.py ... 14_reasoning_models.py
examples/                   ← naïve-vs-optimized prompts for 6 real use cases
  01_customer_support_reply.py ... 06_classification.py
hands_on/
  optimize.py               ← capstone: A/B-compare two prompts on a labeled set
```

---

## Troubleshooting

Run `secrun python check_setup.py` first. It catches most problems. Then, by symptom:

| What you see | What it means / the fix |
|--------------|-------------------------|
| `PROVIDER=... needs ... in the environment` | Set `PROVIDER` in `.env`, then load the key from your keychain by running under `secrun`. See [SECRETS.md](../docs/SECRETS.md). |
| `ModuleNotFoundError` (openai / anthropic / rich) | Dependencies aren't installed or the venv isn't active. `source .venv/bin/activate` then `pip install -r requirements.txt`. |
| `AuthenticationError` / 401 | The key is present but wrong; check it matches the `PROVIDER` you set. |
| A JSON lesson prints prose instead of JSON | A weaker model, often a local one, ignored the format. `json=True` and `structured()` help, and the lessons also parse defensively. |
| Running against a local model and it's flaky on JSON or ReAct | Small models follow strict formats less reliably, so try a more capable one such as qwen2.5 or llama3.1, or the hosted stack. |
| `SyntaxError` or odd type errors on startup | You're likely on Python 3.9 or older. This repo needs 3.10+, and `check_setup.py` confirms your version. |

Still stuck? Every file is small and self-contained. Open it, read the docstring
at the top, and run it directly.

---

## The series

This is one of the standalone, hands-on deep dives into building with LLM APIs. Eight
core dives, plus the bonus ones listed below. Each one stands on its own, with its own
setup, examples, and capstone, and they all share one house style. Provider-agnostic,
built from scratch with no frameworks, offline-first examples, and a real capstone at
the end. Do them in any order. This sequence builds naturally.

1. [OpenAI API](https://github.com/alexvervloet/openai-api-deep-dive): the API from zero
2. [Claude API](https://github.com/alexvervloet/claude-api-deep-dive): the same ideas, the Anthropic way
3. [Prompt Engineering](https://github.com/alexvervloet/prompt-engineering-deep-dive): shape model behavior with better prompts, using zero-shot and few-shot, chain-of-thought, and roles
4. [RAG](https://github.com/alexvervloet/rag-deep-dive): answer questions over your own documents
5. [Evals](https://github.com/alexvervloet/evals-deep-dive): measure whether a change actually helps
6. [Agents](https://github.com/alexvervloet/agents-deep-dive): give a model tools and a loop so it can act
7. [Prompt Injection & Guardrails](https://github.com/alexvervloet/prompt-injection-deep-dive): attack and defend all of the above
8. [Production](https://github.com/alexvervloet/ai-in-production-deep-dive): operate one app end to end, across observability, cost, reliability, caching, guardrails, prompt versioning, and eval gates

**Bonus dives**, standalone and slotting in where they're most useful:

- [Context Engineering](https://github.com/alexvervloet/context-engineering-deep-dive): manage what's in the window, with memory, compaction, and assembly
- [AI Data Engineering](https://github.com/alexvervloet/ai-data-engineering-deep-dive): the corpus behind the index, with versions, lineage, ACLs, and deletes
- [Multimodal](https://github.com/alexvervloet/multimodal-deep-dive): images and audio as well as text
- [Fine-tuning](https://github.com/alexvervloet/fine-tuning-deep-dive): teach a model new behavior by example
- [MCP](https://github.com/alexvervloet/mcp-deep-dive): serve tools, data, and prompts to any LLM over a standard protocol
- [Local Models](https://github.com/alexvervloet/local-models-deep-dive): run open-weight models on your own machine
- [Agent Harnesses](https://github.com/alexvervloet/agent-harness-deep-dive): build on the loop, adding hooks, permissions, sandboxing, and subagents
- [Realtime Voice](https://github.com/alexvervloet/realtime-voice-deep-dive): low-latency speech-to-speech agents
- [Observability](https://github.com/alexvervloet/observability-deep-dive): watch a running app over time, covering drift, quality, alerting, and the feedback loop
- [Architecture](https://github.com/alexvervloet/architecture-deep-dive): the seams between the components, each decision measured rather than asserted
- [GenAI Security](https://github.com/alexvervloet/genai-security-deep-dive): treat the model as an untrusted principal, and put identity, supply chain, isolation, budgets, and release gates around it
- [Inference Platform Engineering](https://github.com/alexvervloet/inference-platform-deep-dive): turn finite GPU memory and a request queue into latency, throughput, and a fleet size you can defend
- [Testing & Delivery](https://github.com/alexvervloet/testing-and-delivery-deep-dive): decide whether a build is fit to promote, using evidence, gates, staged rollout, and rollback
- [Professional Tools](https://github.com/alexvervloet/professional-tools-deep-dive): rebuild each hand-written piece with the tool professionals reach for, and measure both

And the whole series lands in one codebase in the
[capstone](https://github.com/alexvervloet/deep-dive-capstone): a codebase Q&A tool
built step by step, one tag per dive.

**You are here: #3, Prompt Engineering.**
