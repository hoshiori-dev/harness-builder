// Loading and validating the portable plugin files (Agent Plugins 1.0.0) and
// the client-specific agent files, plus the small helpers every script shares.
import { Ajv2020 } from "ajv/2020";
import type { ErrorObject } from "ajv/2020";
import { extractYaml, test as hasFrontmatter } from "@std/front-matter";
import { parse as parseToml } from "@std/toml";
import { fromFileUrl, join } from "@std/path";
import { exists, fail, readJson, readText } from "./findings.ts";

export const SPEC_VERSION = "1.0.0";
/** Vendored schemas, resolved from this file so checks work from any working directory. */
export const SCHEMA_DIR = fromFileUrl(
  new URL(`../schemas/agent-plugins/${SPEC_VERSION}/`, import.meta.url),
);
export const PLUGIN_SCHEMA_URL =
  `https://agent-plugins.org/schemas/${SPEC_VERSION}/plugin.schema.json`;
export const MCP_SCHEMA_URL = `https://agent-plugins.org/schemas/${SPEC_VERSION}/mcp.schema.json`;
export const ANTIGRAVITY_SCHEMA_URL = "https://antigravity.google/schemas/v1/plugin.json";

/** Intersection of the name rules of the spec, Claude Code, Codex, and Antigravity. */
export const PORTABLE_NAME_RE = /^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$/;
/** agentskills.io: 1-64 chars, lowercase alphanumerics and single hyphens. */
export const SKILL_NAME_RE = /^(?!.*--)[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$/;

export interface PluginManifest {
  $schema: string;
  name: string;
  version?: string;
  description?: string;
  author?: { name?: string; email?: string; url?: string };
  homepage?: string;
  repository?: string;
  license?: string;
  keywords?: string[];
  extensions?: Record<string, Record<string, unknown>>;
}

export interface StdioServer {
  type: "stdio";
  command: string;
  args?: string[];
  env?: Record<string, string>;
  cwd?: string;
}

export interface HttpServer {
  type: "streamable-http" | "sse";
  url: string;
  headers?: Record<string, string>;
}

export type McpServer = StdioServer | HttpServer;

export interface McpFile {
  $schema: string;
  mcpServers: Record<string, McpServer>;
}

export const PLACEHOLDERS = ["${PLUGIN_ROOT}", "${PLUGIN_DATA}"] as const;

function validator(kind: "plugin" | "mcp") {
  const ajv = new Ajv2020({ strict: false, allErrors: true });
  const schema = readJson(join(SCHEMA_DIR, `${kind}.schema.json`));
  return ajv.compile(schema as object);
}

/** Schema violations as `path: message` strings, empty when valid. */
export function schemaErrors(kind: "plugin" | "mcp", data: unknown): string[] {
  const validate = validator(kind);
  if (validate(data)) return [];
  return (validate.errors ?? []).map((e: ErrorObject) => {
    const where = e.instancePath === "" ? "(root)" : e.instancePath;
    const extra = e.keyword === "additionalProperties"
      ? ` (${(e.params as { additionalProperty: string }).additionalProperty})`
      : "";
    return `${where} ${e.message ?? e.keyword}${extra}`;
  });
}

export function loadManifest(root: string): { manifest: PluginManifest; errors: string[] } {
  const path = join(root, "plugin.json");
  if (!exists(path)) fail(`${path} not found: the plugin root must hold plugin.json`);
  const data = readJson(path);
  return { manifest: data as PluginManifest, errors: schemaErrors("plugin", data) };
}

/** `mcp` is null when the plugin ships no mcp.json, which the spec allows. */
export function loadMcp(root: string): { mcp: McpFile | null; errors: string[] } {
  const path = join(root, "mcp.json");
  if (!exists(path)) return { mcp: null, errors: [] };
  const data = readJson(path);
  return { mcp: data as McpFile, errors: schemaErrors("mcp", data) };
}

/** Frontmatter attributes of a Markdown file, or null when it has none. */
export function frontmatter(path: string): Record<string, unknown> | null {
  const text = readText(path);
  if (!hasFrontmatter(text, ["yaml"])) return null;
  try {
    return extractYaml<Record<string, unknown>>(text).attrs;
  } catch (error) {
    return fail(`${path}: frontmatter is not valid YAML: ${(error as Error).message}`);
  }
}

/** `name` and `description` of an agent file in either client format. */
export function agentHeader(path: string): { name?: string; description?: string } | null {
  if (path.endsWith(".toml")) {
    try {
      const table = parseToml(readText(path)) as Record<string, unknown>;
      return { name: str(table.name), description: str(table.description) };
    } catch (error) {
      return fail(`${path}: not valid TOML: ${(error as Error).message}`);
    }
  }
  const attrs = frontmatter(path);
  if (attrs === null) return null;
  return { name: str(attrs.name), description: str(attrs.description) };
}

function str(value: unknown): string | undefined {
  return typeof value === "string" ? value : undefined;
}

/** Deterministic JSON: two-space indent, trailing newline, keys in insertion order. */
export function stableJson(value: unknown): string {
  return JSON.stringify(value, null, 2) + "\n";
}

/** Copies `source` into a new object with only the listed keys, in that order. */
export function pick<T extends object>(source: T, keys: readonly (keyof T)[]): Partial<T> {
  const out: Partial<T> = {};
  for (const key of keys) {
    if (source[key] !== undefined) out[key] = source[key];
  }
  return out;
}
