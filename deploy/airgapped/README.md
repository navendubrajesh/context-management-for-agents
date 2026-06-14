# Air-gapped installation

Offline bundle for on-prem deployments without outbound network access.

## Bundle contents

1. Vendored Python wheels (`wheels/`)
2. Pre-pulled container images (`images/*.tar`)
3. SBOM + checksums (`sbom/`)
4. Signature bundles (`signatures/`)
5. Helm chart + Terraform module (this repo `deploy/`)

## Procedure

1. Transfer `deploy/airgapped/bundle/` to the target environment.
2. Verify signatures: `python security/verify_signature.py sbom/runtime.cdx.json sbom/runtime.cdx.json.sha256`
3. Load images: `docker load -i images/context-skills-api.tar`
4. Install wheels offline: `pip install --no-index --find-links wheels/ -e runtime/core -e runtime/api`
5. Deploy: `helm install context-skills deploy/helm/context-skills --set auth.mode=enforced`
6. Configure mock IdP / vault / OPA from local files (no external calls).

## Offline policy & auth

- OPA: embedded evaluator (default when `CONTEXT_SKILLS_OPA_URL` unset)
- OIDC: HMAC secret for local IdP JWTs
- Vault: `CONTEXT_SKILLS_VAULT_TYPE=file`

## Region pinning

Set `CONTEXT_SKILLS_REGION` and disable external telemetry exporters.
