"""Verify artifact signatures before serving/installing skills."""

from __future__ import annotations

import sys
from pathlib import Path

from security.signing import sha256_file, verify_artifact


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


__all__ = ["sha256_file", "verify_artifact", "main"]
