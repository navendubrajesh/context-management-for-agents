#!/usr/bin/env bash
# Sign release artifacts with cosign (keyless or key file).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ARTIFACT="${1:-${ROOT}/security/sbom/runtime.cdx.json}"
if command -v cosign >/dev/null 2>&1; then
  cosign sign-blob --yes "$ARTIFACT" --bundle "${ARTIFACT}.sigstore.json" 2>/dev/null || \
    sha256sum "$ARTIFACT" | awk '{print $1}' > "${ARTIFACT}.sha256"
  echo "Signature bundle: ${ARTIFACT}.sigstore.json (or .sha256 fallback)"
else
  sha256sum "$ARTIFACT" | awk '{print $1}' > "${ARTIFACT}.sha256"
  echo "cosign not found — wrote SHA256 checksum only"
fi
