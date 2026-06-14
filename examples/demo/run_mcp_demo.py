#!/usr/bin/env python3
"""MCP integration demo: tools/list, route_task, run_context_pipeline via stdio transport."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MCP_SERVER = REPO_ROOT / "runtime" / "mcp" / "server.py"
CORE_DIR = REPO_ROOT / "runtime" / "core"


def _pipeline_session() -> dict:
    """Benchmark-compatible session (combined pipeline fixture)."""
    return {
        "system_prompt": (
            "You are a senior software engineer helping with code review and refactoring. "
            "You specialize in Python, testing, and clean architecture."
        )
        * 2,
        "tool_schemas": json.dumps(
            [
                {
                    "name": f"tool_{i}",
                    "description": (
                        f"Tool {i} description with detailed parameters and usage examples. "
                        "This tool is used for various operations including reading, writing, and processing data."
                    ),
                    "parameters": {"param1": "string", "param2": "integer"},
                }
                for i in range(12)
            ],
            indent=2,
        ),
        "retrieved_docs": "# Architecture Guide\n"
        + "\n".join(
            f"## Section {i}\nThis section covers architecture decisions for component {i}. " * 5
            for i in range(10)
        ),
        "conversation_history": "\n".join(
            f"[Turn {i}] User: Review feature_{i}\nAssistant: Looking at feature_{i}...\n"
            f"Tool Output: {json.dumps({'status': 'ok', 'file': f'feature_{i}.py', 'lines': 50, 'issues': []})}\n"
            f"Assistant: Feature_{i} looks good, no issues found."
            for i in range(15)
        ),
        "current_task": "Now please review the authentication module and suggest improvements.",
    }


async def main() -> None:
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except ImportError as exc:
        print("Install MCP client deps: pip install -e runtime/core -e runtime/mcp")
        raise SystemExit(1) from exc

    session = _pipeline_session()
    task = "compress conversation history for a handoff"

    env = dict(**{k: v for k, v in __import__("os").environ.items()})
    env["PYTHONPATH"] = str(CORE_DIR)

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(MCP_SERVER)],
        env=env,
    )

    print("=" * 60)
    print("Context Management for Agents — MCP Demo")
    print("=" * 60)

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session_client:
            await session_client.initialize()

            tools = await session_client.list_tools()
            tool_names = sorted(t.name for t in tools.tools)
            print(f"\n--- tools/list ({len(tool_names)} tools) ---")
            for name in tool_names[:8]:
                print(f"  • {name}")
            if len(tool_names) > 8:
                print(f"  ... and {len(tool_names) - 8} more")

            print(f"\n--- route_task: {task!r} ---")
            route_result = await session_client.call_tool(
                "route_task",
                arguments={"task": task, "top_k": 3},
            )
            route_payload = json.loads(route_result.content[0].text)
            print(f"  Top skill: {route_payload[0]['skill']} (score {route_payload[0]['score']:.1f})")
            assert route_payload[0]["skill"] == "context-compression"

            print("\n--- run_context_pipeline ---")
            pipe_result = await session_client.call_tool(
                "run_context_pipeline",
                arguments={"session": session},
            )
            pipe_payload = json.loads(pipe_result.content[0].text)
            metrics = pipe_payload["metrics"]
            before = metrics["tokens_before"]
            after = metrics["tokens_after"]
            saved = before - after
            pct = metrics.get("savings_pct") or (saved / before * 100 if before else 0)
            print(f"  Tokens before: {before:,}")
            print(f"  Tokens after:  {after:,}")
            print(f"  Tokens saved:  {saved:,} ({pct:.1f}%)")
            print("\n[+] MCP demo complete (stdio transport, offline).")


if __name__ == "__main__":
    asyncio.run(main())
