# Harness Maintenance

Read at the reclamation anchor, when `AGENTS.md` passes 120 lines, when an
agent reports a mismatch between the harness and the repository, or before
editing any harness file.

## Realtime rule

Before editing a harness file (`AGENTS.md`, this knowledge base, a project
skill, a check), inspect the artifacts its `Keep In Sync` row names and fix
or report every mismatch found, not only the one that prompted the edit.
The checks (`just harness-check`, `just skills-check`) catch broken links,
unknown recipes, unreachable knowledge, budget overruns, symlink drift, and
shared-block divergence; they cannot catch a stale sentence. Verify the
other direction too: after editing a rule, confirm the recipe, script, or
directory it describes behaves as written.

## Mismatch reports

An agent that finds the harness contradicting the repository fixes it in the
same change when the fix is small and certain, queues it as a pending
decision when the intent is unclear or the fix exceeds the task, or opens an
issue labelled `type:task` + `area:harness` when it is large and deferred.
Saying it in the conversation alone is not an outcome.

## Periodic reclamation

Anchor: every tenth merged pull request, or quarterly, whichever comes first.
Walk every harness component and hunt:

- stale paths and dead commands: run them, do not trust them;
- rules the code or a client now contradicts (re-run `just clients-validate`
  and `just versions`, update the verification log in `client-matrix.md`);
- the same fact stated twice;
- content unreachable from `AGENTS.md`;
- a `[§x.y]` tag in a skill whose section in the methodology document moved
  or changed meaning;
- **thickness no longer earned**: a check that never fires, a shared block
  one skill uses, a knowledge file no task reads, a rule written for a
  problem long fixed. Thinning is as much reclamation as fixing.

Dispose of every finding in the same run: update, reconnect, merge, thin, or
delete. Record the run below.

### Standing items

Walk every row of `.agents/knowledge/compatibility-watch.md`: run its
"Re-check how" column, and when "Resolved when" holds, execute "Then" in one
change and delete the row. Record client and tool versions with
`just versions`. Re-read the Zensical language page (`docs-site.md`).

### Runs

| Date | Merged PRs since last run | Findings and dispositions |
|---|---|---|
| 2026-10-29 | initial build | none; baseline |
