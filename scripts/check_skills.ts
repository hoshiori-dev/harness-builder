#!/usr/bin/env -S deno run --allow-read --allow-run=git
// Lints the skills this plugin ships under skills/. check_plugin.ts holds the
// Agent Plugins floor (layout, name, description length); this script holds
// the quality bar the knowledge base documents: frontmatter budgets, body
// size, structure, links, reachability, script hygiene, and the repository's
// own invariants (layer ownership phrases, shared blocks, entry invocation,
// delivered-asset tests and placeholders). Errors are findings; advice is a
// warning on stderr that never changes the exit code.
import { dirname, join, normalize, relative } from "@std/path";
import {
  exists,
  Findings,
  gitFiles,
  isDirectory,
  listDir,
  readText,
  warn,
} from "./lib/findings.ts";
import { LAYERS, ownershipPhrase } from "./lib/layers.ts";
import { frontmatter, SKILL_NAME_RE } from "./lib/plugin.ts";

const root = Deno.cwd();
const findings = new Findings();
const tracked = gitFiles(root);

const SKILLS_DIR = "skills";
const CANON_PATH = ".agents/knowledge/shared-blocks.md";
const ENTRY_SKILLS = ["harness-create", "harness-improve"];
const PENDING_DECISIONS = [
  "skills/harness-create/references/pending-decisions.md",
  "skills/harness-improve/references/pending-decisions.md",
  "skills/authority-building/references/pending-decisions.md",
];
const INSERTION_MARKER = "<!-- harness: spec-workflow -->";
const INSTALL_CMD_RE =
  /npx skills add|pnpm dlx skills|bunx skills|yarn dlx skills|skills add \S+\/skills/;
const TRIGGER_RE = /\b(when|before|if|on|after|during)\b/i;
const LINK_RE = /\[[^\]]*\]\(([^)\s]+)\)/g;
const SHARED_RE = /<!-- shared:([a-z0-9-]+) -->\n([\s\S]*?)<!-- \/shared:\1 -->/g;
const PLACEHOLDER_RE = /\{\{[A-Z_]+\}\}/;
const DESCRIPTION_LIMIT = 1024;
const DESCRIPTION_WARN = 900;
const COMPATIBILITY_LIMIT = 500;
const BODY_LINE_WARN = 500;
const BODY_TOKEN_WARN = 5000;

const skills = isDirectory(join(root, SKILLS_DIR))
  ? listDir(join(root, SKILLS_DIR)).filter((e) => e.isDirectory).map((e) => e.name)
  : [];

if (skills.length === 0) {
  console.log("check_skills: ok (no skills)");
  Deno.exit(0);
}

const bodies = new Map<string, string>();
for (const name of skills) checkSkill(name);
checkLayerOwnership();
checkSharedBlocks();
checkPendingDecisions();
checkInsertionMarkers();
Deno.exit(findings.report("check_skills"));

function skillFiles(name: string): string[] {
  const prefix = `${SKILLS_DIR}/${name}/`;
  return tracked.filter((p) => p.startsWith(prefix) && p !== `${prefix}SKILL.md`);
}

function checkSkill(name: string) {
  const dir = `${SKILLS_DIR}/${name}`;
  const file = `${dir}/SKILL.md`;
  if (!exists(join(root, file))) return; // check_plugin reports skill-shape
  const text = readText(join(root, file));
  bodies.set(name, text);
  const attrs = frontmatter(join(root, file));
  if (attrs === null) {
    findings.add({
      file,
      rule: "skill-frontmatter",
      problem: "no YAML frontmatter.",
      fix: "start the file with --- name/description/license ---.",
    });
    return;
  }
  checkFrontmatter(name, file, attrs);
  checkBodySize(file, text);
  checkStructure(name, dir);
  checkLinksAndReachability(name, dir, file, text);
  checkScripts(name);
  checkBodyRules(name, file, text);
  checkEntryInvocation(name, file, attrs);
}

