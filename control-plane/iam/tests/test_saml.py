from __future__ import annotations

import base64
import json
from pathlib import Path

import pytest

from context_iam.config import AuthConfig
from context_iam.saml import (
    SAMLValidationError,
    generate_sp_metadata,
    parse_saml_assertion_xml,
    validate_saml_assertion,
)

FIXTURE = Path(__file__).parent / "fixtures" / "saml_assertion.xml"
ENTITY_ID = "https://context-skills.example.com"


@pytest.fixture
def config() -> AuthConfig:
    return AuthConfig(
        mode="enforced",
        oidc_issuer=None,
        oidc_audience=None,
        oidc_jwks_uri=None,
        oidc_hmac_secret=None,
        saml_entity_id=ENTITY_ID,
        saml_metadata_url="https://idp.example.com/metadata",
        api_keys_raw=None,
    )


def test_parse_saml_xml_assertion(config: AuthConfig) -> None:
    principal = parse_saml_assertion_xml(FIXTURE.read_bytes(), config)
    assert principal.subject == "saml-user@example.com"
    assert principal.tenant_id == "tenant-a"
    assert "viewer" in principal.roles
    assert principal.auth_method == "saml"


def test_validate_saml_assertion_b64_xml(config: AuthConfig, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CONTEXT_SKILLS_SAML_MOCK", raising=False)
    encoded = base64.b64encode(FIXTURE.read_bytes()).decode("ascii")
    principal = validate_saml_assertion(encoded, config)
    assert principal.subject == "saml-user@example.com"


def test_saml_mock_json_mode(config: AuthConfig, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CONTEXT_SKILLS_SAML_MOCK", "1")
    payload = {
        "sub": "mock-user",
        "aud": ENTITY_ID,
        "tenant_id": "tenant-b",
        "roles": ["operator"],
    }
    encoded = base64.b64encode(json.dumps(payload).encode()).decode("ascii")
    principal = validate_saml_assertion(encoded, config)
    assert principal.subject == "mock-user"
    assert principal.tenant_id == "tenant-b"
    assert principal.roles == ("operator",)


def test_saml_audience_mismatch(config: AuthConfig, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CONTEXT_SKILLS_SAML_MOCK", raising=False)
    encoded = base64.b64encode(FIXTURE.read_bytes()).decode("ascii")
    bad_config = AuthConfig(
        mode="enforced",
        oidc_issuer=None,
        oidc_audience=None,
        oidc_jwks_uri=None,
        oidc_hmac_secret=None,
        saml_entity_id="wrong-entity",
        saml_metadata_url=None,
        api_keys_raw=None,
    )
    with pytest.raises(SAMLValidationError, match="audience"):
        validate_saml_assertion(encoded, bad_config)


def test_sp_metadata_contains_acs(config: AuthConfig) -> None:
    xml = generate_sp_metadata(config, acs_url="https://api.example.com/auth/saml/acs")
    assert ENTITY_ID in xml
    assert "https://api.example.com/auth/saml/acs" in xml
    assert "SPSSODescriptor" in xml
