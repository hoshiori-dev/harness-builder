#!/usr/bin/env -S deno run --allow-read --allow-run=git,just
// Checks the agent harness itself: the entrypoint, knowledge files, and
// project skills. Harness drift misleads every future agent with confidence,
// so these rules run in CI next to the code checks.
import { dirname, join, normalize, relative } from "@std/path";
import {
  exists,
  fail,
  Findings,
  gitFiles,
  isDirectory,
  listDir,
  readLinkOrNull,
  readText,
} from "./lib/findings.ts";
import { frontmatter, SKILL_NAME_RE } from "./lib/plugin.ts";

const root = Deno.cwd();
const AGENTS_MD_LIMIT = 120;
const LINK_RE = /\[[^\]]*\]\(([^)\s]+)\)/g;
const findings = new Findings();
const tracked = gitFiles(root);

const docs = tracked.filter((p) =>
  p === "AGENTS.md" || p === "CLAUDE.md" || p === "README.md" || p === "README.en.md" ||
  p === "CONTRIBUTING.md" ||
  p.startsWith(".agents/knowledge/") && p.endsWith(".md") ||
  p.startsWith(".agents/skills/") && p.endsWith(".md") ||
  p.startsWith("skills/") && p.endsWith(".md") ||
  p.startsWith("com.") && p.endsWith(".md")
);

checkEntrypoint();
checkLinks();
checkRecipes();
checkKnowledgeReachable();
checkSkillFrontmatter();
checkClaudeSkillLinks();
checkSymlinks();
checkOpenSpecTarget();
checkDocsReachable();
checkReadmes();
Deno.exit(findings.report("check_harness"));

function checkEntrypoint() {
  if (!exists(join(root, "AGENTS.md"))) {
    findings.add({
      file: "AGENTS.md",
      rule: "entrypoint",
      problem: "file is missing.",
      fix: "create the agent entrypoint.",
    });
    return;
  }
  const lines = readText(join(root, "AGENTS.md")).split("\n").length;
  if (lines > AGENTS_MD_LIMIT) {
    findings.add({
      file: "AGENTS.md",
      rule: "entrypoint-budget",
      problem: `has ${lines} lines (limit ${AGENTS_MD_LIMIT}).`,
      fix:
        "move detail into .agents/knowledge/ or a project skill and leave a when-to-read pointer.",
    });
  }
  if (!exists(join(root, "CLAUDE.md"))) {
    findings.add({
      file: "CLAUDE.md",
      rule: "claude-import",
      problem: "file is missing.",
      fix: "create CLAUDE.md containing @AGENTS.md.",
    });
  } else if (!readText(join(root, "CLAUDE.md")).includes("@AGENTS.md")) {
    findings.add({
      file: "CLAUDE.md",
      rule: "claude-import",
      problem: "does not import AGENTS.md.",
      fix: "make the file contain @AGENTS.md so both entrypoints stay one.",
    });
  }
}

function checkLinks() {
  for (const doc of docs) {
    const text = readText(join(root, doc));
    const lines = text.split("\n");
    lines.forEach((line, index) => {
      for (const match of line.matchAll(LINK_RE)) {
        const target = match[1];
        if (/^(https?:|mailto:|#)/.test(target)) continue;
        const path = target.split("#")[0];
        if (path === "") continue;
        const resolved = normalize(join(dirname(doc), path));
        if (!exists(join(root, resolved))) {
          findings.add({
            file: doc,
            line: index + 1,
            rule: "doc-link",
            problem: `link target ${target} does not exist.`,
            fix: "correct the path or remove the pointer.",
          });
        }
      }
    });
  }
}

function checkRecipes() {
  if (!exists(join(root, "justfile"))) {
    findings.add({
      file: "justfile",
      rule: "recipes",
      problem: "file is missing.",
      fix: "add the justfile; documentation refers to `just <recipe>` commands.",
    });
    return;
  }
  const result = new Deno.Command("just", {
    args: ["--summary"],
    cwd: root,
    stdout: "piped",
    stderr: "piped",
  }).outputSync();
  if (!result.success) {
    fail(`just --summary exited ${result.code}: ${new TextDecoder().decode(result.stderr).trim()}`);
  }
  const recipes = new Set(new TextDecoder().decode(result.stdout).trim().split(/\s+/));
  for (const doc of docs) {
    const lines = readText(join(root, doc)).split("\n");
    lines.forEach((line, index) => {
      for (const match of line.matchAll(/`just ([a-z][a-z0-9-]*)/g)) {
        if (!recipes.has(match[1])) {
          findings.add({
            file: doc,
            line: index + 1,
            rule: "doc-recipe",
            problem: `mentions \`just ${match[1]}\`, which is not a recipe.`,
            fix: "add the recipe to the justfile or correct the document.",
          });
        }
      }
    });
  }
}

