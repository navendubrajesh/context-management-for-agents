"""Vault interface — env/file adapters; no secrets in code or logs."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Protocol

_SECRET_PATTERN = re.compile(
    r"(api[_-]?key|secret|password|token|authorization)\s*[:=]\s*\S+",
    re.IGNORECASE,
)


class Vault(Protocol):
    def get(self, key: str) -> str | None: ...


class EnvVault:
    def get(self, key: str) -> str | None:
        return os.environ.get(key)


class FileVault:
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self._cache: dict[str, str] | None = None

    def _load(self) -> dict[str, str]:
        if self._cache is None:
            if self.path.is_file():
                self._cache = json.loads(self.path.read_text(encoding="utf-8"))
            else:
                self._cache = {}
        return self._cache

    def get(self, key: str) -> str | None:
        return self._load().get(key)


def get_vault() -> Vault:
    vault_type = os.environ.get("CONTEXT_SKILLS_VAULT_TYPE", "env").lower()
    if vault_type == "file":
        path = os.environ.get("CONTEXT_SKILLS_VAULT_PATH", "secrets.json")
        return FileVault(path)
    return EnvVault()


def redact_text(text: str) -> str:
    return _SECRET_PATTERN.sub(r"\1=***REDACTED***", text)
