# Sync Skill

Read when the user chooses a sync project skill for a concern.

One skill per concern: a "sync everything" skill has no precise trigger and
loads for nothing. Before handing over, settle with the user:

- **the concern**: one document (or document part) and the artifacts it
  describes, with the source of truth that wins;
- **the forward trigger**: the concrete changes that oblige an update, in
  the words a session would contain ("a recipe is added, renamed, or
  removed"), plus the reverse phrasing "when asked to edit <document>";
- **the reverse checks**: what to run or read before editing the document,
  and the duty to fix or report every mismatch found;
- **the completion criterion**: what verified looks like (named recipes
  exist and behave as described, paths resolve, the self-check is clean).

Rework [the sync skill shape](../assets/sync-skill.md) with these facts and
hand it to the skill that writes project skills, saying: "the project needs
a project skill that keeps <document> true to <artifacts>; here is the
starting shape with its concern, triggers, checks, and completion
criterion." That skill writes, lints, and tests it; this one does not.

Then delete the concern's row from the Keep In Sync table. A one-line
pointer in the keep-in-sync section ("the commands section is kept in sync
by the project skill `sync-commands`") is allowed; a second copy of its
triggers or checks is not.

When a concern's document lives outside the repository (a wiki page, a
tracker document), the reverse checks carry the weight: that content does
not version with the code, so every touch inspects it.
