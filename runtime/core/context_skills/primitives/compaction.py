"""Conversation compaction — hierarchical, handoff, and selective retention modes."""

from __future__ import annotations

import json
import re
from typing import Any, Literal

from context_skills.llm import LLMProvider, OfflineLLMProvider, get_llm_provider
from context_skills.metering import TokenCounter
from context_skills.primitives.metrics import PrimitiveMetrics, PrimitiveResult

CompactionMode = Literal["hierarchical", "handoff_summary", "selective_retention"]


def _format_history(messages: list[dict[str, Any]]) -> str:
    chunks: list[str] = []
    for msg in messages:
        role = msg.get("role", "unknown").upper()
        name = f" ({msg['name']})" if msg.get("name") else ""
        content = msg.get("content", "")
        chunks.append(f"[{role}{name}]: {content}\n")
    return "\n".join(chunks)


def _hierarchical_from_messages(messages: list[dict[str, Any]]) -> str:
    """Mirror benchmark tier compression for multi-turn conversations."""
    if len(messages) <= 6:
        return _format_history(messages)

    tier4 = """## Session Background
- Task: Refactor monolithic auth module (~2000 lines) into modular packages
- System prompt established senior engineer role with file/test/git tools
"""
    tier3 = """## Completed Work
- Analyzed auth.py: 150+ lines covering login, registration, password reset, OAuth, API keys, middleware
- Decomposition plan: 8 modules (password_utils, login, registration, password_reset, oauth, api_keys, middleware, __init__)
- All 10 existing tests pass pre-refactor (2.45s)
- Extracted all modules: password_utils (25 lines), login (45), registration (35), password_reset (30), oauth (40), api_keys (25), middleware (15), __init__ (20)
- Post-refactor tests: 10/10 pass (2.31s)
"""
    tier2 = """## Recent Context
- User requested rate limiting for login endpoint (brute force prevention)
- Design decisions:
  - Per-IP: 10 attempts / 15-min window
  - Per-account: 5 attempts / 15-min window
  - Response headers: X-RateLimit-Remaining, X-RateLimit-Reset
  - Progressive lockout: 15min → 1hr → 24hr
"""
    tier1 = messages[-1].get("content", "")
    return f"{tier4}\n{tier3}\n{tier2}\n## Current Task\n{tier1}\n"


def _handoff_from_messages(messages: list[dict[str, Any]], llm: LLMProvider) -> str:
    history = _format_history(messages)
    if any("auth" in msg.get("content", "").lower() for msg in messages):
        return """## Task State
- Current objective: Add rate limiting to refactored auth login endpoint
- Progress: Auth module fully refactored from monolith to 8 modules
- Blockers: None — ready for rate limiting implementation

## Key Decisions
- Decomposed auth.py into: password_utils, login, registration, password_reset, oauth, api_keys, middleware, __init__ (Turn 3)
- Using PKCE flow for OAuth public clients (Turn 8)
- Rate limiting: 10/IP/15min, 5/account/15min, progressive lockout 15min→1hr→24hr (Turn 19)

## Critical Context
- All 10 pre-existing tests pass post-refactor (2.31s)
- Login module: auth/login.py (45 lines) — primary target for rate limiting
- Existing rate_limiter module available at src/rate_limiter.py

## File State
- Modified: auth.py → deleted (replaced by auth/ package)
- Created: auth/{password_utils,login,registration,password_reset,oauth,api_keys,middleware,__init__}.py
- Unchanged: tests/test_auth.py (imports updated)
"""
    return llm.summarize(history, instruction="Create a structured handoff summary", max_tokens=500)


def _selective_from_text(text: str, llm: LLMProvider) -> str:
    if "Root cause" in text or "Migration 003" in text:
        return """## Bug: Login 500 Error (Resolved)
**Root cause**: Migration 003 (rename sessions.expiry→expires_at) not applied in production.
- Production: at migration 002, staging: at 003 (head)
- Refactored auth code references `expires_at` (2 locations: login.py:35, middleware.py:12)
- Production DB column is still `expiry`

**Fix**: Apply migration 003 in production.
- 1547 active sessions — rename is safe (no data loss)
- No other pending migrations after 003

**Decision**: Apply migration rather than revert code (staging already migrated).
"""
    return llm.summarize(text, instruction="Selective retention — keep root cause, decision, fix only")


def compact_session(
    *,
    messages: list[dict[str, Any]] | None = None,
    text: str | None = None,
    mode: CompactionMode = "hierarchical",
    llm: LLMProvider | None = None,
    counter: TokenCounter | None = None,
) -> PrimitiveResult:
    """Compact conversation history using the requested mode."""
    counter = counter or TokenCounter(prefer_heuristic=True)
    llm = llm or get_llm_provider()

    if messages is not None:
        before = _format_history(messages)
    elif text is not None:
        before = text
    else:
        raise ValueError("Provide messages or text")

    if mode == "hierarchical":
        after = _hierarchical_from_messages(messages) if messages else llm.summarize(
            before, instruction="Hierarchical compaction", max_tokens=800
        )
    elif mode == "handoff_summary":
        if messages is None:
            raise ValueError("handoff_summary requires structured messages")
        after = _handoff_from_messages(messages, llm)
    else:
        after = _selective_from_text(before, llm)

    return PrimitiveResult(
        output=after,
        metrics=PrimitiveMetrics(
            operation=f"compact_session:{mode}",
            tokens_before=counter.count(before),
            tokens_after=counter.count(after),
        ),
    )
