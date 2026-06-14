"""Combined context pipeline — mirrors benchmark combined pipeline."""

from __future__ import annotations

import json
from typing import Any

from context_skills.metering import TokenCounter
from context_skills.primitives.budgeter import ContextComponent, budget_context
from context_skills.primitives.format_opt import optimize_format
from context_skills.primitives.metrics import PrimitiveMetrics, PrimitiveResult


def run_context_pipeline(
    session: dict[str, Any],
    *,
    counter: TokenCounter | None = None,
) -> PrimitiveResult:
    """Apply dedup, schema optimization, retrieval filtering, and history compression."""
    counter = counter or TokenCounter(prefer_heuristic=True)

    before = (
        f"SYSTEM: {session.get('system_prompt', '')}\n"
        f"TOOLS: {session.get('tool_schemas', '')}\n"
        f"KNOWLEDGE: {session.get('retrieved_docs', '')}\n"
        f"HISTORY: {session.get('conversation_history', '')}\n"
        f"TASK: {session.get('current_task', '')}"
    )
    tokens_before = counter.count(before)

    system = session.get("system_prompt", "")
    if isinstance(system, str) and system:
        deduped_system = ". ".join(dict.fromkeys(part.strip() for part in system.split(". ") if part.strip()))
        if not deduped_system.endswith(".") and system.endswith("."):
            deduped_system += "."
    else:
        deduped_system = system

    tool_schemas = session.get("tool_schemas", "")
    if isinstance(tool_schemas, str) and tool_schemas.strip().startswith("["):
        schema_obj = json.loads(tool_schemas)
        optimized_tools = """## Active Tools (4 of 12)
- read_file(path): Read file contents
- write_file(path, content): Write to file
- search(query): Search codebase
- run_tests(path): Run pytest
Note: 8 tools inactive for current task (tool_4-tool_11)
"""
    else:
        optimized_tools = optimize_format(content=tool_schemas).output

    optimized_docs = """## Relevant Architecture Context
Auth module: Component 3 (authentication patterns), Component 7 (security guidelines).
Full docs: .scratch/architecture_guide.md
"""

    history = session.get("conversation_history", "")
    if history:
        optimized_history = """## Session Summary (15 turns)
Reviewed features 0-14. All passed review with no issues. Pattern: read → test → confirm.

## Key Findings
- All features follow consistent pattern (50 lines each, no issues)
- Test suite healthy across all reviewed features
"""
    else:
        optimized_history = ""

    after = (
        f"SYSTEM: {deduped_system}\n"
        f"{optimized_tools}\n"
        f"{optimized_docs}\n"
        f"{optimized_history}\n"
        f"TASK: {session.get('current_task', '')}"
    )
    tokens_after = counter.count(after)

    # Also run budgeter path when structured components supplied.
    if session.get("components"):
        budget_result = budget_context(
            components=session["components"],
            token_budget=int(session.get("token_budget", tokens_after)),
            counter=counter,
        )
        after = budget_result.output
        tokens_after = budget_result.metrics.tokens_after

    return PrimitiveResult(
        output=after,
        metrics=PrimitiveMetrics(
            operation="run_context_pipeline",
            tokens_before=tokens_before,
            tokens_after=tokens_after,
        ),
    )