function checkKnowledgeReachable() {
  if (!exists(join(root, "AGENTS.md"))) return;
  const agentsMd = readText(join(root, "AGENTS.md"));
  for (
    const file of tracked.filter((p) => p.startsWith(".agents/knowledge/") && p.endsWith(".md"))
  ) {
    if (!agentsMd.includes(file)) {
      findings.add({
        file,
        rule: "knowledge-reachable",
        problem: "not referenced from AGENTS.md.",
        fix: "add a when-to-read row pointing at this file, or delete the file.",
      });
    }
  }
}

function checkSkillFrontmatter() {
  const skillFiles = tracked.filter((p) => /^(\.agents\/skills|skills)\/[^/]+\/SKILL\.md$/.test(p));
  for (const file of skillFiles) {
    const dir = file.split("/").at(-2)!;
    const attrs = frontmatter(join(root, file));
    if (attrs === null) {
      findings.add({
        file,
        rule: "skill-frontmatter",
        problem: "no YAML frontmatter.",
        fix: "start the file with --- name/description ---.",
      });
      continue;
    }
    if (attrs.name !== dir) {
      findings.add({
        file,
        rule: "skill-name",
        problem: `frontmatter name ${JSON.stringify(attrs.name)} differs from the directory name.`,
        fix: `set name: ${dir}.`,
      });
    } else if (!SKILL_NAME_RE.test(dir) || dir.length > 64) {
      findings.add({
        file,
        rule: "skill-name",
        problem: `"${dir}" is not a valid agentskills.io name.`,
        fix: "use 1-64 lowercase letters, digits, and single hyphens.",
      });
    }
    const description = attrs.description;
    if (typeof description !== "string" || description.trim() === "" || description.length > 1024) {
      findings.add({
        file,
        rule: "skill-description",
        problem: "description is missing, empty, or over 1024 characters.",
        fix: "write a 1-1024 character description.",
      });
    }
  }
}

function checkClaudeSkillLinks() {
  const projectSkills = new Set(
    tracked.filter((p) => /^\.agents\/skills\/[^/]+\/SKILL\.md$/.test(p)).map((p) =>
      p.split("/")[2]
    ),
  );
  for (const name of [...projectSkills].sort()) {
    const link = join(root, ".claude/skills", name);
    const target = readLinkOrNull(link);
    if (target !== `../../.agents/skills/${name}`) {
      findings.add({
        file: `.claude/skills/${name}`,
        rule: "claude-skill-link",
        problem: target === null
          ? "missing symlink; Claude Code reads project skills only from .claude/skills/."
          : `points to ${target}.`,
        fix: `ln -sfn ../../.agents/skills/${name} .claude/skills/${name}`,
      });
    }
  }
  if (isDirectory(join(root, ".claude/skills"))) {
    for (const entry of listDir(join(root, ".claude/skills"))) {
      if (entry.isDirectory && !entry.isSymlink) {
        findings.add({
          file: `.claude/skills/${entry.name}`,
          rule: "claude-skill-link",
          problem:
            "is a real directory, so it can drift from .agents/skills (openspec update with a Claude target does this).",
          fix:
            `replace it with a symlink: rm -r .claude/skills/${entry.name} && ln -s ../../.agents/skills/${entry.name} .claude/skills/${entry.name}`,
        });
      }
    }
  }
}

function checkSymlinks() {
  for (const path of tracked) {
    const full = join(root, path);
    let info: Deno.FileInfo;
    try {
      info = Deno.lstatSync(full);
    } catch (error) {
      if (error instanceof Deno.errors.NotFound) continue; // deleted but not yet staged
      throw error;
    }
    if (!info.isSymlink) continue;
    const target = normalize(join(dirname(full), Deno.readLinkSync(full)));
    if (!exists(target)) {
      findings.add({
        file: path,
        rule: "dangling-symlink",
        problem: `points to ${relative(root, target)}, which does not exist.`,
        fix: "restore the target or remove the link.",
      });
    } else if (relative(root, target).startsWith("..")) {
      findings.add({
        file: path,
        rule: "symlink-escape",
        problem: "points outside the repository.",
        fix: "link only to paths inside the repository.",
      });
    }
  }
}

