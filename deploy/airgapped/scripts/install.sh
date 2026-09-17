#!/usr/bin/env bash
# Offline install from air-gap bundle (see deploy/airgapped/README.md).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
BUNDLE="${ROOT}/deploy/airgapped/bundle"
DRY_RUN=0
if [ "${1:-}" = "--dry-run" ]; then
  DRY_RUN=1
fi

if [ ! -d "${BUNDLE}" ]; then
  echo "Bundle not found. Run deploy/airgapped/scripts/build_bundle.sh first." >&2
  exit 1
fi

if [ "${DRY_RUN}" -eq 1 ]; then
  echo "Dry run: bundle present at ${BUNDLE}"
  test -f "${BUNDLE}/manifest.json"
  exit 0
fi

echo "==> Verify SBOM signature"
python "${ROOT}/security/verify_signature.py" "${BUNDLE}/sbom/runtime.cdx.json"

echo "==> Install Python wheels offline"
pip install --no-index --find-links "${BUNDLE}/wheels" \
  -e "${ROOT}/runtime/core" \
  -e "${ROOT}/runtime/api" \
  -e "${ROOT}/control-plane/storage"

echo "==> Load container images"
if [ -d "${BUNDLE}/images" ]; then
  for image in "${BUNDLE}/images/"*.tar; do
    [ -f "$image" ] || continue
    docker load -i "$image"
  done
fi

echo "==> Deploy with Helm"
helm upgrade --install context-skills "${BUNDLE}/deploy/helm/context-skills" \
  --set auth.mode=enforced \
  --set opa.sidecar=true

echo "Offline install complete"
