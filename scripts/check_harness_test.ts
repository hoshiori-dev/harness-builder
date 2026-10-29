import { assertEquals, assertStringIncludes } from "@std/assert";
import { FileSpec, makeTree, runScript, writeTree } from "./lib/testing.ts";

function harness(): Record<string, FileSpec> {
  return {
    "AGENTS.md": "# Fixture\n\nRead [the guide](.agents/knowledge/guide.md). Run `just check`.\n",
    "CLAUDE.md": "@AGENTS.md\n",
    "justfile": "check:\n    echo ok\n",
    ".agents/knowledge/guide.md": "# Guide\n",
    ".agents/skills/helper/SKILL.md":
      "---\nname: helper\ndescription: Fixture project skill.\n---\n",
    ".claude/skills/helper": { symlink: "../../.agents/skills/helper" },
  };
}

function gitInit(root: string) {
  for (const args of [["init", "-q"], ["add", "-A"]]) {
    const r = new Deno.Command("git", { args, cwd: root, stdout: "null", stderr: "piped" })
      .outputSync();
    if (!r.success) throw new Error(new TextDecoder().decode(r.stderr));
  }
}

Deno.test("check_harness passes on a consistent fixture harness", () => {
  const root = makeTree(harness());
  gitInit(root);
  const result = runScript("check_harness.ts", [], root);
  assertEquals(result.code, 0, result.output);
});

Deno.test("check_harness reports broken links, unknown recipes, unreachable knowledge, and link drift", () => {
  const files = harness();
  files["AGENTS.md"] =
    "# Fixture\n\nRead [the guide](.agents/knowledge/missing.md). Run `just nope`.\n";
  files[".agents/knowledge/orphan.md"] = "# Orphan\n";
  files[".claude/skills/helper"] = "not a link\n";
  files[".agents/skills/Bad/SKILL.md"] = "---\nname: bad\ndescription: x\n---\n";
  files["dangling"] = { symlink: "nowhere" };
  const root = makeTree(files);
  gitInit(root);
  writeTree(root, { "AGENTS.md": files["AGENTS.md"] + Array(130).fill("line").join("\n") });
  const result = runScript("check_harness.ts", [], root);
  assertEquals(result.code, 1);
  for (
    const expected of [
      "AGENTS.md:3: doc-link",
      "AGENTS.md:3: doc-recipe",
      "AGENTS.md: entrypoint-budget",
      ".agents/knowledge/orphan.md: knowledge-reachable",
      ".agents/skills/Bad/SKILL.md: skill-name",
      ".claude/skills/helper: claude-skill-link",
      "dangling: dangling-symlink",
    ]
  ) assertStringIncludes(result.output, expected);
});

function readme(lang: "zh" | "en", rows: string[]): string {
  const heading = lang === "zh" ? "## 技能" : "## Skills";
  return `# Fixture\n\n${heading}\n\n| Skill | Purpose |\n|---|---|\n${
    rows.map((r) => `| [${r}](skills/${r}/) | x |`).join("\n")
  }\n`;
}

Deno.test("check_harness mirrors the READMEs and the docs nav", () => {
  const files = harness();
  files["README.md"] = readme("zh", ["alpha", "beta"]);
  files["README.en.md"] = readme("en", ["alpha"]);
  files["skills/alpha/SKILL.md"] = "---\nname: alpha\ndescription: x\n---\n";
  files["skills/gamma/SKILL.md"] = "---\nname: gamma\ndescription: x\n---\n";
  files["docs/index.md"] = "# Docs\n";
  files["docs/guide.md"] = "# Guide\n";
  files["docs/.nav.yml"] = "nav:\n  - index.md\n";
  const root = makeTree(files);
  gitInit(root);
  const result = runScript("check_harness.ts", [], root);
  assertEquals(result.code, 1, result.output);
  for (
    const expected of [
      "README.en.md: readme-mirror: skill table lacks the row for beta",
      "README.en.md: readme-mirror: does not link skills/beta/",
      "README.md: readme-skill-table: skill table has no row for skills/gamma",
      "README.en.md: readme-skill-table: skill table has no row for skills/gamma",
      "docs/guide.md: doc-reachable",
    ]
  ) assertStringIncludes(result.output, expected);
  writeTree(root, {
    "README.en.md": "[中文](README.md)\n\n" + readme("en", ["alpha", "beta", "gamma"]),
    "README.md": "[English](README.en.md)\n\n" + readme("zh", ["alpha", "beta", "gamma"]),
    "skills/beta/SKILL.md": "---\nname: beta\ndescription: x\n---\n",
    "docs/.nav.yml": "nav:\n  - index.md\n  - guide.md\n",
  });
  const fixed = runScript("check_harness.ts", [], root);
  assertEquals(fixed.code, 0, fixed.output);
});
