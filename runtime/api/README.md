# Context Skills REST API

Stateless FastAPI service exposing skill discovery and routing.

## Run locally

```bash
pip install -e runtime/core -e runtime/api
uvicorn app:app --app-dir runtime/api --host 0.0.0.0 --port 8080
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/healthz` | Liveness probe |
| GET | `/skills` | Skill index (name + description) |
| GET | `/skills/{name}` | Full skill body + reference paths |
| POST | `/route` | Lexical routing (`{"task": "...", "top_k": 5}`) |
| GET | `/skills/{name}/references/{path}` | Reference markdown content |

OpenAPI docs: `http://localhost:8080/docs`

## Example

```bash
curl http://localhost:8080/skills
curl -X POST http://localhost:8080/route \
  -H "Content-Type: application/json" \
  -d '{"task":"How do I compress conversation history for a handoff?","top_k":3}'
```

## Phase 2 hooks

`phase2_middleware` in `app.py` is a no-op placeholder for future auth, RBAC, and policy enforcement.
