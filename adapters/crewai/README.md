# CrewAI Adapter (CM-402)

CrewAI tools and example crew for context-skills.

## Install

```bash
pip install -e adapters/crewai
pip install -e adapters/crewai[crewai]
pip install -e runtime/core -e runtime/sdk-python
```

## Usage

```python
from context_adapters_crewai import create_context_tools, build_context_crew

tools = create_context_tools()
print(tools[0]["name"])  # portable mode without crewai installed

crew = build_context_crew()
result = crew.kickoff(inputs={"task": "optimize a long coding agent session"})
print(result)
```
