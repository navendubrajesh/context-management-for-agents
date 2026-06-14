#!/usr/bin/env python3
"""MCP server exposing context-management-for-agents skills and runtime primitives."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

CORE_DIR = Path(__file__).resolve().parent.parent / "core"
if str(CORE_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_DIR))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, TextContent, Tool

from context_skills import get_reference, get_skill, list_skills, route
from context_skills.primitives import (
    budget_context,
    compact_session,
    mask_observation,
    optimize_format,
    run_context_pipeline,
)
from context_skills.primitives.budgeter import ContextComponent
from context_skills.primitives.service import run_primitive

server = Server("context-skills")

_PRIMITIVE_TOOLS = {
    "mask_observation",
    "compact_session",
    "budget_context",
    "optimize_format",
    "run_context_pipeline",
}


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="list_skills",
            description="Return the skill index (name and description only).",
            inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
        ),
        Tool(
            name="get_skill",
            description="Return full SKILL.md body and reference paths for a skill.",
            inputSchema={
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
                "additionalProperties": False,
            },
        ),
        Tool(
            name="route_task",
            description="Rank skills for a natural-language task using the lexical router.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task": {"type": "string"},
                    "top_k": {"type": "integer", "minimum": 1, "maximum": 28, "default": 5},
                },
                "required": ["task"],
                "additionalProperties": False,
            },
        ),
        Tool(
            name="get_reference",
            description="Load a reference markdown file for a skill.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "path": {"type": "string"},
                },
                "required": ["name", "path"],
                "additionalProperties": False,
            },
        ),
        Tool(
            name="mask_observation",
            description="Mask a verbose tool/observation output with a compact summary.",
            inputSchema={
                "type": "object",
                "properties": {
                    "tool_name": {"type": "string"},
                    "content": {},
                    "query": {"type": "string"},
                },
                "required": ["tool_name", "content"],
                "additionalProperties": False,
            },
        ),
        Tool(
            name="compact_session",
            description="Compact conversation history (hierarchical, handoff_summary, selective_retention).",
            inputSchema={
                "type": "object",
                "properties": {
                    "messages": {"type": "array"},
                    "text": {"type": "string"},
                    "mode": {
                        "type": "string",
                        "enum": ["hierarchical", "handoff_summary", "selective_retention"],
                    },
                },
                "additionalProperties": False,
            },
        ),
        Tool(
            name="budget_context",
            description="Fit context components under a token budget by priority.",
            inputSchema={
                "type": "object",
                "properties": {
                    "components": {"type": "array"},
                    "token_budget": {"type": "integer"},
                },
                "required": ["components", "token_budget"],
                "additionalProperties": False,
            },
        ),
        Tool(
            name="optimize_format",
            description="Compact verbose JSON or text payloads.",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {},
                    "kind": {"type": "string", "enum": ["json", "text", "auto"]},
                },
                "required": ["content"],
                "additionalProperties": False,
            },
        ),
        Tool(
            name="run_context_pipeline",
            description="Run the combined context optimization pipeline on a session payload.",
            inputSchema={
                "type": "object",
                "properties": {"session": {"type": "object"}},
                "required": ["session"],
                "additionalProperties": False,
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    args = arguments or {}

    if name == "list_skills":
        payload = list_skills()
    elif name == "get_skill":
        payload = get_skill(args["name"])
    elif name == "route_task":
        payload = route(args["task"], args.get("top_k", 5))
    elif name == "get_reference":
        payload = {
            "name": args["name"],
            "path": args["path"],
            "content": get_reference(args["name"], args["path"]),
        }
    elif name == "mask_observation":
        result = run_primitive(
            mask_observation,
            tool_name=args["tool_name"],
            content=args["content"],
            query=args.get("query"),
        )
        payload = {"output": result.output, "metrics": result.metrics.to_dict()}
    elif name == "compact_session":
        result = run_primitive(
            compact_session,
            messages=args.get("messages"),
            text=args.get("text"),
            mode=args.get("mode", "hierarchical"),
        )
        payload = {"output": result.output, "metrics": result.metrics.to_dict()}
    elif name == "budget_context":
        components = [ContextComponent(**item) for item in args["components"]]
        result = run_primitive(
            budget_context,
            components=components,
            token_budget=args["token_budget"],
        )
        payload = {"output": result.output, "metrics": result.metrics.to_dict()}
    elif name == "optimize_format":
        result = run_primitive(
            optimize_format,
            content=args["content"],
            kind=args.get("kind", "auto"),
        )
        payload = {"output": result.output, "metrics": result.metrics.to_dict()}
    elif name == "run_context_pipeline":
        result = run_primitive(run_context_pipeline, args["session"])
        payload = {"output": result.output, "metrics": result.metrics.to_dict()}
    else:
        raise ValueError(f"Unknown tool: {name}")

    return [TextContent(type="text", text=json.dumps(payload, indent=2))]


@server.list_resources()
async def list_resources() -> list[Resource]:
    resources: list[Resource] = []
    for item in list_skills():
        skill_name = item["name"]
        resources.append(
            Resource(
                uri=f"skill://{skill_name}",
                name=skill_name,
                description=item["description"],
                mimeType="text/markdown",
            )
        )
    return resources


@server.read_resource()
async def read_resource(uri: str) -> str:
    if not uri.startswith("skill://"):
        raise ValueError(f"Unsupported resource URI: {uri}")

    skill_name = uri.removeprefix("skill://")
    detail = get_skill(skill_name)
    return f"# {detail['name']}\n\n{detail['description']}\n\n{detail['body']}"


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
