"""Token counting with tiktoken and documented heuristic fallback."""

from __future__ import annotations

import json
from typing import Any

try:
    import tiktoken

    _ENCODING = tiktoken.get_encoding("cl100k_base")
    _TIKTOKEN_AVAILABLE = True
except Exception:  # noqa: BLE001
    _ENCODING = None
    _TIKTOKEN_AVAILABLE = False


def heuristic_count_tokens(text: str) -> int:
    """Benchmark-compatible BPE approximation (~3.7 chars/token)."""
    if not text:
        return 0
    char_estimate = len(text) / 3.7
    word_estimate = len(text.split())
    return int(max(char_estimate, word_estimate))


class TokenCounter:
    """Count tokens using tiktoken when available, else heuristic fallback."""

    def __init__(self, *, prefer_heuristic: bool = False) -> None:
        self.prefer_heuristic = prefer_heuristic

    @property
    def method(self) -> str:
        if self.prefer_heuristic or not _TIKTOKEN_AVAILABLE:
            return "heuristic"
        return "tiktoken_cl100k_base"

    def count(self, text: str) -> int:
        if not text:
            return 0
        if not self.prefer_heuristic and _TIKTOKEN_AVAILABLE and _ENCODING is not None:
            return len(_ENCODING.encode(text))
        return heuristic_count_tokens(text)

    def count_json(self, obj: Any, *, indent: int | None = 2) -> int:
        if indent is None:
            payload = json.dumps(obj, separators=(",", ":"))
        else:
            payload = json.dumps(obj, indent=indent)
        return self.count(payload)
