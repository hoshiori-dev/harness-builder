# Choosing the Carrier

Read when presenting the carrier question and its alternatives, when the
carrier already in use does not fit the project's shape, when the user asks
to change carriers, or when the project keeps a framework that is neither
OpenSpec, Spec-Kit, nor hand-written per-change documents.

The carrier is where an approved goal and its scenarios live while a change
is built. The form matters less than the alignment it forces before code is
written: a large engineered project can carry a framework, a small feature a
`SPEC.md` or `PLAN.md`, a one-file script change a plan agreed in plan
mode. [§4.1]

## The order

Apply in order; the first match is the one recommendation.

| # | Fact observed or recorded | Recommend | Reason to give |
|---|---|---|---|
| 1 | A carrier is already in use (the inventory lists it) | Keep it; ask nothing | Migration costs more than any fit gained; changes in flight live in it |
| 2 | One maintainer, small repository, with or without code | Lightweight: per-change `SPEC.md`/`PLAN.md` committed with the change, or plan mode for a one-file change | Approval happens in conversation; a framework adds files nobody else reads |
| 3 | Existing code | OpenSpec | Its living per-capability specs describe an existing system and change by deltas |
| 4 | No code yet, an application delivered feature by feature | Spec-Kit | Its numbered feature specs follow how the product ships |

No row matches (no code yet, a library or infrastructure project, a team):
recommend OpenSpec, because a library's contract is per capability, not per
feature.

Cite the matching row's fact as the reason: "existing code", "solo small
project", "already in use".

## Alternatives, one sentence each

- **OpenSpec**: changes carry a proposal, delta specs, design, and tasks, and
  merge into living specs on archive; fits existing code and libraries.
- **Spec-Kit**: each feature gets a numbered directory with spec, plan, and
  tasks; fits an application built feature by feature.
- **Lightweight**: a committed `SPEC.md`/`PLAN.md` per change, or plan mode
  for the smallest changes; fits a solo maintainer who approves in
  conversation.

Present only the ones not recommended.

## A kept carrier that does not fit

When the carrier in use mismatches the project's shape (Spec-Kit in a
library, a framework in a solo script collection), keep it, state the
mismatch in one sentence with its consequence, and offer a migration as a
separate change the user may decline. Never fold a migration into this
build: in-flight changes would move under an unapproved layout.

## A framework none of the three

Kiro specs, an IDE's native spec files, or a custom layout the user keeps
have no carrier skill here. Record in the contract:

- the implementer as the executor of every gate (approval noted in the
  conversation or on the request, freeze done by hand);
- the structural check the project adopts for its specs, or "none" with the
  gap named to the layer owning hard boundaries;
- the framework's automation (status labels, archive check) as remaining
  work in the report.

Hand off nothing.

## Every framework declined

A user who refuses every framework and keeps hand-written per-change
documents has chosen the lightweight carrier. Record it as that and hand off
to the skill that owns per-change `SPEC.md`/`PLAN.md` and plan-mode
alignment. Install nothing.
