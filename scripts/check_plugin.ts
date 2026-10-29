#!/usr/bin/env -S deno run --allow-read --allow-run=git
// Checks the plugin package and its client wiring: schema conformance of the
// portable files, agreement between files that must name the same things,
// skill and agent layout, and the 1:1 relation between the OpenSpec catalogs
// and what the package ships. Every finding names the file and the fix.
//
//   check_plugin.ts                  run every rule
//   check_plugin.ts --footprint <id> print the files that belong to one client
import { join } from "@std/path";
import { parse as parseToml } from "@std/toml";
import { clientById, CLIENTS, ClientSpec, footprint } from "./lib/clients.ts";
import { exists, fail, Findings, isDirectory, listDir, readText } from "./lib/findings.ts";
import {
  agentHeader,
  frontmatter,
  loadManifest,
  loadMcp,
  McpFile,
  PluginManifest,
  PORTABLE_NAME_RE,
  SKILL_NAME_RE,
} from "./lib/plugin.ts";

const root = Deno.cwd();

if (Deno.args[0] === "--footprint") {
  const id = Deno.args[1];
  if (!id) fail("--footprint needs a client id: " + CLIENTS.map((c) => c.id).join(", "));
  try {
    for (const path of footprint(clientById(id), root)) {
      console.log(path);
    }
  } catch (error) {
    fail((error as Error).message);
  }
  Deno.exit(0);
}
if (Deno.args.length > 0) {
  fail(`unknown arguments ${Deno.args.join(" ")}; use --footprint <client> or nothing`);
}

const findings = new Findings();
const { manifest, errors: manifestErrors } = loadManifest(root);
for (const e of manifestErrors) {
  findings.add({
    file: "plugin.json",
    rule: "schema-plugin",
    problem: `${e}.`,
    fix: "match the Agent Plugins 1.0.0 plugin schema (scripts/schemas/).",
  });
}
const { mcp, errors: mcpErrors } = loadMcp(root);
for (const e of mcpErrors) {
  findings.add({
    file: "mcp.json",
    rule: "schema-mcp",
    problem: `${e}.`,
    fix: "match the Agent Plugins 1.0.0 mcp schema (scripts/schemas/).",
  });
}

checkName(manifest);
checkMcp(mcp);
const skills = checkSkills();
const agents = checkAgents();
checkCodex(manifest);
checkCatalogs(skills, mcp, agents);
Deno.exit(findings.report("check_plugin"));

function checkName(manifest: PluginManifest) {
  if (typeof manifest.name !== "string") return; // the schema finding covers it
  if (!PORTABLE_NAME_RE.test(manifest.name)) {
    findings.add({
      file: "plugin.json",
      rule: "name-portable",
      problem: `name "${manifest.name}" is not accepted by every supported client.`,
      fix:
        "use lowercase letters, digits, and single hyphens, starting and ending with a letter or digit.",
    });
  }
}

function checkMcp(mcp: McpFile | null) {
  if (mcp === null) return;
  for (const [name, server] of Object.entries(mcp.mcpServers)) {
    const at = `mcp.json#mcpServers.${name}`;
    if (server.type === "stdio") {
      if (server.command.includes("${PLUGIN_")) {
        findings.add({
          file: at,
          rule: "mcp-placeholder",
          problem: "command contains a placeholder.",
          fix: "placeholders expand only in args, env values, and cwd; move the path into args.",
        });
      }
      for (const arg of server.args ?? []) {
        const m = arg.match(/^\$\{PLUGIN_ROOT\}\/(.+)$/);
        if (m && !exists(join(root, m[1]))) {
          findings.add({
            file: at,
            rule: "mcp-server-file",
            problem: `args reference ${m[1]}, which does not exist.`,
            fix: "create the file or correct the path.",
          });
        }
      }
    } else {
      for (
        const [field, value] of [
          ["url", server.url],
          ...Object.entries(server.headers ?? {}).map(([k, v]) => [`headers.${k}`, v]),
        ]
      ) {
        if (value.includes("${PLUGIN_")) {
          findings.add({
            file: at,
            rule: "mcp-placeholder",
            problem: `${field} contains a placeholder.`,
            fix: "remote servers get no placeholder expansion; use a literal value.",
          });
        }
      }
    }
  }
}

