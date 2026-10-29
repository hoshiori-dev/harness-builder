# Specification Workflow

Read before proposing, implementing, or archiving a change to a shipped skill
or agent, and when unsure whether a change needs a spec.

Level: spec-anchored. The specs under `openspec/specs/` are the living
description of what the plugin does; the skills and the agent implement them.
Tool: OpenSpec 1.15.0 (`openspec` CLI, `spec-driven` schema), initialised on
2026-10-27 by the template with `openspec init --tools agents`.

## Artifact map

| Artifact | Path | Owns |
|---|---|---|
| Catalog rules | `openspec/specs/<catalog>/spec.md` for `skill`, `agent` | rules every entry of the catalog follows |
| Entry spec | `openspec/specs/<catalog>/<name>/spec.md` | observable behaviour of one shipped entry, the clients it ships to, and its behavioural test cases (scenarios) |
| Change | `openspec/changes/<id>/` (`proposal.md`, `design.md`, `tasks.md`, `specs/` deltas, `.openspec.yaml`) | one proposed change until archived |
| Archive | `openspec/changes/archive/<date>-<id>/` | the record of a merged change |
| Project rules for artifacts | `openspec/config.yaml` | context and per-artifact rules the OpenSpec skills apply |

Source of truth per fact: behaviour → the entry spec; package metadata →
`plugin.json`; conventions → this knowledge base; the methodology → the
document under `docs/` once it lands, which the skills reference by section.
Nothing restates a spec; `AGENTS.md` and the skills point to it.

## Artifact roles

| Artifact | Owns | Never holds |
|---|---|---|
| proposal | the end state: why, what changes, which entries, and `## Acceptance` with **Becomes true** and **Stays true** lists | the contract itself, the approach, steps |
| delta specs | the contract: requirements with scenarios a reader judges without opening the skill | implementation choices |
| design | how the end state is reached: Goals / Non-Goals each with how it is checked, decisions with rejected alternatives, what only this change needs | the goal, acceptance, steps, secrets |
| tasks | implementation steps, each with its own verification; written only after gate 1 | acceptance; anything gate 1 must see |

An invariant that holds under any approach goes in the proposal's "Stays
true"; one that holds only because of the chosen approach goes in the design.

## Scope

- A change to any shipped skill or agent carries a delta spec; `just
  validate` enforces that every entry has a spec and every spec an entry.
- A change that touches no shipped entry (harness, scripts, CI,
  documentation, docs site, generated files) is spec-less: it goes straight
  to a pull request, labelled `spec:skipped` by the `pr-labels` workflow. The
  harness is machine-checked (`just harness-check`, `just skills-check`)
  instead of specified; a spec for it would be a second copy. A large
  harness change that deserves a recorded design opens a change with
  `skip_specs: true` in `.openspec.yaml` and ships proposal, design, and
  tasks; it is archived before merge like any other.
- Specs describe behaviour the change touches; nothing is back-filled.

## Lifecycle and gates

1. **Propose**: `openspec-propose` (or `openspec-explore` first); commit the
   change directory on the issue branch; open a draft pull request that
   carries it (combined shape: one PR holds change, implementation, and
   archive).
2. **Gate 1, proposal approval**: the maintainer reads proposal, design, and
   delta specs on the PR, discusses in the conversation, and adds
   `spec:approved`. The `pr-labels` workflow records the approval (commit,
   account, hash of every file under the unarchived changes) and keeps the
   label only while that package is unchanged; an edit puts `spec:pending`
   back. Tasks are written only after the label.
3. **Implement**: `openspec-apply-change`, one task at a time, `just check`
   green between tasks; `just gen` after any change to `plugin.json` or an
   agents directory.
4. **Gate 2, implementation acceptance**: the agent runs the behavioural
   tests the delta specs define (`.agents/knowledge/skill-quality.md`),
   records the results in the PR, self-reviews, and marks the PR ready
   (`.agents/knowledge/agent-authority.md`); the maintainer reviews.
5. **Freeze**: after the review, the implementer archives on the branch with
   `openspec-archive-change`; the archive commit is the frozen record and a
   commit after it reopens the deliberation. The `pr` workflow reports the
   required check `checks / spec-archived` only when no unarchived change
   remains, so the merge is blocked until then (`just spec-archived`).

State labels, maintained by `pr-labels` from the tree and never by hand:
`spec:skipped`, `spec:pending`, `spec:approved` (added by a person with write
permission, recorded, package unchanged), `spec:archived`. `just pr-labels
<n>` prints the decision without writing.

## Validation of a skill change

`openspec validate --strict` proves structure. Behaviour is proven by the
scenarios: trigger scenarios run as prompts to clean-context subagents that
do not name the skill, outcome scenarios as tasks judged against their
rubric, both on the least capable model tier the session offers. They run by
hand before gate 2 and are not CI jobs: CI has no agent credentials and the
runs are costly. When no subagent is available, say so in the PR and run the
prompts in a fresh session instead.

## Bootstrap exception (2026-10-29)

The first build of this repository ran in pairing mode. One change,
`openspec/changes/bootstrap-harness-builder/`, carried the proposal, the
design, and one delta spec per skill and for the agent. Gate 1 closed in the
conversation, before the `pr-labels` workflow and the ruleset existed on the
remote; the tasks were written after that conversational approval; the change
was archived before the first merge into `main`. Every later change follows
the lifecycle above.

## Update triggers

- New catalog → add `openspec/specs/<catalog>/spec.md`, extend
  `scripts/check_plugin.ts`'s catalog list, and this map.
- OpenSpec release adopted → `openspec init --tools agents --force` (never
  `openspec update`), `just harness-check`, update the version above.
