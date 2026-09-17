"""Shared file IO helpers for researcher eval tooling."""

from __future__ import annotations

import json
from pathlib import Path


def read_json(path: Path) -> dict | list:
    """Load JSON from UTF-8 or UTF-16 encoded files."""
    raw = path.read_bytes()
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        text = raw.decode("utf-16")
    elif raw.startswith(b"\xef\xbb\xbf"):
        text = raw.decode("utf-8-sig")
    else:
        text = raw.decode("utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        obj, _ = json.JSONDecoder().raw_decode(text.lstrip("\ufeff"))
        return obj