/** Returns the skill directory names. */
function checkSkills(): string[] {
  const dir = join(root, "skills");
  if (!isDirectory(dir)) return [];
  const names: string[] = [];
  const projectSkills = isDirectory(join(root, ".agents/skills"))
    ? new Set(listDir(join(root, ".agents/skills")).filter((e) => e.isDirectory).map((e) => e.name))
    : new Set<string>();
  for (const entry of listDir(dir)) {
    if (!entry.isDirectory) continue;
    const file = `skills/${entry.name}/SKILL.md`;
    if (!exists(join(root, file))) {
      findings.add({
        file: `skills/${entry.name}/`,
        rule: "skill-shape",
        problem: "directory has no SKILL.md.",
        fix: "add SKILL.md with name and description frontmatter, or delete the directory.",
      });
      continue;
    }
    names.push(entry.name);
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
    checkSkillFrontmatter(file, entry.name, attrs);
    if (projectSkills.has(entry.name)) {
      findings.add({
        file,
        rule: "skill-name-collision",
        problem: `a project skill .agents/skills/${entry.name} has the same name.`,
        fix: "rename one of them; Codex and Antigravity load both directories.",
      });
    }
  }
  return names;
}

function checkSkillFrontmatter(file: string, dir: string, attrs: Record<string, unknown>) {
  const name = attrs.name;
  if (name !== dir) {
    findings.add({
      file,
      rule: "skill-name",
      problem: `frontmatter name ${JSON.stringify(name)} differs from the directory name.`,
      fix: `set name: ${dir}.`,
    });
  } else if (!SKILL_NAME_RE.test(dir) || dir.length > 64) {
    findings.add({
      file,
      rule: "skill-name",
      problem: `"${dir}" is not a valid agentskills.io name.`,
      fix:
        "use 1-64 lowercase letters, digits, and single hyphens; rename the directory and the frontmatter.",
    });
  }
  const description = attrs.description;
  if (
    typeof description !== "string" || description.trim().length === 0 || description.length > 1024
  ) {
    findings.add({
      file,
      rule: "skill-description",
      problem: "description is missing, empty, or over 1024 characters.",
      fix: "write a 1-1024 character description saying what the skill does and when to use it.",
    });
  }
}

interface AgentFile {
  client: ClientSpec;
  file: string;
  name: string;
  description?: string;
}

/** Returns agent names → files per client, after per-file checks. */
function checkAgents(): Map<string, AgentFile[]> {
  const byName = new Map<string, AgentFile[]>();
  for (const client of CLIENTS) {
    const spec = client.agents;
    if (!spec) {
      // The client's plugin system carries no agents (compatibility watch W2,
      // W9): an agents directory under its namespace would ship to nobody.
      const stray = `${client.namespaceDir}/agents`;
      if (isDirectory(join(root, stray))) {
        findings.add({
          file: stray,
          rule: "agent-unsupported",
          problem: `${client.id} plugins carry no agents, so nothing loads this directory.`,
          fix:
            "remove it; keep the role in the client's own workspace configuration, outside the plugin.",
        });
      }
      continue;
    }
    const dir = join(root, spec.dir);
    if (!isDirectory(dir)) continue;
    for (const entry of listDir(dir)) {
      if (!entry.isFile) continue;
      const file = `${spec.dir}/${entry.name}`;
      if (!entry.name.endsWith(spec.ext)) {
        findings.add({
          file,
          rule: "agent-extension",
          problem: `${client.id} agents are ${spec.ext} files.`,
          fix: `rename the file or move it to the right client directory.`,
        });
        continue;
      }
      const stem = entry.name.slice(0, -spec.ext.length);
      const header = agentHeader(join(root, file));
      if (header === null || header.name === undefined) {
        findings.add({
          file,
          rule: "agent-name",
          problem: "no name field.",
          fix: `declare name = "${stem}" (TOML) or name: ${stem} (frontmatter).`,
        });
        continue;
      }
      if (header.name !== stem) {
        findings.add({
          file,
          rule: "agent-name",
          problem: `name "${header.name}" differs from the file name.`,
          fix: `rename the file to ${header.name}${spec.ext} or set name to ${stem}.`,
        });
      }
      if (!header.description) {
        findings.add({
          file,
          rule: "agent-description",
          problem: "no description.",
          fix: "add a one-sentence description; clients use it to decide when to delegate.",
        });
      }
      const list = byName.get(header.name) ?? [];
      list.push({ client, file, name: header.name, description: header.description });
      byName.set(header.name, list);
    }
  }
  for (const [name, files] of byName) {
    for (const client of CLIENTS) {
      const spec = client.agents;
      if (!spec) continue;
      if (!files.some((f) => f.client === client)) {
        findings.add({
          file: `${spec.dir}/${name}${spec.ext}`,
          rule: "agent-parity",
          problem: `agent "${name}" exists for ${
            files.map((f) => f.client.id).join(", ")
          } but not for ${client.id}.`,
          fix: `add the ${client.id} version, or remove the agent from every client.`,
        });
      }
    }
    const descriptions = new Set(files.map((f) => f.description));
    if (descriptions.size > 1) {
      findings.add({
        file: files[0].file,
        rule: "agent-description-parity",
        problem: `agent "${name}" has different descriptions across clients.`,
        fix: "use the same description text in every client version.",
      });
    }
  }
  return byName;
}

