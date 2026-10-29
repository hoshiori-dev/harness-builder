---
name: plugin-development
description: >-
  Adds, changes, or removes a skill, MCP server, or agent shipped by this
  plugin, end to end: OpenSpec change, implementation per catalog, client
  file generation, checks, and per-client verification. Use when the user
  asks to add or modify what the plugin ships, when a catalog check fails,
  or when a client stops loading a component. Not for changing which clients
  or catalogs the template supports (template-adjust) or for GitHub issue
  and PR mechanics (github-project-workflow).
---

# Plugin development

Every shipped entry lives in exactly one catalog and is described by exactly
one spec; `just validate` enforces the pairing. Work spec first.

## Workflow

1. **Spec.** Read `.agents/knowledge/spec-workflow.md`. Run the
   `openspec-propose` skill with the capability path
   `<catalog>/<name>` (for example `skill/release-notes`); for a new catalog
   entry the delta spec creates `openspec/specs/<catalog>/<name>/spec.md`.
   State in the proposal which clients the entry ships to. Stop until the
   pull request carries `spec: approved`.
2. **Implement by catalog** (read `.agents/knowledge/client-matrix.md` first):
   - *skill*: `skills/<name>/SKILL.md` with `name: <name>` and a 1-1024
     character description; `references/`, `scripts/`, `assets/` as needed.
     Keep instructions client-neutral; client-specific steps go in a
     reference organised by client.
   - *mcp*: add the server to `mcp.json` (spec `$schema`, `type`,
     placeholders only in `args`/`env`/`cwd`); bundled code goes in
     `mcp/<name>/` with a `*_test.ts` that starts the server from the
     `mcp.json` declaration.
   - *agent*: one file per supported client whose plugin system carries
     agents, same `name` and identical `description`; today that is
     `com.anthropic.claude-code/agents/<name>.md` only. Codex and Antigravity
     get no agent files: their plugins cannot carry them
     (`.agents/knowledge/compatibility-watch.md` W9, W2) and `just validate`
     rejects an `agents/` directory under their namespaces. Read-only tools
     unless the spec justifies writes.
3. **Generate.** `just gen` after any change to `plugin.json`, `mcp.json`, or
   an agents directory; commit the generated files with the change.
4. **Check.** `just check`. Fix findings at their source; never edit a
   generated file or relax a check.
5. **Verify in clients.** `just clients-validate`, then exercise the entry by
   hand in at least one client using the commands in `client-matrix.md`
   (`claude --plugin-dir .`, the Codex marketplace, `agy plugin install .`
   then `agy plugin uninstall <name>`). Record anything that contradicts the
   matrix.
6. **Finish.** `openspec-apply-change` tracks tasks; archive per
   `spec-workflow.md`; the PR follows `github-project-workflow`.

## Removing an entry

Delete the implementation and the spec in one change (a delta spec with
`## REMOVED Requirements`), run `just gen` so pointer lists shrink, and
`just check`.

## Gotchas

- `claude plugin validate --strict` fails on any unknown top-level key in
  `.claude-plugin/plugin.json`; that file is generated, so fix `gen.ts`, not
  the output.
- Antigravity has no `${PLUGIN_ROOT}`; a stdio server must work with paths
  relative to the plugin root. `just gen` fails loudly on `cwd`, `sse`, and
  `${PLUGIN_DATA}` for Antigravity rather than dropping them.
- A skill name must not also exist under `.agents/skills/`; Codex and
  Antigravity load both directories here.
