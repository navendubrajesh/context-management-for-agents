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
    """Resolve provider from config/env; always falls back to offline implementation (CM-605)."""
    import os

    from context_skills.llm.offline import OfflineLLMProvider

    config = dict(config or {})
    provider = (config.get("provider") or os.environ.get("CONTEXT_SKILLS_LLM_PROVIDER", "")).strip().lower()
    api_key = config.get("api_key") or os.environ.get("CONTEXT_SKILLS_LLM_API_KEY")
    model = config.get("model") or os.environ.get("CONTEXT_SKILLS_LLM_MODEL", "gpt-4o-mini")

    if provider in {"", "offline", "heuristic"}:
        return OfflineLLMProvider()

    if provider == "http":
        from context_skills.llm.http_adapter import HttpLLMProvider

        base_url = config.get("base_url") or os.environ.get("CONTEXT_SKILLS_LLM_BASE_URL", "")
        return HttpLLMProvider(base_url=base_url, model=model, api_key=api_key)

    if provider in {"openai", "anthropic"}:
        from context_skills.llm.http_adapter import HttpLLMProvider

        defaults = {
            "openai": "https://api.openai.com/v1",
            "anthropic": "https://api.anthropic.com/v1",
        }
        base_url = config.get("base_url") or os.environ.get("CONTEXT_SKILLS_LLM_BASE_URL") or defaults[provider]
        return HttpLLMProvider(base_url=base_url, model=model, api_key=api_key)

    return OfflineLLMProvider()
