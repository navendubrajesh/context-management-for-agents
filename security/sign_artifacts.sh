#!/usr/bin/env bash
# Sign release artifacts (cosign bundle or SHA256 checksum).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ARTIFACT="${1:-${ROOT}/security/sbom/runtime.cdx.json}"

python -c "
import sys
from pathlib import Path
sys.path.insert(0, '${ROOT}')
from security.signing import sign_artifact
result = sign_artifact(Path('${ARTIFACT}'), prefer_cosign=True)
print(f\"Signed {result['artifact']} via {result['method']}\")
if result.get('signature'):
    print(f\"  SHA256: {result['signature']}\")
if result.get('bundle'):
    print(f\"  Bundle: {result['bundle']}\")
"
