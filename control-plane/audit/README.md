# Audit, lineage & secrets

## Audit log

Append-only, hash-chained security event log. Export via `GET /audit/events`.

## Lineage

Primitive operations record input/output references (hashes) — no payloads by default.

## Secrets

Use `CONTEXT_SKILLS_VAULT_TYPE=env|file` with `CONTEXT_SKILLS_VAULT_PATH`.
Secrets are redacted from logs/traces via middleware.
