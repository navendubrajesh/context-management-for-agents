from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CHART_DIR = REPO_ROOT / "deploy" / "helm" / "context-skills"

REQUIRED_FILES = [
    "Chart.yaml",
    "values.yaml",
    "templates/_helpers.tpl",
    "templates/deployment.yaml",
    "templates/service.yaml",
    "templates/ingress.yaml",
    "templates/configmap.yaml",
    "templates/secret.yaml",
    "templates/hpa.yaml",
    "templates/opa-deployment.yaml",
    "templates/opa-configmap.yaml",
    "templates/serviceaccount.yaml",
    "templates/NOTES.txt",
]


def test_helm_chart_files_exist() -> None:
    missing = [rel for rel in REQUIRED_FILES if not (CHART_DIR / rel).is_file()]
    assert missing == [], f"Missing Helm files: {missing}"


def test_chart_yaml_has_metadata() -> None:
    text = (CHART_DIR / "Chart.yaml").read_text(encoding="utf-8")
    assert "name: context-skills" in text
    assert "version:" in text
    assert "appVersion:" in text


def test_values_declares_core_settings() -> None:
    text = (CHART_DIR / "values.yaml").read_text(encoding="utf-8")
    for key in ("auth:", "ingress:", "opa:", "autoscaling:", "service:"):
        assert key in text


def test_deployment_references_configmap_and_secret() -> None:
    text = (CHART_DIR / "templates/deployment.yaml").read_text(encoding="utf-8")
    assert "configMapRef" in text
    assert "secretRef" in text
    assert "livenessProbe" in text
    assert "readinessProbe" in text
    assert "failureThreshold" in text


def test_opa_sidecar_in_api_deployment() -> None:
    text = (CHART_DIR / "templates/deployment.yaml").read_text(encoding="utf-8")
    values = (CHART_DIR / "values.yaml").read_text(encoding="utf-8")
    assert "opa.sidecar" in text
    assert "name: opa" in text
    assert "sidecar: true" in values


def test_hpa_includes_memory_and_behavior() -> None:
    text = (CHART_DIR / "templates/hpa.yaml").read_text(encoding="utf-8")
    assert "memory" in text
    assert "behavior:" in text
    assert "stabilizationWindowSeconds" in text


def test_opa_templates_present_when_enabled() -> None:
    opa_deploy = (CHART_DIR / "templates/opa-deployment.yaml").read_text(encoding="utf-8")
    opa_policy = (CHART_DIR / "templates/opa-configmap.yaml").read_text(encoding="utf-8")
    values = (CHART_DIR / "values.yaml").read_text(encoding="utf-8")
    assert ".Values.opa.image.repository" in opa_deploy
    assert "openpolicyagent/opa" in values
    assert "package contextskills" in opa_policy
    assert "context-skills-opa" in opa_deploy


@pytest.mark.skipif(shutil.which("helm") is None, reason="helm CLI not installed")
def test_helm_template_renders() -> None:
    proc = subprocess.run(
        ["helm", "template", "context-skills-test", str(CHART_DIR)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    rendered = proc.stdout
    for kind in ("Deployment", "Service", "Ingress", "HorizontalPodAutoscaler", "ConfigMap", "Secret"):
        assert kind in rendered, f"Expected {kind} in helm template output"
