"""Artifact signing and verification — SHA256 checksums and optional cosign bundles."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_signature_path(artifact: Path) -> Path:
    return Path(str(artifact) + ".sha256")


def sigstore_bundle_path(artifact: Path) -> Path:
    return Path(str(artifact) + ".sigstore.json")


def sign_sha256(artifact: Path) -> Path:
    sig_path = sha256_signature_path(artifact)
    sig_path.write_text(sha256_file(artifact) + "\n", encoding="utf-8")
    return sig_path


def sign_cosign(artifact: Path) -> Path | None:
    bundle = sigstore_bundle_path(artifact)
    proc = subprocess.run(
        ["cosign", "sign-blob", "--yes", str(artifact), "--bundle", str(bundle)],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return None
    if not bundle.is_file():
        return None
    return bundle


def sign_artifact(artifact: Path, *, prefer_cosign: bool = True) -> dict[str, Any]:
    if not artifact.is_file():
        raise FileNotFoundError(artifact)

    result: dict[str, Any] = {"artifact": str(artifact), "method": "sha256"}
    if prefer_cosign:
        bundle = sign_cosign(artifact)
        if bundle is not None:
            result["method"] = "cosign"
            result["bundle"] = str(bundle)
            return result

    sig = sign_sha256(artifact)
    result["signature"] = str(sig)
    return result


def verify_sha256(artifact: Path, signature_path: Path | None = None) -> bool:
    sig = signature_path or sha256_signature_path(artifact)
    if not sig.is_file():
        return False
    expected = sig.read_text(encoding="utf-8").strip().split()[0]
    return sha256_file(artifact) == expected


def verify_cosign_bundle(artifact: Path, bundle_path: Path | None = None) -> bool:
    bundle = bundle_path or sigstore_bundle_path(artifact)
    if not bundle.is_file():
        return False
    proc = subprocess.run(
        ["cosign", "verify-blob", str(artifact), "--bundle", str(bundle)],
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode == 0


def verify_artifact(artifact: Path, signature_path: Path | None = None) -> bool:
    if not artifact.is_file():
        return False
    if verify_sha256(artifact, signature_path):
        return True
    try:
        return verify_cosign_bundle(artifact)
    except FileNotFoundError:
        return False