function checkFrontmatter(name: string, file: string, attrs: Record<string, unknown>) {
  if (attrs.name !== name) {
    findings.add({
      file,
      rule: "skill-name",
      problem: `frontmatter name ${JSON.stringify(attrs.name)} differs from the directory name.`,
      fix: `set name: ${name}.`,
    });
  } else if (!SKILL_NAME_RE.test(name) || name.length > 64) {
    findings.add({
      file,
      rule: "skill-name",
      problem: `"${name}" is not a valid skill name.`,
      fix: "use 1-64 lowercase letters, digits, and single hyphens.",
    });
  }
  const description = attrs.description;
  if (typeof description !== "string" || description.trim() === "") {
    findings.add({
      file,
      rule: "skill-description",
      problem: "description is missing or empty.",
      fix: "write a description that names the capability and lists the triggers.",
    });
  } else {
    const length = [...description].length;
    if (length > DESCRIPTION_LIMIT) {
      findings.add({
        file,
        rule: "skill-description",
        problem: `description has ${length} characters (limit ${DESCRIPTION_LIMIT}).`,
        fix: "cut identity that the body already states; keep one trigger per branch.",
      });
    } else if (length > DESCRIPTION_WARN) {
      warn({
        file,
        rule: "skill-description-long",
        problem: `description has ${length} characters (advice: stay under ${DESCRIPTION_WARN}).`,
        fix: "prune restated capability; every character is permanent context load.",
      });
    }
  }
  if (typeof attrs.license !== "string" || attrs.license.trim() === "") {
    findings.add({
      file,
      rule: "skill-license",
      problem: "frontmatter has no license.",
      fix: "add license: Apache-2.0 (the plugin's license).",
    });
  }
  const hasScripts = skillFiles(name).some((p) => p.endsWith(".py"));
  if ("compatibility" in attrs) {
    const compat = attrs.compatibility;
    if (typeof compat !== "string" || [...compat].length > COMPATIBILITY_LIMIT) {
      findings.add({
        file,
        rule: "skill-compatibility",
        problem: `compatibility is not a string of at most ${COMPATIBILITY_LIMIT} characters.`,
        fix: "state only the runtime the bundled scripts require, briefly.",
      });
    }
    if (!hasScripts) {
      warn({
        file,
        rule: "skill-compatibility",
        problem: "declares compatibility but bundles no script.",
        fix: "remove the field; a SKILL.md-only skill has no environment requirement.",
      });
    }
  } else if (hasScripts) {
    warn({
      file,
      rule: "skill-compatibility",
      problem: "bundles scripts but declares no compatibility.",
      fix: "add a compatibility line naming the runtime (Python 3.10+, uv optional).",
    });
  }
}

function checkBodySize(file: string, text: string) {
  const body = text.replace(/^---\n[\s\S]*?\n---\n?/, "");
  const lines = body.split("\n").length;
  const tokens = Math.round(body.length / 4);
  if (lines > BODY_LINE_WARN || tokens > BODY_TOKEN_WARN) {
    warn({
      file,
      rule: "skill-body-size",
      problem:
        `body has ${lines} lines and about ${tokens} tokens (advice: under ${BODY_LINE_WARN} lines and ${BODY_TOKEN_WARN} tokens).`,
      fix: "disclose branch-specific material into references/ behind a when-to-read pointer.",
    });
  }
}

function checkStructure(name: string, dir: string) {
  for (const sub of ["scripts", "references", "assets"]) {
    const path = join(root, dir, sub);
    if (!isDirectory(path)) continue;
    if (!tracked.some((p) => p.startsWith(`${dir}/${sub}/`))) {
      findings.add({
        file: `${dir}/${sub}/`,
        rule: "skill-structure",
        problem: "directory holds no tracked file.",
        fix: "delete the empty directory or put the file it was made for in it.",
      });
    }
  }
  if (exists(join(root, dir, "README.md"))) {
    findings.add({
      file: `${dir}/README.md`,
      rule: "skill-structure",
      problem: "a skill root holds no README; SKILL.md is the whole entry.",
      fix: "move the content into SKILL.md or a references/ file and delete README.md.",
    });
  }
  const unexpected = skillFiles(name).filter((p) => {
    const rel = p.slice(dir.length + 1);
    return !/^(scripts|references|assets)\//.test(rel) && rel !== "README.md";
  });
  for (const p of unexpected) {
    findings.add({
      file: p,
      rule: "skill-structure",
      problem: "file sits outside scripts/, references/, and assets/.",
      fix: "move it into one of those directories and link it from SKILL.md.",
    });
  }
}

