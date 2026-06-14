# Context Skills Runtime (Phase 2)

Programmatic runtime for discovering, routing, and **applying** Agent Skills with measured context primitives, telemetry, and FinOps metering.

## Layout

| Directory | Purpose |
|-----------|---------|
| `core/` | Loader, router, **primitives**, LLM provider, metering, telemetry |
| `mcp/` | MCP stdio server (skills + primitives) |
| `api/` | FastAPI REST service |
| `sdk-python/` | Python client (local + REST) |
| `sdk-ts/` | TypeScript client (local skills + remote primitives) |
| `tests/` | pytest + vitest suites |

## Quick start

```bash
# Install Python packages (from repo root)
pip install -e runtime/core -e runtime/api -e runtime/mcp -e runtime/sdk-python

# Run tests
pytest runtime/tests
cd runtime/sdk-ts && npm install && npm test

# Run REST API with telemetry (console exporter)
set OTEL_SERVICE_NAME=context-skills-api
set OTEL_TRACES_EXPORTER=console
uvicorn app:app --app-dir runtime/api --host 0.0.0.0 --port 8080

# Docker
docker compose -f runtime/docker-compose.yml up --build
```

## Phase 2 primitives

| Primitive | MCP tool | REST endpoint |
|-----------|----------|---------------|
| Observation masking | `mask_observation` | `POST /primitives/mask_observation` |
| Session compaction | `compact_session` | `POST /primitives/compact_session` |
| Token budgeter | `budget_context` | `POST /primitives/budget_context` |
| Format optimization | `optimize_format` | `POST /primitives/optimize_format` |
| Combined pipeline | `run_context_pipeline` | `POST /primitives/run_context_pipeline` |

Usage records: `GET /usage?limit=50`

## Example — curl

```bash
curl -s http://localhost:8080/primitives/mask_observation \
  -H "Content-Type: application/json" \
  -d '{"tool_name":"database_query","content":"{\"rows\":[{\"id\":1}],\"row_count\":1,\"query\":\"SELECT 1\",\"status\":\"ok\",\"execution_time_ms\":12}"}'

curl -s http://localhost:8080/usage
```

## Example — Python SDK

```python
from context_skills_sdk import SkillsClient

client = SkillsClient(base_url="http://localhost:8080")
result = client.mask_observation(tool_name="database_query", content={"rows": [], "row_count": 0, "query": "SELECT 1", "status": "ok", "execution_time_ms": 1})
print(result["metrics"])
print(client.get_usage())
```

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OTEL_SERVICE_NAME` | No | Service name for OpenTelemetry (default: `context-skills-api`) |
| `OTEL_TRACES_EXPORTER` | No | `console` (default) or configure OTLP via standard OTel env vars |
| `CONTEXT_SKILLS_LLM_PROVIDER` | No | `offline` (default) or `http` with `CONTEXT_SKILLS_LLM_BASE_URL`, `CONTEXT_SKILLS_LLM_MODEL`, `CONTEXT_SKILLS_LLM_API_KEY` |

Pricing for `est_cost_usd` is **operator-configured** in `runtime/core/context_skills/metering/pricing.json` — placeholder values only.

## Phase 3 extension points

- `tenant_id` on `UsageRecord` (null in Phase 2)
- `context_skills.policy.evaluate_policy()` — allow-all stub for future OPA/RBAC
