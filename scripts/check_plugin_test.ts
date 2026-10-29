import { assertEquals, assertStringIncludes } from "@std/assert";
import { join } from "@std/path";
import { fixturePlugin, makeTree, MANIFEST, runScript, writeTree } from "./lib/testing.ts";

Deno.test("check_plugin passes on the fixture plugin", () => {
  const root = makeTree(fixturePlugin());
  const result = runScript("check_plugin.ts", [], root);
  assertEquals(result.code, 0, result.output);
});

Deno.test("check_plugin reports layout and wiring findings", () => {
  const root = makeTree(fixturePlugin());
  writeTree(root, {
    "skills/beta/SKILL.md": "---\nname: Beta\ndescription: x\n---\n",
    ".agents/skills/alpha/SKILL.md": "---\nname: alpha\ndescription: project skill\n---\n",
    "com.openai/agents/rogue.toml": 'name = "rogue"\ndescription = "Codex cannot ship this."\n',
    "openspec/specs/agent/ghost/spec.md": "# ghost\n",
  });
  Deno.removeSync(join(root, "openspec/specs/skill/alpha/spec.md"));
  const result = runScript("check_plugin.ts", [], root);
  assertEquals(result.code, 1);
  for (
    const expected of [
      "skills/beta/SKILL.md: skill-name",
      "skills/alpha/SKILL.md: skill-name-collision",
      "com.openai/agents: agent-unsupported",
      "openspec/specs/skill/alpha/spec.md: catalog-missing-spec",
      "openspec/specs/agent/ghost/spec.md: catalog-orphan-spec",
      "openspec/specs/skill/beta/spec.md: catalog-missing-spec",
    ]
  ) assertStringIncludes(result.output, expected);
});

Deno.test("check_plugin requires the Codex extension block and config for a supported Codex", () => {
  const files = fixturePlugin();
  files[".codex/config.toml"] = '[plugins."fixture-plugin@fixture-plugin"]\nenabled = false\n';
  const root = makeTree(files);
  const result = runScript("check_plugin.ts", [], root);
  assertEquals(result.code, 1);
  assertStringIncludes(result.output, ".codex/config.toml: codex-plugin-enabled");

  const manifest = structuredClone(MANIFEST) as Record<string, unknown>;
  manifest.extensions = { "com.example": {} };
  writeTree(root, { "plugin.json": JSON.stringify(manifest) + "\n" });
  const noBlock = runScript("check_plugin.ts", [], root);
  assertStringIncludes(noBlock.output, "plugin.json: extension-namespace");
  assertStringIncludes(noBlock.output, "plugin.json: codex-extension");
});

Deno.test("check_plugin skips catalogs loudly when openspec is absent", () => {
  const root = makeTree(fixturePlugin());
  Deno.removeSync(join(root, "openspec"), { recursive: true });
  const result = runScript("check_plugin.ts", [], root);
  assertEquals(result.code, 0, result.output);
  assertStringIncludes(result.output, "openspec/specs is absent; catalog checks skipped");
});

Deno.test("check_plugin --footprint lists a client's files", () => {
  const root = makeTree(fixturePlugin());
  runScript("gen.ts", [], root);
  const result = runScript("check_plugin.ts", ["--footprint", "antigravity"], root);
  assertEquals(result.code, 0);
  assertEquals(result.output.trim().split("\n"), ["mcp_config.json"]);
  const codex = runScript("check_plugin.ts", ["--footprint", "codex"], root);
  assertEquals(codex.output.trim().split("\n"), [
    ".agents/plugins/marketplace.json",
    ".codex/config.toml",
  ]);
});

Deno.test("check_plugin accepts an entry whose spec an unarchived change proposes", () => {
  const root = makeTree(fixturePlugin());
  Deno.removeSync(join(root, "openspec/specs/skill/alpha/spec.md"));
  writeTree(root, { "openspec/changes/add-alpha/specs/skill/alpha/spec.md": "# Spec Delta\n" });
  const pending = runScript("check_plugin.ts", [], root);
  assertEquals(pending.code, 0, pending.output);
  writeTree(root, {
    "openspec/changes/archive/2026-01-01-old/specs/skill/alpha/spec.md": "# Spec Delta\n",
  });
  Deno.removeSync(join(root, "openspec/changes/add-alpha"), { recursive: true });
  const archivedOnly = runScript("check_plugin.ts", [], root);
  assertEquals(archivedOnly.code, 1);
  assertStringIncludes(
    archivedOnly.output,
    "openspec/specs/skill/alpha/spec.md: catalog-missing-spec",
  );
});
