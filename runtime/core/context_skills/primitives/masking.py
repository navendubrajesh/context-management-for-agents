"""Observation masking — replace verbose tool outputs with compact summaries."""

from __future__ import annotations

import json
from typing import Any

from context_skills.metering import TokenCounter
from context_skills.primitives.metrics import PrimitiveMetrics, PrimitiveResult


def _mask_database_query(raw_data: dict[str, Any]) -> str:
    rows = raw_data.get("rows", [])
    total_orders = sum(1 for row in rows if row.get("order_id"))
    completed = sum(1 for row in rows if row.get("status") == "completed")
    totals = [row["total"] for row in rows if row.get("total")]
    total_revenue = sum(totals)
    unique_users = len({row["id"] for row in rows})
    no_orders = [str(row["id"]) for row in rows if row.get("order_id") is None]
    highest = max(totals) if totals else 0
    highest_user = next(
        (row["id"] for row in rows if row.get("total") == highest),
        "?",
    )
    raw_len = len(json.dumps(raw_data))
    return (
        f"[database_query output — {raw_len} chars, summarized]\n"
        f"Query returned {raw_data.get('row_count', len(rows))} rows in {raw_data.get('execution_time_ms', '?')}ms.\n"
        "Key findings:\n"
        f"- {unique_users} unique users since 2025-01-01\n"
        f"- {total_orders} orders across users ({completed} completed)\n"
        f"- Total revenue: ${total_revenue:,.2f}\n"
        f"- {len(no_orders)} users with no orders (IDs: {', '.join(no_orders)})\n"
        f"- Highest single order: ${highest:,.2f} (user #{highest_user})\n"
        "Full results saved to: tool_outputs/database_query_20260605.json\n"
    )


def _generic_mask(tool_name: str, content: str, *, max_lines: int = 6) -> str:
    lines = [line for line in content.splitlines() if line.strip()]
    preview = "\n".join(lines[:max_lines])
    return (
        f"[{tool_name} output — {len(content)} chars, summarized]\n"
        f"{preview}\n"
        f"... ({max(0, len(lines) - max_lines)} lines omitted; full output offloaded)\n"
    )


def mask_observation(
    *,
    tool_name: str,
    content: str | dict[str, Any],
    query: str | None = None,
    counter: TokenCounter | None = None,
) -> PrimitiveResult:
    """Mask a completed tool/observation output for subsequent turns."""
    counter = counter or TokenCounter(prefer_heuristic=True)

    if isinstance(content, dict):
        raw_data = content
        raw_text = json.dumps(content, indent=2)
    else:
        raw_text = content
        try:
            raw_data = json.loads(content)
        except json.JSONDecodeError:
            raw_data = None

    if query:
        before = (
            f"[Tool Call: {tool_name}]\nQuery: {query}\n"
            f"Status: {raw_data.get('status') if raw_data else 'ok'}\n"
            f"Full Results:\n{raw_text}\n"
        )
    elif raw_data and "rows" in raw_data and "query" in raw_data:
        before = (
            f"[Tool Call: {tool_name}]\nQuery: {raw_data['query']}\n"
            f"Status: {raw_data.get('status')}\n"
            f"Execution time: {raw_data.get('execution_time_ms')}ms\n"
            f"Rows returned: {raw_data.get('row_count')}\n\n"
            f"Full Results:\n{json.dumps(raw_data.get('rows'), indent=2)}\n"
        )
    else:
        before = f"[Tool: {tool_name}]\n{raw_text}\n"

    if raw_data and "rows" in raw_data and "query" in raw_data:
        after = _mask_database_query(raw_data)
    else:
        after = _generic_mask(tool_name, raw_text)

    tokens_before = counter.count(before)
    tokens_after = counter.count(after)
    return PrimitiveResult(
        output=after,
        metrics=PrimitiveMetrics(
            operation="mask_observation",
            tokens_before=tokens_before,
            tokens_after=tokens_after,
        ),
    )
