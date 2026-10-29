# Harness improvement plan

Goal (user's words): <the text given at invocation, or "audit only">
Decision: <repair | rebuild>, chosen <date>
Kinds of work: <hardening | thinning | carrier migration | platform migration | re-layering>

## Boundaries

| Kind | Changes | Preserved |
| --- | --- | --- |
| <kind> | <what moves> | <task runner, lint configuration, branching habit, ...> |

## Grades

| Layer | Current | Proposed | Variable | Confirmed |
| --- | --- | --- | --- | --- |
| Environment and sandbox | <grade> (observed) | unchanged | - | - |
| Knowledge and routing | <grade> | <grade> | <variable and reason> | <yes, date> |
| Hard boundary | <grade> | unchanged | - | - |
| Authority | <grade> | unchanged | - | - |
| Specification and completion | <grade> | unchanged | - | - |
| Entropy | <grade> | <grade> | <variable and reason> | <yes, date> |

Platform lifecycle: <untouched | rebuilt, not graded>

## Items

Drift items come first; every later item lists them under Depends on.

| # | Layer | File | Action | Finding | Disposition | Source of truth | Verification | Depends on |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | <layer> | <path> | <add / change / delete> | <class: what is wrong> | <disposition> | <file or tool> | <command or read-back> | - |
| 2 | <layer> | <path> | <action> | <finding> | <disposition> | <source> | <verification> | 1 |

## Kept by the user

| Finding | Disposition | Reason given |
| --- | --- | --- |
| <finding> | keep | <what it still catches> |

## Separate decisions

Not authorised by approving this plan; each is asked when reached.

| Item | Action | Decision |
| --- | --- | --- |
| <#> | <push / remote setting / branch deletion / wider permissions> | <pending> |

## Checkpoints

One commit per verified layer, in the project's convention
(<convention observed in history>), no attribution trailer, nothing pushed
without a decision.

## Separate recommended changes

Migrations the audit suggests for the team; nothing above depends on them.

- <change>: <reason and expected cost>
