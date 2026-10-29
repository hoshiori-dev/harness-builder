# com.anthropic.claude-code

Claude Code-specific files, namespaced as the Agent Plugins specification
requires (§8). It is the only such directory in this plugin: Codex's
client-specific data is the `extensions.com.openai` block in `plugin.json`,
and Antigravity has none. Claude Code does not read the Agent Plugins
manifest, so `.claude-plugin/plugin.json` (generated) mirrors the root
`plugin.json` and points here.

- `agents/*.md` — Claude Code subagents (hand-written).
- `mcp.json` — **generated** from the root `mcp.json` by `just gen`
  (`streamable-http` becomes `http`, `${PLUGIN_ROOT}` becomes
  `${CLAUDE_PLUGIN_ROOT}`). Do not edit by hand.
