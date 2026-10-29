// The client registry: the one place that declares which coding-agent clients
// this plugin supports, where each keeps its files, and what `gen.ts`
// produces for it. Supporting a client is a project decision recorded here,
// never inferred from the tree. To drop a client: run
// `just client-footprint <id>`, delete those files, then remove the entry and
// its id from `ClientId`; the type checker then points at every branch in
// `gen.ts` and `check_plugin.ts` that has to go.
import { join } from "@std/path";
import { exists, isDirectory } from "./findings.ts";

export type ClientId = "codex" | "claude-code" | "antigravity";

export interface ClientSpec {
  id: ClientId;
  /**
   * Reverse-domain directory for the client's hand-written files (Agent
   * Plugins §8). It exists only while the client has such files; today only
   * Claude Code does.
   */
  namespaceDir: string;
  /**
   * Where this client's hand-written agent files live and their extension.
   * Absent when the client's plugin system carries no agents: the plugin then
   * ships none to it and `check_plugin.ts` rejects an agents directory under
   * its namespace (compatibility watch W2, W9).
   */
  agents?: { dir: string; ext: ".md" | ".toml" };
  /** Hand-written wiring files outside the namespace directory. */
  wiringFiles: string[];
  /** Files `gen.ts` writes for this client. */
  generatedFiles: string[];
  /** Symlinks inside the namespace directory, as `link -> target`. */
  links: { path: string; target: string }[];
}

export const CLIENTS: readonly ClientSpec[] = [
  {
    id: "codex",
    namespaceDir: "com.openai",
    wiringFiles: [".codex/config.toml"],
    generatedFiles: [".agents/plugins/marketplace.json"],
    links: [],
  },
  {
    id: "claude-code",
    namespaceDir: "com.anthropic.claude-code",
    agents: { dir: "com.anthropic.claude-code/agents", ext: ".md" },
    wiringFiles: [],
    generatedFiles: [
      ".claude-plugin/plugin.json",
      ".claude-plugin/marketplace.json",
      "com.anthropic.claude-code/mcp.json",
    ],
    links: [],
  },
  {
    id: "antigravity",
    namespaceDir: "com.google.antigravity",
    wiringFiles: [],
    // Transitional: Antigravity reads mcp.json only behind its Agent Plugins
    // flag; until then it reads mcp_config.json at the plugin root (watch W1).
    generatedFiles: ["mcp_config.json"],
    links: [],
  },
];

export function clientById(id: string): ClientSpec {
  const client = CLIENTS.find((c) => c.id === id);
  if (!client) {
    throw new Error(`unknown client "${id}"; known: ${CLIENTS.map((c) => c.id).join(", ")}`);
  }
  return client;
}

/** Every existing path that belongs to a client: what dropping the client deletes. */
export function footprint(client: ClientSpec, root: string): string[] {
  const paths = new Set<string>([
    client.namespaceDir,
    ...client.wiringFiles,
    ...client.generatedFiles,
    ...client.links.map((l) => l.path),
  ]);
  return [...paths].filter((p) => isDirectory(join(root, p)) || exists(join(root, p))).sort();
}
