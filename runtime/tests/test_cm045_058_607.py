from __future__ import annotations

from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Thread

import jwt
import pytest
from fastapi.testclient import TestClient

from context_finops.quota_alerts import get_quota_alert_store
from context_finops.quotas import get_quota_store
from context_tenancy.store import get_tenant_store


@pytest.fixture
def client() -> TestClient:
    import app as api_app

    return TestClient(api_app.app)


@pytest.fixture(autouse=True)
def reset_stores(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CONTEXT_SKILLS_AUTH_MODE", "enforced")
    monkeypatch.setenv("CONTEXT_SKILLS_OIDC_HMAC_SECRET", "test-secret-key-at-least-32-bytes!!")
    monkeypatch.setenv("CONTEXT_SKILLS_OIDC_ISSUER", "https://mock-idp.local")
    monkeypatch.setenv("CONTEXT_SKILLS_OIDC_AUDIENCE", "context-skills-api")
    get_quota_store().reset()
    get_quota_alert_store().reset_fired()


def _token(*, roles: str = "admin", tenant: str = "tenant-a") -> dict[str, str]:
    tok = jwt.encode(
        {
            "sub": "test-user",
            "iss": "https://mock-idp.local",
            "aud": "context-skills-api",
            "roles": roles,
            "tenant_id": tenant,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        },
        "test-secret-key-at-least-32-bytes!!",
        algorithm="HS256",
    )
    return {"Authorization": f"Bearer {tok}"}


def test_quota_webhook_fires_at_threshold() -> None:
    received: list[dict] = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:  # noqa: N802
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length).decode("utf-8")
            received.append({"path": self.path, "body": body})
            self.send_response(200)
            self.end_headers()

        def log_message(self, format: str, *args) -> None:  # noqa: A003
            return

    server = HTTPServer(("127.0.0.1", 0), Handler)
    port = server.server_address[1]
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        store = get_quota_alert_store()
        store.set_config("tenant-a", callback_url=f"http://127.0.0.1:{port}/hook")
        quota = get_quota_store()
        quota._token_usage["tenant-a"] = 400_000  # noqa: SLF001 — 80% of 500k
        quota._maybe_quota_alert("tenant-a")
        assert received
        assert "80" in received[0]["body"]
    finally:
        server.shutdown()


def test_tenant_admin_overview_and_skills(client: TestClient) -> None:
    headers = _token(roles="tenant-admin", tenant="tenant-a")
    overview = client.get("/tenant-admin/overview", headers=headers)
    assert overview.status_code == 200
    assert overview.json()["tenant"]["tenant_id"] == "tenant-a"

    patch = client.patch(
        "/tenant-admin/skills",
        headers=headers,
        json={"enabled_skills": ["context-compression", "evaluation"]},
    )
    assert patch.status_code == 200
    assert "context-compression" in patch.json()["enabled_skills"]


def test_tenant_admin_invite_user(client: TestClient) -> None:
    headers = _token(roles="tenant-admin", tenant="tenant-a")
    invite = client.post(
        "/tenant-admin/users/invite",
        headers=headers,
        json={"email": "new.user@example.com", "display_name": "New User", "roles": ["viewer"]},
    )
    assert invite.status_code == 201
    users = client.get("/tenant-admin/users", headers=headers)
    assert any(u["userName"] == "new.user@example.com" for u in users.json()["users"])


def test_configure_quota_alerts_api(client: TestClient) -> None:
    headers = _token(roles="admin", tenant="tenant-a")
    put = client.put(
        "/finops/alerts/quota",
        headers=headers,
        json={"callback_url": "https://hooks.example.com/quota", "thresholds": [80, 95]},
    )
    assert put.status_code == 200
    get = client.get("/finops/alerts/quota", headers=headers)
    assert get.json()["configured"] is True


def test_demo_gif_exists() -> None:
    gif = Path(__file__).resolve().parents[2] / "assets" / "demo.gif"
    assert gif.is_file()
    assert gif.stat().st_size > 100
