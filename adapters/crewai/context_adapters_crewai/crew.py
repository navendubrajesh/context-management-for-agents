"""Example CrewAI crew wiring context-skills tools."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from context_adapters_crewai.tools import create_context_tools


def build_context_crew(
    *,
    base_url: str | None = None,
    repo_root: Path | None = None,
) -> Any:
    """Build a CrewAI Crew when crewai is installed; otherwise return tool specs."""
    tools = create_context_tools(base_url=base_url, repo_root=repo_root)

    try:
        from crewai import Agent, Crew, Process, Task
    except ImportError as exc:
        raise ImportError(
            "crewai is required for build_context_crew(). "
            "Install with: pip install context-adapters-crewai[crewai]"
        ) from exc

    router = Agent(
        role="Context Router",
        goal="Select and apply context engineering techniques for agent sessions",
        backstory="Expert in context window budgeting and skill routing.",
        tools=tools,
        verbose=False,
    )
    task = Task(
        description="Route the task '{task}' and recommend context optimization steps.",
        expected_output="Ranked skills and recommended primitive sequence.",
        agent=router,
    )
    return Crew(agents=[router], tasks=[task], process=Process.sequential)
