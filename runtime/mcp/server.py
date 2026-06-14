#!/usr/bin/env python3
"""MCP server exposing context-management-for-agents skills over stdio."""

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

server = Server("context-skills")


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
