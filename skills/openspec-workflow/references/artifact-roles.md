# Artifact roles and formats

Read when writing, reviewing, or repairing a proposal, a delta spec, a design,
or a task list, or when the strict validator rejects one.

## What each artifact owns

| Artifact | Owns | Never holds |
|---|---|---|
| `proposal.md` | the end state: why, what changes, what is affected, and `## Acceptance` last | the approach, steps, the requirements themselves |
| delta specs `specs/<capability>/spec.md` | the contract: requirements with scenarios a reader judges without reading the code | implementation choices, file contents |
| `design.md` | how the end state is reached: bounds of the approach, decisions with rejected alternatives | the goal, acceptance, steps, secrets or private data |
| `tasks.md` | ordered implementation steps, each naming its verification | anything the approver must see before approving |

An invariant that holds under any approach goes in the proposal's **Stays
true**; one that holds only because of the chosen approach goes in the design.
Approval covers the outcome, the non-goals, and the bounds of the approach,
never the task list, which is why the task list comes after the gate. [§4.2]

## Proposal: Acceptance last

Every proposal ends with this section. Each item is checkable by a command,
a scenario, or a walkthrough someone can run; mark an item that is not yet
checkable and say what would make it so.

```markdown
## Acceptance

**Becomes true:**
- <observable result>, checked by <command, scenario, or walkthrough>

**Stays true:**
- <invariant that must hold under any approach>, checked by <…>
```

A proposal that stops at Impact gets the section before it is published.

## Delta specs

- Describe observable behaviour, never the diff ("a duplicate email returns
  409", not "add a unique index"). Every requirement has at least one
  scenario; the spec as a whole has at least one failure or edge scenario.
  Non-goals are written down. [§4.1]
- Headings exactly: `## ADDED Requirements` (or MODIFIED, REMOVED,
  RENAMED), `### Requirement: <name>`, `#### Scenario: <name>`, with
  `- **WHEN** …` / `- **THEN** …` lines. A scenario at `###` or bullets
  without bold keywords fail strict validation.
- A MODIFIED block replaces the whole requirement at archive time: copy
  every existing scenario into it, changed or not.
- A delta that creates a capability carries `## Purpose` with at least 50
  characters before its requirements; otherwise the archive writes a
  placeholder Purpose that fails strict validation afterwards.

## Design

Write one only when the project's rule, or the skill's default, warrants it.

```markdown
## Goals / Non-Goals

**Goals:**
- <constraint of the chosen approach>. Checked by <how>.

**Non-Goals:**
- <what the approach deliberately leaves out>. Checked by <how>.

## Decisions

### <decision>
<the choice and why>. Rejected: <alternative> because <reason>.
```

A design that lists the order in which files are edited has steps in it:
move the order to the task list and leave bounds, decisions, and rejected
alternatives.

## Tasks

- Written or finished only after the first gate closes, even when the
  propose step generated them with the rest.
- Each task names its own verification; a task is ticked only after that
  verification ran and passed.
- No task archives the change; the archive follows the review.

## Spec-less change record

The archive of a change marked `skip_specs: true` needs `--skip-specs`,
which the bundled script adds.
