# Failure modes: diagnose an existing skill

Read when improving, reviewing, pruning, or diagnosing any existing skill.
Start from the observed symptom, confirm the cause in the skill's text, apply
the smallest general fix, then run the pruning passes, the linter, and the
tests.

## Symptom index

| Observed symptom | Cause | Fix |
|---|---|---|
| Never loads, or only when named | Description lacks the words users say | Rewrite triggers from real prompts; add indirect phrasings |
| Loads on unrelated tasks | Description claims territory it does not own | One trigger per branch; sharpen the capability clause; add the neighbour to "Not for" |
| Two skills both load | Overlapping descriptions | Re-cut the boundary or merge |
| Quits a step early, skips verification, rushes to the end | Premature completion: missing or vague `Done when:` | Sharpen the criterion; hide later steps only as a last resort |
| Shallow work inside a step (reads one file where a sweep was due) | Thin legwork: no demand in the criterion | Make the criterion exhaustive or plant a stronger word |
| Never opens a reference it needed | Weak pointer wording | State the precise condition; inline only if that fails |
| Behaves differently run to run on the same task | Any of the above | Work the whole index |
| Hard to edit; instructions contradict | Duplication or sediment | Single source of truth; relevance pass |
| Long, every line legitimate | Sprawl | Disclose, then split by branch or sequence |
| A sentence visibly changes nothing | No-op | Delete it whole |

## Wrong or missing triggers

The description is the only text read before activation, so a trigger
failure is a description failure. The body changes only by what the pruning
passes remove. Read `description.md` in this directory when rewriting the
description to fix a trigger failure.

## Premature completion

Ending a step before it is done because attention slipped to being done.
Needs steps to occur; a step-less skill that quits early is thin legwork.

Confirm: find the rushed step and read its boundary. If a criterion exists
but a reader cannot tell done from not done, neither could the agent.

Fix, in this order:

1. Add or sharpen the completion criterion: replace "understanding reached"
   with "every call site listed with file and line". Where thoroughness
   matters, make it exhaustive.
2. Hide the later steps, only when the criterion is irreducibly fuzzy and
   the rush was observed: split the sequence so the tempting steps live in a
   second skill or a subagent dispatch. Hiding works only across a real
   context boundary; an inline call clears nothing.

## Thin legwork

The step runs to completion but the work inside it is shallow. Raise the
demand: make the criterion exhaustive ("every rule applied to every changed
file") or plant a stronger leading word (_exhaustive_, _relentless_) where
the work is specified. Not an extra paragraph.

## Never-loaded references

Confirm the pointer states a condition the run actually met. Read
`hierarchy.md` in this directory when rewording the pointer or deciding
whether to inline the material.

## Duplication, sediment, no-op

Duplication is one meaning in more than one place; sediment is stale layers
that settle because adding feels safe and removing feels risky; a no-op is a
line the floor-tier model already obeys. Each is fixed by its pruning pass
(deduplicate, relevance, no-op hunt). Read `pruning.md` in this directory
when running that pass.

## Sprawl

Too long even when every line is live and unique. In order of preference:
disclose branch-specific reference behind conditional pointers; split by
branch when two invocation cases share little; split by sequence at the point
where the remaining steps can run in a fresh context.

## Review checklist

Apply every item; report each as pass or fail with the offending line.

- Description: third person, leading word first, one trigger per branch,
  indirect phrasings covered, "Not for" present, no body identity restated.
- Invocation mode matches use; a host-specific switch is noted in the body.
- Steps with a meaningful boundary carry a checkable `Done when:`; exhaustive
  where thoroughness matters; absent where it would change nothing.
- Every reference pointer states a precise condition.
- Inline content is needed by every branch; branch-specific content is
  disclosed.
- Each concept's definition, rules, and caveats sit together.
- Every asset is fixed or stable-pattern material the agent copies; none
  wraps its payload in how-to-use prose.
- No meaning has two homes; no sentence fails the no-op test; no stale line.
- Linter exits 0; every warning has a stated reason.
