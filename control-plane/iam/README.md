# IAM — Identity & Access (Phase 3 WS1)

OIDC/SAML authentication, SCIM 2.0 provisioning, RBAC, and API-key service auth for the context skills runtime.

## Auth modes

| `CONTEXT_SKILLS_AUTH_MODE` | Behavior |
|----------------------------|----------|
| `disabled` (default) | Phase 1–2 unchanged — no auth required |
| `enforced` | Deny-by-default; Bearer JWT or `X-API-Key` required |

## OIDC (config-driven)

```bash
CONTEXT_SKILLS_OIDC_ISSUER=https://idp.example.com
CONTEXT_SKILLS_OIDC_AUDIENCE=context-skills-api
CONTEXT_SKILLS_OIDC_JWKS_URI=https://idp.example.com/.well-known/jwks.json
# Optional HS256 for local/mock IdP:
CONTEXT_SKILLS_OIDC_HMAC_SECRET=dev-only-secret
```

## API keys

```bash
CONTEXT_SKILLS_API_KEYS="svc-orchestrator:operator:tenant-a,key2:viewer:tenant-b"
# format: key_id:role:tenant_id (comma-separated)
```

## RBAC roles

| Role | Permissions |
|------|-------------|
| viewer | skills:read, usage:read |
| author | viewer + skills:publish |
| operator | viewer + primitives:run |
| admin | all permissions |

## SCIM 2.0

Mount at `/scim/v2` when auth is enforced (requires admin role for mutating calls in production configs).
