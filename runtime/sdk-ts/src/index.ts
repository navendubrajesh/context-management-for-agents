export interface SkillSummary {
  name: string;
  description: string;
}

export interface SkillDetail {
  name: string;
  description: string;
  body: string;
  references: string[];
}

export interface RouteResult {
  skill: string;
  score: number;
}

export interface SkillsClientOptions {
  baseUrl?: string;
  repoRoot?: string;
}

const WORD_RE = /\b[a-z0-9-]{3,}\b/g;

function getWords(text: string): Set<string> {
  const words = text.toLowerCase().match(WORD_RE) ?? [];
  return new Set(words);
}

function findRepoRoot(start: string): string {
  const fs = require("node:fs") as typeof import("node:fs");
  const path = require("node:path") as typeof import("node:path");
  let current = path.resolve(start);
  while (true) {
    if (
      fs.existsSync(path.join(current, "skills")) &&
      fs.existsSync(path.join(current, "researcher"))
    ) {
      return current;
    }
    const parent = path.dirname(current);
    if (parent === current) {
      throw new Error("Could not locate repository root");
    }
    current = parent;
  }
}

function parseFrontmatter(content: string): { frontmatter: Record<string, string>; body: string } {
  const match = content.match(/^---\s*\n([\s\S]*?)\n---\s*\n?/);
  if (!match) {
    return { frontmatter: {}, body: content };
  }
  const frontmatter: Record<string, string> = {};
  for (const line of match[1].split("\n")) {
    const idx = line.indexOf(":");
    if (idx > -1) {
      frontmatter[line.slice(0, idx).trim()] = line.slice(idx + 1).trim();
    }
  }
  return { frontmatter, body: content.slice(match[0].length) };
}

function scoreSkillMatch(query: string, skill: {
  name: string;
  nameWords: Set<string>;
  descWords: Set<string>;
  contentWords: Set<string>;
}): number {
  const queryWords = getWords(query);
  if (queryWords.size === 0) return 0;

  let score =
    [...queryWords].filter((w) => skill.nameWords.has(w)).length * 5 +
    [...queryWords].filter((w) => skill.descWords.has(w)).length * 2 +
    [...queryWords].filter((w) => skill.contentWords.has(w)).length * 0.5;

  if (skill.name === "context-fundamentals") {
    if ([...queryWords].some((w) =>
      ["prevent", "failure", "poisoning", "distraction", "clash", "degrade", "degradation"].includes(w),
    )) {
      score *= 0.5;
    }
  } else if (skill.name === "context-degradation") {
    if ([...queryWords].some((w) =>
      ["prevent", "failure", "poisoning", "distraction", "clash", "degrade", "degradation"].includes(w),
    )) {
      score *= 2;
    }
  }

  if (skill.name === "context-optimization") {
    if ([...queryWords].some((w) => ["compress", "history", "handoff", "summarize"].includes(w))) {
      score *= 0.5;
    }
  } else if (skill.name === "context-compression") {
    if ([...queryWords].some((w) => ["compress", "history", "handoff", "summarize"].includes(w))) {
      score *= 2;
    }
  }

  return score;
}

export class SkillsClient {
  private readonly baseUrl?: string;
  private readonly repoRoot: string;

  constructor(options: SkillsClientOptions = {}) {
    this.baseUrl = options.baseUrl?.replace(/\/$/, "");
    this.repoRoot = options.repoRoot ?? findRepoRoot(process.cwd());
  }

  get mode(): "local" | "remote" {
    return this.baseUrl ? "remote" : "local";
  }

  async listSkills(): Promise<SkillSummary[]> {
    if (this.baseUrl) {
      const response = await fetch(`${this.baseUrl}/skills`);
      if (!response.ok) throw new Error(`listSkills failed: ${response.status}`);
      return response.json() as Promise<SkillSummary[]>;
    }
    return this.listSkillsLocal();
  }

  async getSkill(name: string): Promise<SkillDetail> {
    if (this.baseUrl) {
      const response = await fetch(`${this.baseUrl}/skills/${encodeURIComponent(name)}`);
      if (!response.ok) throw new Error(`getSkill failed: ${response.status}`);
      return response.json() as Promise<SkillDetail>;
    }
    return this.getSkillLocal(name);
  }

