# Skill Quality

Read before writing or editing anything under `skills/*`: a `SKILL.md`, a
reference, an asset, or a script. `just skills-check` enforces the
mechanical rules below; the rest is judgement this file makes explicit.

A skill earns its place in two ways: it supplies context the agent does not
have (this methodology, non-obvious procedures, exact formats) and it
restricts output so the same process runs every time. Write every rule for
the least capable model the plugin should support, not for the model at hand:
a stronger model tolerates a restriction it does not need; a weaker one
breaks without it.

## Scope

- One skill covers one coherent unit of work. Too narrow and it collides
  with its neighbours; too broad and it triggers unreliably.
- Two kinds of skill ship here. **Entry skills** (`harness-create`,
  `harness-improve`) are user-invoked: `disable-model-invocation: true`,
  self-contained workflows. **Model-invoked skills** (the layer builders, the
  manual, the SDD skills) are reached by their descriptions; a layer builder
  states `Owns the <layer> layer` once, using a layer name from
  `scripts/lib/layers.ts`, because the entry skills route by that phrase.
- A skill is self-contained: no link leaves its directory, no other skill
  library or install command is named. Repeated paragraphs are shared blocks
  (`.agents/knowledge/shared-blocks.md`).
- Methodology paragraphs carry a `[§x.y]` tag naming the section of the
  methodology document (docs/, when it lands) they operationalise, so drift
  between the two is auditable.

## Frontmatter

- `name` equals the directory name: lowercase, digits, single hyphens, at
  most 64 characters.
- `description`: third person, opens on the skill's leading word, gives most
  of its length to triggers ("Use when …"), names the neighbours it is not
  for ("Not for …"), restates nothing from the body. Error above 1024
  characters, warning above 900.
- `license: Apache-2.0`. `compatibility` only when the skill ships scripts.

## Body

- Order: `# Title`, one purpose paragraph, `## Rules on every step`,
  `## Workflow` with numbered steps, `## Gotchas`. A step ends with
  `Done when:` only where the boundary is checkable and changes how the step
  is executed or judged.
- Every pointer to a reference states its load condition: "Read
  `references/x.md` when …", never "see references/".
- Inline what every branch needs; disclose into `references/` what only some
  branches reach. Co-locate a concept's definition, rules, and caveats.
- Give one default per decision and present it as a recommendation; a skill
  that leaves two equal options makes agents choose inconsistently.
- Assets are raw starting shapes the agent reworks line by line; the
  how-to-use text belongs in `SKILL.md` or a reference, not in the asset.
  Placeholders `{{NAME}}` are allowed only on lines marked `# CONFIGURE:`.
- Under about 500 lines and 5000 tokens; longer means a split is overdue.

## Scripts and script assets

Delivered to other machines, so written in Python with PEP 723 inline
metadata: shebang `#!/usr/bin/env -S uv run --script` (or
`#!/usr/bin/env python3` when there are no dependencies), a `# /// script`
block with `requires-python = ">=3.10"`, standard library preferred so the
script also runs on a plain `python3` without uv. Every script: no
interactive prompt, `--help` with a usage example, data on stdout (JSON
preferred) and diagnostics on stderr, exit codes 0 / 1 / 2 (success / finding
or error / bad arguments), idempotent, errors that say what is wrong and how
to fix it, output above about 10,000 characters summarised by default with
`--full` or `--output`. Every script and script asset has a sibling
`<name>_test.py` run by `just test`; `ruff` (`just lint`) applies, with
`BLE001` and `S110` as errors: no bare `except`, no silent `pass`.

## Pruning

Three passes over anything written or touched, description included:
deduplicate (one source of truth per meaning), relevance (delete what no
longer bears on the skill), no-op hunt (delete every sentence that would not
change behaviour on the weakest supported model). Delete sentences whole; do
not rewrite them softer.

## Behavioural tests

Every skill's OpenSpec spec carries its test cases as scenarios: at least
three prompts that should load it and three near misses that should not, and
at least two outcome tasks with a rubric a reader can judge without seeing
the skill. They run by hand through clean-context subagents on the least
capable model tier available, never in CI (`.agents/knowledge/spec-workflow.md`,
validation); the pull request records the results. Trigger prompts never
name the skill.

## Diagnosing a misbehaving skill

Start from the symptom: never triggers or fires on the wrong task → the
description; stops a step early or works shallowly → missing or weak
`Done when:`; never opens a reference → its pointer has no condition; hard to
edit or self-contradicting → duplication; long but every line looks
legitimate → sprawl, prune. Apply the smallest general fix, then prune and
re-run `just skills-check`.
