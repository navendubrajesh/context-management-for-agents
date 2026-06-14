# Context Skills Runtime (Phase 1)

Programmatic runtime for discovering and routing Agent Skills without modifying skill content.

## Layout

| Directory | Purpose |
|-----------|---------|
| `core/` | Loader, manifest schema, lexical router |
| `mcp/` | MCP stdio server |
| `api/` | FastAPI REST service |
| `sdk-python/` | Python client (local + REST) |
| `sdk-ts/` | TypeScript client (local + REST) |
| `tests/` | pytest + vitest suites |

## Quick start

```bash
# Install Python packages (from repo root)
pip install -e runtime/core -e runtime/api -e runtime/mcp -e runtime/sdk-python

# Run tests
pytest runtime/tests
cd runtime/sdk-ts && npm install && npm test

# Run REST API
uvicorn app:app --app-dir runtime/api --host 0.0.0.0 --port 8080

# Run MCP server (stdio)
python runtime/mcp/server.py

# Docker
docker compose -f runtime/docker-compose.yml up --build
```

## Phase 2 hooks

The REST API includes a no-op middleware layer for future auth, policy, and budgeting services.
