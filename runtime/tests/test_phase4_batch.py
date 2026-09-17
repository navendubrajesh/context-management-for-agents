from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
import pytest
from fastapi.testclient import TestClient

from context_skills.freshness import is_stale
from context_skills.residency import is_air_gapped, telemetry_allowed
from context_skills.session_health import classify_session_health


@pytest.fixture
def client() -> TestClient:
    import app as api_app

    return TestClient(api_app.app)


@pytest.fixture(autouse=True)
def auth_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CONTEXT_SKILLS_AUTH_MODE", "enforced")
    monkeypatch.setenv("CONTEXT_SKILLS_OIDC_HMAC_SECRET", "test-secret-key-at-least-32-bytes!!")
    monkeypatch.setenv("CONTEXT_SKILLS_OIDC_ISSUER", "https://mock-idp.local")
    monkeypatch.setenv("CONTEXT_SKILLS_OIDC_AUDIENCE", "context-skills-api")


def _token(roles: str = "admin") -> str:
    return jwt.encode(
        {
            "sub": "batch-user",
            "iss": "https://mock-idp.local",
            "aud": "context-skills-api",
            "roles": roles,
            "tenant_id": "tenant-a",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        },
        "test-secret-key-at-least-32-bytes!!",
        algorithm="HS256",
    )


def test_session_health_zones() -> None:
    healthy = classify_session_health(50000, context_limit=128000)
    assert healthy["zone"] == "healthy"
    degraded = classify_session_health(120000, context_limit=128000)
    assert degraded["zone"] in {"degraded", "critical"}


def test_freshness_stale_detection() -> None:
    assert is_stale(last_reviewed="2020-01-01", freshness_days=90) is True
    assert is_stale(last_reviewed="2099-01-01", freshness_days=90) is False


def test_policy_rollout_api(client: TestClient) -> None:
    headers = {"Authorization": f"Bearer {_token('admin')}"}
    response = client.post("/policy/rollout", headers=headers, json={"version": "3.1.0", "canary": True, "tenant_ids": ["tenant-a"]})
    assert response.status_code == 200
    version = client.get("/policy/version", headers={**headers, "x-tenant-id": "tenant-a"})
    assert version.json()["version"] == "3.1.0"


def test_pricing_admin_api(client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pricing_file = tmp_path / "pricing.json"
    pricing_file.write_text(
        json.dumps(
            {
                "default_model": "gpt-4o-mini",
                "default_tier": "standard",
                "tiers": {"standard": {"default_model": "gpt-4o-mini"}},
                "models": {"gpt-4o-mini": {"input_per_1k_tokens_usd": 0.001, "output_per_1k_tokens_usd": 0.002}},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("CONTEXT_SKILLS_PRICING_PATH", str(pricing_file))
    headers = {"Authorization": f"Bearer {_token('admin')}"}
    response = client.get("/finops/pricing", headers=headers)
    assert response.status_code == 200
    update = client.put("/finops/pricing", headers=headers, json={"table": response.json()})
    assert update.status_code == 200


def test_marketplace_submit_and_install(client: TestClient) -> None:
    headers = {"Authorization": f"Bearer {_token('admin')}"}
    submit = client.post(
        "/marketplace/submit",
        headers=headers,
        json={"name": "custom-skill", "version": "1.0.0", "description": "demo"},
    )
    assert submit.status_code == 201
    approval_id = submit.json()["approval"]["id"]
    client.post(f"/approvals/{approval_id}/decide", headers=headers, json={"approve": True})
    entry_id = submit.json()["entry"]["id"]
    install = client.post(f"/marketplace/{entry_id}/install", headers=headers)
    assert install.status_code == 200


def test_efficiency_metrics(client: TestClient) -> None:
    headers = {"Authorization": f"Bearer {_token('operator')}"}
    response = client.get("/metrics/efficiency", headers=headers)
    assert response.status_code == 200
    assert "savings_pct" in response.json()


def test_residency_airgap_blocks_telemetry(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CONTEXT_SKILLS_DEPLOYMENT_MODE", "air-gapped")
    assert is_air_gapped() is True
    assert telemetry_allowed() is False


def test_console_auth_login_redirect(client: TestClient) -> None:
    response = client.get("/console/auth/login", follow_redirects=False)
    assert response.status_code in {302, 307}
