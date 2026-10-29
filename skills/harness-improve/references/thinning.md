# Thinning

Read when the agreed work includes thinning, or when a finding is classified
excessive. Over-thickness is quieter entropy than staleness: it never
fails, it only makes agents slower, more conservative, and spend output on
passing gates. The trigger is "what this constraint catches no longer
occurs". [§6.2]

## Candidates

- A lint rule or custom check for a long-fixed historical problem.
- A skill written for a one-off migration that has finished.
- A routing entry for a module that was removed.
- A gate thicker than the layer's confirmed grade (an architecture check
  at a medium-graded hard boundary; a full test suite in pre-commit that
  belongs in CI).
- Entrypoint content loaded every session that applies to rare tasks:
  move it behind a conditional route instead of deleting it.

## Evidence per removal

Every removal names three things in the plan:

1. **Constraint**: the file and line (rule id, skill, route, hook).
2. **What it caught**: the problem it was written for, from its comment,
   commit message, or linked issue.
3. **Evidence it no longer occurs**: the removed module or API (search
   shows no remaining use), the finished migration, a check whose last
   failure is outside recent history, or a rule duplicated by a stronger
   one.

No evidence, no removal: the item becomes a question to the user. A
constraint that still catches something, or that the user kept, stays.

## Boundary

Changes: the named constraints and the routes and sync entries that
mention them. Preserved: every constraint without evidence, every
constraint the user kept, and the grade of each untouched layer. Re-grade
each layer a removal moves (for example the hard-boundary layer from thick
to medium when architecture checks leave CI) and get the user's
confirmation.
