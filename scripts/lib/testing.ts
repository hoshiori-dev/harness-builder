// Helpers for the management-code tests: build a throwaway repository from a
// file map and run a script against it as a subprocess, the way `just` does.
import { dirname, fromFileUrl, join } from "@std/path";

export type FileSpec = string | { symlink: string };

/** Creates a temp directory holding `files`; keys are relative paths. */
export function makeTree(files: Record<string, FileSpec>): string {
  const root = Deno.makeTempDirSync({ prefix: "aps-test-" });
  writeTree(root, files);
  return root;
}

export function writeTree(root: string, files: Record<string, FileSpec>): void {
  for (const [path, spec] of Object.entries(files)) {
    const full = join(root, path);
    Deno.mkdirSync(dirname(full), { recursive: true });
    if (typeof spec === "string") Deno.writeTextFileSync(full, spec);
    else Deno.symlinkSync(spec.symlink, full);
  }
}

const scriptsDir = fromFileUrl(new URL("../", import.meta.url));

/** Runs scripts/<script> with cwd=root; returns exit code and combined output. */
export function runScript(
  script: string,
  args: string[],
  root: string,
): { code: number; output: string } {
  const result = new Deno.Command(Deno.execPath(), {
    args: [
      "run",
      "--quiet",
      `--config=${join(scriptsDir, "..", "deno.json")}`,
      "--allow-read",
      "--allow-write",
      "--allow-run",
      "--allow-env",
      join(scriptsDir, script),
      ...args,
    ],
    cwd: root,
    stdout: "piped",
    stderr: "piped",
  }).outputSync();
  const decoder = new TextDecoder();
  return {
    code: result.code,
    output: decoder.decode(result.stdout) + decoder.decode(result.stderr),
  };
}

export const MANIFEST = {
  $schema: "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  name: "fixture-plugin",
  version: "1.2.3",
  description: "Fixture plugin.",
  author: { name: "Fixture Team" },
  homepage: "https://example.com/fixture",
  extensions: {
    "com.openai": {
      interface: {
        displayName: "Fixture",
        shortDescription: "Fixture plugin.",
        developerName: "Fixture Team",
        category: "Productivity",
        websiteURL: "https://example.com/fixture",
      },
    },
  },
};

export const MCP = {
  $schema: "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
  mcpServers: {
    local: {
      type: "stdio",
      command: "deno",
      args: ["run", "${PLUGIN_ROOT}/mcp/local/server.ts"],
      env: { CONFIG: "${PLUGIN_ROOT}/config.json" },
    },
    remote: {
      type: "streamable-http",
      url: "https://example.com/mcp",
      headers: { "X-Tenant": "t" },
    },
  },
};

const skill = (name: string) =>
  `---\nname: ${name}\ndescription: Fixture skill ${name}. Use when testing.\n---\n# ${name}\n`;
const mdAgent = (name: string) => `---\nname: ${name}\ndescription: Fixture agent.\n---\nBody.\n`;

/** A complete, valid plugin for every registered client. */
export function fixturePlugin(): Record<string, FileSpec> {
  return {
    "plugin.json": JSON.stringify(MANIFEST, null, 2) + "\n",
    "mcp.json": JSON.stringify(MCP, null, 2) + "\n",
    "mcp/local/server.ts": "// server\n",
    "config.json": "{}\n",
    "skills/alpha/SKILL.md": skill("alpha"),
    "com.anthropic.claude-code/agents/reviewer.md": mdAgent("reviewer"),
    ".codex/config.toml": '[plugins."fixture-plugin@fixture-plugin"]\nenabled = true\n',
    "openspec/specs/skill/spec.md": "# Skill Catalog\n",
    "openspec/specs/skill/alpha/spec.md": "# alpha\n",
    "openspec/specs/mcp/spec.md": "# MCP Catalog\n",
    "openspec/specs/mcp/local/spec.md": "# local\n",
    "openspec/specs/mcp/remote/spec.md": "# remote\n",
    "openspec/specs/agent/spec.md": "# Agent Catalog\n",
    "openspec/specs/agent/reviewer/spec.md": "# reviewer\n",
  };
}
