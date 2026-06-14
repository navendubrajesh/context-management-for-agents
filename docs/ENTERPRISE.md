# Enterprise deployment guide (Phase 3)

This platform supports regulated enterprise deployment patterns. It **enables** controls that map to common compliance frameworks — it does **not** imply SOC 2, FedRAMP, or ISO certification.

## Architecture

```
Clients → SSO (OIDC/SAML) → API + Console
                ↓
         RBAC + OPA policy + Approvals
                ↓
    Tenants → Skills / Primitives / Usage / Audit
```

## Local stack (mock IdP, OPA, vault)

```powershell
# Install packages
pip install -e control-plane/iam -e control-plane/tenancy -e control-plane/policy `
  -e control-plane/audit -e control-plane/finops -e runtime/core -e runtime/api

# Mock IdP (HMAC JWT)
$env:CONTEXT_SKILLS_AUTH_MODE = "enforced"
$env:CONTEXT_SKILLS_OIDC_HMAC_SECRET = "dev-secret-at-least-32-characters-long"
$env:CONTEXT_SKILLS_OIDC_ISSUER = "https://mock-idp.local"
$env:CONTEXT_SKILLS_OIDC_AUDIENCE = "context-skills-api"
$env:CONTEXT_SKILLS_CONSOLE = "enabled"

# Start API
cd runtime/api; uvicorn app:app --port 8080
```

Generate a test token (Python):

```python
import jwt, datetime
print(jwt.encode({"sub":"admin1","iss":"https://mock-idp.local","aud":"context-skills-api",
  "roles":"admin","tenant_id":"tenant-a","exp":datetime.datetime.utcnow()+datetime.timedelta(hours=1)},
  "dev-secret-at-least-32-characters-long", algorithm="HS256"))
```

Open http://localhost:8080/console/ — paste token, browse catalog.

## Workstream exercise flows

| WS | Flow |
|----|------|
| WS1 | Unauthenticated `GET /skills` → 401; viewer token → 200; viewer `POST /primitives/*` → 403 |
| WS2 | tenant-a vs tenant-b skill lists differ; usage scoped per tenant |
| WS3 | tenant-c `GET /skills/advanced-evaluation` → 403; create + approve publish request |
| WS4 | `GET /audit/events` shows hash chain; secrets redacted in logs |
| WS5 | Set `CONTEXT_SKILLS_QUOTA_ENFORCE=block`; exceed quota → 429; `GET /finops/chargeback` |
| WS6 | `./security/generate_sbom.sh`; `python security/verify_signature.py ...` |
| WS7 | Console catalog + usage + audit panels |
| WS8 | `helm template deploy/helm/context-skills`; air-gap per `deploy/airgapped/README.md` |

## Deployment modes

- **SaaS** — multi-tenant, shared cluster
- **Customer VPC** — Terraform module with dedicated region
- **Air-gapped** — offline bundle, embedded OPA, file vault

## Default behavior (Phases 1–2)

`CONTEXT_SKILLS_AUTH_MODE=disabled` (default) preserves prior behavior with no auth prompts.
