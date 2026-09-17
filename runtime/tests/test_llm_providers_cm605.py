from __future__ import annotations

import os

import pytest

from context_skills.llm.provider import get_llm_provider


def test_openai_provider_resolves_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CONTEXT_SKILLS_LLM_PROVIDER", "openai")
    monkeypatch.setenv("CONTEXT_SKILLS_LLM_MODEL", "gpt-4o-mini")
    provider = get_llm_provider()
    assert provider.name.startswith("http:")


def test_offline_fallback_default() -> None:
    old = os.environ.pop("CONTEXT_SKILLS_LLM_PROVIDER", None)
    try:
        provider = get_llm_provider()
        assert provider.name.startswith("offline")
    finally:
        if old is not None:
            os.environ["CONTEXT_SKILLS_LLM_PROVIDER"] = old