function checkOpenSpecTarget() {
  if (!isDirectory(join(root, "openspec"))) return;
  const marker = join(root, ".agents/skills/.openspec-target");
  const value = exists(marker) ? readText(marker).trim() : null;
  if (value !== "agents") {
    findings.add({
      file: ".agents/skills/.openspec-target",
      rule: "openspec-target",
      problem: value === null ? "marker is missing." : `marker says "${value}".`,
      fix:
        "regenerate the OpenSpec skills with `openspec init --tools agents --force`; never run `openspec update` here.",
    });
  }
}

// Every page of the documentation site is reachable from its navigation file;
// a page outside the nav is published nowhere and read by nobody.
function checkDocsReachable() {
  const pages = tracked.filter((p) => p.startsWith("docs/") && p.endsWith(".md"));
  if (pages.length === 0) return;
  const navPath = "docs/.nav.yml";
  if (!exists(join(root, navPath))) {
    findings.add({
      file: navPath,
      rule: "doc-reachable",
      problem: "docs/ holds pages but no navigation file.",
      fix: "create docs/.nav.yml (awesome-nav) listing every page.",
    });
    return;
  }
  const nav = readText(join(root, navPath));
  for (const page of pages) {
    const rel = page.slice("docs/".length);
    if (rel === "index.md") continue;
    if (!nav.includes(rel)) {
      findings.add({
        file: page,
        rule: "doc-reachable",
        problem: `not listed in ${navPath}.`,
        fix: "add the page to the nav or delete it.",
      });
    }
  }
}

// README.md (Chinese) and README.en.md mirror each other: the skill table of
// each lists the same skills, every shipped skill appears in both, and the
// relative links agree (the cross-links between the two READMEs excepted).
function checkReadmes() {
  const readmes = ["README.md", "README.en.md"];
  const shipped = tracked.filter((p) => /^skills\/[^/]+\/SKILL\.md$/.test(p)).map((p) =>
    p.split("/")[1]
  );
  const tables = new Map<string, Set<string>>();
  const links = new Map<string, Set<string>>();
  for (const readme of readmes) {
    if (!exists(join(root, readme))) {
      if (shipped.length > 0 || exists(join(root, readmes[0]))) {
        findings.add({
          file: readme,
          rule: "readme-mirror",
          problem: "file is missing.",
          fix: "write it as the translation of the other README, same skill table.",
        });
      }
      continue;
    }
    const text = readText(join(root, readme));
    tables.set(readme, skillTableNames(text));
    links.set(
      readme,
      new Set(
        [...text.matchAll(LINK_RE)].map((m) => m[1]).filter((t) =>
          !/^(https?:|mailto:|#)/.test(t) && !/^README(\.[a-z]{2})?\.md$/.test(t)
        ),
      ),
    );
  }
  if (tables.size === 2) {
    const [a, b] = readmes;
    for (const name of tables.get(a)!) {
      if (!tables.get(b)!.has(name)) {
        findings.add({
          file: b,
          rule: "readme-mirror",
          problem: `skill table lacks the row for ${name}, which ${a} lists.`,
          fix: `add the ${name} row so both READMEs describe the same skills.`,
        });
      }
    }
    for (const name of tables.get(b)!) {
      if (!tables.get(a)!.has(name)) {
        findings.add({
          file: a,
          rule: "readme-mirror",
          problem: `skill table lacks the row for ${name}, which ${b} lists.`,
          fix: `add the ${name} row so both READMEs describe the same skills.`,
        });
      }
    }
    for (const target of links.get(a)!) {
      if (!links.get(b)!.has(target)) {
        findings.add({
          file: b,
          rule: "readme-mirror",
          problem: `does not link ${target}, which ${a} links.`,
          fix: "keep the relative links of both READMEs identical.",
        });
      }
    }
  }
  for (const readme of readmes) {
    const names = tables.get(readme);
    if (names === undefined) continue;
    for (const skill of shipped) {
      if (!names.has(skill)) {
        findings.add({
          file: readme,
          rule: "readme-skill-table",
          problem: `skill table has no row for skills/${skill}.`,
          fix: `add a row naming ${skill} with its one-line purpose.`,
        });
      }
    }
  }
}

/** Skill names from table rows under the first heading that mentions skills (English or Chinese). */
function skillTableNames(text: string): Set<string> {
  const names = new Set<string>();
  let inSection = false;
  for (const line of text.split("\n")) {
    if (/^#{1,6}\s/.test(line)) inSection = /skills?|技能/i.test(line);
    if (!inSection) continue;
    const m = line.match(/^\| \*{0,2}`?\[?([a-z0-9-]+)/);
    if (m && m[1] !== "skill") names.add(m[1]);
  }
  return names;
}
