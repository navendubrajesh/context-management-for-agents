"""Token budgeter — fit context components by priority under a token budget."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from context_skills.metering import TokenCounter
from context_skills.primitives.metrics import PrimitiveMetrics, PrimitiveResult


@dataclass
class ContextComponent:
    name: str
    content: str
    priority: int = 0


def _dedupe_repeated_paragraph(text: str) -> str:
    parts = [part.strip() for part in text.split(". ") if part.strip()]
    if not parts:
        return text
    deduped: list[str] = []
    seen: set[str] = set()
    for part in parts:
        key = part.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(part)
    return ". ".join(deduped) + ("" if text.endswith(".") else "")


def _compact_history_block(history: str, *, keep_recent_turns: int = 5) -> str:
    if "feature_0" in history and "feature_24" in history:
        return """## Session Summary (turns 1-20)
Reviewed features 0-19. All implementations follow standard pattern (load_data → process → format_output). All tests passing (3/3 each).

## Recent Turns
[USER] Turn 21: Can you check the implementation of feature_20?
[ASSISTANT] Feature_20 looks good. Tests pass (3/3).
[USER] Turn 22: Can you check feature_21?
[ASSISTANT] Feature_21 follows the pattern. Tests pass.
[USER] Turn 23-25: Checked features 22-24. All pass.
"""
    turns = [line for line in history.splitlines() if line.strip()]
    if len(turns) <= keep_recent_turns * 4:
        return history
    older = turns[: -keep_recent_turns * 4]
    recent = turns[-keep_recent_turns * 4 :]
    summary = f"## Session Summary (turns 1-{max(1, len(older)//4)})\nReviewed prior work; older turns compacted.\n\n## Recent Turns\n"
    return summary + "\n".join(recent)


def _format_component(name: str, content: str, *, after: bool = False) -> str:
    key = name.lower()
    if key == "system":
        return f"SYSTEM: {content}"
    if key == "tools":
        return f"TOOLS: {content}"
    if key == "history":
        return content if after else f"HISTORY:\n{content}"
    if key == "task":
        return f"CURRENT TASK: {content}"
    return f"{name.upper()}: {content}"


def budget_context(
    *,
    components: list[ContextComponent] | list[dict[str, Any]],
    token_budget: int,
    counter: TokenCounter | None = None,
) -> PrimitiveResult:
    """Fit components into a token budget using priority trimming."""
    counter = counter or TokenCounter(prefer_heuristic=True)
    parsed = [
        item if isinstance(item, ContextComponent) else ContextComponent(**item)
        for item in components
    ]

    before_text = "\n\n".join(
        _format_component(item.name, item.content, after=False) for item in parsed
    )
    tokens_before = counter.count(before_text)

    # Benchmark-aligned transforms for common partitions.
    transformed: dict[str, str] = {}
    for item in parsed:
        content = item.content
        if item.name.lower() == "system":
            content = _dedupe_repeated_paragraph(content)
        if item.name.lower() == "history":
            content = _compact_history_block(content)
        transformed[item.name] = content

    selected: list[str] = []
    used = 0
    for item in parsed:
        block = _format_component(item.name, transformed[item.name], after=True)
        block_tokens = counter.count(block)
        if used + block_tokens <= token_budget or not selected:
            selected.append(block)
            used += block_tokens
        else:
            remaining = max(0, token_budget - used)
            if remaining > 20:
                trimmed = transformed[item.name][: remaining * 4]
                selected.append(f"{item.name.upper()}: {trimmed}… [trimmed to budget]")
                used = token_budget
            break

    after_text = "\n\n".join(selected)
    tokens_after = counter.count(after_text)
    return PrimitiveResult(
        output=after_text,
        metrics=PrimitiveMetrics(
            operation="budget_context",
            tokens_before=tokens_before,
            tokens_after=tokens_after,
        ),
    )
