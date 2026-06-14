# Supply-chain integrity

Scripts for SBOM generation, artifact signing, vulnerability scanning, and signature verification.

## Tools (CI)

- [Syft](https://github.com/anchore/syft) — CycloneDX SBOM
- [Grype](https://github.com/anchore/grype) — vulnerability scan
- [Cosign](https://github.com/sigstore/cosign) — artifact signing (Sigstore)

## Usage

```bash
./security/generate_sbom.sh
./security/scan_vulnerabilities.sh
./security/sign_artifacts.sh
python security/verify_signature.py <artifact> <signature>
```

## Policy gate

CI fails on CRITICAL vulnerabilities unless listed in `security/vuln-allowlist.json`.
Unsigned artifacts are rejected by the skill registry verifier.
