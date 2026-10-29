# The Entrypoint

Read when drafting or restructuring `AGENTS.md`, when it exceeds its budget,
when a `CLAUDE.md` or a subdirectory entry file is involved, or when the user
asks why a line is or is not in the entrypoint.

## Order

1. **Title and purpose**: the project name and one or two sentences.
2. **Always**: rules whose breach harms regardless of task type. They are
   few, and they come first because attention decays with position. The
   section ends with the project map: the long-lived top-level directories,
   one line each, which every task needs. Omit the map when an architecture
   document already carries it and route to that document instead. A map
   that changes when a file is added is too detailed.
3. **When To Read What**: one row per situation, naming the file (and
   section, when only part of it applies) or the skill to load.
4. **Validation**: one row per check, naming the recipe.
5. **Keep In Sync**: the heading and the marker
   `<!-- harness: keep-in-sync -->`, nothing else. The layer owning entropy
   fills or removes it. [§2.1]

## The task-type test

Ask of each rule: does breaking it cause harm whatever the task is? Yes →
Always. Only on some tasks → a routing row. Examples:

| Rule | Class | Why |
|---|---|---|
| Run the formatter before committing | Always | every task can end in a commit |
| Never commit secrets | Always | any edit can leak one |
| Read the schema notes before touching the ORM | Routing row | only ORM work needs it |
| Release steps and rollback | Routing row to a skill or file | only release tasks |

## Routing rows

- The condition is a situation or task the agent can recognise from its
  own work ("Changing a database migration", "A fixture fails to load"),
  never a topic heading.
- The row and the knowledge file's first line name the same situation.
- The table also declares where each kind of fact lives; organise it by
  source of truth, so two rows never point at two copies of one fact.
  [§5.2]

## Validation rows

Name the recipe (`just test`), read from the task runner; never paste the
raw command the recipe runs. When no task runner is agreed, name the plain
command and add the recipe to the pending decisions list.

## Why the budget

Always rules never leave for budget: content behind a pointer loads only
when the pointer's condition fires. The budget exists to force the inline
or route choice for every paragraph (question 4 of the check). [§2.1]

## Readability

Humans review the entrypoint to confirm what agents will do. Write plain
sentences; never compress with private abbreviations or symbols. [§2.1]

## CLAUDE.md

Claude Code expands the `@AGENTS.md` import, so both clients read one
source. A rule moved out of an existing `CLAUDE.md` goes to Always or a
routing row by the task-type test. [§5.2]

## Subdirectory entry files

Recommend none: clients disagree on whether and when they load a
subdirectory file and which file wins, so a rule placed there may never
load. [§2.2] When the user insists (`packages/api/AGENTS.md`), write it
with local orientation only (what the directory holds, its local commands
by recipe name), open it with "The root `AGENTS.md` governs; this file adds
local orientation only.", and put no safety, commit, or publishing rule in
it and nothing that contradicts the root.

## Restructuring an oversized entrypoint

1. Number every line block and classify it: Always, routing row plus file,
   inline, self-described by code (drop), stale (drop), duplicate (keep the
   current copy).
2. Present the classification with the four answers for each new file.
3. Move content only where the user approved; each moved block leaves a
   routing row at the same change.
4. When content moves into an existing architecture document, the row
   names the file and the target heading byte-exactly in inline code
   (`ARCHITECTURE.md`, section `## Data Flow`), so an agent finds it with
   `grep -n '^## Data Flow'`. Renaming that heading breaks the row; say so in
   the report for the layer owning entropy.
