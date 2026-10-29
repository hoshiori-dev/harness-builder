import { assertEquals } from "@std/assert";
import { join } from "@std/path";
import { fixturePlugin, makeTree, runScript } from "./lib/testing.ts";

function git(root: string, ...args: string[]) {
  const r = new Deno.Command("git", {
    args: [
      "-c",
      "user.name=t",
      "-c",
      "user.email=t@example.com",
      "-c",
      "commit.gpgsign=false",
      ...args,
    ],
    cwd: root,
    env: { GIT_CONFIG_GLOBAL: "/dev/null", GIT_CONFIG_NOSYSTEM: "1" },
    stdout: "piped",
    stderr: "piped",
  }).outputSync();
  if (!r.success) throw new Error(new TextDecoder().decode(r.stderr));
}

Deno.test("dist archives the portable plugin with every client's generated files", () => {
  const root = makeTree(fixturePlugin());
  assertEquals(runScript("gen.ts", [], root).code, 0);
  git(root, "init", "-q");
  git(root, "add", "-A");
  git(root, "commit", "-q", "-m", "fixture");
  const result = runScript("dist.ts", ["--tag", "v1.2.3"], root);
  assertEquals(result.code, 0, result.output);
  const list = new Deno.Command("unzip", {
    args: ["-Z1", join(root, "dist/fixture-plugin-1.2.3.zip")],
    stdout: "piped",
    stderr: "piped",
  }).outputSync();
  assertEquals(list.success, true, `unzip failed: ${new TextDecoder().decode(list.stderr)}`);
  const entries = new TextDecoder().decode(list.stdout).trim().split("\n");
  for (
    const expected of [
      "fixture-plugin/plugin.json",
      "fixture-plugin/mcp.json",
      "fixture-plugin/skills/alpha/SKILL.md",
      "fixture-plugin/.claude-plugin/plugin.json",
      "fixture-plugin/.claude-plugin/marketplace.json",
      "fixture-plugin/com.anthropic.claude-code/mcp.json",
      "fixture-plugin/com.anthropic.claude-code/agents/reviewer.md",
      "fixture-plugin/mcp_config.json",
      "fixture-plugin/.agents/plugins/marketplace.json",
    ]
  ) assertEquals(entries.includes(expected), true, `missing ${expected} in ${entries.join(", ")}`);
  assertEquals(
    entries.some((e) => e.startsWith("fixture-plugin/openspec/")),
    false,
    "specs are not shipped",
  );
});
