# Auditing an Existing Harness

Read when asked what an existing harness gets wrong, before judging any
file. An audit reads and reports; it changes nothing. Read
[methodology-map.md](methodology-map.md) when the audit ends, for the
improvement entry to name in the closing.

## Sequence

1. Inventory every agent-visible artifact: entrypoints (root and
   subdirectory), knowledge and reference files, project skills, scripts,
   task-runner recipes, checks and CI configuration, framework
   configuration (permissions, hooks, rules) [§6.3].
2. Run the project's own harness self-check when one exists (a
   `check_harness.py`, or a task-runner recipe that runs one) and quote its
   output. Manual findings add only what the output does not cover; do not
   re-derive what the check already reports [§5.3].
3. For each artifact record: how a future agent finds it (the routing line
   or pointer that reaches it), when it loads, what its source of truth is,
   and what keeps it current. No path to it means invisible; no source of
   truth usually means drifted [§2.1] [§5.2].
4. Compare the harness with the current project by following the
   entrypoint's pointers the way an agent would: paths exist, commands
   exist as recipes, interfaces match, validation runs as documented. Use
   git history only to tell current conventions from abandoned ones
   [§5.3] [§6.3].
5. Classify each gap and propose one fix.

## Gap classes

- **Stale**: describes a path, command, or structure that no longer exists.
- **Duplicated**: one fact in two places, still agreeing.
- **Contradictory**: one fact in two places, disagreeing; the fix names the
  source and the adjudication rule as
  [source-of-truth.md](source-of-truth.md) defines them; read it when
  classifying the first such finding [§5.2].
- **Invisible**: no entrypoint or routing line reaches it; the fix is the
  routing line or the deletion [§2.3].
- **Missing**: a layer the five variables call for has nothing; the absent
  self-check is a missing finding for the entropy layer whenever an
  entrypoint and knowledge files exist [§5.3] [§6.1].
- **Excessive**: a constraint, lint rule, skill, or routing entry for a
  problem the project no longer has; the fix is removal, because an unused
  constraint only slows the agent [§6.2].

## Finding format

One line per finding: `<file>: <gap class>, <what is wrong>. Fix: <action>.`
Group by layer. End with the resulting entrypoint line count against the
100-line target when the entrypoint is among the files [§2.1].

## Checks that are always made

- Every knowledge file has a reachable load condition [§2.3].
- The entrypoint keeps always-applicable constraints first and within
  budget [§2.1].
- No document restates a fact code states (directory listings, command
  flags) [§1.3].
- Every sync rule passes the trigger test in source-of-truth.md "Forward
  and reverse triggers" [§5.2].
- A self-check exists, runs, and its failure messages name the fix [§5.3].
- Subdirectory entrypoints pass the defensive rule in loading-modes.md;
  read [loading-modes.md](loading-modes.md) when the harness has one
  [§2.2].
- No project check calls a script inside a skill directory [§5.3].

## Decision rules for the proposed fix

Update (needed but wrong), reconnect (correct but unreachable: add the
routing line), move (loaded too often for how rarely it applies: push
behind a narrower pointer), merge (two files always read together), split
(one file loads every run but only part is always needed; prefer merging
over splitting), thin (valid but overweight), remove (obsolete, duplicated,
or for a problem that is gone), leave (accurate, reachable, proportionate).
Ask before proposing removal of anything that looks maintained.

## When there is nothing to audit

A repository with no entrypoint, no knowledge files, and no agent
configuration has no harness. Report that, state what the code already
describes on its own (layout from the file system, commands from the task
runner, interfaces from types) [§1.3], and point the user to the creation
entry instead of inventing findings.

## Closing

End with the handoff wording in methodology-map.md, naming the improvement
entry.
