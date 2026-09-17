from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULES = [
    REPO_ROOT / "deploy" / "terraform" / "modules" / "context-skills",
    REPO_ROOT / "deploy" / "terraform" / "modules" / "saas",
    REPO_ROOT / "deploy" / "terraform" / "modules" / "customer-vpc",
]


@pytest.mark.parametrize("module_dir", MODULES, ids=[m.name for m in MODULES])
def test_terraform_module_files_exist(module_dir: Path) -> None:
    assert (module_dir / "main.tf").is_file()
    assert (module_dir / "variables.tf").is_file() or module_dir.name == "saas"
    assert (module_dir / "outputs.tf").is_file()


def test_context_skills_module_declares_aws_resources() -> None:
    text = (REPO_ROOT / "deploy/terraform/modules/context-skills/main.tf").read_text(encoding="utf-8")
    for resource in ("aws_vpc", "aws_eks_cluster", "aws_db_instance", "aws_lb"):
        assert resource in text


def test_saas_module_wraps_base() -> None:
    text = (REPO_ROOT / "deploy/terraform/modules/saas/main.tf").read_text(encoding="utf-8")
    assert 'source = "../context-skills"' in text
    assert "deployment_mode" in text or "saas" in text


def test_customer_vpc_module_has_region_pin() -> None:
    text = (REPO_ROOT / "deploy/terraform/modules/customer-vpc/main.tf").read_text(encoding="utf-8")
    assert "customer-vpc" in text
    assert "region_pin" in text or "var.region" in text


@pytest.mark.skipif(shutil.which("terraform") is None, reason="terraform CLI not installed")
@pytest.mark.parametrize("module_dir", MODULES, ids=[m.name for m in MODULES])
def test_terraform_validate(module_dir: Path) -> None:
    init = subprocess.run(
        ["terraform", "init", "-backend=false", "-input=false"],
        cwd=module_dir,
        capture_output=True,
        text=True,
        check=False,
    )
    assert init.returncode == 0, init.stderr
    validate = subprocess.run(
        ["terraform", "validate"],
        cwd=module_dir,
        capture_output=True,
        text=True,
        check=False,
    )
    assert validate.returncode == 0, validate.stderr
