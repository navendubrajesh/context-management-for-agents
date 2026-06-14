#!/usr/bin/env python3
"""Smoke test for MCP tool handlers (in-process, no stdio transport)."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

MCP_DIR = Path(__file__).resolve().parent
CORE_DIR = MCP_DIR.parent / "core"
sys.path[:0] = [str(CORE_DIR), str(MCP_DIR)]

from server import call_tool, list_tools  # noqa: E402


async def main() -> None:
    tools = await list_tools()
    assert any(tool.name == "route_task" for tool in tools), "route_task tool missing"

    route_result = await call_tool(
        "route_task",
        {"task": "How do I compress conversation history for a handoff?", "top_k": 3},
    )
    payload = json.loads(route_result[0].text)
    assert payload[0]["skill"] == "context-compression", payload

    list_result = await call_tool("list_skills", {})
    skills = json.loads(list_result[0].text)
    assert len(skills) == 28

    print("[+] MCP smoke test passed")


if __name__ == "__main__":
    asyncio.run(main())
