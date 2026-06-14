#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const os = require('os');

// Helper to recursively copy directories
function copyRecursiveSync(src, dest) {
  const exists = fs.existsSync(src);
  const stats = exists && fs.statSync(src);
  const isDirectory = exists && stats.isDirectory();
  if (isDirectory) {
    if (!fs.existsSync(dest)) {
      fs.mkdirSync(dest, { recursive: true });
    }
    fs.readdirSync(src).forEach((childItemName) => {
      copyRecursiveSync(path.join(src, childItemName), path.join(dest, childItemName));
    });
  } else {
    fs.copyFileSync(src, dest);
  }
}

function printUsage() {
  console.log(`
Usage:
  npx context-management-for-copilot [options]

Options:
  (default)       Install to .github/skills/ of the current repository and
                  generate/extend .github/copilot-instructions.md with a
                  progressive-disclosure skill index
  --global        Install to ~/.copilot/skills and generate/extend
                  ~/.copilot/copilot-instructions.md (Copilot CLI)
  --path <path>   Install skills to a custom directory path (no index generated)
  --help, -h      Show this help message
`);
}

// Parse skill name + description from a SKILL.md YAML frontmatter
function readSkillMeta(skillMdPath) {
  const content = fs.readFileSync(skillMdPath, 'utf8');
  const fm = content.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!fm) return null;
  const name = (fm[1].match(/^name:\s*(.+)$/m) || [])[1];
  const description = (fm[1].match(/^description:\s*(.+)$/m) || [])[1];
  if (!name || !description) return null;
  return { name: name.trim(), description: description.trim() };
}

function buildInstructionsIndex(skillsDir, relSkillsPath) {
  const lines = [
    '',
    '<!-- BEGIN context-management-for-copilot skill index -->',
    '## Agent Skills for Context Engineering',
    '',
    `Specialized skills are installed under \`${relSkillsPath}\`. To keep context usage low, do NOT read all skill files up front. Use this index to decide relevance; when a skill matches the current task, read its \`SKILL.md\` (and only then any files in its \`references/\` directory).`,
    ''
  ];
  const skills = fs.readdirSync(skillsDir).filter((s) =>
    fs.existsSync(path.join(skillsDir, s, 'SKILL.md'))
  );
  for (const skill of skills) {
    const meta = readSkillMeta(path.join(skillsDir, skill, 'SKILL.md'));
    if (meta) {
      lines.push(`- **\`${meta.name}\`** (\`${relSkillsPath}/${skill}/SKILL.md\`): ${meta.description}`);
    }
  }
  lines.push('<!-- END context-management-for-copilot skill index -->', '');
  return lines.join('\n');
}

function writeInstructions(instructionsPath, index) {
  if (fs.existsSync(instructionsPath)) {
    const existing = fs.readFileSync(instructionsPath, 'utf8');
    if (existing.includes('BEGIN context-management-for-copilot skill index')) {
      const updated = existing.replace(
        /<!-- BEGIN context-management-for-copilot skill index -->[\s\S]*?<!-- END context-management-for-copilot skill index -->\n?/,
        index.trim() + '\n'
      );
      fs.writeFileSync(instructionsPath, updated);
      console.log(`  [✓] Updated skill index in: ${instructionsPath}`);
    } else {
      fs.appendFileSync(instructionsPath, index);
      console.log(`  [✓] Appended skill index to existing: ${instructionsPath}`);
    }
  } else {
    fs.mkdirSync(path.dirname(instructionsPath), { recursive: true });
    fs.writeFileSync(instructionsPath, '# Copilot Instructions\n' + index);
    console.log(`  [✓] Created: ${instructionsPath}`);
  }
}

function main() {
  const args = process.argv.slice(2);

  if (args.includes('--help') || args.includes('-h')) {
    printUsage();
    process.exit(0);
  }

  let targetDir = '';
  let instructionsPath = '';
  let relSkillsPath = '';
  const pathIndex = args.indexOf('--path');

  if (pathIndex !== -1 && pathIndex < args.length - 1) {
    targetDir = path.resolve(process.cwd(), args[pathIndex + 1]);
  } else if (args.includes('--global')) {
    targetDir = path.join(os.homedir(), '.copilot', 'skills');
    instructionsPath = path.join(os.homedir(), '.copilot', 'copilot-instructions.md');
    relSkillsPath = '~/.copilot/skills';
  } else {
    targetDir = path.join(process.cwd(), '.github', 'skills');
    instructionsPath = path.join(process.cwd(), '.github', 'copilot-instructions.md');
    relSkillsPath = '.github/skills';
  }

  console.log(`Installing Context Engineering Skills to: ${targetDir}`);

  const sourceSkillsDir = path.join(__dirname, '..', 'skills');
  const sourceRootSkill = path.join(__dirname, '..', 'SKILL.md');

  if (!fs.existsSync(sourceSkillsDir)) {
    console.error(`Error: Source skills directory not found at ${sourceSkillsDir}`);
    process.exit(1);
  }

  try {
    fs.mkdirSync(targetDir, { recursive: true });

    const skills = fs.readdirSync(sourceSkillsDir);
    let copiedCount = 0;

    for (const skill of skills) {
      const srcPath = path.join(sourceSkillsDir, skill);
      if (fs.statSync(srcPath).isDirectory()) {
        const destPath = path.join(targetDir, skill);
        copyRecursiveSync(srcPath, destPath);
        console.log(`  [✓] Copied skill: ${skill}`);
        copiedCount++;
      }
    }

    if (fs.existsSync(sourceRootSkill)) {
      fs.copyFileSync(sourceRootSkill, path.join(targetDir, 'SKILL.md'));
      console.log(`  [✓] Copied collection SKILL.md`);
    }

    if (instructionsPath) {
      const index = buildInstructionsIndex(targetDir, relSkillsPath);
      writeInstructions(instructionsPath, index);
    }

    console.log(`\nSuccess! Installed ${copiedCount} skills to ${targetDir}`);
    if (instructionsPath) {
      console.log(`Copilot will discover the skills via: ${instructionsPath}`);
    }
  } catch (err) {
    console.error(`\nError occurred during installation:`, err.message);
    process.exit(1);
  }
}

main();
