#!/usr/bin/env bash
# Build offline air-gap bundle: wheels, SBOM, signatures, Helm/Terraform copies.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
BUNDLE="${ROOT}/deploy/airgapped/bundle"
WHEELS="${BUNDLE}/wheels"
IMAGES="${BUNDLE}/images"
SBOM_DIR="${BUNDLE}/sbom"
SIG_DIR="${BUNDLE}/signatures"

rm -rf "${BUNDLE}"
mkdir -p "${WHEELS}" "${IMAGES}" "${SBOM_DIR}" "${SIG_DIR}"

echo "==> Building Python wheels"
pip wheel --wheel-dir "${WHEELS}" \
  "${ROOT}/runtime/core" \
  "${ROOT}/runtime/api" \
  "${ROOT}/runtime/mcp" \
  "${ROOT}/control-plane/iam" \
  "${ROOT}/control-plane/tenancy" \
  "${ROOT}/control-plane/policy" \
  "${ROOT}/control-plane/audit" \
  "${ROOT}/control-plane/finops" \
  "${ROOT}/control-plane/storage"

echo "==> Generating SBOM"
python "${ROOT}/security/sbom_generator.py" --strict --out "${SBOM_DIR}/runtime.cdx.json"
python -c "
import sys
sys.path.insert(0, '${ROOT}')
from security.signing import sign_artifact
from pathlib import Path
sign_artifact(Path('${SBOM_DIR}/runtime.cdx.json'), prefer_cosign=False)
"
cp "${SBOM_DIR}/runtime.cdx.json.sha256" "${SIG_DIR}/" 2>/dev/null || true

echo "==> Copying deploy artifacts"
mkdir -p "${BUNDLE}/deploy"
cp -r "${ROOT}/deploy/helm" "${BUNDLE}/deploy/"
cp -r "${ROOT}/deploy/terraform" "${BUNDLE}/deploy/"

echo "==> Saving container images (if docker available)"
if command -v docker >/dev/null 2>&1; then
  docker pull openpolicyagent/opa:0.68.0 || true
  docker save openpolicyagent/opa:0.68.0 -o "${IMAGES}/opa-0.68.0.tar" 2>/dev/null || \
    echo "Skipping OPA image save (image not available locally)"
else
  echo "docker not found — skipping image tar export"
fi

echo "==> Writing bundle manifest"
cat > "${BUNDLE}/manifest.json" <<EOF
{
  "name": "context-skills-airgap-bundle",
  "version": "3.0.0",
  "created": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "contents": ["wheels/", "images/", "sbom/", "signatures/", "deploy/"]
}
EOF

echo "Air-gap bundle ready at ${BUNDLE}"
