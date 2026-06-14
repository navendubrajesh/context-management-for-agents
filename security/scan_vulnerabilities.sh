#!/usr/bin/env bash
# Vulnerability scan against SBOM (requires grype).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SBOM="${ROOT}/security/sbom/runtime.cdx.json"
if command -v grype >/dev/null 2>&1 && [ -f "$SBOM" ]; then
  grype "sbom:$SBOM" --fail-on critical
else
  echo "grype not installed or SBOM missing — skipping scan (offline/dev mode)"
fi
