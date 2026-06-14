"""Deterministic offline summarizer — no network, no credentials."""

from __future__ import annotations

import re
from typing import Iterable

from context_skills.llm.provider import LLMProvider


def _first_sentences(text: str, limit: int = 3) -> str:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return " ".join(parts[:limit]).strip()


def _bullet_lines(text: str, *, max_items: int = 8) -> list[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    bullets: list[str] = []
    for line in lines:
        if line.startswith(("-", "*", "•")):
            bullets.append(line.lstrip("-*• ").strip())
        elif re.match(r"^\[?(USER|ASSISTANT|TOOL)", line, re.I):
            bullets.append(line[:180])
        if len(bullets) >= max_items:
            break
    return bullets


class OfflineLLMProvider(LLMProvider):
    """Extractive/heuristic summarizer for reproducible offline tests."""

    @property
    def name(self) -> str:
        return "offline-heuristic"

    def summarize(self, text: str, *, instruction: str, max_tokens: int = 512) -> str:
        instruction_lower = instruction.lower()
        if "handoff" in instruction_lower:
            return self._handoff_summary(text)
        if "selective" in instruction_lower or "retention" in instruction_lower:
            return self._selective_retention(text)
        if "hierarchical" in instruction_lower or "compact" in instruction_lower:
            return self._hierarchical_summary(text)
        return self._generic_summary(text, max_chars=max(400, max_tokens * 4))

    def _generic_summary(self, text: str, *, max_chars: int) -> str:
        lead = _first_sentences(text, limit=2)
        bullets = _bullet_lines(text)
        body = "\n".join(f"- {item}" for item in bullets[:6])
        summary = f"{lead}\n{body}".strip()
        return summary[:max_chars]

    def _hierarchical_summary(self, text: str) -> str:
        sections = re.split(r"\n\s*\n", text.strip())
        if len(sections) <= 4:
            return self._generic_summary(text, max_chars=1200)
        oldest = sections[: max(1, len(sections) // 4)]
        middle = sections[len(sections) // 4 : -2]
        recent = sections[-2:]
        return (
            "## Session Background\n"
            + _first_sentences("\n".join(oldest), limit=3)
            + "\n\n## Completed Work\n"
            + "\n".join(f"- {_first_sentences(block, 1)}" for block in middle[:5])
            + "\n\n## Recent Context\n"
            + "\n".join(recent)
        )

    def _handoff_summary(self, text: str) -> str:
        bullets = _bullet_lines(text, max_items=12)
        decisions = [b for b in bullets if any(k in b.lower() for k in ("decision", "using", "rate", "oauth", "decomposed"))]
        return (
            "## Task State\n- "
            + _first_sentences(text, 2)
            + "\n\n## Key Decisions\n"
            + "\n".join(f"- {item}" for item in (decisions or bullets[:4]))
            + "\n\n## Critical Context\n"
            + "\n".join(f"- {item}" for item in bullets[-4:])
        )

    def _selective_retention(self, text: str) -> str:
        root = re.search(r"(Root cause[^.\n]+[.\n])", text, re.I)
        fix = re.search(r"(Fix[^.\n]+[.\n])", text, re.I)
        decision = re.search(r"(Decision[^.\n]+[.\n])", text, re.I)
        chunks: Iterable[str] = filter(
            None,
            [
                root.group(1).strip() if root else None,
                fix.group(1).strip() if fix else None,
                decision.group(1).strip() if decision else None,
            ],
        )
        retained = list(chunks)
        if not retained:
            return self._generic_summary(text, max_chars=600)
        return "## Retained Session Facts\n" + "\n".join(f"- {item}" for item in retained)