  async route(task: string, topK = 5): Promise<RouteResult[]> {
    if (this.baseUrl) {
      const response = await fetch(`${this.baseUrl}/route`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task, top_k: topK }),
      });
      if (!response.ok) throw new Error(`route failed: ${response.status}`);
      const payload = (await response.json()) as { results: RouteResult[] };
      return payload.results;
    }
    return this.routeLocal(task, topK);
  }

  async getReference(name: string, refPath: string): Promise<string> {
    if (this.baseUrl) {
      const response = await fetch(
        `${this.baseUrl}/skills/${encodeURIComponent(name)}/references/${refPath}`,
      );
      if (!response.ok) throw new Error(`getReference failed: ${response.status}`);
      const payload = (await response.json()) as { content: string };
      return payload.content;
    }
    return this.getReferenceLocal(name, refPath);
  }

  private listSkillsLocal(): SkillSummary[] {
    const fs = require("node:fs") as typeof import("node:fs");
    const path = require("node:path") as typeof import("node:path");
    const skillsDir = path.join(this.repoRoot, "skills");
    const names = fs.readdirSync(skillsDir).filter((name: string) =>
      fs.existsSync(path.join(skillsDir, name, "SKILL.md")),
    );
    return names.sort().map((name: string) => {
      const detail = this.getSkillLocalSync(name);
      return { name: detail.name, description: detail.description };
    });
  }

  private getSkillLocalSync(name: string): SkillDetail {
    const fs = require("node:fs") as typeof import("node:fs");
    const path = require("node:path") as typeof import("node:path");
    const skillPath = path.join(this.repoRoot, "skills", name, "SKILL.md");
    const content = fs.readFileSync(skillPath, "utf8");
    const { frontmatter, body } = parseFrontmatter(content);
    const refsDir = path.join(this.repoRoot, "skills", name, "references");
    const references: string[] = [];
    if (fs.existsSync(refsDir)) {
      for (const file of this.walkMarkdown(refsDir)) {
        references.push(path.relative(path.join(this.repoRoot, "skills", name), file).replace(/\\/g, "/"));
      }
      references.sort();
    }
    return {
      name: frontmatter.name ?? name,
      description: frontmatter.description ?? "",
      body,
      references,
    };
  }

  private async getSkillLocal(name: string): Promise<SkillDetail> {
    return this.getSkillLocalSync(name);
  }

  private walkMarkdown(dir: string): string[] {
    const fs = require("node:fs") as typeof import("node:fs");
    const path = require("node:path") as typeof import("node:path");
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    const files: string[] = [];
    for (const entry of entries) {
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        files.push(...this.walkMarkdown(full));
      } else if (entry.isFile() && entry.name.endsWith(".md")) {
        files.push(full);
      }
    }
    return files;
  }

  private routeLocal(task: string, topK: number): RouteResult[] {
    const fs = require("node:fs") as typeof import("node:fs");
    const path = require("node:path") as typeof import("node:path");
    const skillsDir = path.join(this.repoRoot, "skills");
    const ranked: RouteResult[] = [];
    for (const name of fs.readdirSync(skillsDir)) {
      const skillPath = path.join(skillsDir, name, "SKILL.md");
      if (!fs.existsSync(skillPath)) continue;
      const content = fs.readFileSync(skillPath, "utf8");
      const { frontmatter } = parseFrontmatter(content);
      const description = frontmatter.description ?? "";
      ranked.push({
        skill: name,
        score: scoreSkillMatch(task, {
          name,
          nameWords: getWords(name.replace(/-/g, " ")),
          descWords: getWords(description),
          contentWords: getWords(content),
        }),
      });
    }
    ranked.sort((a, b) => b.score - a.score);
    return ranked.slice(0, topK);
  }

  private getReferenceLocal(name: string, refPath: string): string {
    const fs = require("node:fs") as typeof import("node:fs");
    const path = require("node:path") as typeof import("node:path");
    const skillRoot = path.resolve(this.repoRoot, "skills", name);
    const resolved = path.resolve(skillRoot, refPath);
    if (!resolved.startsWith(skillRoot)) {
      throw new Error(`Reference path escapes skill directory: ${refPath}`);
    }
    return fs.readFileSync(resolved, "utf8");
  }
}
