## Harness Reclamation

Run at every monthly release, before tagging. Last run: never. <!-- # CONFIGURE: the anchor event and cadence the user confirmed; the absolute date of the first sweep (YYYY-MM-DD), "never" only while the user defers it. -->

Walk the entrypoint, every knowledge file, every project skill, and the open
`type:harness-drift` issues, and hunt: <!-- # CONFIGURE: the drift label, or `.agents/drift.md` without an issue tracker. -->

1. Stale or dead content: run every documented command, open every path and
   link; do not trust them.
2. Rules the code now contradicts.
3. The same rule stated in two places; keep one owner, point the others.
4. Content no pointer from the entrypoint reaches.
5. Triggers that can no longer fire: a skill or row whose subject moved or
   vanished.
6. Over-thick constraints. The thinning signal is "what this constraint
   blocks no longer occurs": a lint rule for a long-fixed bug that has
   blocked nothing since, a skill for a finished migration, a route to a
   retired module.

Give every finding one disposition: update, reconnect, merge, thin, or
delete, with its evidence. Thin only after the user approves the finding and
its evidence; delete only on current, unambiguous evidence (a path that does
not exist, a command that fails) or the user's approval; otherwise report
it. When repeated
agent failures on one instruction prompted the run, report the pattern and a
recommendation and edit nothing on that basis alone.

Close the run by updating `Last run:` to today's absolute date and closing
the drift issues it resolved.
