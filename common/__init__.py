"""Shared utilities for the prompt-engineering playground."""

from .llm import chat, chat_stream, get_client, DEFAULT_MODEL, rule, header

__all__ = ["chat", "chat_stream", "get_client", "DEFAULT_MODEL", "rule", "header"]
