from __future__ import annotations

import os

import pytest

from context_storage.database import get_engine, init_database, is_database_enabled
from context_storage.repositories import ApprovalRepository, AuditRepository, TenantRepository


@pytest.fixture(autouse=True)
def sqlite_db(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    db_path = tmp_path / "test.db"
    url = f"sqlite:///{db_path.as_posix()}"
    monkeypatch.setenv("CONTEXT_SKILLS_DATABASE_URL", url)
    get_engine.cache_clear()
    init_database()
    yield
    monkeypatch.delenv("CONTEXT_SKILLS_DATABASE_URL", raising=False)
    get_engine.cache_clear()


def test_database_enabled() -> None:
    assert is_database_enabled() is True


def test_tenant_repository_roundtrip() -> None:
    repo = TenantRepository()
    repo.upsert("tenant-x", "Tenant X", ["evaluation"], region="eu-west-1")
    row = repo.get("tenant-x")
    assert row is not None
    assert row["name"] == "Tenant X"
    assert "evaluation" in row["enabled_skills"]
    assert row["region"] == "eu-west-1"


def test_audit_repository_append_and_list() -> None:
    repo = AuditRepository()
    event = {
        "id": "evt-1",
        "timestamp": "2026-01-01T00:00:00Z",
        "event_type": "test.event",
        "actor": "tester",
        "tenant_id": "tenant-a",
        "correlation_id": "corr-1",
        "detail": {"ok": True},
        "prev_hash": "0" * 64,
        "event_hash": "abc123",
    }
    repo.append(event)
    items = repo.list_events(tenant_id="tenant-a", limit=10)
    assert len(items) == 1
    assert items[0]["event_type"] == "test.event"


def test_approval_repository_save_and_get() -> None:
    repo = ApprovalRepository()
    item = {
        "id": "appr-1",
        "operation": "skills:publish",
        "tenant_id": "tenant-a",
        "actor": "author",
        "status": "pending",
        "created_at": "2026-01-01T00:00:00Z",
        "payload": {"skill": "x"},
        "decided_by": None,
        "decided_at": None,
        "reason": None,
    }
    repo.save(item)
    loaded = repo.get("appr-1")
    assert loaded is not None
    assert loaded["status"] == "pending"
    assert loaded["payload"]["skill"] == "x"
