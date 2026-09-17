# Supply-chain integrity

Scripts for SBOM generation, artifact signing, vulnerability scanning, and signature verification.

## Tools (CI)

- [Syft](https://github.com/anchore/syft) — CycloneDX SBOM (preferred)
- Python `sbom_generator.py` — offline fallback when syft is unavailable
- [Grype](https://github.com/anchore/grype) — vulnerability scan
- [Cosign](https://github.com/sigstore/cosign) — artifact signing (Sigstore), SHA256 fallback

## Usage

```bash
# Generate SBOM (strict mode fails on empty components)
./security/generate_sbom.sh --strict
python security/sbom_generator.py --strict

# Scan with allowlist (High/Critical unless allowlisted)
./security/scan_vulnerabilities.sh --strict
python security/vuln_scan.py --strict

# Sign and verify
./security/sign_artifacts.sh security/sbom/runtime.cdx.json
python security/verify_signature.py security/sbom/runtime.cdx.json
```

## Policy gate

- CI runs SBOM generation in strict mode (non-empty components required).
- CI runs grype with `security/vuln-allowlist.json` — fails on unallowlisted **High** or **Critical** findings.
- Release artifacts must pass `verify_signature.py` before install (SHA256 or cosign bundle).

## Allowlist format

Edit `security/vuln-allowlist.json`:

```json
{
  "schema_version": 1,
  "entries": [
    {"id": "CVE-2024-0001", "reason": "false positive", "expires": "2026-12-31"}
  ]
}
```
