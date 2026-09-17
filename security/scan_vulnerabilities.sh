#!/usr/bin/env bash
# Vulnerability scan against SBOM (grype + allowlist).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SBOM="${ROOT}/security/sbom/runtime.cdx.json"
STRICT=0
for arg in "$@"; do
  if [ "$arg" = "--strict" ]; then
    STRICT=1
  fi
done

ARGS=(--sbom "$SBOM" --min-severity High)
if [ "$STRICT" -eq 1 ]; then
  ARGS+=(--strict)
fi

python "${ROOT}/security/vuln_scan.py" "${ARGS[@]}"
