from __future__ import annotations

import base64
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

FIXTURE = (
    Path(__file__).resolve().parents[2]
    / "control-plane"
    / "iam"
    / "tests"
    / "fixtures"
    / "saml_assertion.xml"
)


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("CONTEXT_SKILLS_SAML_ENTITY_ID", "https://context-skills.example.com")
    monkeypatch.delenv("CONTEXT_SKILLS_SAML_MOCK", raising=False)
    import app as api_app

    return TestClient(api_app.app)


def test_saml_metadata_endpoint(client: TestClient) -> None:
    response = client.get("/auth/saml/metadata")
    assert response.status_code == 200
    assert "application/samlmetadata+xml" in response.headers.get("content-type", "")
    assert "SPSSODescriptor" in response.text


def test_policy_version_endpoint(client: TestClient) -> None:
    response = client.get("/policy/version")
    assert response.status_code == 200
    data = response.json()
    assert data["bundle"] == "contextskills"
    assert data["version"] == "3.0.0"


def test_saml_acs_accepts_xml_response(client: TestClient) -> None:
    encoded = base64.b64encode(FIXTURE.read_bytes()).decode("ascii")
    response = client.post("/auth/saml/acs", data={"SAMLResponse": encoded})
    assert response.status_code == 200
    data = response.json()
    assert data["subject"] == "saml-user@example.com"
    assert data["tenant_id"] == "tenant-a"
