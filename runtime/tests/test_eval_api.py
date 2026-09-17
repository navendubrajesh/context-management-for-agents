from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi.testclient import TestClient

from context_skills.paths import find_repo_root
from researcher.eval.store import get_eval_store


@pytest.fixture
def client() -> TestClient:
    import app as api_app

    api_app.app.state.repo_root = str(find_repo_root())
    get_eval_store().clear()
    return TestClient(api_app.app)


@pytest.fixture(autouse=True)
def auth_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CONTEXT_SKILLS_AUTH_MODE", "enforced")
    monkeypatch.setenv("CONTEXT_SKILLS_OIDC_HMAC_SECRET", "test-secret-key-at-least-32-bytes!!")
    monkeypatch.setenv("CONTEXT_SKILLS_OIDC_ISSUER", "https://mock-idp.local")
    monkeypatch.setenv("CONTEXT_SKILLS_OIDC_AUDIENCE", "context-skills-api")


def _token(roles: str = "operator") -> str:
    return jwt.encode(
        {
            "sub": "eval-user",
            "iss": "https://mock-idp.local",
            "aud": "context-skills-api",
            "roles": roles,
            "tenant_id": "tenant-a",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        },
        "test-secret-key-at-least-32-bytes!!",
        algorithm="HS256",
    )


def test_eval_run_passes_benchmark_gate(client: TestClient) -> None:
    headers = {"Authorization": f"Bearer {_token('operator')}"}
    response = client.post(
        "/eval/run",
        headers=headers,
        json={
            "checks": [
                {"type": "benchmark_threshold", "technique": "Handoff Summary", "min_savings_pct": 90}
            ]
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pass"
    assert data["passed"] is True
    assert data["id"]


def test_eval_results_list(client: TestClient) -> None:
    headers = {"Authorization": f"Bearer {_token('viewer')}"}
    client.post(
        "/eval/run",
        headers={"Authorization": f"Bearer {_token('operator')}"},
        json={"checks": []},
    )
    response = client.get("/eval/results", headers=headers)
    assert response.status_code == 200
    assert len(response.json()["results"]) >= 1


def test_eval_run_forbidden_for_viewer(client: TestClient) -> None:
    headers = {"Authorization": f"Bearer {_token('viewer')}"}
    response = client.post("/eval/run", headers=headers, json={"checks": []})
    assert response.status_code == 403
