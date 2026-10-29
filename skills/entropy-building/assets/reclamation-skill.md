---
name: harness-reclamation  # CONFIGURE: the skill name the user confirms.
description: >-  # CONFIGURE: the confirmed anchor event and cadence in the trigger sentence.
  Sweeps the agent harness for entropy: stale paths, dead commands,
  contradicted or duplicated rules, unreachable content, triggers that
  cannot fire, and constraints thicker than the project still needs. Use at
  every monthly release before tagging, or when asked to audit, reclaim, or
  clean up the harness.
---

# Harness Reclamation

Runs at every monthly release, before tagging. Last run: never. <!-- # CONFIGURE: the anchor event and cadence the user confirmed; the absolute date of the first sweep (YYYY-MM-DD), "never" only while the user defers it. -->

## Sweep

Walk the entrypoint, every knowledge file, every project skill, and the open
`type:harness-drift` issues: <!-- # CONFIGURE: the confirmed drift label, or `.agents/drift.md` without an issue tracker; while the label is pending write "the open drift issues". -->

1. Run every documented command and open every path and link; fix or
   report what fails.
2. Find rules the code now contradicts.
3. Find the same rule stated in two places; keep one owner.
4. Find content no pointer from the entrypoint reaches.
5. Find triggers whose subject moved or vanished.
6. Find over-thick constraints: what the constraint blocks no longer occurs.

## Dispositions

Every finding gets one: update, reconnect, merge, thin, or delete, with its
evidence. Thin only after the user approves the finding and its evidence;
delete only on current, unambiguous evidence (a path that does not exist, a
command that fails) or the user's approval; otherwise report. A run prompted by repeated agent
failures reports the pattern and a recommendation and edits nothing on that
basis alone.

## Close

Set `Last run:` above to today's absolute date and close the drift issues
the run resolved.

Done when: every finding has an applied or reported disposition with its
evidence and `Last run:` holds today's date.
