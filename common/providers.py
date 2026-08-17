"""
common/providers.py: the ONLY file in this repo that talks to a model provider.

Prompt engineering is provider-agnostic: a clearer prompt is a clearer prompt
whether OpenAI or Claude serves it. So we hide the one provider-specific thing 
turning a list of messages into a reply, behind a few small functions, and every
lesson stays focused on the *prompting*, not the plumbing.

Pick your stack with `PROVIDER` in `.env`:

    PROVIDER=openai  ->  OpenAI chat     (needs OPENAI_API_KEY)
    PROVIDER=claude  ->  Claude messages (needs ANTHROPIC_API_KEY)

Because the OpenAI stack uses the OpenAI SDK, it *also* speaks to any
OpenAI-compatible local server (Ollama, LM Studio, llama.cpp, vLLM): keep
`PROVIDER=openai` and point `OPENAI_BASE_URL` at the local endpoint. So this one
file gives you hosted OpenAI, hosted Claude, and local models, with no change to
any lesson.

What this module exposes:
  - chat(messages, ...)        -> a text reply (the workhorse)
  - chat_stream(messages, ...) -> yields the reply in chunks (the capstone)
  - structured(messages, schema) -> JSON forced to match a schema
  - provider_name / chat_model / describe / ensure_ready  (small helpers)

The provider differences this file quietly absorbs:
  - Claude takes the system prompt as a separate `system=` argument, not a
    message with role "system"; we split it out for you.
  - "Give me JSON" is `response_format` on OpenAI and an assistant *prefill* on
    Claude; `chat(..., json=True)` does the right one.
  - A strict JSON *schema* is `json_schema` on OpenAI and a forced *tool call* on
    Claude; `structured()` does the right one.
  - `stop` strings are `stop` on compatible OpenAI models and `stop_sequences`
    on Claude. Unsupported GPT-5 combinations fail loudly; nothing is dropped.
  - `reasoning_effort` uses OpenAI's Responses API or Claude adaptive thinking.
"""

import json as _json
import os
import sys
from functools import lru_cache

from dotenv import load_dotenv

# Load `.env` once, when this module is first imported (never commit `.env`).
load_dotenv()

_OPENAI_CHAT = "gpt-5.4-nano"
_CLAUDE_CHAT = "claude-haiku-4-5"

_KEYS = {
    "openai": ["OPENAI_API_KEY"],
    "claude": ["ANTHROPIC_API_KEY"],
}


def provider_name() -> str:
    """The active stack: 'openai' (default) or 'claude'. Set via PROVIDER in .env."""
    return os.getenv("PROVIDER", "openai").strip().lower()


def chat_model() -> str:
    """The default chat model for the active stack (override with MODEL in .env)."""
    override = os.getenv("MODEL")
    if override:
        return override
    return _CLAUDE_CHAT if provider_name() == "claude" else _OPENAI_CHAT


def required_keys() -> list[str]:
    return _KEYS.get(provider_name(), [])


def describe() -> str:
    """One-line summary of the active stack, handy for a lesson to print."""
    p = provider_name()
    if p in _KEYS:
        return f"{p}  (chat={chat_model()})"
    return f"unknown provider {p!r}"


def ensure_ready() -> None:
    """Fail fast with a friendly message if the chosen stack isn't configured.

    Called automatically by `chat`/`chat_stream`/`structured`, so individual
    lessons don't have to, but you can call it yourself right after startup.
    """
    p = provider_name()
    if p not in _KEYS:
        sys.exit(
            f"PROVIDER={p!r} is not recognized. Set PROVIDER=openai or claude in .env."
        )
    missing = [k for k in required_keys() if not os.getenv(k)]
    if missing:
        sys.exit(
            f"PROVIDER={p} needs {', '.join(missing)} in the environment. "
            f"Provide them via secrun (see SECRETS.md), or run `secrun python check_setup.py`."
        )