function linksOf(text: string): { target: string; line: number }[] {
  const out: { target: string; line: number }[] = [];
  text.split("\n").forEach((line, index) => {
    for (const match of line.matchAll(LINK_RE)) {
      const target = match[1];
      if (/^(https?:|mailto:|#)/.test(target)) continue;
      const path = target.split("#")[0];
      if (path !== "") out.push({ target: path, line: index + 1 });
    }
  });
  return out;
}

function checkLinksAndReachability(name: string, dir: string, file: string, text: string) {
  const reachable = new Set<string>();
  const visit = (from: string, body: string, hop: number) => {
    for (const { target, line } of linksOf(body)) {
      const resolved = normalize(join(dirname(from), target));
      if (target.startsWith("/") || relative(dir, resolved).startsWith("..")) {
        findings.add({
          file: from,
          line,
          rule: "skill-link-escape",
          problem: `link ${target} leaves the skill directory.`,
          fix: "a skill is self-contained: copy the material into the skill or drop the link.",
        });
        continue;
      }
      if (!exists(join(root, resolved))) {
        findings.add({
          file: from,
          line,
          rule: "skill-link",
          problem: `link target ${target} does not exist.`,
          fix: "correct the path or remove the pointer.",
        });
        continue;
      }
      if (reachable.has(resolved)) continue;
      reachable.add(resolved);
      if (hop === 0 && resolved.endsWith(".md")) visit(resolved, readText(join(root, resolved)), 1);
    }
  };
  visit(file, text, 0);
  for (const p of skillFiles(name)) {
    if (p.endsWith("_test.py")) continue;
    if (!reachable.has(p)) {
      findings.add({
        file: p,
        rule: "skill-file-reachable",
        problem: "not linked from SKILL.md or from a file SKILL.md links.",
        fix: "link it at first mention with its load condition, or delete it.",
      });
    }
  }
}

function checkScripts(name: string) {
  const scripts = skillFiles(name).filter((p) =>
    p.endsWith(".py") && !p.endsWith("_test.py") &&
    /^skills\/[^/]+\/(scripts|assets)\//.test(p)
  );
  for (const p of scripts) {
    const text = readText(join(root, p));
    const firstLine = text.split("\n")[0];
    if (
      firstLine !== "#!/usr/bin/env -S uv run --script" && firstLine !== "#!/usr/bin/env python3"
    ) {
      findings.add({
        file: p,
        line: 1,
        rule: "script-shebang",
        problem: "first line is not a uv or python3 shebang.",
        fix:
          "use `#!/usr/bin/env -S uv run --script` (or `#!/usr/bin/env python3` for stdlib-only).",
      });
    }
    if (!text.includes("# /// script") || !/requires-python\s*=\s*">=3\.10"/.test(text)) {
      findings.add({
        file: p,
        rule: "script-pep723",
        problem: 'no PEP 723 block with requires-python = ">=3.10".',
        fix: "add the `# /// script` block so uv and plain python3 agree on the runtime.",
      });
    }
    if (!text.includes("--help")) {
      findings.add({
        file: p,
        rule: "script-help",
        problem: "does not mention --help.",
        fix: "accept --help with a usage example; agents read it before running the script.",
      });
    }
    const test = p.replace(/\.py$/, "_test.py");
    if (!exists(join(root, test))) {
      findings.add({
        file: p,
        rule: "asset-has-test",
        problem: `has no sibling ${test.split("/").at(-1)}.`,
        fix: "add the pytest file; delivered management code is tested in this repository.",
      });
    }
  }
  const assets = skillFiles(name).filter((p) => /^skills\/[^/]+\/assets\//.test(p));
  for (const p of assets) {
    const lines = readText(join(root, p)).split("\n");
    lines.forEach((line, index) => {
      if (PLACEHOLDER_RE.test(line) && !line.includes("# CONFIGURE:")) {
        findings.add({
          file: p,
          line: index + 1,
          rule: "asset-no-placeholder",
          problem: "placeholder outside a `# CONFIGURE:` line.",
          fix:
            "assets are starting shapes with real text; mark the few settings a target fills with `# CONFIGURE:`.",
        });
      }
    });
  }
}

function checkBodyRules(name: string, file: string, text: string) {
  const lines = text.split("\n");
  lines.forEach((line, index) => {
    if (INSTALL_CMD_RE.test(line)) {
      findings.add({
        file,
        line: index + 1,
        rule: "skill-no-install-cmd",
        problem: "names an external skill-library install command.",
        fix:
          "the plugin is self-contained; state the rule here instead of pointing at another library.",
      });
    }
    if (/\]\((?:\.\/)?references\/[^)]+\.md\)/.test(line) && !TRIGGER_RE.test(line)) {
      warn({
        file,
        line: index + 1,
        rule: "skill-pointer-has-trigger",
        problem: "links a reference without a load condition on the same line.",
        fix: 'word the pointer as "Read references/x.md when …".',
      });
    }
  });
  for (const p of skillFiles(name).filter((p) => p.endsWith(".md"))) {
    readText(join(root, p)).split("\n").forEach((line, index) => {
      if (INSTALL_CMD_RE.test(line)) {
        findings.add({
          file: p,
          line: index + 1,
          rule: "skill-no-install-cmd",
          problem: "names an external skill-library install command.",
          fix:
            "the plugin is self-contained; state the rule here instead of pointing at another library.",
        });
      }
    });
  }
}

function checkEntryInvocation(name: string, file: string, attrs: Record<string, unknown>) {
  const isEntry = ENTRY_SKILLS.includes(name);
  const flag = attrs["disable-model-invocation"];
  if (isEntry && flag !== true) {
    findings.add({
      file,
      rule: "entry-invocation",
      problem: "an entry skill must be user-invoked only.",
      fix: "add `disable-model-invocation: true` to the frontmatter.",
    });
  } else if (!isEntry && flag !== undefined) {
    findings.add({
      file,
      rule: "entry-invocation",
      problem:
        "only the entry skills (harness-create, harness-improve) may disable model invocation.",
      fix:
        "remove `disable-model-invocation`; builders are reached by the entries through their descriptions.",
    });
  }
}

function checkLayerOwnership() {
  const phraseRe = /Owns the ([a-z -]+?) layer/g;
  for (const [name, text] of bodies) {
    const attrs = frontmatter(join(root, SKILLS_DIR, name, "SKILL.md"));
    const description = typeof attrs?.description === "string" ? attrs.description : "";
    const file = `${SKILLS_DIR}/${name}/SKILL.md`;
    const phrases = [...description.matchAll(phraseRe)].map((m) => m[1]);
    const isBuilder = name.endsWith("-building") && name !== "project-skill-building";
    if (isBuilder) {
      if (phrases.length !== 1) {
        findings.add({
          file,
          rule: "layer-ownership",
          problem:
            `description carries ${phrases.length} ownership phrases; a layer builder carries exactly one.`,
          fix: `write "${
            ownershipPhrase("<layer>")
          }" once, with a layer from scripts/lib/layers.ts.`,
        });
      } else if (!(LAYERS as readonly string[]).includes(phrases[0])) {
        findings.add({
          file,
          rule: "layer-ownership",
          problem: `"${phrases[0]}" is not a layer.`,
          fix: `use one of: ${LAYERS.join(", ")}.`,
        });
      }
    } else if (phrases.length > 0 || phraseRe.test(text)) {
      findings.add({
        file,
        rule: "layer-ownership",
        problem: "carries an ownership phrase but is not a layer builder.",
        fix: "remove the phrase; only <layer>-building skills own a layer.",
      });
    }
    phraseRe.lastIndex = 0;
  }
}

function checkSharedBlocks() {
  const canonPath = join(root, CANON_PATH);
  const canon = new Map<string, string>();
  const used = new Set<string>();
  if (exists(canonPath)) {
    for (const m of readText(canonPath).matchAll(SHARED_RE)) canon.set(m[1], trimLines(m[2]));
  }
  for (const [name, text] of bodies) {
    const file = `${SKILLS_DIR}/${name}/SKILL.md`;
    for (const m of text.matchAll(SHARED_RE)) {
      const id = m[1];
      used.add(id);
      if (!canon.has(id)) {
        findings.add({
          file,
          rule: "shared-block",
          problem: `shared block "${id}" has no canon in ${CANON_PATH}.`,
          fix: `add the block under the same delimiters to ${CANON_PATH}, or drop the delimiters.`,
        });
      } else if (trimLines(m[2]) !== canon.get(id)) {
        findings.add({
          file,
          rule: "shared-block",
          problem: `shared block "${id}" differs from its canon.`,
          fix: `copy the block from ${CANON_PATH} verbatim (or change the canon and every user).`,
        });
      }
    }
  }
  for (const id of canon.keys()) {
    if (!used.has(id)) {
      findings.add({
        file: CANON_PATH,
        rule: "shared-block",
        problem: `canon block "${id}" is used by no skill.`,
        fix: "delete the block from the canon or add it to the skill that needs it.",
      });
    }
  }
}

function trimLines(text: string): string {
  return text.split("\n").map((l) => l.trimEnd()).join("\n");
}

function checkPendingDecisions() {
  const present = PENDING_DECISIONS.filter((p) => exists(join(root, p)));
  if (present.length < 2) return;
  const canon = readText(join(root, present[0]));
  for (const p of present.slice(1)) {
    if (readText(join(root, p)) !== canon) {
      findings.add({
        file: p,
        rule: "pending-decisions-identical",
        problem: `differs from ${present[0]}.`,
        fix:
          "the pending-decisions format has one text; copy it byte for byte into every skill that carries it.",
      });
    }
  }
}

function checkInsertionMarkers() {
  for (const platform of ["github", "gitlab"]) {
    const dir = `skills/platform-lifecycle-building/assets/${platform}`;
    if (!isDirectory(join(root, dir))) continue;
    let count = 0;
    for (const p of tracked.filter((p) => p.startsWith(`${dir}/`))) {
      count += readText(join(root, p)).split(INSERTION_MARKER).length - 1;
    }
    if (count !== 3) {
      findings.add({
        file: `${dir}/`,
        rule: "insertion-markers",
        problem:
          `${count} insertion marker(s) "${INSERTION_MARKER}" across the assets; exactly 3 are expected.`,
        fix:
          "one marker each in the request template, the project skill's finish step, and the platform knowledge file.",
      });
    }
  }
}
