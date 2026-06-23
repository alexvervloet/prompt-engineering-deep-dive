"""
A thin wrapper around the OpenAI SDK shared by every example in this repo.

Why a wrapper?
  - One place to configure the client so the rest of the code stays focused on
    *prompting*, not plumbing.
  - It reads the model + endpoint from environment variables, so the exact same
    scripts run against OpenAI's hosted API or a LOCAL model (Ollama, LM Studio,
    llama.cpp, vLLM) just by editing `.env` -- no code changes.

The OpenAI Chat Completions API is the de-facto standard that local servers
implement, which is exactly why we use the `openai` package here.
"""

import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

# Load variables from a local `.env` file if present (never commit `.env`).
load_dotenv()

DEFAULT_MODEL = os.getenv("MODEL", "gpt-4o-mini")

_client: OpenAI | None = None


def get_client() -> OpenAI:
    """Return a singleton OpenAI client configured from the environment.

    - OPENAI_API_KEY  : your key (any non-empty string works for most local servers)
    - OPENAI_BASE_URL : optional; point this at a local server's /v1 endpoint
    """
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL") or None

        if not api_key:
            sys.exit(
                "Missing OPENAI_API_KEY.\n"
                "  -> Copy .env.example to .env and fill it in.\n"
                "  -> For a local model, any non-empty key works (e.g. OPENAI_API_KEY=local)."
            )

        _client = OpenAI(api_key=api_key, base_url=base_url)
    return _client


def chat(
    messages: list[dict],
    model: str | None = None,
    temperature: float = 0.7,
    **kwargs,
) -> str:
    """Send a list of chat messages and return the assistant's text reply.

    `messages` is the standard list of {"role": ..., "content": ...} dicts.
    Extra keyword args (max_tokens, response_format, seed, top_p, ...) are
    forwarded straight to the API.
    """
    client = get_client()
    response = client.chat.completions.create(
        model=model or DEFAULT_MODEL,
        messages=messages,
        temperature=temperature,
        **kwargs,
    )
    return response.choices[0].message.content or ""


def chat_stream(messages: list[dict], model: str | None = None, **kwargs):
    """Yield reply chunks as they arrive -- handy for a live, typewriter feel."""
    client = get_client()
    stream = client.chat.completions.create(
        model=model or DEFAULT_MODEL,
        messages=messages,
        stream=True,
        **kwargs,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


# --- tiny presentation helpers so demos read nicely in a terminal ---------


def rule(char: str = "-", width: int = 70) -> None:
    print(char * width)


def header(title: str) -> None:
    rule("=")
    print(title)
    rule("=")
