"""Shared skill loader, manifest validator, and lexical router."""

from context_skills.loader import get_reference, get_skill, list_skills
from context_skills.manifest import build_skill_manifest, validate_all_skill_manifests
from context_skills.router import route, score_skill_match

__all__ = [
    "list_skills",
    "get_skill",
    "get_reference",
    "route",
    "score_skill_match",
    "build_skill_manifest",
    "validate_all_skill_manifests",
]
