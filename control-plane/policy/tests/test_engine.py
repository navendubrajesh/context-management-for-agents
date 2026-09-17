from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from context_policy.engine import PolicyDecision, evaluate_opa
from context_policy.tenant_config import enrich_policy_payload, tenant_denials


def test_tenant_denials_for_tenant_c() -> None:
    denials = tenant_denials("tenant-c")
    assert "advanced-evaluation" in denials["denied_skills"]
    assert "gpt-4o" in denials["denied_models"]


def test_tenant_denials_empty_for_other_tenants() -> None:
    denials = tenant_denials("tenant-a")
    assert denials["denied_skills"] == []
    assert denials["denied_models"] == []


def test_enrich_policy_payload_injects_tenant_denials() -> None:
    payload = enrich_policy_payload(
        {"tenant_id": "tenant-c", "skill": "advanced-evaluation", "rbac_allowed": True}
    )
    assert "advanced-evaluation" in payload["denied_skills"]
    assert "gpt-4o" in payload["denied_models"]


def test_embedded_denies_skill_for_tenant_c() -> None:
    decision = evaluate_opa(
        {
            "tenant_id": "tenant-c",
            "skill": "advanced-evaluation",
            "rbac_allowed": True,
            "operation": "skills:read",
        }
    )
    assert decision.allowed is False
    assert "Skill denied" in decision.reason


def test_embedded_allows_other_skills_for_tenant_c() -> None:
    decision = evaluate_opa(
        {
            "tenant_id": "tenant-c",
            "skill": "evaluation",
            "rbac_allowed": True,
            "operation": "skills:read",
        }
    )
    assert decision.allowed is True


def test_embedded_denies_model_for_tenant_c() -> None:
    decision = evaluate_opa(
        {
            "tenant_id": "tenant-c",
            "model": "gpt-4o",
            "rbac_allowed": True,
            "operation": "primitives:run",
        }
    )
    assert decision.allowed is False
    assert "Model denied" in decision.reason


def test_embedded_requires_approval_for_publish() -> None:
    decision = evaluate_opa(
        {
            "tenant_id": "tenant-a",
            "rbac_allowed": True,
            "operation": "skills:publish",
        }
    )
    assert decision.allowed is True
    assert decision.requires_approval is True


def test_embedded_denies_when_rbac_denied() -> None:
    decision = evaluate_opa(
        {
            "tenant_id": "tenant-a",
            "rbac_allowed": False,
            "operation": "skills:read",
        }
    )
    assert decision.allowed is False
    assert decision.reason == "RBAC denied"


@patch.dict("os.environ", {"CONTEXT_SKILLS_OPA_URL": "http://opa:8181"}, clear=False)
def test_opa_http_path_uses_enriched_payload() -> None:
    opa_response = {"result": {"allow": False, "require_approval": False}}
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps(opa_response).encode("utf-8")
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=False)

    captured: dict = {}

    def fake_urlopen(request, timeout=5):  # noqa: ARG001
        captured["body"] = json.loads(request.data.decode("utf-8"))
        return mock_response

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        decision = evaluate_opa(
            {
                "tenant_id": "tenant-c",
                "skill": "evaluation",
                "rbac_allowed": True,
                "operation": "skills:read",
            }
        )

    assert decision.allowed is False
    assert "advanced-evaluation" in captured["body"]["input"]["denied_skills"]
    assert "gpt-4o" in captured["body"]["input"]["denied_models"]


@patch.dict("os.environ", {"CONTEXT_SKILLS_OPA_URL": "http://opa:8181"}, clear=False)
def test_opa_http_fallback_on_error() -> None:
    with patch("urllib.request.urlopen", side_effect=TimeoutError("opa down")):
        decision = evaluate_opa(
            {
                "tenant_id": "tenant-c",
                "skill": "advanced-evaluation",
                "rbac_allowed": True,
                "operation": "skills:read",
            }
        )
    assert decision.allowed is False


def test_policy_decision_to_dict() -> None:
    decision = PolicyDecision(True, "allowed", requires_approval=True)
    assert decision.to_dict() == {
        "allowed": True,
        "reason": "allowed",
        "requires_approval": True,
    }
