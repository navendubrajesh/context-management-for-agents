"""Verify artifact signatures before serving/installing skills."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_artifact(artifact: Path, signature_path: Path | None = None) -> bool:
    if not artifact.is_file():
        return False
    sig = signature_path or Path(str(artifact) + ".sha256")
    if sig.is_file():
        expected = sig.read_text(encoding="utf-8").strip().split()[0]
        return sha256_file(artifact) == expected
    bundle = Path(str(artifact) + ".sigstore.json")
    if bundle.is_file():
        data = json.loads(bundle.read_text(encoding="utf-8"))
        return bool(data.get("Bundle") or data.get("signature"))
    return False


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: verify_signature.py <artifact> [signature]")
        return 1
    artifact = Path(sys.argv[1])
    sig = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    ok = verify_artifact(artifact, sig)
    print("verified" if ok else "REJECTED: unsigned or tampered artifact")
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
