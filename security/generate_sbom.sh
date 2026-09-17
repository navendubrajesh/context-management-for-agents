#!/usr/bin/env bash
# Generate CycloneDX SBOM for runtime + control-plane packages.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${ROOT}/security/sbom/runtime.cdx.json"
STRICT=0
for arg in "$@"; do
  if [ "$arg" = "--strict" ]; then
    STRICT=1
  fi
done

mkdir -p "$(dirname "$OUT")"

if command -v syft >/dev/null 2>&1; then
  syft packages dir:"${ROOT}/runtime" dir:"${ROOT}/control-plane" -o cyclonedx-json > "$OUT"
  echo "SBOM written to $OUT (syft)"
else
  echo "syft not found — using Python SBOM generator"
  python "${ROOT}/security/sbom_generator.py" --out "$OUT" $([ "$STRICT" -eq 1 ] && echo --strict)
fi

# Fail strict builds when SBOM has no components
if [ "$STRICT" -eq 1 ]; then
  python -c "
import json, sys
from pathlib import Path
p = Path('${OUT}')
data = json.loads(p.read_text(encoding='utf-8'))
if not data.get('components'):
    print('ERROR: strict mode requires non-empty SBOM components', file=sys.stderr)
    sys.exit(1)
print(f\"Strict SBOM check passed ({len(data['components'])} components)\")
"
fi
