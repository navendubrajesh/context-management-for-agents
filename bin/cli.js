#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const os = require('os');

const PLATFORMS = ['copilot', 'cursor', 'kiro', 'antigravity', 'amazonq', 'claude'];
const INDEX_MARKER = 'context-management-for-agents';
const SKILL_NAMESPACE = 'context-engineering';

function copyRecursiveSync(src, dest) {
  const stats = fs.statSync(src);
  if (stats.isDirectory()) {
    if (!fs.existsSync(dest)) fs.mkdirSync(dest, { recursive: true });
    for (const child of fs.readdirSync(src)) {
      copyRecursiveSync(path.join(src, child), path.join(dest, child));
    }
  } else {
    fs.copyFileSync(src, dest);
  }
}

function printUsage() {
  console.log(`
Usage:
  npx context-management-for-agents [options]

Options:
  --platform <name>  Target platform: copilot | cursor | kiro | antigravity | amazonq | claude
                     (default: copilot)
  --global           Global install (Copilot CLI / user-level paths where supported)
  --path <dir>       Copy skills only to a custom directory (no index generated)
  --setup            After copy, create per-skill discovery dirs with SKILL.md symlinks
                     (Claude Code / GStack-compatible layout)
  --help, -h         Show this help

Install paths use namespace "${SKILL_NAMESPACE}/" to coexist with GStack and other skill packs.
`);
}

function readSkillMeta(skillMdPath) {
  const content = fs.readFileSync(skillMdPath, 'utf8');
  const fm = content.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!fm) return null;
  const name = (fm[1].match(/^name:\s*(.+)$/m) || [])[1];
  const description = (fm[1].match(/^description:\s*(.+)$/m) || [])[1];
  if (!name || !description) return null;
  return { name: name.trim(), description: description.trim() };
}

function listSkills(skillsDir) {
  return fs.readdirSync(skillsDir)
    .filter((s) => fs.existsSync(path.join(skillsDir, s, 'SKILL.md')))
    .sort();
}

function buildCoStackSection() {
  return [
    '',
    '### Co-installation with workflow skill packs (e.g. GStack)',
    '',
    '- **Workflow packs** (`/ship`, `/qa`, `/review`, …): building, testing, shipping, browser QA.',
    '- **Context engineering skills** (this index): context window discipline — compression, masking, budgeting, platform context mechanics.',
    '- Read **one** matching `SKILL.md` on activation; do not load all skills up front.',
    '- When a workflow skill is active, follow its procedure; use context skills for *what to keep, compress, or mask* — not for release/QA steps.',
    ''
  ].join('\n');
}

function buildIndexLines(skillsDir, relSkillsPath) {
  const lines = [
    '',
    `<!-- BEGIN ${INDEX_MARKER} skill index -->`,
    '## Agent Skills for Context Engineering',
    '',
    `Skills are installed under \`${relSkillsPath}\`. Do NOT read all skill files up front. Use this index to decide relevance; when a skill matches, read its \`SKILL.md\` (then \`references/\` only if needed).`,
    buildCoStackSection()
  ];
  for (const skill of listSkills(skillsDir)) {
    const meta = readSkillMeta(path.join(skillsDir, skill, 'SKILL.md'));
    if (meta) {
      lines.push(`- **\`${meta.name}\`** (\`${relSkillsPath}/${skill}/SKILL.md\`): ${meta.description}`);
    }
  }
  lines.push(`<!-- END ${INDEX_MARKER} skill index -->`, '');
  return lines.join('\n');
}

function writeOrUpdateFile(filePath, index, createHeader) {
  if (fs.existsSync(filePath)) {
    const existing = fs.readFileSync(filePath, 'utf8');
    const re = new RegExp(
      `<!-- BEGIN ${INDEX_MARKER} skill index -->[\\s\\S]*?<!-- END ${INDEX_MARKER} skill index -->\\n?`
    );
    if (existing.includes(`BEGIN ${INDEX_MARKER} skill index`)) {
      fs.writeFileSync(filePath, existing.replace(re, index.trim() + '\n'));
      console.log(`  [✓] Updated skill index in: ${filePath}`);
    } else {
      fs.appendFileSync(filePath, index);
      console.log(`  [✓] Appended skill index to: ${filePath}`);
    }
  } else {
    fs.mkdirSync(path.dirname(filePath), { recursive: true });
    fs.writeFileSync(filePath, createHeader + index);
    console.log(`  [✓] Created: ${filePath}`);
  }
}