@lru_cache(maxsize=1)
def _openai_client():
    from openai import OpenAI

    # base_url lets PROVIDER=openai also reach a local OpenAI-compatible server.
    return OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL") or None,
    )


@lru_cache(maxsize=1)
def _anthropic_client():
    import anthropic

    return anthropic.Anthropic()


def _split_system(messages: list[dict]) -> tuple[str, list[dict]]:
    """Claude wants the system prompt separate; pull system messages out of the list."""
    system_parts = [m["content"] for m in messages if m["role"] == "system"]
    convo = [
        {"role": m["role"], "content": m["content"]}
        for m in messages
        if m["role"] != "system"
    ]
    return "\n\n".join(system_parts), convo


def _openai_model_rejects_temperature(model: str) -> bool:
    """GPT-5.6 controls depth with reasoning effort, not sampling knobs."""
    return model.startswith("gpt-5.6")


def _validate_openai_controls(
    model: str,
    *,
    temperature: float | None,
    stop: list[str] | None = None,
) -> None:
    """Reject known-incompatible controls before a confusing remote 400."""
    if temperature is not None and _openai_model_rejects_temperature(model):
        raise ValueError(
            f"{model} does not accept temperature. Pass temperature=None and, "
            "for reasoning work, set reasoning_effort instead."
        )
    if stop and model.startswith("gpt-5"):
        raise ValueError(
            f"{model} does not support stop sequences. Use a stop-compatible "
            "model for classic text ReAct, or use native tool calling / structured outputs."
        )


def chat(
    messages: list[dict],
    *,
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: int = 2048,
    json: bool = False,
    stop: list[str] | None = None,
    reasoning_effort: str | None = None,
) -> str:
    """Send a list of {"role", "content"} messages; return the assistant's text.

    `json=True` asks the provider for a valid JSON object. `stop` ends generation
    on models that support it. `reasoning_effort` deliberately selects a
    reasoning-capable request path; it is never simulated or silently ignored.
    """
    ensure_ready()
    p = provider_name()

    if p == "openai":
        selected_model = model or chat_model()
        _validate_openai_controls(
            selected_model, temperature=temperature, stop=stop
        )
        if reasoning_effort is not None:
            if temperature is not None or stop or json:
                raise ValueError(
                    "reasoning_effort cannot be combined here with temperature, "
                    "stop, or json; keep the reasoning request minimal."
                )
            system, convo = _split_system(messages)
            params: dict = {
                "model": selected_model,
                "input": convo,
                "max_output_tokens": max_tokens,
                "reasoning": {"effort": reasoning_effort},
            }
            if system:
                params["instructions"] = system
            response = _openai_client().responses.create(**params)
            return response.output_text

        params: dict = {}
        if temperature is not None:
            params["temperature"] = temperature
        if json:
            params["response_format"] = {"type": "json_object"}
        if stop:
            params["stop"] = stop
        resp = _openai_client().chat.completions.create(
            model=selected_model,
            messages=messages,  # type: ignore[arg-type]
            max_completion_tokens=max_tokens,
            **params,
        )
        return resp.choices[0].message.content or ""

    if p == "claude":
        system, convo = _split_system(messages)
        selected_model = model or chat_model()
        params: dict = {"max_tokens": max_tokens}
        if temperature is not None:
            # Claude's range is 0.0-1.0 (not 0-2).
            params["temperature"] = min(temperature, 1.0)
        if system:
            params["system"] = system
        if stop:
            params["stop_sequences"] = stop
        if json:
            if reasoning_effort is not None:
                raise ValueError(
                    "Claude reasoning_effort cannot be combined with the JSON "
                    "assistant-prefill path; use structured() instead."
                )
            # Prefill an opening brace so the model must continue a JSON object.
            convo = convo + [{"role": "assistant", "content": "{"}]
        if reasoning_effort is not None:
            if selected_model == "claude-haiku-4-5":
                raise ValueError(
                    "claude-haiku-4-5 has no adaptive effort control. Set "
                    "REASONING_MODEL to a recent reasoning model such as "
                    "claude-sonnet-4-6."
                )
            if temperature is not None:
                raise ValueError(
                    "Claude adaptive thinking cannot be combined with temperature; "
                    "pass temperature=None."
                )
            params["thinking"] = {"type": "adaptive"}
            params["output_config"] = {"effort": reasoning_effort}
        resp = _anthropic_client().messages.create(
            model=selected_model,
            messages=convo,  # type: ignore[arg-type]
            **params,
        )
        text = "".join(b.text for b in resp.content if b.type == "text")
        return ("{" + text) if json else text

    raise ValueError(f"Unknown PROVIDER={p!r} (expected 'openai' or 'claude').")


