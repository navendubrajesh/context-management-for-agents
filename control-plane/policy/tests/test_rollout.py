from __future__ import annotations

from context_policy.rollout import get_rollout_store


def test_canary_rollout_and_rollback() -> None:
    store = get_rollout_store()
    store.rollout(version="3.1.0", tenant_ids=["tenant-a"], canary=True)
    assert store.resolve_version("tenant-a") == "3.1.0"
    assert store.resolve_version("tenant-b") != "3.1.0"
    event = store.rollback()
    assert event["action"] == "rollback"
