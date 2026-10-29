# Design

## Context

See proposal.md for motivation. The repository is a tailored copy of
agent-plugins-starter: `plugin.json` and `skills/` are the portable plugin,
`just gen` writes the client files, `just check` runs the Deno management
scripts under `scripts/` and the OpenSpec strict validation. The harness
(`AGENTS.md`, `.agents/knowledge/`) already states the rules the skills must
follow: `skill-quality.md` (frontmatter, body, scripts, pruning, behavioural
tests), `shared-blocks.md` (paragraphs repeated across skills, canon here),
`spec-workflow.md` (scenarios are the behavioural tests; bootstrap
exception). `just skills-check` enforces the mechanical part of those rules,
including the `Owns the <layer> layer` phrase, the `disable-model-invocation`
switch on the two entry skills, the PEP 723 shape of every Python script, and
the test file beside each one.

The methodology document the skills operationalise is not in the repository
yet; the skills tag the sections they implement (`[§x.y]`) so the later docs
pull request can be checked against them.

Upstream prior art (the `meta` and `sdd` catalogs of ryan-minato/skills) is
read for content and house style only. Nothing is copied that the plan drops:
disposable markers and disposal, the never-commit rule, platform-neutral
model vocabulary and its leak greps, the contract→platform→two-phase chain and
its thirteen extension slots, GPU and Python-defaults builders, the `/spec`
comment commands, the tarball discovery script, and every mention of another
skill library or of an install command.

## Goals / Non-Goals

**Goals:**

- Every decision a skill takes in a target project is confirmed with the
  user; defaults appear only as recommendations. Checked by: every
  Behavior scenario that involves a choice names the recommendation and the
  user's confirmation; the `confirm-not-guess` and
  `recommendation-not-decision` shared blocks appear in every skill that
  decides anything (`just skills-check`, rule `shared-block`).
- The entry skills route to layer builders by description, so adding or
  renaming a builder needs no change to an entry skill. Checked by: no entry
  skill names a builder; `just skills-check` `layer-ownership`.
- Each skill is self-contained and portable across the three clients.
  Checked by: `skill-link-escape`, `skill-no-install-cmd`, client-neutral
  body with per-client references (`openspec/specs/skill/spec.md`).
- Delivered scripts run wherever a target project runs. Checked by: PEP 723
  block with `requires-python = ">=3.10"`, `uv run` and plain `python3`
  smoke in each `_test.py`, `just test`.
- Behaviour is testable before release. Checked by: Triggering and Outcomes
  scenarios in every delta spec; results recorded in the pull request.
- The repository's own checks stay green at every task commit. Checked by:
  `just check-fast` per skill commit, `just check` before ready.

**Non-Goals:**

- Writing the methodology document or its translation into `docs/`.
- An MCP server, hooks, or commands (outside Agent Plugins 1.0.0).
- Behavioural tests in CI, or a canary harness in CI.
- GitLab-specific scripts beyond the automation assets each skill ships;
  the repository itself is GitHub-hosted and `clients-validate` stays local.
- Agents for Codex or Antigravity (W9, W2).

## Decisions

- **Two user-invoked entries rather than one orchestrator.** `harness-create`
  and `harness-improve` each carry a complete workflow; the shared
  methodology lives in `harness-architecture`, and the paragraphs that must
  read identically are shared blocks. Rejected: a model-invoked
  `harness-building` orchestrator the entries hand to (one more skill the
  entries would have to name, and a description-matched skill that rewrites
  harnesses is exactly what the user wants to prevent); one `harness` skill
  with sub-modes (a body far over the size budget).
- **Routing by the `Owns the <layer> layer` phrase**, layer names fixed in
  `scripts/lib/layers.ts`. Rejected: a routing table inside the entry skills
  (a second copy of the catalog that drifts).
- **Project skills get their own builder** (`project-skill-building`) and
  `knowledge-routing-building` only decides whether a procedure deserves
  one. Rejected: folding the skill-writing methodology into the knowledge
  builder (a body over budget; "fix a misfiring project skill" has its own
  trigger vocabulary).
- **Python + uv for every delivered script**, with stdlib preferred so a plain
  `python3` also runs them; Deno stays the language of this repository's own
  management code. Rejected: Deno for delivered scripts (target machines
  without Deno could not use the plugin fully); Bash (no tests, no JSON
  discipline). The target project's own management-script language is a
  separate, user-confirmed decision made by `hard-boundary-building`.
- **Three insertion markers instead of extension slots.**
  `platform-lifecycle-building` writes `<!-- harness: spec-workflow -->` in
  the PR/MR template, the project skill's Finish step, and the platform
  knowledge file; `spec-completion-building` fills whatever it finds. Rejected:
  the upstream slot register (thirteen named slots, two-phase builder).
- **GitHub and GitLab as branches inside one skill** (`references/github.md`,
  `references/gitlab.md`, `assets/github/`, `assets/gitlab/`). Rejected:
  one skill per platform (two bodies restating the same procedure).
- **Specs carry the behavioural tests.** Trigger prompts and outcome tasks
  are scenarios, run by hand through clean-context subagents. Rejected: a
  separate test directory (a second source of truth for what the skill does).
- **Build order**: `harness-architecture` first (every other skill points
  at its reasoning), then `project-skill-building` (every later skill is
  written to its procedure), then the five remaining layer builders,
  `platform-lifecycle-building`, the four SDD skills, the two entries, the
  agent last (so `just gen` adds the `agents` pointer once).

## Client files

- `com.anthropic.claude-code/agents/harness-verifier.md`: hand-written.
- `.claude-plugin/plugin.json`: regenerated by `just gen`; gains
  `agents: ["./com.anthropic.claude-code/agents/harness-verifier.md"]`.
- `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`:
  regenerated, unchanged in content.
- No files under `com.openai/` or `com.google.antigravity/`.

## Risks / Trade-offs

- [Fourteen skills written in one change are hard to review as a whole] →
  one task and one commit per skill; the delta specs are reviewed before any
  skill is written; each skill's scenarios are run before ready.
- [Shared blocks tempt copy drift] → `just skills-check` fails on any
  divergence; the canon is edited first.
- [Descriptions compete: a layer builder fires when an entry skill is meant]
  → entry skills carry `disable-model-invocation: true`; every builder
  description names its layer and its "Not for" neighbours; the Triggering
  scenarios include near misses across sibling skills.
- [Delivered Python assets drift from the repository's conventions] → every
  asset has a `_test.py` run by `just test`, ruff with BLE001/S110, and the
  `script-pep723`/`script-help` rules.
- [The methodology document is referenced by section before it exists in
  `docs/`] → tags are `[§x.y]` only; the docs pull request adds the
  section→skill map check; until then `harness-architecture/references/methodology-map.md`
  is the index.

## Open Questions

None that change the specs or the task breakdown. The canary target for
Phase 3 (which scratch repository to run `/harness-create` against) is chosen
when the tasks reach it.
