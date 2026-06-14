# How Skills Built This

## 1. `multi-agent-patterns`
- **Topology choice**: Demonstrates both Supervisor and Peer-to-Peer modes based on task complexity.

## 2. `memory-systems`
- **Shared memory store**: Agents read and write to a common memory registry that maps variables and state objects, ensuring state consistency.

## 3. `filesystem-context`
- **Shared-file handoffs**: The supervisor writes compact task briefs to a shared filesystem location; each sub-agent reads only its own brief, isolating context without re-sending the full conversation.
