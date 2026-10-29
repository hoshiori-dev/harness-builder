# The Spec-Kit feature directory

Read when checking a feature directory against the kit, when a feature was
made by hand, or when someone asserts what the kit's feature script does.

Verified on 2026-10-29 against the kit's README, its `create-new-feature`
script, its `converge` command, and its spec, plan, and tasks templates.
The kit has renamed its commands before (they are now `/speckit-specify`,
`/speckit-plan`, `/speckit-tasks`, `/speckit-implement`,
`/speckit-converge`); read the project's installed copy before quoting one.

## What the kit lays down

- `.specify/` at the repository root marks a Spec-Kit project. The
  constitution lives at `.specify/memory/constitution.md`; the plan step
  reads it, so engineering principles belong there and not in a plan.
- One directory per feature under `specs/`, named `NNN-short-name`
  (sequential, at least three digits) or, with `--timestamp`,
  `YYYYMMDD-HHMMSS-short-name`.
- The feature script records the current feature in `.specify/feature.json`
  (`feature_directory`) unless `SPECIFY_FEATURE_NO_PERSIST` is set; the
  plan, tasks, and implement steps find the feature through it or through
  `SPECIFY_FEATURE`.
- `spec.md` and `plan.md` are required; `tasks.md` holds the checkboxes
  (`- [ ] T001 …`). Research, data-model, contracts, and quickstart files are
  optional.
- `converge` appends a `## Phase N: Convergence` section of new tasks to
  `tasks.md` and writes nothing else.

## Branches

Branch creation lives in the kit's optional git extension
(`create-new-feature-branch`). Before telling the user what happened, find
the project's copy (`find .specify -name 'create-new-feature*'`) and check
for `git checkout -b` or `git switch -c` in it, and whether
`.specify/extensions.yml` enables the git extension. When nothing creates a
branch, say so and point to the project's branching rule.

## The heading check

No programmatic validator exists. Compare the feature's files with these
template headings, list present and missing ones, and say it is a heading
check only. Prefer the project's own templates under `.specify/` when they
exist: a preset may have changed them.

| File | Headings |
|---|---|
| `spec.md` | `# Feature Specification:`, `## User Scenarios & Testing`, `### Edge Cases`, `## Requirements`, `### Functional Requirements`, `## Success Criteria`, `### Measurable Outcomes`, `## Assumptions` |
| `plan.md` | `# Implementation Plan:`, `## Summary`, `## Technical Context`, `## Constitution Check`, `## Project Structure`, `## Complexity Tracking` |
| `tasks.md` | `# Tasks:`, at least one `## Phase` heading, at least one `- [ ]` or `- [x]` line |

Template text (`[NEEDS CLARIFICATION]` markers, `**Feature Branch**:`
fields) stays inside the kit's files; do not copy it into the project's
contract.

## A hand-made feature directory

A directory made by hand has no `.specify/feature.json` entry and may not
follow the template, so the kit's later steps may not find what they read.
Recommend recreating it through the kit's specify step and moving the
written content into the generated files; the alternative is setting
`SPECIFY_FEATURE` for each later step, which every session must remember.