function writePlatformIndex(platform, skillsDir, relSkillsPath, cwd, globalInstall) {
  const index = buildIndexLines(skillsDir, relSkillsPath);
  const home = os.homedir();

  switch (platform) {
    case 'copilot': {
      const instructionsPath = globalInstall
        ? path.join(home, '.copilot', 'copilot-instructions.md')
        : path.join(cwd, '.github', 'copilot-instructions.md');
      writeOrUpdateFile(instructionsPath, index, '# Copilot Instructions\n');
      break;
    }
    case 'cursor': {
      const rulesDir = path.join(cwd, '.cursor', 'rules');
      fs.mkdirSync(rulesDir, { recursive: true });
      const mdcPath = path.join(rulesDir, 'context-engineering-skills-index.mdc');
      const body = `---
description: Index of context-engineering skills. Read individual SKILL.md files on demand — do not load all skills up front. Coexists with GStack at .cursor/skills/gstack.
alwaysApply: true
---

${index.trim()}`;
      fs.writeFileSync(mdcPath, body);
      console.log(`  [✓] Created/updated: ${mdcPath}`);
      break;
    }
    case 'claude': {
      const claudeMdPath = path.join(cwd, 'CLAUDE.md');
      writeOrUpdateFile(claudeMdPath, index, '# Claude Code Instructions\n\n');
      break;
    }
    case 'kiro': {
      const steeringDir = globalInstall
        ? path.join(home, '.kiro', 'steering')
        : path.join(cwd, '.kiro', 'steering');
      fs.mkdirSync(steeringDir, { recursive: true });
      const steeringPath = path.join(steeringDir, 'context-engineering-skills-index.md');
      const body = `---
inclusion: always
---

${index.trim()}`;
      fs.writeFileSync(steeringPath, body);
      console.log(`  [✓] Created/updated: ${steeringPath}`);
      break;
    }
    case 'antigravity': {
      const agentsMdPath = path.join(cwd, 'AGENTS.md');
      writeOrUpdateFile(agentsMdPath, index, '# Agent Instructions\n\n');
      break;
    }
    case 'amazonq': {
      const rulesDir = path.join(cwd, '.amazonq', 'rules');
      fs.mkdirSync(rulesDir, { recursive: true });
      const rulesPath = path.join(rulesDir, 'context-engineering-skills-index.md');
      const body = `# Context Engineering Skills Index\n\n${index.trim()}`;
      fs.writeFileSync(rulesPath, body);
      console.log(`  [✓] Created/updated: ${rulesPath}`);
      break;
    }
    default:
      throw new Error(`Unknown platform: ${platform}`);
  }
}

function resolveTarget(platform, globalInstall, customPath, cwd) {
  const home = os.homedir();
  if (customPath) {
    return { targetDir: path.resolve(cwd, customPath), relSkillsPath: customPath, generateIndex: false, skillsParent: null };
  }
  const ns = SKILL_NAMESPACE;
  const configs = {
    copilot: {
      targetDir: globalInstall
        ? path.join(home, '.copilot', 'skills', ns)
        : path.join(cwd, '.github', 'skills', ns),
      relSkillsPath: globalInstall ? `~/.copilot/skills/${ns}` : `.github/skills/${ns}`,
      generateIndex: true,
      skillsParent: globalInstall ? path.join(home, '.copilot', 'skills') : path.join(cwd, '.github', 'skills')
    },
    cursor: {
      targetDir: path.join(cwd, '.cursor', 'skills', ns),
      relSkillsPath: `.cursor/skills/${ns}`,
      generateIndex: true,
      skillsParent: path.join(cwd, '.cursor', 'skills')
    },
    claude: {
      targetDir: globalInstall
        ? path.join(home, '.claude', 'skills', ns)
        : path.join(cwd, '.claude', 'skills', ns),
      relSkillsPath: globalInstall ? `~/.claude/skills/${ns}` : `.claude/skills/${ns}`,
      generateIndex: true,
      skillsParent: globalInstall ? path.join(home, '.claude', 'skills') : path.join(cwd, '.claude', 'skills')
    },
    kiro: {
      targetDir: globalInstall
        ? path.join(home, '.kiro', 'skills', ns)
        : path.join(cwd, '.kiro', 'skills', ns),
      relSkillsPath: globalInstall ? `~/.kiro/skills/${ns}` : `.kiro/skills/${ns}`,
      generateIndex: true,
      skillsParent: globalInstall ? path.join(home, '.kiro', 'skills') : path.join(cwd, '.kiro', 'skills')
    },
    antigravity: {
      targetDir: path.join(cwd, '.agents', 'skills', ns),
      relSkillsPath: `.agents/skills/${ns}`,
      generateIndex: true,
      skillsParent: path.join(cwd, '.agents', 'skills')
    },
    amazonq: {
      targetDir: path.join(cwd, '.amazonq', 'skills', ns),
      relSkillsPath: `.amazonq/skills/${ns}`,
      generateIndex: true,
      skillsParent: path.join(cwd, '.amazonq', 'skills')
    }
  };
  return configs[platform];
}

