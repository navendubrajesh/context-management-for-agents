"""Canonical skill inventory and category mapping for runtime manifests."""

from __future__ import annotations

# Expected 28 skills (13 platform-agnostic + 15 platform-specific).
# Keep in sync with researcher/scripts/* EXPECTED_SKILLS sets.
EXPECTED_SKILLS: frozenset[str] = frozenset(
    {
        "advanced-evaluation",
        "amazonq-context-architecture",
        "amazonq-customization",
        "amazonq-session-management",
        "antigravity-context-architecture",
        "antigravity-customization",
        "antigravity-session-management",
        "context-compression",
        "context-degradation",
        "context-fundamentals",
        "context-optimization",
        "copilot-context-architecture",
        "copilot-customization",
        "copilot-session-management",
        "cursor-context-architecture",
        "cursor-customization",
        "cursor-session-management",
        "evaluation",
        "filesystem-context",
        "harness-engineering",
        "hosted-agents",
        "kiro-context-architecture",
        "kiro-customization",
        "kiro-session-management",
        "memory-systems",
        "multi-agent-patterns",
        "project-development",
        "tool-design",
    }
)

VALID_CATEGORIES: frozenset[str] = frozenset(
    {"platform", "foundational", "architectural", "operational", "methodology", "cognitive"}
)

SKILL_CATEGORIES: dict[str, str] = {
    # Foundational
    "context-fundamentals": "foundational",
    "context-degradation": "foundational",
    "context-compression": "foundational",
    # Architectural
    "multi-agent-patterns": "architectural",
    "memory-systems": "architectural",
    "tool-design": "architectural",
    "filesystem-context": "architectural",
    "hosted-agents": "architectural",
    # Operational
    "context-optimization": "operational",
    "evaluation": "operational",
    "advanced-evaluation": "operational",
    # Methodology
    "harness-engineering": "methodology",
    "project-development": "methodology",
    # Platform — Copilot
    "copilot-context-architecture": "platform",
    "copilot-session-management": "platform",
    "copilot-customization": "platform",
    # Platform — Cursor
    "cursor-context-architecture": "platform",
    "cursor-session-management": "platform",
    "cursor-customization": "platform",
    # Platform — Kiro
    "kiro-context-architecture": "platform",
    "kiro-session-management": "platform",
    "kiro-customization": "platform",
    # Platform — Antigravity
    "antigravity-context-architecture": "platform",
    "antigravity-session-management": "platform",
    "antigravity-customization": "platform",
    # Platform — Amazon Q
    "amazonq-context-architecture": "platform",
    "amazonq-session-management": "platform",
    "amazonq-customization": "platform",
}

DEFAULT_SKILL_VERSION = "1.0.0"
