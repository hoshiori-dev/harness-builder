## Keep In Sync

When harness content here, in `.agents/knowledge/`, or in a project skill
contradicts the code, deal with it in the same task. A report only in the
conversation does not count: it vanishes with the session and the next
agent hits the same contradiction. <!-- # CONFIGURE: name the project's own knowledge directory and skill directory. -->

- **Fix it** in the same change when the deviation is small and you are
  sure of the correct state (a renamed path, a changed flag); say so in the
  commit message.
- **Add it to the pending decisions list** when the intended state is
  unclear or the fix is outside the current task's authority.
- **Open an issue** labelled `type:harness-drift` when the deviation is
  large and not handled now. <!-- # CONFIGURE: the confirmed drift label; without an issue tracker write "Add an entry to `.agents/drift.md`" instead; while the label is a pending decision write "Open an issue" with no label. -->

When two places disagree, the code and the `justfile` win over the document
that describes them: correct the document. In the mirror pair `README.md` /
`README.en.md`, `README.md` wins: correct `README.en.md`. <!-- # CONFIGURE: the task runner's file; each mirror pair with its confirmed source side first; append each pair for which the user recorded the opposite ruling. -->

Before finishing an edit to any harness document, run the "Check first"
cell of every row naming that document, and fix or report every mismatch
found there, not only the one that prompted the edit.

| When this changes | Update | Check first when editing that document |
|---|---|---|
| a `justfile` recipe is added, renamed, or removed | the commands section of this file | `just --summary`; run each recipe the section names and compare its behaviour with the description |
| a top-level directory is added, moved, or removed | the layout section of `ARCHITECTURE.md` | list the directories the section names |
| a file under `.agents/knowledge/` is added, moved, or removed | the when-to-read table of this file | every listed path exists |
| a section named in the mirror pair changes in `README.md` (an edit made first in `README.en.md` is copied back to `README.md`) | the same section of `README.en.md`, in the same change | `just harness-check`; compare the section's links, code, and tables in both files | <!-- # CONFIGURE: one row per mirror pair, its source side in the first cell and the corrected side in the second. -->

<!-- # CONFIGURE: one row per concern from the inventory that the table owns; delete rows that do not apply; a concern owned by a sync project skill gets no row. -->
