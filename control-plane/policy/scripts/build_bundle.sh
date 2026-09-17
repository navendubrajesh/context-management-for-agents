#!/usr/bin/env bash
# Build OPA policy bundle from bundled Rego (requires opa in PATH).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUNDLE_DIR="${ROOT}/bundles"
OUT="${BUNDLE_DIR}/contextskills.tar.gz"

mkdir -p "${BUNDLE_DIR}"

if command -v opa >/dev/null 2>&1; then
  opa build -b "${BUNDLE_DIR}" -o "${OUT}"
  echo "OPA bundle written to ${OUT}"
else
  tar -czf "${OUT}" -C "${BUNDLE_DIR}" contextskills.rego
  echo "opa not found — Rego-only bundle written to ${OUT}"
fi
