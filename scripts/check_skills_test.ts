import { assertEquals, assertStringIncludes } from "@std/assert";
import { FileSpec, makeTree, runScript, writeTree } from "./lib/testing.ts";

const PY = [
  "#!/usr/bin/env -S uv run --script",
  "# /// script",
  '# requires-python = ">=3.10"',
  "# ///",
  '"""Usage: tool.py --help"""',
  "",
].join("\n");

function skill(name: string, description: string, extra = ""): string {
  return `---\nname: ${name}\ndescription: ${description}\nlicense: Apache-2.0\n${extra}---\n# ${name}\n\nBody.\n`;
}

function fixture(): Record<string, FileSpec> {
  return {
    "skills/environment-building/SKILL.md": skill(
      "environment-building",
      "Owns the environment layer of an agent harness. Use when a build reaches it.",
    ) + "Read [threat model](references/threat-model.md) when rating isolation.\n" +
      "<!-- shared:plan-is-not-approval -->\nA plan is not approval.\n<!-- /shared:plan-is-not-approval -->\n",
    "skills/environment-building/references/threat-model.md": "# Threat model\n",
    "skills/harness-create/SKILL.md": skill(
      "harness-create",
      "Creates a harness. Use when the user invokes it.",
      "disable-model-invocation: true\n",
    ),
    "skills/entropy-building/SKILL.md": skill(
      "entropy-building",
      "Owns the entropy layer. Use when a build reaches it.",
      "compatibility: Python 3.10+.\n",
    ) + "Run [the check](assets/check_harness.py) after depositing it.\n",
    "skills/entropy-building/assets/check_harness.py": PY + "print('ok')\n",
    "skills/entropy-building/assets/check_harness_test.py": "def test_ok():\n    pass\n",
    ".agents/knowledge/shared-blocks.md":
      "# Shared blocks\n\n<!-- shared:plan-is-not-approval -->\nA plan is not approval.\n<!-- /shared:plan-is-not-approval -->\n",
  };
}

function gitInit(root: string) {
  for (const args of [["init", "-q"], ["add", "-A"]]) {
    const r = new Deno.Command("git", { args, cwd: root, stdout: "null", stderr: "piped" })
      .outputSync();
    if (!r.success) throw new Error(new TextDecoder().decode(r.stderr));
  }
}

Deno.test("check_skills passes with no skills directory", () => {
  const root = makeTree({ "plugin.json": "{}\n" });
  gitInit(root);
  const result = runScript("check_skills.ts", [], root);
  assertEquals(result.code, 0, result.output);
  assertStringIncludes(result.output, "no skills");
});

Deno.test("check_skills passes on a consistent fixture", () => {
  const root = makeTree(fixture());
  gitInit(root);
  const result = runScript("check_skills.ts", [], root);
  assertEquals(result.code, 0, result.output);
});

Deno.test("check_skills reports every repository rule", () => {
  const files = fixture();
  // layer builder without a phrase; non-builder with a phrase; entry without the flag
  files["skills/authority-building/SKILL.md"] = skill(
    "authority-building",
    "Authority rules. Use when asked.",
  ) + "See [notes](references/notes.md).\n" +
    "<!-- shared:nothing-lands -->\ntext\n<!-- /shared:nothing-lands -->\n";
  files["skills/authority-building/references/notes.md"] = "# Notes\n";
  files["skills/authority-building/references/orphan.md"] = "# Orphan\n";
  files["skills/authority-building/references/pending-decisions.md"] = "A\n";
  files["skills/harness-create/references/pending-decisions.md"] = "B\n";
  files["skills/harness-create/SKILL.md"] = skill(
    "harness-create",
    "Creates a harness. Owns the entropy layer. Use when invoked.",
  ) + "Install with `npx skills add someone/skills`.\n" +
    "Read [pending](references/pending-decisions.md) when blocked.\n";
  files["skills/harness-improve/SKILL.md"] = skill(
    "harness-improve",
    "Improves a harness.",
    "disable-model-invocation: true\n",
  ) + "Escape [up](../harness-create/SKILL.md) when needed.\n" +
    "Missing [file](references/none.md) when needed.\n";
  files["skills/entropy-building/assets/check_harness.py"] = "print('no shebang')\n";
  files["skills/entropy-building/assets/sync.py"] = PY + "x = '{{OWNER}}'\n";
  files["skills/entropy-building/SKILL.md"] = skill(
    "entropy-building",
    "Owns the entropy layer. Use when a build reaches it.",
    "disable-model-invocation: true\n",
  ) + "Run [the check](assets/check_harness.py) and [sync](assets/sync.py) after depositing.\n";
  files["skills/entropy-building/README.md"] = "# nope\n";
  files["skills/entropy-building/stray.txt"] = "x\n";
  files["skills/platform-lifecycle-building/SKILL.md"] = skill(
    "platform-lifecycle-building",
    "Owns the platform lifecycle layer. Use when a build reaches it.",
  ) + "Copy [the template](assets/github/pull-request-template.md) when asked.\n";
  files["skills/platform-lifecycle-building/assets/github/pull-request-template.md"] =
    "<!-- harness: spec-workflow -->\n";
  const root = makeTree(files);
  gitInit(root);
  writeTree(root, {
    "skills/environment-building/SKILL.md": files["skills/environment-building/SKILL.md"]
      .toString().replace("A plan is not approval.", "A plan is approval."),
  });
  const result = runScript("check_skills.ts", [], root);
  assertEquals(result.code, 1, result.output);
  for (
    const expected of [
      "skills/authority-building/SKILL.md: layer-ownership",
      'shared block "nothing-lands" has no canon',
      "skills/authority-building/references/orphan.md: skill-file-reachable",
      "skills/harness-create/SKILL.md: entry-invocation",
      "skills/harness-create/SKILL.md: layer-ownership",
      "skill-no-install-cmd",
      "skills/harness-improve/SKILL.md:10: skill-link-escape",
      "skills/harness-improve/SKILL.md:11: skill-link",
      "skills/entropy-building/assets/check_harness.py:1: script-shebang",
      "skills/entropy-building/assets/check_harness.py: script-pep723",
      "skills/entropy-building/assets/sync.py: asset-has-test",
      "skills/entropy-building/assets/sync.py:6: asset-no-placeholder",
      "skills/entropy-building/SKILL.md: entry-invocation",
      "skills/entropy-building/README.md: skill-structure",
      "skills/entropy-building/stray.txt: skill-structure",
      "skills/environment-building/SKILL.md: shared-block",
      "pending-decisions-identical",
      "skills/platform-lifecycle-building/assets/github/: insertion-markers",
    ]
  ) assertStringIncludes(result.output, expected);
});

Deno.test("check_skills warns without failing", () => {
  const files = fixture();
  files["skills/environment-building/SKILL.md"] = skill(
    "environment-building",
    "Owns the environment layer. " + "x".repeat(900),
    "compatibility: none needed\n",
  ) + "Read [threat model](references/threat-model.md).\n" +
    "<!-- shared:plan-is-not-approval -->\nA plan is not approval.\n<!-- /shared:plan-is-not-approval -->\n";
  const root = makeTree(files);
  gitInit(root);
  const result = runScript("check_skills.ts", [], root);
  assertEquals(result.code, 0, result.output);
  for (
    const expected of [
      "WARN skills/environment-building/SKILL.md: skill-description-long",
      "WARN skills/environment-building/SKILL.md: skill-compatibility",
      "skill-pointer-has-trigger",
    ]
  ) assertStringIncludes(result.output, expected);
});