function checkCodex(manifest: PluginManifest) {
  // Every extensions block must belong to a supported client (Agent Plugins §8
  // namespaces); a block for a client this project dropped is dead data.
  const namespaces = new Set(CLIENTS.map((c) => c.namespaceDir));
  for (const ns of Object.keys(manifest.extensions ?? {})) {
    if (namespaces.has(ns)) continue;
    findings.add({
      file: "plugin.json",
      rule: "extension-namespace",
      problem: `extensions.${ns} belongs to no supported client.`,
      fix: "remove the block, or register the client in scripts/lib/clients.ts.",
    });
  }
  const client = CLIENTS.find((c) => c.id === "codex");
  if (!client) return;
  if (manifest.extensions?.["com.openai"] === undefined) {
    findings.add({
      file: "plugin.json",
      rule: "codex-extension",
      problem: "Codex is a supported client but extensions.com.openai is missing.",
      fix:
        "add the block with interface.{displayName,shortDescription,developerName,category}, or drop Codex from scripts/lib/clients.ts.",
    });
    return;
  }
  const iface =
    (manifest.extensions?.["com.openai"] as { interface?: Record<string, unknown> }).interface ??
      {};
  const pairs: [string, unknown, string, unknown][] = [
    ["interface.shortDescription", iface.shortDescription, "description", manifest.description],
    ["interface.developerName", iface.developerName, "author.name", manifest.author?.name],
    ["interface.websiteURL", iface.websiteURL, "homepage", manifest.homepage],
  ];
  for (const [field, value, source, expected] of pairs) {
    if (value !== undefined && expected !== undefined && value !== expected) {
      findings.add({
        file: "plugin.json",
        rule: "codex-interface",
        problem: `extensions.com.openai.${field} differs from ${source}.`,
        fix: `set it to the same value as ${source}, which is the source of truth.`,
      });
    }
  }
  const configPath = ".codex/config.toml";
  if (!exists(join(root, configPath))) {
    findings.add({
      file: configPath,
      rule: "codex-wiring",
      problem: "file is missing.",
      fix: "create it with the [plugins] table (see com.openai/README.md).",
    });
    return;
  }
  let config: Record<string, unknown>;
  try {
    config = parseToml(readText(join(root, configPath))) as Record<string, unknown>;
  } catch (error) {
    return fail(`${configPath}: not valid TOML: ${(error as Error).message}`);
  }
  const key = `${manifest.name}@${manifest.name}`;
  const plugins = (config.plugins ?? {}) as Record<string, { enabled?: boolean }>;
  if (plugins[key]?.enabled !== true) {
    findings.add({
      file: configPath,
      rule: "codex-plugin-enabled",
      problem: `no [plugins."${key}"] enabled = true.`,
      fix: "add that table so the local marketplace plugin is enabled for this project.",
    });
  }
}

function checkCatalogs(skills: string[], _mcp: McpFile | null, agents: Map<string, AgentFile[]>) {
  const specs = join(root, "openspec/specs");
  if (!isDirectory(specs)) {
    console.log("note: openspec/specs is absent; catalog checks skipped");
    return;
  }
  const catalogs: [string, string[], string][] = [
    ["skill", skills, "skills/<name>/"],
    ["agent", [...agents.keys()], "<client>/agents/<name>"],
  ];
  for (const [catalog, implemented, where] of catalogs) {
    const dir = join(specs, catalog);
    const specNames = isDirectory(dir)
      ? listDir(dir).filter((e) => e.isDirectory && exists(join(dir, e.name, "spec.md"))).map((e) =>
        e.name
      )
      : [];
    if ((implemented.length > 0 || specNames.length > 0) && !exists(join(dir, "spec.md"))) {
      findings.add({
        file: `openspec/specs/${catalog}/spec.md`,
        rule: "catalog-rules",
        problem: `the ${catalog} catalog has entries but no shared rules spec.`,
        fix: "write the catalog-level spec.md with the rules every entry follows.",
      });
    }
    for (const name of implemented) {
      if (!specNames.includes(name)) {
        findings.add({
          file: `openspec/specs/${catalog}/${name}/spec.md`,
          rule: "catalog-missing-spec",
          problem: `${where.replace("<name>", name)} is implemented but has no spec.`,
          fix: "add the spec through an OpenSpec change, or remove the implementation.",
        });
      }
    }
    for (const name of specNames) {
      if (!implemented.includes(name)) {
        findings.add({
          file: `openspec/specs/${catalog}/${name}/spec.md`,
          rule: "catalog-orphan-spec",
          problem: `spec exists but ${where.replace("<name>", name)} is not implemented.`,
          fix: "implement it, or archive a change that removes the spec.",
        });
      }
    }
  }
}
