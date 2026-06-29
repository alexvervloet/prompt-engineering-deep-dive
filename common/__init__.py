"""Shared utilities for the prompt-engineering playground.

`providers.py` is the only file that talks to a model provider (OpenAI or Claude);
`display.py` holds the little terminal helpers. Lessons import from here.
"""

from .display import header, rule
from .providers import (
    chat,
    chat_model,
    chat_stream,
    describe,
    ensure_ready,
    provider_name,
    required_keys,
    structured,
)

__all__ = [
    "chat",
    "chat_stream",
    "structured",
    "chat_model",
    "provider_name",
    "describe",
    "ensure_ready",
    "required_keys",
    "header",
    "rule",
]
