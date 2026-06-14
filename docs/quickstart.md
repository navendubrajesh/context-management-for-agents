# Quickstart

## 5-minute path

### 1. Clone and install

```bash
git clone https://github.com/navendubrajesh/context-management-for-agents.git
cd context-management-for-agents
pip install -e runtime/core -e runtime/mcp -e runtime/api
```

### 2. Run the proof demo

```bash
python examples/demo/run_demo.py
python examples/demo/run_mcp_demo.py
```

Expected: router picks **context-compression**; handoff compaction shows **~93% token reduction** on the bundled conversation fixture.

### 3. Register MCP in Cursor / Copilot

`.cursor/mcp.json` (adjust paths):

```json
{
  "mcpServers": {
    "context-skills": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "/path/to/context-management-for-agents/runtime/mcp",
      "env": {
        "PYTHONPATH": "/path/to/context-management-for-agents/runtime/core"
      }
    }
  }
}
```

Tools: `list_skills`, `route_task`, `get_skill`, `compact_session`, `run_context_pipeline`, and more.

### 4. One-line REST smoke test

```bash
uvicorn app:app --app-dir runtime/api --port 8080 &
curl -s http://localhost:8080/skills | head -c 200
```

### 5. Install skills into your editor (optional)

```bash
npx context-management-for-agents --platform cursor
```

## npm package

```bash
npm i context-management-for-agents
```

See the [root README](https://github.com/navendubrajesh/context-management-for-agents#installation) for all platform targets.

## Next steps

- [Runtime reference](runtime.md)
- [Benchmarks](benchmarks.md) — reproduce measurements
- [Enterprise deployment](ENTERPRISE.md) — SSO, tenancy, policy (Phase 3)