function createDiscoverySymlinks(skillsParent, targetDir, platform) {
  if (!skillsParent) return;
  fs.mkdirSync(skillsParent, { recursive: true });
  const skills = listSkills(targetDir);
  let linked = 0;
  for (const skill of skills) {
    const discoveryDir = path.join(skillsParent, skill);
    const skillMdLink = path.join(discoveryDir, 'SKILL.md');
    const skillMdSrc = path.join(targetDir, skill, 'SKILL.md');
    if (!fs.existsSync(skillMdSrc)) continue;
    fs.mkdirSync(discoveryDir, { recursive: true });
    try {
      if (fs.existsSync(skillMdLink)) fs.unlinkSync(skillMdLink);
      const type = process.platform === 'win32' ? 'file' : 'file';
      fs.symlinkSync(path.resolve(skillMdSrc), skillMdLink, type);
      linked++;
    } catch (err) {
      console.warn(`  [!] Could not symlink ${skill}: ${err.message}`);
    }
  }
  if (linked > 0) {
    console.log(`  [✓] Created ${linked} per-skill discovery symlink(s) under ${skillsParent}`);
  }
}

function parseArgs(argv) {
  const args = argv.slice(2);
  if (args.includes('--help') || args.includes('-h')) {
    printUsage();
    process.exit(0);
  }
  const globalInstall = args.includes('--global');
  const runSetup = args.includes('--setup');
  const pathIdx = args.indexOf('--path');
  const platformIdx = args.indexOf('--platform');
  let platform = 'copilot';
  if (platformIdx !== -1 && platformIdx < args.length - 1) {
    platform = args[platformIdx + 1].toLowerCase();
  }
  if (!PLATFORMS.includes(platform)) {
    console.error(`Error: Unknown platform '${platform}'. Choose: ${PLATFORMS.join(', ')}`);
    process.exit(1);
  }
  const customPath = pathIdx !== -1 && pathIdx < args.length - 1 ? args[pathIdx + 1] : null;
  return { platform, globalInstall, customPath, runSetup };
}

function main() {
  const { platform, globalInstall, customPath, runSetup } = parseArgs(process.argv);
  const cwd = process.cwd();
  const sourceSkillsDir = path.join(__dirname, '..', 'skills');
  const sourceRootSkill = path.join(__dirname, '..', 'SKILL.md');

  if (!fs.existsSync(sourceSkillsDir)) {
    console.error(`Error: Source skills directory not found at ${sourceSkillsDir}`);
    process.exit(1);
  }

  const { targetDir, relSkillsPath, generateIndex, skillsParent } = resolveTarget(platform, globalInstall, customPath, cwd);
  console.log(`Installing Context Engineering Skills (${platform}) to: ${targetDir}`);

  try {
    fs.mkdirSync(targetDir, { recursive: true });
    let copiedCount = 0;
    for (const skill of fs.readdirSync(sourceSkillsDir)) {
      const srcPath = path.join(sourceSkillsDir, skill);
      if (fs.statSync(srcPath).isDirectory()) {
        copyRecursiveSync(srcPath, path.join(targetDir, skill));
        console.log(`  [✓] Copied skill: ${skill}`);
        copiedCount++;
      }
    }
    if (fs.existsSync(sourceRootSkill)) {
      fs.copyFileSync(sourceRootSkill, path.join(targetDir, 'SKILL.md'));
      console.log('  [✓] Copied collection SKILL.md');
    }
    if (generateIndex) {
      writePlatformIndex(platform, targetDir, relSkillsPath, cwd, globalInstall);
    }
    if (runSetup && skillsParent) {
      createDiscoverySymlinks(skillsParent, targetDir, platform);
    }
    console.log(`\nSuccess! Installed ${copiedCount} skills to ${targetDir}`);
    if (runSetup) {
      console.log('Per-skill discovery symlinks enabled (--setup).');
    } else {
      console.log(`Tip: run with --setup for GStack/Claude Code per-skill discovery under ${skillsParent || 'skills parent'}.`);
    }
  } catch (err) {
    console.error('\nError occurred during installation:', err.message);
    process.exit(1);
  }
}

main();
