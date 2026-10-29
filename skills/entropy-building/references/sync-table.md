# Sync Table

Read when presenting the table-or-skill choice, or writing table rows.

## The choice

Recommend the Keep In Sync table when the concerns fit in about ten rows
and each update is linear (change X, edit document Y): agents reread the
entrypoint every session, so the table needs no trigger to load. Name the
sync project skill as the alternative for a concern that is frequent,
branchy, or spans several artifacts that must be compared and updated
together, because a skill's description fires on that concern's own words.
Decide per concern; the user may mix. One mechanism owns each concern:
a concern a skill owns has no table row. [§5.2]

A table past about ten rows means the project has enough moving parts for
skills; say so instead of growing it.

## Rows

Derive rows from the inventory: the task-runner recipes, the directory
layout, the knowledge index, each mirror pair, each generated file. Each
row states, in one line:

- **the change**, concrete: "a recipe is added, renamed, or removed", never
  "the docs change";
- **the document** and the part of it to update;
- **the check first**: what to run or read before editing that document,
  so the reverse direction is as concrete as the forward one.

A mirror pair's row starts from its confirmed source side: "a section named
in the pair changes in `README.md`" → "the same section of `README.en.md`,
in the same change". An edit made first to the corrected side is copied
back to the source side in the same change, so the source still wins.

## Rules beside the table

- **Standing reverse rule**: before finishing an edit to a harness
  document, run the check of every row naming it and fix or report every
  mismatch found, not only the one that prompted the edit. Editing a
  harness document carries the same verification duty as editing code.
- **Tie-break**: the code or the task runner wins and the document is
  corrected. For a mirror pair of two documents, recommend a source side
  (the original language wins and the translation is corrected), get it
  confirmed, and name it in the row and in the tie-break sentence. A pair
  where the user recorded the opposite ruling is named beside the rule,
  never left implicit.

## Existing mechanisms

A populated table or a sync skill already owning a concern stays: add no
second mechanism for it, do not reopen its choice, and report any
contradiction between it and the inventory for the user to decide. Only
these two count as existing sync mechanisms; a reclamation note or a check
script owns no concern. An empty reserved heading is not an existing
mechanism; fill it.
