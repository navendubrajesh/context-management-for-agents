from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi.testclient import TestClient

from context_policy.approvals import get_approval_store
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
    get_approval_store().clear()


def _token(sub: str, roles: str, tenant: str) -> str:
    return jwt.encode(
        {
            "sub": sub,
            "iss": "https://mock-idp.local",
            "aud": "context-skills-api",
            "roles": roles,
            "tenant_id": tenant,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        },
        "test-secret-key-at-least-32-bytes!!",
        algorithm="HS256",
    )


def test_policy_denies_skill_for_tenant(client: TestClient) -> None:
    headers = {"Authorization": f"Bearer {_token('v', 'viewer', 'tenant-c')}"}
    assert client.get("/skills/advanced-evaluation", headers=headers).status_code == 403
    assert client.get("/skills/evaluation", headers=headers).status_code == 200


def test_publish_requires_approval(client: TestClient) -> None:
    author = {"Authorization": f"Bearer {_token('auth', 'author', 'tenant-a')}"}
    created = client.post("/approvals", headers=author, json={"operation": "skills:publish", "payload": {"skill": "x"}})
    assert created.status_code == 201
    approval_id = created.json()["id"]
    admin = {"Authorization": f"Bearer {_token('adm', 'admin', 'tenant-a')}"}
    decided = client.post(f"/approvals/{approval_id}/decide", headers=admin, json={"approve": True})
    assert decided.status_code == 200
    assert decided.json()["status"] == "approved"


def test_policy_allows_same_skill_for_other_tenants(client: TestClient) -> None:
    # default tenant has full catalog; policy denial is tenant-c specific
    headers = {"Authorization": f"Bearer {_token('v', 'viewer', 'default')}"}
    assert client.get("/skills/advanced-evaluation", headers=headers).status_code == 200


def test_policy_denied_skill_returns_403_not_404(client: TestClient) -> None:
    headers = {"Authorization": f"Bearer {_token('v', 'viewer', 'tenant-c')}"}
    response = client.get("/skills/advanced-evaluation", headers=headers)
    assert response.status_code == 403
    assert response.status_code != 404
