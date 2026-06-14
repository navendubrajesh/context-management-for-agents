#!/usr/bin/env bash
# Generate CycloneDX SBOM for runtime packages (requires syft in PATH).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${ROOT}/security/sbom/runtime.cdx.json"
mkdir -p "$(dirname "$OUT")"
if command -v syft >/dev/null 2>&1; then
  syft packages dir:"${ROOT}/runtime" -o cyclonedx-json > "$OUT"
  echo "SBOM written to $OUT"
else
  echo '{"bomFormat":"CycloneDX","specVersion":"1.4","components":[],"metadata":{"component":{"name":"context-skills-runtime","type":"application"}}}' > "$OUT"
  echo "syft not found — stub SBOM written to $OUT"
fi
