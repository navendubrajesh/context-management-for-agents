from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from context_audit.log import get_audit_log
from context_tenancy.store import TenantConfig, get_tenant_store


@pytest.fixture
def sqlite_env(monkeypatch: pytest.MonkeyPatch, tmp_path) -> str:
    url = f"sqlite:///{(tmp_path / 'platform.db').as_posix()}"
    monkeypatch.setenv("CONTEXT_SKILLS_DATABASE_URL", url)
    monkeypatch.setenv("CONTEXT_SKILLS_AUTH_MODE", "disabled")
    from context_storage.database import get_engine, init_database

    get_engine.cache_clear()
    init_database()
    import context_tenancy.store as tenant_module

    tenant_module._GLOBAL_STORE = tenant_module.TenantStore()
    get_audit_log().clear()
    return url


def test_tenant_upsert_persists_to_sqlite(sqlite_env: str) -> None:
    store = get_tenant_store()
    store.upsert(
        TenantConfig(
            tenant_id="tenant-persist",
            name="Persist Tenant",
            enabled_skills=["evaluation"],
            region="ap-south-1",
        )
    )
    from context_storage.repositories import TenantRepository

    repo = TenantRepository()
    row = repo.get("tenant-persist")
    assert row is not None
    assert row["region"] == "ap-south-1"


def test_audit_event_persists_to_sqlite(sqlite_env: str) -> None:
    log = get_audit_log()
    log.append(
        event_type="integration.test",
        actor="tester",
        tenant_id="tenant-a",
        correlation_id="c1",
        detail={"phase": "CM-065"},
    )
    from context_storage.repositories import AuditRepository

    repo = AuditRepository()
    events = repo.list_events(tenant_id="tenant-a")
    assert any(e["event_type"] == "integration.test" for e in events)
