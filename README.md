# Prompt Engineering Fundamentals

A hands-on playground for learning prompt engineering — from the basics
(zero/few-shot, chain-of-thought, role & system prompts) through to practical,
optimized prompts for real use cases. Every concept is a small, runnable Python
script you can read, run, and tweak.

Built on the **OpenAI Python SDK** so the exact same code runs against OpenAI's
hosted API **or a local model** (Ollama, LM Studio, llama.cpp, vLLM) — you only
change a couple of environment variables.

---

## Quick start

```bash
# 1. (recommended) create a virtual environment
python3 -m venv .venv && source .venv/bin/activate

# 2. install dependencies
pip install -r requirements.txt

# 3. configure your model / key
cp .env.example .env
#   then edit .env  (hosted OpenAI key, OR a local server's base URL)

# 4. run any lesson
python fundamentals/01_zero_shot.py
python examples/03_code_review.py
```

> Each script is self-contained and prints a **before/after** or
> **technique demo** so you can see the effect of each idea.

### Using a local model

Local servers speak the OpenAI API, so you only swap the endpoint. In `.env`:

```bash
OPENAI_API_KEY=local                          # any non-empty string
OPENAI_BASE_URL=http://localhost:11434/v1     # Ollama (see .env.example for others)
MODEL=llama3.1
```

That's the whole reason this repo uses the OpenAI SDK: **one codebase, any
OpenAI-compatible backend.**

---

## What's inside

### `fundamentals/` — the core techniques

| File | Technique | One-line idea |
|------|-----------|---------------|
| [01_zero_shot.py](fundamentals/01_zero_shot.py) | Zero-shot | Ask clearly, constrain the output — no examples. |
| [02_few_shot.py](fundamentals/02_few_shot.py) | Few-shot | Teach format & conventions with 2–5 examples. |
| [03_chain_of_thought.py](fundamentals/03_chain_of_thought.py) | Chain-of-thought | Let the model reason step by step before answering. |
| [04_role_prompting.py](fundamentals/04_role_prompting.py) | Role / persona | Assign expertise + audience to steer tone & depth. |
| [05_system_prompts.py](fundamentals/05_system_prompts.py) | System prompts | Set durable behavior: role, rules, format, fallback. |
| [06_structured_output.py](fundamentals/06_structured_output.py) | Structured output | Force machine-readable JSON (schema/json_object). |
| [07_delimiters_and_context.py](fundamentals/07_delimiters_and_context.py) | Delimiters & grounding | Separate instructions from data; answer only from context; resist injection. |
| [08_prompt_chaining.py](fundamentals/08_prompt_chaining.py) | Prompt chaining | Decompose into a pipeline; generate→critique→revise. |
| [09_self_consistency.py](fundamentals/09_self_consistency.py) | Self-consistency | Sample N times and majority-vote for accuracy. |
| [10_parameters.py](fundamentals/10_parameters.py) | Decoding params | temperature, top_p, max_tokens, seed, stop. |

### `examples/` — optimizing prompts for 5 real use cases

Each shows a **naïve prompt vs an optimized prompt** and explains *why* every
change helps.

| File | Use case | Techniques combined |
|------|----------|---------------------|
| [01_customer_support_reply.py](examples/01_customer_support_reply.py) | Support email responder | system prompt · policy constraints · tone · fallback |
| [02_data_extraction.py](examples/02_data_extraction.py) | Unstructured text → typed JSON | schema · normalization · null policy · json_object |
| [03_code_review.py](examples/03_code_review.py) | Security-aware code review | persona · rubric · severity · fixed format |
| [04_summarization.py](examples/04_summarization.py) | Audience-targeted TL;DR | audience · length limits · focus · grounding |
| [05_text_to_sql.py](examples/05_text_to_sql.py) | Natural language → SQL | schema grounding · dialect · safety · few-shot |

### `common/` — shared plumbing

[common/llm.py](common/llm.py) wraps the OpenAI SDK (`chat`, `chat_stream`)
and reads the model/endpoint from `.env`, so the lessons stay focused on
*prompting* rather than setup.

---

## The mental model (cheat sheet)

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
- **Give room to think** on hard problems; **hide the reasoning** if the end
  user doesn't need it.
- **Constrain the output** when code will parse it, and still parse defensively.
- **Match temperature to the task:** `0` for extraction/classification/code,
  higher for creative work.
- **Iterate.** Prompt engineering is empirical — change one thing, observe,
  repeat.

---

## Notes & costs

- Running a script makes real API calls. Against the hosted OpenAI API this
  costs a small amount of money; against a local model it's free.
- `09_self_consistency.py` and `10_parameters.py` make several calls each by
  design (they sample multiple times).
- Never commit your `.env` — it's already in `.gitignore`.
