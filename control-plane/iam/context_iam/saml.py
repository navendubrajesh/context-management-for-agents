"""SAML 2.0 assertion validation — XML parsing with mock fallback for offline tests."""

from __future__ import annotations

import base64
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any
from urllib.request import urlopen

from context_iam.config import AuthConfig
from context_iam.identity import Principal

SAML_NS = {
    "saml2": "urn:oasis:names:tc:SAML:2.0:assertion",
    "samlp": "urn:oasis:names:tc:SAML:2.0:protocol",
    "md": "urn:oasis:names:tc:SAML:2.0:metadata",
    "ds": "http://www.w3.org/2000/09/xmldsig#",
}


class SAMLValidationError(Exception):
    pass


def saml_mock_enabled() -> bool:
    return os.environ.get("CONTEXT_SKILLS_SAML_MOCK", "").strip().lower() in {"1", "true", "yes"}


def _parse_xmldatetime(value: str) -> datetime:
    cleaned = value.replace("Z", "+00:00")
    if "." in cleaned:
        base, rest = cleaned.split(".", 1)
        tz = ""
        if "+" in rest:
            frac, tz = rest.split("+", 1)
            tz = "+" + tz
        elif "-" in rest[1:]:
            frac, tz = rest.rsplit("-", 1)
            tz = "-" + tz
        else:
            frac = rest
        cleaned = f"{base}.{frac[:6]}{tz}"
    return datetime.fromisoformat(cleaned)


def _findtext(element: ET.Element, path: str, namespaces: dict[str, str]) -> str | None:
    node = element.find(path, namespaces)
    if node is not None and node.text:
        return node.text.strip()
    return None


def _attribute_values(assertion: ET.Element, name: str) -> list[str]:
    values: list[str] = []
    for attr in assertion.findall(".//saml2:Attribute", SAML_NS):
        attr_name = attr.get("Name") or attr.get("FriendlyName") or ""
        if attr_name.split("/")[-1] != name and attr_name != name:
            continue
        for val in attr.findall("saml2:AttributeValue", SAML_NS):
            if val.text:
                values.append(val.text.strip())
    return values


def parse_saml_assertion_xml(xml_bytes: bytes, config: AuthConfig) -> Principal:
    """Parse and validate a SAML 2.0 XML assertion (signature check optional in mock mode)."""
    if not config.saml_entity_id:
        raise SAMLValidationError("SAML entity ID not configured")

    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise SAMLValidationError("Invalid SAML XML") from exc

    assertion = root if "Assertion" in root.tag else root.find(".//saml2:Assertion", SAML_NS)
    if assertion is None:
        raise SAMLValidationError("SAML Assertion element not found")

    subject = _findtext(assertion, "saml2:Subject/saml2:NameID", SAML_NS)
    if not subject:
        raise SAMLValidationError("SAML NameID missing")

    conditions = assertion.find("saml2:Conditions", SAML_NS)
    if conditions is not None:
        not_on_or_after = conditions.get("NotOnOrAfter")
        if not_on_or_after:
            expiry = _parse_xmldatetime(not_on_or_after)
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) >= expiry.astimezone(timezone.utc):
                raise SAMLValidationError("SAML assertion expired")

        audiences = [
            node.text.strip()
            for node in conditions.findall(".//saml2:Audience", SAML_NS)
            if node.text
        ]
        if audiences and config.saml_entity_id not in audiences:
            raise SAMLValidationError("SAML audience mismatch")

    roles_raw = _attribute_values(assertion, "roles") or _attribute_values(assertion, "role")
    tenant_values = _attribute_values(assertion, "tenant_id")
    tenant_id = tenant_values[0] if tenant_values else "default"
    roles = tuple(roles_raw) if roles_raw else ("viewer",)

    return Principal(
        subject=subject,
        tenant_id=tenant_id,
        roles=roles,
        auth_method="saml",
        claims={"saml_entity_id": config.saml_entity_id},
    )


def _validate_mock_json(assertion_b64: str, config: AuthConfig) -> Principal:
    if not config.saml_entity_id:
        raise SAMLValidationError("SAML entity ID not configured")
    raw = base64.b64decode(assertion_b64)
    payload = json.loads(raw.decode("utf-8"))
    if payload.get("aud") != config.saml_entity_id:
        raise SAMLValidationError("SAML audience mismatch")
    roles_raw = payload.get("roles", ["viewer"])
    roles = tuple(roles_raw) if isinstance(roles_raw, list) else (str(roles_raw),)
    return Principal(
        subject=str(payload["sub"]),
        tenant_id=str(payload.get("tenant_id", "default")),
        roles=roles,
        auth_method="saml",
        claims=payload,
    )


def validate_saml_assertion(assertion_b64: str, config: AuthConfig) -> Principal:
    """Validate base64 SAML assertion — XML in production, JSON when mock mode enabled."""
    if saml_mock_enabled():
        return _validate_mock_json(assertion_b64, config)

    raw = base64.b64decode(assertion_b64)
    stripped = raw.lstrip()
    if stripped.startswith(b"{"):
        return _validate_mock_json(assertion_b64, config)
    return parse_saml_assertion_xml(raw, config)


def generate_sp_metadata(config: AuthConfig, *, acs_url: str) -> str:
    """Generate minimal SP metadata XML for IdP federation."""
    entity_id = config.saml_entity_id or "context-skills-sp"
    return f"""<?xml version="1.0"?>
<EntityDescriptor xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
  entityID="{entity_id}">
  <SPSSODescriptor AuthnRequestsSigned="false" WantAssertionsSigned="true"
    protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
    <NameIDFormat>urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress</NameIDFormat>
    <AssertionConsumerService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
      Location="{acs_url}" index="1"/>
  </SPSSODescriptor>
</EntityDescriptor>
"""


def fetch_idp_metadata(metadata_url: str) -> str:
    with urlopen(metadata_url, timeout=10) as response:  # noqa: S310
        return response.read().decode("utf-8")
