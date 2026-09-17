# LangGraph Adapter (CM-401)

LangGraph-compatible nodes wrapping context-skills primitives.

## Install

```bash
pip install -e adapters/langgraph
pip install -e adapters/langgraph[langgraph]  # optional LangGraph compile support
pip install -e runtime/core -e runtime/sdk-python
```

## Usage

```python
from context_adapters_langgraph import build_context_graph, run_default_graph

# Offline sequential run (no langgraph required)
state = run_default_graph({
    "task": "compact a long agent session",
    "session": {"messages": [{"role": "user", "content": "hello"}]},
})
print(state["pipeline_result"])

# With LangGraph installed
graph = build_context_graph()
result = graph.invoke({"task": "mask verbose tool output", "content": "..."})
```
