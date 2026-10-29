# Brownfield Projects

Read when step 1 classified the project as brownfield: any build or test
command, task runner, CI, hook, branch habit, or agent-facing file. The core
risk is turning the harness build into a project overhaul: replacing the
existing layout, commands, and checks with an ideal structure, until the
harness describes a project the team does not recognise. [§6.3]

## Three principles

1. **Investigate before designing.** Start from what the project states
   itself: directory structure, build commands, existing checks, existing
   entry files, commit history habits. Ask only what it cannot state: team
   decisions, risk tolerance, which existing behaviour is deliberate.
2. **Working choices are preserved by default.** A task runner, lint
   configuration, or branch habit in use is a source of truth the harness
   points at, not something to replace. A migration with a clear reason and
   reasonable cost is offered as a suggestion; if the team accepts, it runs
   as a separate change, never inside the harness build.
3. **Grade each layer from the thinnest.** For each layer state what exists
   now, then what is needed, and plan only the difference. A first harness
   for an inherited project is often one root entrypoint and a few routes to
   the docs and commands it already has.

## Inventory

For every agent-facing file, project skill, permission file, hook, and
registered tool, record four facts:

- **found by**: how a future agent finds it (always loaded by the client, a
  route in an entrypoint, a skill description, nothing).
- **loads when**: at session start, on a matching path, on a description
  match, never.
- **source of truth**: the file or system that owns the facts it states
  (the `justfile`, CI configuration, `pyproject.toml`), or none.
- **kept current by**: a check, a sync rule, a person, or nothing.

When the methodology manual skill is installed, read its audit reference
before judging an existing artifact.

With no agent-facing file at all, the inventory reports only the missing
artifacts; the observed task runner and CI checks are recorded as the
sources of truth the harness will route to.

## Problem classes

Classify each finding as one of six, citing the evidence:

| Class | Meaning | Example evidence |
| --- | --- | --- |
| stale | states something no longer true | `CLAUDE.md` names `make test-all`; the `Makefile` has no such target |
| duplicated | the same fact in two places, one a copy | the test command in both `AGENTS.md` and `CONTRIBUTING.md` |
| contradictory | two sources disagree and neither is clearly the copy | `CLAUDE.md` demands Conventional Commits; `CONTRIBUTING.md` and the log show unprefixed titles |
| invisible | exists but no agent will find it | a knowledge file no entrypoint routes to |
| missing | needed for the confirmed grades and absent | no secret scanning at a hard-boundary grade of light or above |
| excessive | constrains something that no longer occurs | a lint rule for a module removed a year ago |

Handling:

- **stale**: the plan removes or corrects the rule, pointing the new
  entrypoint at the working command; the removal lands in a checkpoint
  commit.
- **contradictory**: cite every file and the log, ask the user which is
  intended before any plan row depends on it. When the chosen side leaves a
  public file (README, CONTRIBUTING, SECURITY) contradicting the harness,
  record a suggested edit for the closing report; do not edit the file.
- **duplicated**: keep the source, route to it, remove the copy.
- **invisible**: route to it or remove it, as the user chooses.
- **excessive**: propose thinning; the user decides.

Done when: every existing artifact has its four facts and, where it has a
problem, one class with evidence; every working choice is recorded as a
source of truth; every proposed migration is listed as a suggestion for a
separate change.
