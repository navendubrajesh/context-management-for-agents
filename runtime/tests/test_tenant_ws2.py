from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi.testclient import TestClient

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
    get_usage_sink().clear()


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


def test_tenant_skill_isolation(client: TestClient) -> None:
    tenant_a = {"Authorization": f"Bearer {_token('a', 'viewer', 'tenant-a')}"}
    tenant_b = {"Authorization": f"Bearer {_token('b', 'viewer', 'tenant-b')}"}
    skills_a = {s["name"] for s in client.get("/skills", headers=tenant_a).json()}
    skills_b = {s["name"] for s in client.get("/skills", headers=tenant_b).json()}
    assert "context-fundamentals" in skills_a
    assert "context-fundamentals" not in skills_b
    assert "tool-design" in skills_b
    assert client.get("/skills/tool-design", headers=tenant_a).status_code == 404
    assert client.get("/skills/context-fundamentals", headers=tenant_b).status_code == 404


def test_usage_scoped_by_tenant(client: TestClient) -> None:
    op_a = {"Authorization": f"Bearer {_token('op-a', 'operator', 'tenant-a')}"}
    op_b = {"Authorization": f"Bearer {_token('op-b', 'operator', 'tenant-b')}"}
    client.post("/primitives/mask_observation", headers=op_a, json={"tool_name": "t", "content": "x" * 50})
    client.post("/primitives/mask_observation", headers=op_b, json={"tool_name": "t", "content": "y" * 50})
    usage_a = client.get("/usage", headers={"Authorization": f"Bearer {_token('v-a', 'viewer', 'tenant-a')}"}).json()
    usage_b = client.get("/usage", headers={"Authorization": f"Bearer {_token('v-b', 'viewer', 'tenant-b')}"}).json()
    assert all(r["tenant_id"] == "tenant-a" for r in usage_a["records"])
    assert all(r["tenant_id"] == "tenant-b" for r in usage_b["records"])
