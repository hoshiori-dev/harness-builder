#!/usr/bin/env -S deno run --allow-read --allow-write --allow-run=git
// Generates the client-specific files that can be derived from the portable
// plugin files (plugin.json, mcp.json, and the agents directory of a client
// whose plugin system carries agents):
//
//   Claude Code   .claude-plugin/plugin.json, com.anthropic.claude-code/mcp.json
//   Antigravity   mcp_config.json (transitional, until its Agent Plugins flag is on)
//   Codex         .agents/plugins/marketplace.json
//
// The clients are those registered in lib/clients.ts.
//
//   gen.ts            write files that differ from the expected content
//   gen.ts --check    write nothing; report STALE, MISSING, and ORPHAN files
//   gen.ts --list     print the paths this run would generate
import { dirname, join } from "@std/path";
import { CLIENTS, ClientSpec } from "./lib/clients.ts";
import { exists, fail, Findings, listDir, readText } from "./lib/findings.ts";
import {
  HttpServer,
  loadManifest,
  loadMcp,
  McpFile,
  McpServer,
  pick,
  PluginManifest,
  stableJson,
  StdioServer,
} from "./lib/plugin.ts";

const METADATA_KEYS = [
  "name",
  "version",
  "description",
  "author",
  "homepage",
  "repository",
  "license",
  "keywords",
] as const;

const root = Deno.cwd();
const flags = new Set(Deno.args);
for (const flag of flags) {
  if (flag !== "--check" && flag !== "--list") fail(`unknown flag ${flag}; use --check or --list`);
}

const { manifest, errors: manifestErrors } = loadManifest(root);
if (manifestErrors.length > 0) {
  fail(`plugin.json violates the Agent Plugins schema:\n  ${manifestErrors.join("\n  ")}`);
}
const { mcp, errors: mcpErrors } = loadMcp(root);
if (mcpErrors.length > 0) {
  fail(`mcp.json violates the Agent Plugins schema:\n  ${mcpErrors.join("\n  ")}`);
}

const expected = new Map<string, string>();
for (const client of CLIENTS) {
  for (const [path, content] of generate(client, manifest, mcp)) expected.set(path, content);
}

if (flags.has("--list")) {
  for (const path of [...expected.keys()].sort()) console.log(path);
  Deno.exit(0);
}

const findings = new Findings();
for (const [path, content] of [...expected].sort()) {
  const full = join(root, path);
  const current = exists(full) ? readText(full) : null;
  if (current === content) continue;
  if (flags.has("--check")) {
    findings.add({
      file: path,
      rule: current === null ? "gen-missing" : "gen-stale",
      problem: current === null
        ? "generated file is missing."
        : "generated file differs from its sources.",
      fix: "run `just gen` and commit the result.",
    });
    continue;
  }
  Deno.mkdirSync(dirname(full), { recursive: true });
  Deno.writeTextFileSync(full, content);
  console.log(`wrote ${path}`);
}

// Generated files whose source (mcp.json) is gone. A dropped client's files
// are not known here any more: `just client-footprint <id>` lists them first.
for (const client of CLIENTS) {
  for (const path of client.generatedFiles) {
    if (expected.has(path) || !exists(join(root, path))) continue;
    findings.add({
      file: path,
      rule: "gen-orphan",
      problem: "generated file exists but its source mcp.json no longer exists.",
      fix: `delete ${path}, or restore mcp.json.`,
    });
  }
}
Deno.exit(findings.report(flags.has("--check") ? "gen --check" : "gen"));

function generate(
  client: ClientSpec,
  manifest: PluginManifest,
  mcp: McpFile | null,
): [string, string][] {
  switch (client.id) {
    case "claude-code":
      return generateClaudeCode(client, manifest, mcp);
    case "antigravity":
      return generateAntigravity(client, manifest, mcp);
    case "codex":
      return generateCodex(manifest);
  }
}

function agentFiles(client: ClientSpec): string[] {
  const spec = client.agents;
  if (!spec) return [];
  const dir = join(root, spec.dir);
  if (!exists(dir)) return [];
  return listDir(dir)
    .filter((e) => e.isFile && e.name.endsWith(spec.ext))
    .map((e) => `${spec.dir}/${e.name}`);
}

