# harness-builder

An Agent Plugins v1.0.0 plugin that builds, improves, and repairs the agent
harness of other projects: two user-invoked entry skills, a methodology
manual, one builder per harness layer, spec-driven development skills, and a
read-only verifier agent. The repository root is the plugin: Codex and
Antigravity read it natively, Claude Code through a generated pointer
manifest. Skills are the portable product; the agent ships to Claude Code
only.

## Always

- Code, comments, this harness, the skills, the agent, and every delivered
  asset are English (the weakest models follow English rules best).
  `README.md` and `docs/` are Chinese first; `README.en.md` mirrors the
  README. Talk to the user in the user's language.
- A change to a shipped skill or agent starts as an OpenSpec change and waits
  for `spec:approved`; harness, script, CI, docs, and generated-file changes
  are spec-less and go straight to a pull request
  (`.agents/knowledge/spec-workflow.md`).
- Never hand-edit generated files: `.claude-plugin/*`,
  `.agents/plugins/marketplace.json` (`just gen`) and
  `.agents/skills/openspec-*/` (`openspec init --tools agents --force`, never
  `openspec update`).
- Never weaken a check, hook, workflow, permission, or this policy to make a
  change pass; propose the change on the pull request instead.
- Commits: Conventional Commits, lowercase imperative subject, no AI or tool
  attribution. Every verified task is one commit; drafts are squashed per
  task before they are pushed and never reach the remote; push one explicit
  ref (`.agents/knowledge/git-workflow.md`).
- Irreversible or outward actions (push, ready, comment, label, release,
  remote settings) happen only when the plan pre-authorised them or as items
  of the pending decisions list; reversible internal work never stops to ask
  (`.agents/knowledge/agent-authority.md`).
- When blocked, finish everything that does not depend on the decision and
  queue the rest; when the harness contradicts the repository, fix it in the
  change, queue it, or open an issue, never only say it
  (`.agents/knowledge/maintenance.md`).
- Nothing secret or private enters the repository, an issue, or a PR; the
  repository is public.

## Project Map

```text
plugin.json                    <- the portable plugin (Agent Plugins 1.0.0); no MCP server
skills/<name>/SKILL.md         <- shipped skills (catalog: skill); scripts and assets are Python + uv
com.anthropic.claude-code/     <- Claude Code's hand-written files: agents/*.md
.claude-plugin/                <- generated Claude Code manifest and marketplace
.codex/config.toml  .agents/plugins/marketplace.json  <- Codex wiring (plugin enable, generated marketplace)
openspec/specs/<catalog>/spec.md, <catalog>/<name>/spec.md  <- catalog rules and entry specs (scenarios = behavioural tests)
scripts/                       <- this repository's management code (Deno): gen, checks, dist, labels
docs/  zensical.toml           <- the Chinese docs site (Zensical, GitHub Pages)
.agents/knowledge/             <- agent knowledge (this file routes into it)
.agents/skills/                <- project skills; Claude Code sees them via .claude/skills symlinks
.github/                       <- workflows, issue forms, PR template, labels
```

## When To Read What

| Situation | Read |
|---|---|
| Adding, changing, or removing a shipped skill or the agent | the `plugin-development` skill, then `.agents/knowledge/skill-quality.md` |
| Writing or editing any `skills/*` file, or a skill misbehaves | `.agents/knowledge/skill-quality.md` |
| Editing a `<!-- shared:… -->` block in a skill | `.agents/knowledge/shared-blocks.md` |
| A client does not load something, or touching `com.*` or a wiring file | `.agents/knowledge/client-matrix.md` |
| Proposing, implementing, or archiving an OpenSpec change | `.agents/knowledge/spec-workflow.md`, then the `openspec-*` skills |
| Taking an issue, opening or finishing a PR, any `gh` write, a red check | the `github-project-workflow` skill, `.agents/knowledge/github-workflow.md`, `.agents/knowledge/github/checks.md` |
| Branching, committing, squashing, pushing, merge method, tags | `.agents/knowledge/git-workflow.md` |
| Before pushing, marking ready, commenting, releasing, or changing a remote setting; an action was refused | `.agents/knowledge/agent-authority.md`, `.agents/knowledge/github/platform-settings.md` |
| Editing `docs/`, `zensical.toml`, or the docs workflow | `.agents/knowledge/docs-site.md` |
| Adding or dropping a client or catalog, changing check strictness, upgrading OpenSpec, pulling starter updates | the `template-adjust` skill |
| Editing this file or any knowledge file; every tenth merged PR | `.agents/knowledge/maintenance.md` |
| A client or OpenSpec was upgraded, behaves differently than documented, or a workaround may go | `.agents/knowledge/compatibility-watch.md` |

## Development Environment

Open the dev container (`.devcontainer/`): deno, uv, just, pre-commit,
betterleaks, openspec, zensical, and the client CLIs (`claude`, `codex`,
`agy`). `.devcontainer/setup.sh` installs the git hooks. Client CLIs may
need the user's own login; never store credentials in the repository.

## Validation

| Check | Command |
|---|---|
| Everything CI runs | `just check` |
| The fast subset the push workflow runs | `just check-fast` |
| Generated client files are current | `just gen --check` (regenerate: `just gen`) |
| Plugin layout, wiring, catalog ↔ implementation | `just validate` |
| Skill quality: frontmatter, links, shared blocks, assets, tests | `just skills-check` |
| Harness links, recipes, budgets, symlinks, README mirror | `just harness-check` |
| Specs and changes, strict | `just spec-check` |
| No unarchived OpenSpec change (merge gate) | `just spec-archived` |
| Deno tests and the skills' Python tests | `just test` |
| Docs site builds strictly | `just docs-check` |
| Package validity in the real clients (local only) | `just clients-validate` |

## Workflow

Issue → `gh issue develop` branch → draft PR carrying the OpenSpec change →
maintainer adds `spec:approved` → implement with task commits and `just
check` green → behavioural tests → self-review, ready → maintainer reviews →
implementer archives on the branch → maintainer squash-merges → version bump
and `v*` tag release.

## Keep In Sync

| When this changes | Update |
|---|---|
| `plugin.json` or any `com.*/agents/` file | run `just gen`; commit the generated files |
| A skill or the agent is added, renamed, or removed | its spec under `openspec/specs/<catalog>/<name>/`, both README skill tables, `just gen` |
| A shared block's canon in `shared-blocks.md` | every skill using that id, in the same change (`just skills-check`) |
| A `justfile` recipe or CI job | the Validation table above, `.agents/knowledge/github/checks.md`, the workflow under `.github/workflows/` |
| `README.md` | `README.en.md`, same change (`just harness-check`) |
| A page under `docs/` | `docs/.nav.yml` |
| A client's loading behaviour (new version) | `.agents/knowledge/client-matrix.md`; the matching rows of `compatibility-watch.md` |
| OpenSpec version | `openspec init --tools agents --force`, `.agents/knowledge/spec-workflow.md` |
| Zensical version | the `justfile` variable only; re-read `docs-site.md` |
| This file passes 120 lines, or every tenth merged PR | the reclamation in `.agents/knowledge/maintenance.md` |
