# harness-builder

An Agent Plugins v1.0.0 plugin and the GitHub template for building one. The
repository root is the plugin: Codex and Antigravity read it natively, Claude
Code through a generated pointer manifest. Skills and MCP are the portable
product; agents demonstrate client-specific files and ship only to Claude
Code, the one client whose plugin system carries them.

## Always

- Repository content is English: code, comments, docs, commits, this harness.
  Talk to the user in the user's language.
- A change to a shipped skill, MCP server, or agent starts as an OpenSpec
  change and waits for `spec: approved`; harness, script, CI, and doc
  changes are spec-less and go straight to a pull request (a change with
  `skip_specs: true` only for a recorded design). See
  `.agents/knowledge/spec-workflow.md`.
- Never hand-edit generated files: `.claude-plugin/plugin.json`,
  `.claude-plugin/marketplace.json`, `com.anthropic.claude-code/mcp.json`,
  `mcp_config.json`, `.agents/plugins/marketplace.json` (`just gen`), and `.agents/skills/openspec-*/`
  (`openspec init --tools agents --force`, never `openspec update`).
- Never weaken a check, hook, workflow, or gate to make a change pass;
  propose the change on the pull request instead.
- Commits: Conventional Commits, lowercase imperative subject, no AI or tool
  attribution trailers. Checkpoint commits are fine; `main` gets one squash.
- Agents mark a pull request ready only after the self-review in
  `.agents/knowledge/agent-authority.md` passes; approving, merging,
  tagging, and remote settings are human actions.
- Nothing secret or private enters the repository, an issue, or a PR; the
  repository is public.

## Project Map

```text
plugin.json  mcp.json          <- the portable plugin (Agent Plugins 1.0.0); mcp_config.json is its generated Antigravity stand-in
skills/<name>/SKILL.md         <- shipped skills (catalog: skill)
mcp/<name>/                    <- bundled MCP server code (catalog: mcp)
com.anthropic.claude-code/     <- Claude Code's client-specific files: agents/*.md, generated mcp.json (the only client with any; spec §8 directories exist only then)
.claude-plugin/                <- generated Claude Code manifest and marketplace
.codex/config.toml  .agents/plugins/marketplace.json  <- Codex workspace wiring (plugin enable, generated marketplace)
openspec/specs/<catalog>/spec.md, <catalog>/<name>/spec.md  <- catalog rules and entry specs
scripts/                       <- management code (Deno): gen, checks, dist, labels; lib/clients.ts declares the supported clients
.agents/knowledge/             <- agent knowledge (this file routes into it)
.agents/skills/                <- project skills; Claude Code sees them via .claude/skills symlinks
.github/                       <- workflows, issue forms, PR template, labels
```

## When To Read What

| Situation | Read |
|---|---|
| Adding or changing a shipped skill, server, or agent | the `plugin-development` skill, then `.agents/knowledge/client-matrix.md` |
| A client does not load something, or touching `com.*` or a wiring file | `.agents/knowledge/client-matrix.md` |
| Proposing, implementing, or archiving an OpenSpec change | `.agents/knowledge/spec-workflow.md`, then the `openspec-*` skills |
| Taking an issue, opening or finishing a PR, any `gh` write, a red check | the `github-project-workflow` skill, `.agents/knowledge/github-workflow.md`, `.agents/knowledge/github/checks.md` |
| Branching, commit format, tags, merge method | `.agents/knowledge/git-workflow.md` |
| Before marking ready, merging, releasing, or changing a remote setting | `.agents/knowledge/agent-authority.md`, `.agents/knowledge/github/platform-settings.md` |
| Adding or dropping a client or catalog, changing check strictness, upgrading OpenSpec, pulling template updates | the `template-adjust` skill |
| Editing this file or any knowledge file; every tenth merged PR | `.agents/knowledge/maintenance.md` |
| A client or OpenSpec was upgraded, a client behaves differently than documented, or you want to remove a workaround | `.agents/knowledge/compatibility-watch.md` |

## Development Environment

Open the dev container (`.devcontainer/`): it provides deno, uv, just,
pre-commit, betterleaks, openspec, and the three client CLIs
(`claude`, `codex`, `agy`). `.devcontainer/setup.sh` installs the git hooks.
Client CLIs may need the user's own login; never store credentials in the
repository. Builder skills under `.agents/skills/meta-*` are gitignored
helpers of the template author, not part of the harness.

## Validation

| Check | Command |
|---|---|
| Everything CI runs | `just check` |
| The Deno-only subset the push workflow runs | `just check-fast` |
| Generated client files are current | `just gen --check` (regenerate: `just gen`) |
| Plugin layout, wiring, catalog ↔ implementation | `just validate` |
| Harness links, recipes, budgets, symlinks | `just harness-check` |
| Specs and changes, strict | `just spec-check` |
| No unarchived OpenSpec change (merge gate) | `just spec-archived` |
| Scripts and the MCP smoke test | `just test` |
| Package validity in the real clients (local only) | `just clients-validate` |

## Workflow

Issue → `gh issue develop` branch → draft PR carrying the OpenSpec change →
maintainer adds `spec: approved` → implement with `just check` green → agent
self-reviews and marks ready → maintainer reviews → implementer archives the
change on the branch → maintainer squash-merges → version bump and `v*` tag
release.

## Keep In Sync

| When this changes | Update |
|---|---|
| `plugin.json`, `mcp.json`, or any `com.*/agents/` file | run `just gen`; commit the generated files |
| A skill, server, or agent is added or removed | its spec under `openspec/specs/<catalog>/<name>/`, every agent-capable client's agent file, `just gen` |
| A `justfile` recipe or CI job | the Validation table above, `.agents/knowledge/github/checks.md`, the job's workflow under `.github/workflows/` |
| A client's loading behaviour (new version) | `.agents/knowledge/client-matrix.md` table and verification log; the matching rows of `.agents/knowledge/compatibility-watch.md` |
| A check, generator branch, or document exists only to work around a client or spec gap | add a row to `.agents/knowledge/compatibility-watch.md` |
| OpenSpec version | `openspec init --tools agents --force`, `.agents/knowledge/spec-workflow.md` |
| This file passes 120 lines, or every tenth merged PR | the reclamation in `.agents/knowledge/maintenance.md` |
