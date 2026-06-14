from __future__ import annotations

import pytest

from context_audit.log import get_audit_log
from context_audit.vault import redact_text


def test_audit_hash_chain() -> None:
    log = get_audit_log()
    log.clear()
    log.append(event_type="test.a", actor="u1", tenant_id="t1", correlation_id="c1", detail={"x": 1})
    log.append(event_type="test.b", actor="u2", tenant_id="t1", correlation_id="c2", detail={"y": 2})
    assert log.verify_chain()
    ordered = list(reversed(log.events()))
    assert ordered[0].prev_hash == log.GENESIS
    assert ordered[1].prev_hash == ordered[0].event_hash


def test_secrets_redacted() -> None:
    text = "api_key=supersecret12345 authorization: Bearer abc"
    redacted = redact_text(text)
    assert "supersecret" not in redacted
    assert "REDACTED" in redacted
