from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi.testclient import TestClient

from context_finops.quotas import get_quota_store
from context_skills.metering import get_usage_sink
from context_skills.paths import find_repo_root


@pytest.fixture
def client() -> TestClient:
    import app as api_app

    api_app.app.state.repo_root = str(find_repo_root())
    return TestClient(api_app.app)


@pytest.fixture(autouse=True)
def reset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CONTEXT_SKILLS_AUTH_MODE", "enforced")
    monkeypatch.setenv("CONTEXT_SKILLS_OIDC_HMAC_SECRET", "test-secret-key-at-least-32-bytes!!")
    monkeypatch.setenv("CONTEXT_SKILLS_OIDC_ISSUER", "https://mock-idp.local")
    monkeypatch.setenv("CONTEXT_SKILLS_OIDC_AUDIENCE", "context-skills-api")
    get_quota_store().reset()
    get_usage_sink().clear()


def _token(tenant: str) -> dict[str, str]:
    tok = jwt.encode(
        {
            "sub": "op",
            "iss": "https://mock-idp.local",
            "aud": "context-skills-api",
            "roles": "operator",
            "tenant_id": tenant,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        },
        "test-secret-key-at-least-32-bytes!!",
        algorithm="HS256",
    )
    return {"Authorization": f"Bearer {tok}"}


def test_quota_blocks_when_enforced(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CONTEXT_SKILLS_QUOTA_ENFORCE", "block")
    store = get_quota_store()
    store._token_usage["tenant-b"] = 200_000  # noqa: SLF001
    response = client.post(
        "/primitives/mask_observation",
        headers=_token("tenant-b"),
        json={"tool_name": "t", "content": "x" * 50},
    )
    assert response.status_code == 429


def test_chargeback_report(client: TestClient) -> None:
    client.post(
        "/primitives/mask_observation",
        headers=_token("tenant-a"),
        json={"tool_name": "t", "content": "x" * 50},
    )
    report = client.get("/finops/chargeback", headers=_token("tenant-a")).json()
    assert report["disclaimer"] == "estimated — operator-configured pricing"
    assert len(report["tenants"]) >= 1
