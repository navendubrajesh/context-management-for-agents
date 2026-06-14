"""Repository root discovery for offline skill loading."""

from __future__ import annotations

import os
from pathlib import Path


def _as_path(value: Path | str | None) -> Path:
    if value is None:
        return Path(__file__).resolve()
    return Path(value).resolve()


def find_repo_root(start: Path | str | None = None) -> Path:
    """Walk upward from *start* until a directory containing ``skills/`` is found."""
    current = _as_path(start)
    if current.is_file():
        current = current.parent

    for candidate in [current, *current.parents]:
        if (candidate / "skills").is_dir() and (candidate / "researcher").is_dir():
            return candidate

    raise FileNotFoundError(
        "Could not locate repository root (expected skills/ and researcher/ directories)"
    )


def skills_dir(repo_root: Path | str | None = None) -> Path:
    """Return the absolute path to the ``skills/`` directory."""
    root = _as_path(repo_root) if repo_root is not None else find_repo_root()
    return root / "skills"


def corpus_index_path(repo_root: Path | str | None = None) -> Path:
    """Return the absolute path to ``researcher/corpus/index.json``."""
    root = _as_path(repo_root) if repo_root is not None else find_repo_root()
    return root / "researcher" / "corpus" / "index.json"
