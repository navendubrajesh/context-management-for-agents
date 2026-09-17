# Policy-as-code

Externalized policies (OPA bundles) and human-in-the-loop approval gates.

## OPA

Set `CONTEXT_SKILLS_OPA_URL` to an OPA server (e.g. `http://localhost:8181`).
When unset, an embedded evaluator mirrors the bundled Rego policy for offline tests.

Bundled Rego: `bundles/contextskills.rego`. Build bundle:

```bash
./scripts/build_bundle.sh
```

Tenant-scoped denials are injected into OPA input via `context_policy.tenant_config`
so embedded and HTTP OPA paths stay aligned.

## Approvals

High-impact operations (`skills:publish`, `tenants:manage`) can require approval.
Configure via `CONTEXT_SKILLS_APPROVAL_REQUIRED=skills:publish,tenants:manage`.

Policy decisions are logged to the audit subsystem when available.
