# Adoption Decision

Read when the user asks whether or at which level to adopt spec-driven
development. This skill recommends; the user decides; the
skill that owns the specification and completion layer records the choice
as a project rule.

## Levels

| Level | The specification is… | Obligation after the change ships |
|---|---|---|
| spec-first | written before the change and used to build it | none; it is archived, folded, or deleted |
| spec-anchored | the living description of the behaviour | every behaviour change updates it first |
| spec-as-source | the only file people edit; code is regenerated | nobody patches code by hand |

Recommend **spec-anchored** when the project is maintained past one release
(observable: tagged releases spanning more than one release cycle, a stated
support horizon, a published library), and **spec-first** otherwise. Do not
recommend spec-as-source: it holds only where a toolchain regenerates code
reliably, and the user must bring that evidence.

Name the selecting fact and the alternative in one sentence each, for
example: "Spec-first at the lightest carrier, because the prototype is
thrown away in two weeks; spec-anchored is the alternative if it survives
that window." Then wait for the user's choice.

## Never "not worth it"

Never answer that specifications are not worth it. The cost scales with the
carrier, not with the discipline: a short-lived prototype gets spec-first in
plan mode, where the specification is a few lines approved in the
conversation. What it buys at any size is a stated acceptance and a list of
non-goals before code anchors the approach. [§4.1]

## Carrier

This skill names only the carrier for the current change: the spec tool in
use, else the lightweight carrier. Asked which spec tool the project should
adopt or switch to, describe the skill that owns the specification and
completion layer as the one that makes that choice; recommend no tool here.

## Recording the choice

When the user agrees, describe the skill that owns the specification and
completion layer as the one that records the level and carrier in the
project's contract; edit no project knowledge file from this skill. When the
user chooses a level but declines to record it, run the current change at
the chosen level and add the unrecorded rule to the pending decisions list:
what stays unrecorded, the options (record it now, record it later, leave it
per change), the recommendation (record it, so the next session does not
ask again), and which finished work each option changes (none).

## Rejected alternatives

- **Approving the specification alone, design as an implementation
  draft**: keeps the gate small but gives the reviewer no say over the
  approach. A bounded design in the package trades a little implementation
  freedom for control, and still excludes steps.
- **Always requiring a design**: a wording change would carry a design that
  says nothing.
- **Labels or issue states as the specification's lifecycle**: the record
  lives in the repository; a status label is a fact derived from it.
