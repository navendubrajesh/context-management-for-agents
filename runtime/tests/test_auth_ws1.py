from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi.testclient import TestClient

from context_iam.scim import get_scim_store
from context_skills.paths import find_repo_root


@pytest.fixture
def client() -> TestClient:
    import app as api_app

    api_app.app.state.repo_root = str(find_repo_root())
    return TestClient(api_app.app)


@pytest.fixture(autouse=True)
def reset_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CONTEXT_SKILLS_AUTH_MODE", raising=False)
    monkeypatch.delenv("CONTEXT_SKILLS_OIDC_HMAC_SECRET", raising=False)
    monkeypatch.delenv("CONTEXT_SKILLS_OIDC_ISSUER", raising=False)
    monkeypatch.delenv("CONTEXT_SKILLS_OIDC_AUDIENCE", raising=False)
    monkeypatch.delenv("CONTEXT_SKILLS_API_KEYS", raising=False)
    get_scim_store().clear()


def _token(sub: str, roles: str, tenant: str = "tenant-a") -> str:
    return jwt.encode(
        {
            "sub": sub,
            "iss": "https://mock-idp.local",
            "aud": "context-skills-api",
            "roles": roles,
            "tenant_id": tenant,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        },
        "test-secret",
        algorithm="HS256",
    )


def test_unauthenticated_denied_when_enforced(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CONTEXT_SKILLS_AUTH_MODE", "enforced")
    monkeypatch.setenv("CONTEXT_SKILLS_OIDC_HMAC_SECRET", "test-secret")
    monkeypatch.setenv("CONTEXT_SKILLS_OIDC_ISSUER", "https://mock-idp.local")
    monkeypatch.setenv("CONTEXT_SKILLS_OIDC_AUDIENCE", "context-skills-api")
    response = client.get("/skills")
    assert response.status_code == 401


def test_viewer_can_read_skills_not_run_primitives(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CONTEXT_SKILLS_AUTH_MODE", "enforced")
    monkeypatch.setenv("CONTEXT_SKILLS_OIDC_HMAC_SECRET", "test-secret")
    monkeypatch.setenv("CONTEXT_SKILLS_OIDC_ISSUER", "https://mock-idp.local")
    monkeypatch.setenv("CONTEXT_SKILLS_OIDC_AUDIENCE", "context-skills-api")
    headers = {"Authorization": f"Bearer {_token('viewer1', 'viewer')}"}
    assert client.get("/skills", headers=headers).status_code == 200
    assert client.post("/primitives/mask_observation", headers=headers, json={"tool_name": "t", "content": "x"}).status_code == 403


def test_operator_can_run_primitives(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CONTEXT_SKILLS_AUTH_MODE", "enforced")
    monkeypatch.setenv("CONTEXT_SKILLS_OIDC_HMAC_SECRET", "test-secret")
    monkeypatch.setenv("CONTEXT_SKILLS_OIDC_ISSUER", "https://mock-idp.local")
    monkeypatch.setenv("CONTEXT_SKILLS_OIDC_AUDIENCE", "context-skills-api")
    headers = {"Authorization": f"Bearer {_token('op1', 'operator')}"}
    response = client.post(
        "/primitives/mask_observation",
        headers=headers,
        json={"tool_name": "database_query", "content": "verbose output " * 20},
    )
    assert response.status_code == 200


def test_api_key_auth(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CONTEXT_SKILLS_AUTH_MODE", "enforced")
    monkeypatch.setenv("CONTEXT_SKILLS_API_KEYS", "orch-key:operator:tenant-b")
    headers = {"X-API-Key": "orch-key"}
    response = client.post(
        "/primitives/optimize_format",
        headers=headers,
        json={"content": "I have successfully read the file located at `src/auth/login.py`. The file contains 45 lines of Python code that implement the login functionality including the `login()` function, the `logout()` function, the `create_session()` helper function, and the `record_failed_attempt()` helper function. The file imports from `password_utils`, `models`, and `database` modules."},
    )
    assert response.status_code == 200


def test_scim_requires_admin(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CONTEXT_SKILLS_AUTH_MODE", "enforced")
    monkeypatch.setenv("CONTEXT_SKILLS_OIDC_HMAC_SECRET", "test-secret")
    monkeypatch.setenv("CONTEXT_SKILLS_OIDC_ISSUER", "https://mock-idp.local")
    monkeypatch.setenv("CONTEXT_SKILLS_OIDC_AUDIENCE", "context-skills-api")
    viewer = {"Authorization": f"Bearer {_token('v', 'viewer')}"}
    assert client.get("/scim/v2/Users", headers=viewer).status_code == 403
    admin = {"Authorization": f"Bearer {_token('a', 'admin')}"}
    created = client.post("/scim/v2/Users", headers=admin, json={"userName": "jane", "displayName": "Jane"})
    assert created.status_code == 201
    assert client.get("/scim/v2/Users", headers=admin).json()["totalResults"] == 1


def test_phase12_unchanged_when_auth_disabled(client: TestClient) -> None:
    assert client.get("/healthz").status_code == 200
    assert client.get("/skills").status_code == 200
    assert len(client.get("/skills").json()) == 28
