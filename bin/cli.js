#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const os = require('os');

const PLATFORMS = ['copilot', 'cursor', 'kiro', 'antigravity', 'amazonq'];
const INDEX_MARKER = 'context-management-for-agents';

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
  --platform <name>  Target platform: copilot | cursor | kiro | antigravity | amazonq
                     (default: copilot)
  --global           Global install (Copilot CLI / user-level paths where supported)
  --path <dir>       Copy skills only to a custom directory (no index generated)
  --help, -h         Show this help
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

function buildIndexLines(skillsDir, relSkillsPath) {
  const lines = [
    '',
    `<!-- BEGIN ${INDEX_MARKER} skill index -->`,
    '## Agent Skills for Context Engineering',
    '',
    `Skills are installed under \`${relSkillsPath}\`. Do NOT read all skill files up front. Use this index to decide relevance; when a skill matches, read its \`SKILL.md\` (then \`references/\` only if needed).`,
    ''
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
description: Index of context-engineering skills. Read individual SKILL.md files on demand — do not load all skills up front.
alwaysApply: true
---

${index.trim()}`;
      fs.writeFileSync(mdcPath, body);
      console.log(`  [✓] Created/updated: ${mdcPath}`);
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
    return { targetDir: path.resolve(cwd, customPath), relSkillsPath: customPath, generateIndex: false };
  }
  const configs = {
    copilot: {
      targetDir: globalInstall ? path.join(home, '.copilot', 'skills') : path.join(cwd, '.github', 'skills'),
      relSkillsPath: globalInstall ? '~/.copilot/skills' : '.github/skills',
      generateIndex: true
    },
    cursor: {
      targetDir: path.join(cwd, '.cursor', 'skills'),
      relSkillsPath: '.cursor/skills',
      generateIndex: true
    },
    kiro: {
      targetDir: globalInstall ? path.join(home, '.kiro', 'skills') : path.join(cwd, '.kiro', 'skills'),
      relSkillsPath: globalInstall ? '~/.kiro/skills' : '.kiro/skills',
      generateIndex: true
    },
    antigravity: {
      targetDir: path.join(cwd, '.agents', 'skills'),
      relSkillsPath: '.agents/skills',
      generateIndex: true
    },
    amazonq: {
      targetDir: path.join(cwd, '.amazonq', 'skills'),
      relSkillsPath: '.amazonq/skills',
      generateIndex: true
    }
  };
  return configs[platform];
}

function parseArgs(argv) {
  const args = argv.slice(2);
  if (args.includes('--help') || args.includes('-h')) {
    printUsage();
    process.exit(0);
  }
  const globalInstall = args.includes('--global');
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
  return { platform, globalInstall, customPath };
}

function main() {
  const { platform, globalInstall, customPath } = parseArgs(process.argv);
  const cwd = process.cwd();
  const sourceSkillsDir = path.join(__dirname, '..', 'skills');
  const sourceRootSkill = path.join(__dirname, '..', 'SKILL.md');

  if (!fs.existsSync(sourceSkillsDir)) {
    console.error(`Error: Source skills directory not found at ${sourceSkillsDir}`);
    process.exit(1);
  }

  const { targetDir, relSkillsPath, generateIndex } = resolveTarget(platform, globalInstall, customPath, cwd);
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
    console.log(`\nSuccess! Installed ${copiedCount} skills to ${targetDir}`);
  } catch (err) {
    console.error('\nError occurred during installation:', err.message);
    process.exit(1);
  }
}

main();
