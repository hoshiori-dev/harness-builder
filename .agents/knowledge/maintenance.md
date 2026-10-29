# Harness Maintenance

Read at the reclamation anchor, when `AGENTS.md` passes 120 lines, or when an
agent reports a mismatch between the harness and the repository.

## Realtime rule

Before editing any harness file (`AGENTS.md`, this knowledge base, a project
skill), inspect the artifacts its `Keep In Sync` row names and fix or report
every mismatch found, not only the one that prompted the edit. `just
harness-check` catches broken links, unknown recipes, unreachable knowledge,
budget overruns, and symlink drift; it cannot catch a stale sentence.

## Periodic reclamation

Anchor: every tenth merged pull request, or quarterly, whichever comes first.
Walk every harness component and hunt:

- stale paths and dead commands: run them, do not trust them;
- rules the code or a client now contradicts (re-run `just clients-validate`
  and `just versions`, update the verification log in `client-matrix.md`);
- the same fact stated twice;
- content unreachable from `AGENTS.md`;
- triggers whose subject moved or vanished;
- thickness no longer earned: a check that never fires, a skill nobody loads,
  a knowledge file no task reads.

Dispose of every finding in the same run: update, reconnect, merge, thin, or
delete. Record the run below.

### Standing items

Walk every row of `.agents/knowledge/compatibility-watch.md`: run its
"Re-check how" column, and when "Resolved when" holds, execute "Then" in one
change and delete the row. Record client and tool versions with
`just versions` in the run below.

### Runs

| Date | Merged PRs since last run | Findings and dispositions |
|---|---|---|
| 2026-10-27 | initial build | none; baseline |
