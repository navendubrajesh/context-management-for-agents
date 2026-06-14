import path from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import { SkillsClient } from "../../sdk-ts/src/index.ts";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..", "..");

describe("SkillsClient local mode", () => {
  it("routes handoff compression queries to context-compression", async () => {
    const client = new SkillsClient({ repoRoot });
    const results = await client.route("How do I compress conversation history for a handoff?", 3);
    expect(results[0]?.skill).toBe("context-compression");
  });

  it("lists all skills with progressive disclosure", async () => {
    const client = new SkillsClient({ repoRoot });
    const skills = await client.listSkills();
    expect(skills.length).toBe(28);
    expect(Object.keys(skills[0] ?? {})).toEqual(["name", "description"]);
  });
});
