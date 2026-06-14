# Context Skills Python SDK

Thin client over the shared loader/router (local) or the REST API (remote).

## Install

```bash
pip install -e runtime/core -e runtime/sdk-python
```

## Local usage

```python
from context_skills_sdk import SkillsClient

client = SkillsClient()
print(client.list_skills())
print(client.route("How do I compress conversation history for a handoff?", top_k=3))
```

## Remote usage

```python
client = SkillsClient(base_url="http://localhost:8080")
print(client.get_skill("context-compression"))
```

## LangGraph example (~10 lines)

```python
from context_skills_sdk import SkillsClient
from langgraph.graph import StateGraph

client = SkillsClient()

def pick_skill(state):
    matches = client.route(state["task"], top_k=1)
    skill = client.get_skill(matches[0]["skill"])
    return {"skill_body": skill["body"]}

graph = StateGraph(dict)
graph.add_node("route", pick_skill)
graph.set_entry_point("route")
app = graph.compile()
```

## CrewAI example (~10 lines)

```python
from context_skills_sdk import SkillsClient
from crewai import Agent, Task, Crew

client = SkillsClient()
top = client.route("Design a handoff summary for a long agent session", top_k=1)[0]
skill = client.get_skill(top["skill"])

researcher = Agent(role="Context Engineer", goal=skill["description"], backstory=skill["body"][:2000])
task = Task(description="Apply the routed skill guidance.", agent=researcher)
crew = Crew(agents=[researcher], tasks=[task])
crew.kickoff()
```
