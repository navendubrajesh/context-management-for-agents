# Context Skills MCP Server

Model Context Protocol server for discovering and routing Agent Skills.

## Tools

- `list_skills` — skill index (name + description)
- `get_skill(name)` — full SKILL.md body
- `route_task(task, top_k)` — lexical skill routing
- `get_reference(name, path)` — reference markdown

## Resources

Each skill is exposed as `skill://<name>` for MCP clients that prefer resources.

## Run (stdio)

```bash
pip install -e runtime/core -e runtime/mcp
cd runtime/mcp
python server.py
```

## Register in clients

### Cursor (`.cursor/mcp.json`)

```json
{
  "mcpServers": {
    "context-skills": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "/absolute/path/to/context-management-for-agents/runtime/mcp",
      "env": {
        "PYTHONPATH": "/absolute/path/to/context-management-for-agents/runtime/core"
      }
    }
  }
}
```

### GitHub Copilot / Claude Desktop

Use the same `mcp.json` snippet from `runtime/mcp/mcp.json`, adjusting absolute paths.

## Smoke test

```bash
python runtime/mcp/smoke_test.py
```

## Phase 2

HTTP/SSE transport can be added alongside stdio without changing tool handlers.
