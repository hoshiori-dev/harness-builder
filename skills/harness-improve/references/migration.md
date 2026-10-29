# Migration

Read when the agreed work moves the project to another spec carrier
(OpenSpec, Spec-Kit, a lightweight `SPEC.md` and `PLAN.md` format) or to
another code-hosting platform (GitHub, GitLab). A migration enters the plan
only when the user asked for it or accepted it. [§6.3]

## Carrier migration

Owned by the specification and completion layer, which hands the carrier
work to the carrier skill for the new format (the carrier skill for
OpenSpec, for Spec-Kit, or for the lightweight format).

1. **Freeze in-flight work.** List every open change or feature in the old
   carrier. Each is finished and archived in the old carrier, or frozen as
   it is and recorded; none is translated half-done.
2. **Sort the specs.** For each existing spec, state one of: moves (it
   covers code that is still changing; translate it into the new carrier's
   format), deleted (it covers code nobody is changing; the code describes
   itself, and an unmaintained spec rots), or fixed first (it contradicts
   the code; the drift item precedes the move).
3. **Swap the automation last.** Remove the old carrier's checks, labels,
   and CI jobs and install the new carrier's only after the user approves
   that item; the CI change and every label or remote setting is a remote
   write with its own approval.
4. **Repoint the harness.** The entrypoint route, the spec workflow
   knowledge file, request templates, and the self-check's strict-validation
   step name the new carrier; the old paths leave every file.

Boundary: changes the spec directory, the carrier's automation, and the
pointers to it. Preserves the completion rules, the approval mode, and
every spec judged to move (in meaning, not format).

## Platform migration

Owned by the platform lifecycle layer; no graded layer changes unless the
plan says so, and the report states that the platform lifecycle layer is
rebuilt without a grade.

The plan lists what to recreate, each with its source and its target:

| Entity | Source | Target |
| --- | --- | --- |
| Labels | label definitions or the platform's list | label file plus a dry-run sync |
| Templates | issue and pull or merge request templates | the target platform's template paths |
| Workflows | CI files | the target platform's CI syntax, same recipes |
| Settings | branch protection, merge method, required checks | a settings record the user applies or approves |
| Platform knowledge | the knowledge file and project skill for the platform | rewritten for the target platform |

Every remote write (creating labels, changing settings, enabling required
checks, archiving the old project) is marked as needing its own approval
and is shown as a dry run first. Settings only an administrator can change
go into the closing report as manual actions.

Boundary: changes platform files and platform knowledge. Preserves the
task-runner recipes CI calls, the branch model unless the user changes it,
and the commit convention.