function generateClaudeCode(client: ClientSpec, manifest: PluginManifest, mcp: McpFile | null) {
  const out: [string, string][] = [];
  // Only fields Claude Code knows: an unknown top-level key fails `claude plugin validate --strict`.
  const claude: Record<string, unknown> = pick(manifest, METADATA_KEYS);
  const agents = agentFiles(client).map((p) => `./${p}`);
  if (agents.length > 0) claude.agents = agents;
  if (mcp !== null) {
    const mcpPath = "com.anthropic.claude-code/mcp.json";
    claude.mcpServers = `./${mcpPath}`;
    const servers: Record<string, unknown> = {};
    for (const [name, server] of Object.entries(mcp.mcpServers)) {
      servers[name] = claudeServer(name, server);
    }
    out.push([mcpPath, stableJson({ mcpServers: servers })]);
  }
  out.push([".claude-plugin/plugin.json", stableJson(claude)]);
  // A marketplace at the repository root lets Claude Code install the plugin
  // straight from GitHub: /plugin marketplace add <owner>/<repo>.
  const marketplace: Record<string, unknown> = { name: manifest.name };
  if (manifest.author?.name !== undefined) marketplace.owner = { name: manifest.author.name };
  if (manifest.description !== undefined) marketplace.description = manifest.description;
  marketplace.plugins = [{ name: manifest.name, source: "./", description: manifest.description }];
  out.push([".claude-plugin/marketplace.json", stableJson(marketplace)]);
  return out;
}

function claudeServer(name: string, server: McpServer): Record<string, unknown> {
  const map = (s: string) =>
    s.replaceAll("${PLUGIN_ROOT}", "${CLAUDE_PLUGIN_ROOT}").replaceAll(
      "${PLUGIN_DATA}",
      "${CLAUDE_PLUGIN_DATA}",
    );
  if (server.type === "stdio") {
    if (server.cwd !== undefined) {
      unsupported(
        name,
        "cwd",
        "claude-code",
        "remove cwd, or extend claudeServer() after verifying the client accepts it",
      );
    }
    const out: Record<string, unknown> = { type: "stdio", command: map(server.command) };
    if (server.args) out.args = server.args.map(map);
    if (server.env) out.env = mapValues(server.env, map);
    return out;
  }
  return httpServer(server, server.type === "streamable-http" ? "http" : "sse");
}

function generateAntigravity(_client: ClientSpec, _manifest: PluginManifest, mcp: McpFile | null) {
  // Antigravity reads the root plugin.json natively, so no manifest is generated.
  // mcp_config.json at the root is transitional (watch W1): the client reads it
  // until its Agent Plugins flag makes it read mcp.json instead.
  const out: [string, string][] = [];
  if (mcp !== null) {
    const servers: Record<string, unknown> = {};
    for (const [name, server] of Object.entries(mcp.mcpServers)) {
      servers[name] = antigravityServer(name, server);
    }
    out.push(["mcp_config.json", stableJson({ mcpServers: servers })]);
  }
  return out;
}

function antigravityServer(name: string, server: McpServer): Record<string, unknown> {
  // Antigravity has no plugin-root placeholder; paths become relative to the
  // plugin root, which is where it starts stdio servers.
  const map = (s: string) => {
    if (s.includes("${PLUGIN_DATA}")) {
      unsupported(
        name,
        "${PLUGIN_DATA}",
        "antigravity",
        "Antigravity has no per-plugin data directory; drop the placeholder",
      );
    }
    return s.replaceAll("${PLUGIN_ROOT}/", "").replaceAll("${PLUGIN_ROOT}", ".");
  };
  if (server.type === "stdio") {
    if (server.cwd !== undefined) {
      unsupported(name, "cwd", "antigravity", "mcp_config.json has no cwd field; remove cwd");
    }
    const out: Record<string, unknown> = { command: map(server.command) };
    if (server.args) out.args = server.args.map(map);
    if (server.env) out.env = mapValues(server.env, map);
    return out;
  }
  if (server.type === "sse") {
    unsupported(
      name,
      'type "sse"',
      "antigravity",
      "Antigravity supports stdio and streamable-http only",
    );
  }
  const { type: _type, ...rest } = httpServer(server, "http");
  return rest;
}

function httpServer(server: HttpServer, type: string): Record<string, unknown> {
  const out: Record<string, unknown> = { type, url: server.url };
  if (server.headers) out.headers = server.headers;
  return out;
}

function generateCodex(manifest: PluginManifest): [string, string][] {
  const iface =
    (manifest.extensions?.["com.openai"] as { interface?: { category?: string } } | undefined)
      ?.interface;
  if (iface?.category === undefined) {
    fail(
      'plugin.json: extensions.com.openai.interface.category is missing; the Codex marketplace entry requires a category. Fix: add it (for example "Productivity").',
    );
  }
  const marketplace = {
    name: manifest.name,
    plugins: [
      {
        name: manifest.name,
        source: { source: "local", path: "./" },
        policy: { installation: "AVAILABLE", authentication: "ON_INSTALL" },
        category: iface.category,
      },
    ],
  };
  return [[".agents/plugins/marketplace.json", stableJson(marketplace)]];
}

function mapValues(
  record: Record<string, string>,
  fn: (s: string) => string,
): Record<string, string> {
  return Object.fromEntries(Object.entries(record).map(([k, v]) => [k, fn(v)]));
}

function unsupported(server: string, what: string, client: string, fix: string): never {
  return fail(
    `mcp.json: mcpServers.${server} uses ${what}, which has no ${client} equivalent. Fix: ${fix}.`,
  );
}

// Keep the type imports referenced for readers; they document the shapes handled above.
export type { StdioServer };
