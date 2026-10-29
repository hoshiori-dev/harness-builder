# Compatibility Watch

Read at every reclamation run, after any client or OpenSpec upgrade, when a
client starts behaving differently from `client-matrix.md`, and before
removing a workaround. This file is the one list of known limitations, the
workarounds built for them, and the condition under which each workaround
goes away. `client-matrix.md` describes how things work today and points
here for why.

## Versions these facts were verified against

| Component | Version | Verified | Re-check with |
|---|---|---|---|
| Agent Plugins specification | 1.0.0 (1.1.0 is a draft) | 2026-10-27 | `scripts/lib/plugin.ts` `SPEC_VERSION`; `just schemas-update` then `git diff scripts/schemas/` |
| agentskills.io SKILL.md format | current page | 2026-10-27 | `SKILL_NAME_RE` and the 1024-character limit in `scripts/lib/plugin.ts` |
| Claude Code | 2.1.311 | 2026-10-27 | `claude --version` |
| Codex CLI | 0.164.0 | 2026-10-27 | `codex --version` |
| Antigravity CLI (`agy`) | 1.4.7 (build 2026-10-24) | 2026-10-27 | `agy changelog` (first line) |
| OpenSpec | 1.15.0 | 2026-10-27 | `openspec --version` |

`just versions` prints the installed versions for the log.

## Watch list

Each row is a limitation the harness carries today, with the workaround built
for it or, where the capability is simply not offered, the check that keeps
it from creeping back. When the resolving condition is true, apply the
disposition in one change, update the matrix, and delete the row.

| ID | Limitation | Workaround in this repository | Re-check how | Resolved when | Then |
|---|---|---|---|---|---|
| W1 | Antigravity reads `mcp.json` only behind the `enable-agent-plugins-spec` flag (off by default). The flag is served by Google's feature-flag service, not by a user setting: no CLI option, `config.json` key, or environment variable turns it on (checked 2026-10-27 against the CLI help, the user config, the docs, and the changelog) | generated root `mcp_config.json` (`scripts/gen.ts`, `generateAntigravity`), a client file at the plugin root that the spec would rather see under `com.google.antigravity/` | `agy plugin validate .` no longer notes the flag, or the Antigravity changelog announces Agent Plugins support | the flag is on by default in the release every team member runs | delete the `mcp_config.json` branch in `scripts/gen.ts` and the file, drop `mcp_config.json` from `.gitattributes` and `scripts/lib/clients.ts`; keep an overlay at `com.google.antigravity/mcp_config.json` only if a server needs fields `mcp.json` cannot express |
| W2 | Antigravity loads plugin agents only from the plugin root `agents/`, never from `com.google.antigravity/agents/`, so this plugin ships no agents to Antigravity | none: the `antigravity` entry in `scripts/lib/clients.ts` has no `agents`, and the `agent-unsupported` rule in `scripts/check_plugin.ts` rejects a `com.google.antigravity/agents/` directory (a workspace link under `.agents/agents/` was tried on 2026-10-27 and removed: not plugin content) | `agy plugin validate .` on a scratch copy with `com.google.antigravity/agents/<n>.md` counts the agent; Antigravity plugin docs | the namespace agents are counted and load from an installed plugin | add `agents: { dir: "com.google.antigravity/agents", ext: ".md" }` to the registry entry, write the Antigravity version of each agent, mark it shipped in `openspec/specs/agent/spec.md` and `client-matrix.md` |
| W3 | Antigravity `mcp_config.json` has no plugin-root placeholder | generator rewrites `${PLUGIN_ROOT}/x` to the root-relative `x`; Antigravity starts stdio servers with the plugin root as working directory (verified) | Antigravity MCP docs for a `${...}` variable | a placeholder exists, or W1 lifts (then `mcp.json` carries `${PLUGIN_ROOT}` itself) | map or delete with W1 |
| W4 | Antigravity has no workspace registration that survives installation: `.agents/plugins.json` did not load in the CLI, and a `.agents/plugins/<name>` link to the repository root makes `agy plugin install` recurse into itself | local testing installs the plugin globally with `agy plugin install .` and removes it with `agy plugin uninstall` | create `.agents/plugins.json` in a scratch copy and run the `agy --print` smoke check | a documented workspace registration loads the root as a plugin without being copied on install | add it to `client-matrix.md` and the `plugin-development` skill |
| W6 | Claude Code reads project skills from `.claude/skills/` only | one symlink per project skill, enforced by the `claude-skill-link` rule in `scripts/check_harness.ts` | Claude Code skills docs for `.agents/skills` | `.agents/skills/` is a documented project location | delete the symlinks and the rule, update `AGENTS.md`'s project map |
| W7 | Claude Code has no Agent Plugins support and its MCP format differs | generated `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `com.anthropic.claude-code/mcp.json` | Claude Code plugin docs mention `agent-plugins.org`, or `claude plugin validate` accepts a root `plugin.json` | Claude Code loads the root manifest and `mcp.json` | stop generating the pointer manifest and MCP file; keep `agents/` under the namespace |
| W8 | `claude plugin validate --strict` fails on this repository because the root `CLAUDE.md` is flagged (it is the development entrypoint, not plugin context) | `just clients-validate` runs the Claude validator non-strict | run it with `--strict` | the validator exempts a repository that is both plugin and workspace, or Claude Code reads `AGENTS.md` natively (then delete `CLAUDE.md`) | switch the recipe back to `--strict` |
| W9 | Codex plugins have no agents component | none: the `codex` entry in `scripts/lib/clients.ts` has no `agents`, and the `agent-unsupported` rule in `scripts/check_plugin.ts` rejects a `com.openai/agents/` directory (workspace `[agents.<n>]` tables in `.codex/config.toml` were tried and removed on 2026-10-27: not plugin content) | Codex plugin docs for an `agents` component | plugins can bundle agent roles | add `agents` to the registry entry at the component location Codex documents, write the TOML version of each agent, update `openspec/specs/agent/spec.md` and `client-matrix.md` |
| W10 | `com.anthropic.claude-code` is a self-chosen namespace | directory name and `scripts/lib/clients.ts` entry | Claude Code docs or the Agent Plugins compatible-clients list name an official namespace | an official value exists | rename the directory and the registry entry, regenerate |
| W11 | Agent Plugins 1.1.0 is a draft; agents, hooks, and commands are outside the spec | per-client agent files under namespace directories; vendored 1.0.0 schemas | spec repository releases; `just schemas-update` | a release adds a component this plugin ships, or publishes 1.1.0 | bump `SPEC_VERSION` and the `$schema` values, run `just schemas-update`, move the component to its portable location, archive an OpenSpec change describing the new layout |
| W12 | OpenSpec writes Antigravity workflows (deprecated by Antigravity on 2026-10-19) and rewrites skills for every detected tool on `update` | `openspec init --tools agents --force` only; `openspec-target` rule in `scripts/check_harness.ts` | release notes of OpenSpec | `openspec update` respects a single configured tool and emits no workflows | allow `openspec update` in `spec-workflow.md` and `template-adjust` |
| W13 | `betterleaks git --pre-commit --staged` fails in this dev container (git reports no repository to the subprocess) | the pre-commit hook scans staged files with `betterleaks dir` | run the git mode from the container | the git mode works | optional: switch the hook back; the file scan is also correct |

## Adding a row

Add a row whenever a check, generator branch, or document exists only because
a client or specification cannot do something yet, or whenever the template
deliberately withholds a capability from a client for that reason. Name the file that carries
the workaround so the disposition can be executed without rediscovery.
