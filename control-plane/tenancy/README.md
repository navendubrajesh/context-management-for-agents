# Multi-tenancy

Per-tenant configuration and isolation for skills, usage, policies, and telemetry.

## Tenant configuration

Each tenant has:

- `enabled_skills` — allow-list (empty = all skills)
- `llm_provider` — operator-configured provider id
- `pricing_tier` — optional pricing override key

## Environment

- `CONTEXT_SKILLS_TENANTS_FILE` — optional JSON file with tenant definitions

## API

When auth is enforced, tenant context comes from the authenticated principal.
Admin routes: `GET/POST /tenants` (requires `tenants:manage`).
