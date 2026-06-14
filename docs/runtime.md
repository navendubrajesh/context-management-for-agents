# Runtime reference

Phase 1–3 runtime under `runtime/`. Default auth is **disabled** (`CONTEXT_SKILLS_AUTH_MODE=disabled`); Phase 3 enterprise controls are optional.

## MCP server

```bash
pip install -e runtime/core -e runtime/mcp
python runtime/mcp/server.py
```

| Tool | Description |
|------|-------------|
| `list_skills` | Skill index (name + description) |
| `get_skill` | Full SKILL.md body + reference paths |
| `route_task` | Rank skills for a natural-language task |
| `get_reference` | Load a reference markdown file |
| `mask_observation` | Compact verbose tool output |
| `compact_session` | Compress conversation history |
| `budget_context` | Fit components under token budget |
| `optimize_format` | Compact JSON/text payloads |
| `run_context_pipeline` | Combined session optimization |

Resources: `skill://<name>` for each skill.

## REST API

```bash
pip install -e runtime/core -e runtime/api
uvicorn app:app --app-dir runtime/api --host 0.0.0.0 --port 8080
```

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/healthz` | GET | Health check |
| `/skills` | GET | Skill index |
| `/skills/{name}` | GET | Skill detail |
| `/route` | POST | Route a task |
| `/primitives/*` | POST | Context primitives |
| `/usage` | GET | Usage records (estimated cost) |

OpenAPI: `http://localhost:8080/docs` when the server is running.

## SDKs

- **Python:** `runtime/sdk-python/` — `pip install -e runtime/sdk-python`
- **TypeScript:** `runtime/sdk-typescript/`

Both call the same public loader and router as MCP/REST.

## Docker

```bash
docker compose -f runtime/docker-compose.yml up --build
```

## Enterprise (Phase 3)

When auth is enforced: OIDC/SAML, SCIM, RBAC, multi-tenancy, OPA policy, audit log, FinOps. See [Enterprise deployment](ENTERPRISE.md).
