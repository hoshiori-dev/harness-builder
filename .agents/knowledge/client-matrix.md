# Client Matrix

Read when adding or changing a skill, MCP server, or agent, when a client does
not load something, or before touching a `com.*` directory or a wiring file.
Facts below were verified on 2026-10-27 with Claude Code 2.1.311, Codex CLI
0.164.0, and Antigravity CLI (`agy` 1.4.7, build 2026-10-24); re-verify when a client
updates and record the date here.

## How each client loads each component

| Component | Codex | Claude Code | Antigravity |
|---|---|---|---|
| Manifest | root `plugin.json` (Agent Plugins 1.0.0) plus `extensions.com.openai` | `.claude-plugin/plugin.json`, generated: metadata mirror plus `agents` and `mcpServers` pointers | root `plugin.json`, read natively (the Agent Plugins `$schema` is recognised) |
| Skills | root `skills/` (spec) | root `skills/` (default scan) | root `skills/` (native location matches the spec) |
| MCP | root `mcp.json` (spec) | `com.anthropic.claude-code/mcp.json`, generated (`streamable-http`→`http`, `${PLUGIN_ROOT}`→`${CLAUDE_PLUGIN_ROOT}`) | root `mcp_config.json`, generated and transitional (no `type`, paths relative to the plugin root); read until the `enable-agent-plugins-spec` flag makes Antigravity read `mcp.json` |
| Agents | none: Codex plugins carry no agents (W9); `just validate` rejects a `com.openai/agents/` directory | `com.anthropic.claude-code/agents/<n>.md`, listed by the generated manifest (shipped) | none: Antigravity reads plugin agents from the plugin root only, which the spec reserves for portable files (W2); `just validate` rejects a `com.google.antigravity/agents/` directory |
| Local load | `codex plugin marketplace add .` then `codex plugin add harness-builder@harness-builder`; marketplace file `.agents/plugins/marketplace.json` (generated) | `claude --plugin-dir .`; GitHub install through the generated `.claude-plugin/marketplace.json` (`/plugin marketplace add <owner>/<repo>`) | `agy plugin install .` (copies the root into `~/.gemini/config/plugins/<name>/`, skipping dot-directories); `agy plugin uninstall <name>` to remove |
| Install from GitHub | `codex plugin marketplace add hoshiori-dev/harness-builder` | `/plugin marketplace add hoshiori-dev/harness-builder` | `agy plugin install https://github.com/hoshiori-dev/harness-builder` |
| Validator | `codex plugin marketplace add .` + `codex plugin list` | `claude plugin validate .` (non-strict: the root `CLAUDE.md` of this development repository draws a warning that `--strict` turns into a failure) | `agy plugin validate .` (non-strict: it notes that `mcp_config.json` is used only while the flag is off) |

Decision rule behind the table: spec-defined things use the spec; a client
that cannot read the spec gets a pointer in its own manifest when it has one,
a generated conversion when the format differs mechanically, and a
hand-written client file when fields differ (agents). Agents ship only where
the client's plugin system has an agents component (Claude Code); a client
without one gets no agent files at all, and the limitation is a watch-list
row rather than a workspace workaround, because workspace wiring is not
plugin content and would only exist to test itself. Which clients are
supported is a project decision declared in `scripts/lib/clients.ts`, never
inferred from the tree; the registry also records where each client's files
live (`agents` absent means the client ships none). A reverse-domain
directory exists only while a client has hand-written files, so today only
`com.anthropic.claude-code/` does; Codex's client-specific data is the
`extensions.com.openai` block, and Antigravity has none. `just
client-footprint <id>` prints the files a client owns.

## Known limitations

Every limitation, the workaround built for it, how to re-check it, and what
to do when it lifts is one row of `.agents/knowledge/compatibility-watch.md`.
Headlines only: Antigravity reads `mcp.json` only behind a flag (W1) and
plugin agents only from the plugin root (W2); Claude Code needs
`.claude/skills` symlinks (W6) and generated pointer files (W7); Codex plugins
ship no agents (W9); `com.anthropic.claude-code` is a self-chosen namespace
(W10).

## Verification log

| Date | What | Result |
|---|---|---|
| 2026-10-27 | `codex plugin marketplace add .` + `codex plugin add` with `source.path: "./"` | installs root plugin (plugin.json, mcp.json, skills, mcp) |
| 2026-10-27 | `claude plugin validate --strict .` with generated pointer manifest and no root `agents/` | passes, no warnings |
| 2026-10-27 | `agy plugin install <root>` with root `plugin.json` (spec `$schema`), `skills/`, generated `mcp_config.json` | skills and mcpServers processed; dot-directories not copied; `agy --print` then lists the plugin and the `echo` tool |
| 2026-10-27 | `.agents/agents/<n>.md` workspace link to an Antigravity agent file under the namespace directory | `agy --print` in the repository lists it as a subagent, so the file format was valid; removed the same day because workspace agents are not plugin content (W2) |
| 2026-10-27 | `.agents/plugins/<name> -> ../..` workspace link to the repository root | loads in the workspace but breaks `agy plugin install` (the copy follows the link into itself); rejected |
| 2026-10-27 | `.agents/plugins.json` with `{"path": ".", "include_only": [...]}` | not picked up by the CLI session; rejected |
| 2026-10-27 | `agy plugin install https://github.com/<owner>/<repo>/tree/main/<dir>` | the CLI clones and installs a subdirectory; not needed now that the root is the plugin |
| 2026-10-27 | `agy plugin validate .` | passes with the note that `mcp_config.json` is used while the flag is off; `--strict` turns the note into a failure |
