# Greenfield Projects

Read when step 1 classified the project as greenfield: no build or test
command, no CI, no hooks, a handful of commits, nothing that shows a habit.

## Report

State the classification, list the little that was observed (README,
license, commit count, language of any source file), and say plainly that
nothing needs preserving. Then ask only what the repository cannot answer:
the goal (step 2), the five variables (step 3), and the intended stack when
no source file shows it.

## What changes when nothing exists

- **The harness sets the first conventions.** With no task runner, commit
  style, or check set to keep, every choice in step 5 comes from its
  recommendation, still confirmed by the user one decision at a time.
- **Commands do not exist yet.** The knowledge and routing checkpoint
  documents only commands that already exist; the hard-boundary checkpoint
  adds each validation command it creates to the entrypoint, so no
  committed entrypoint names a missing command.
- **Start thin.** A first harness is a root entrypoint, the always-applies
  rules, and the few checks the grades call for. Thickness grows with the
  friction agents actually hit; a layer the variables do not demand stays
  omitted or light. [§6.3]
- **Specifications start with the first change.** Recommend the
  specification carrier for the work about to begin, not a back-fill of
  documents for code that does not exist.

Done when: the report lists every observed fact and states that nothing
needs preserving, and every question asked is one the repository cannot
answer.
