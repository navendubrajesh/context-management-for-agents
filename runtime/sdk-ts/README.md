# Context Skills TypeScript SDK

Local in-process loader/router plus optional REST client.

## Install

```bash
cd runtime/sdk-ts
npm install
npm run build
npm test
```

## Usage

```typescript
import { SkillsClient } from "@context-management/skills-sdk";

const client = new SkillsClient({ repoRoot: "/path/to/context-management-for-agents" });
const matches = await client.route("How do I compress conversation history for a handoff?", 3);
```

Remote mode:

```typescript
const remote = new SkillsClient({ baseUrl: "http://localhost:8080" });
await remote.listSkills();
```
