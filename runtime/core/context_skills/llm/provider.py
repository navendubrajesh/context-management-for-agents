"""LLM provider abstraction for summarization-capable primitives."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    """Summarization interface — optional remote adapter, offline default required."""

    @abstractmethod
    def summarize(self, text: str, *, instruction: str, max_tokens: int = 512) -> str: ...

    @property
    @abstractmethod
    def name(self) -> str: ...


def get_llm_provider(config: dict[str, Any] | None = None) -> LLMProvider:
    """Resolve provider from config/env; always falls back to offline implementation."""
    from context_skills.llm.offline import OfflineLLMProvider

    config = config or {}
    provider = (config.get("provider") or "").strip().lower()
    if provider in {"", "offline", "heuristic"}:
        return OfflineLLMProvider()

    # Optional remote adapter — configured by operator, never hardcoded vendor defaults.
    if provider == "http":
        from context_skills.llm.http_adapter import HttpLLMProvider

        return HttpLLMProvider(
            base_url=config["base_url"],
            model=config.get("model", "default"),
            api_key=config.get("api_key"),
        )

    return OfflineLLMProvider()