def chat_stream(
    messages: list[dict],
    *,
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: int = 2048,
):
    """Yield the reply in chunks as it's generated, for a live, typewriter feel."""
    ensure_ready()
    p = provider_name()

    if p == "openai":
        selected_model = model or chat_model()
        _validate_openai_controls(selected_model, temperature=temperature)
        params: dict = {}
        if temperature is not None:
            params["temperature"] = temperature
        stream = _openai_client().chat.completions.create(  # type: ignore[call-overload]
            model=selected_model,
            messages=messages,  # type: ignore[arg-type]
            max_completion_tokens=max_tokens,
            stream=True,
            **params,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
        return

    if p == "claude":
        system, convo = _split_system(messages)
        params: dict = {"max_tokens": max_tokens}
        if temperature is not None:
            params["temperature"] = min(temperature, 1.0)
        if system:
            params["system"] = system
        with _anthropic_client().messages.stream(
            model=model or chat_model(),
            messages=convo,  # type: ignore[arg-type]
            **params,  # type: ignore[arg-type]
        ) as stream:
            for text in stream.text_stream:
                yield text
        return

    raise ValueError(f"Unknown PROVIDER={p!r} (expected 'openai' or 'claude').")


def structured(
    messages: list[dict],
    schema: dict,
    *,
    name: str = "result",
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: int = 2048,
) -> str:
    """Force the reply to match a JSON Schema; return it as a JSON string.

    This is the strongest "give me exactly these fields" guarantee each provider
    offers: OpenAI's strict `json_schema`, and Claude's forced tool call (the
    tool's input schema *is* your schema). Both hand back a JSON string you can
    `json.loads` with confidence.
    """
    ensure_ready()
    p = provider_name()

    if p == "openai":
        selected_model = model or chat_model()
        _validate_openai_controls(selected_model, temperature=temperature)
        params: dict = {}
        if temperature is not None:
            params["temperature"] = temperature
        resp = _openai_client().chat.completions.create(
            model=selected_model,
            messages=messages,  # type: ignore[arg-type]
            max_completion_tokens=max_tokens,
            response_format={
                "type": "json_schema",
                "json_schema": {"name": name, "schema": schema, "strict": True},
            },
            **params,
        )
        return resp.choices[0].message.content or ""

    if p == "claude":
        system, convo = _split_system(messages)
        params: dict = {"max_tokens": max_tokens}
        if temperature is not None:
            params["temperature"] = min(temperature, 1.0)
        if system:
            params["system"] = system
        resp = _anthropic_client().messages.create(  # type: ignore[call-overload]
            model=model or chat_model(),
            messages=convo,  # type: ignore[arg-type]
            tools=[
                {
                    "name": name,
                    "description": f"Return the {name} as structured data.",
                    "input_schema": schema,
                }
            ],
            tool_choice={"type": "tool", "name": name},
            **params,
        )
        for block in resp.content:
            if block.type == "tool_use":
                return _json.dumps(block.input)
        return ""

    raise ValueError(f"Unknown PROVIDER={p!r} (expected 'openai' or 'claude').")
