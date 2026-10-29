# Reclamation

Read when installing or filling the periodic reclamation routine, or when
the project is long-lived but graded below thick.

Sync rules catch drift at edit time; reclamation catches what nobody
edited. It is part of the thick grade. When a project is long-lived but
its confirmed grade is medium, recommend raising the entropy grade to
thick, ask, and install nothing until the user confirms. [§6.1]

## What the routine carries

- **The hunt**: stale or dead content (run the commands, open the paths),
  rules the code contradicts, duplicated rules, content unreachable from
  the entrypoint, triggers that cannot fire, over-thick constraints, and
  the drift issues or drift file the correction-report rule fills.
- **The thinning signal**: "what this constraint blocks no longer occurs".
  A lint rule for a bug fixed long ago that has blocked nothing since is
  reported with the disposition "thin" and the evidence (rule, history,
  zero hits), and removed only after the user approves. Over-thickness
  never fails loudly; it makes agents slower and more cautious, so it is
  hunted on purpose. [§6.2]
- **Dispositions**: update, reconnect, merge, thin, or delete, one per
  finding with its evidence. Thinning needs the user's approval of the
  finding and its evidence; deletion needs current, unambiguous evidence
  (a path that does not exist, a command that fails) or the user's
  approval.
- **Cadence anchored to a team rhythm**: a release, a retro, a sprint end.
  Monthly for fast-moving projects, quarterly for slower ones; the anchor
  gives the routine a trigger instead of an intention.
- **`Last run:`** with an absolute date. The installation runs the first
  sweep and sets it to that day; "never" stays only when the user defers
  that sweep, recorded as a pending decision.

## Form

Recommend a dated section in a knowledge file the entrypoint routes to
([the section shape](../assets/reclamation-section.md)), because the sweep
is a linear checklist. Offer a project skill
([the skill shape](../assets/reclamation-skill.md)) when the harness has
many skills or the sweep branches by component; hand that shape to the
skill that writes project skills with the hunt, thinning signal, cadence,
`Last run:`, and dispositions filled in, and do not finish it yourself.

## Failure-prompted cleanup

When repeated agent failures on one instruction prompt a run, the routine
reports the failure pattern and a recommendation and makes no automatic
edit to knowledge: a harness that rewrites itself from failure history
needs controls (review gates, rollback, audit trail) this harness does not
have.
