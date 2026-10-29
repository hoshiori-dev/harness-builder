# The Completion Boundary

Read when writing the completion section of the contract, when the user
asks what a spec must contain, or when a recorded spec format leaves one of
the eight items below out.

Without a finish line an agent ends one of two ways: it stops early, taking
"the tests ran" for "done", or it keeps adding. Whatever the carrier, every
spec answers four questions and obeys four rules. The contract lists all
eight so a reader who never saw this skill can name them. [§4.1]

## Four answers every spec gives

1. **How done is judged**: acceptance scenarios or a final check command the
   agent runs itself, never one only a person can run. Task-level finish
   conditions belong here too, such as "no draft commit left on the branch".
2. **What is not done**: the non-goals. They curb scope creep better than
   goals do, because a model tends to add "one more thing".
3. **What is delivered**: a pull request, a report, a deployment, and the
   pending decisions list for everything that waited on the user.
4. **Which irreversible actions are pre-authorised**: which branch may be
   pushed, whether a comment may be posted, whether a pull request may be
   opened. Without this answer the agent halts at the first such action.
   The layer owning authority defines how such an action is classified; the
   spec only lists the ones this change may take.

## Four quality rules

- **Judgeable scenarios.** Every goal has at least one scenario that a
  reader who never saw the code can judge. Across the whole spec, at least
  one scenario covers a failure or edge path: one per spec, not one per goal.
- **Non-goals written.** An exclusion not written down is a future dispute.
- **Behaviour, not diff.** "A duplicate email returns 409" is a goal; "add a
  unique index" is implementation. An implementation written into a goal
  anchors the agent on that implementation.
- **Verified against run results.** Scenarios are executed; reading the diff
  and finding it plausible is not verification.

The more checkable the finish, the more precisely the pre-authorised
actions can be written: how far the work goes and how far it may go are the
same question. [§4.1]

## Per carrier

- **OpenSpec, Spec-Kit**: the tool's own files carry the scenarios and
  tasks; the contract states which file answers each of the four and adds
  the rules the tool does not enforce (usually the failure-path scenario,
  pre-authorised actions, and delivery).
- **Lightweight** (per-change `SPEC.md`/`PLAN.md`, plan mode): the contract
  lists the five headings every per-change spec or plan carries, each with
  the answers and rules it holds, so all eight items appear. Rename the
  headings in the project's terms; keep the mapping:

  | Heading | Holds |
  |---|---|
  | `## Done when` | Answer 1; rule "verified against run results" |
  | `## Not doing` | Answer 2; rule "non-goals written" |
  | `## Delivers` | Answer 3 |
  | `## Pre-authorised` | Answer 4 |
  | `## Scenarios` | Rules "judgeable scenarios" (one failure or edge path per spec) and "behaviour, not diff" |

  It refers to no template file; the headings are the format. A plan agreed
  in plan mode states the same four answers in the conversation before work
  starts.
- **Other framework kept**: the same as the lightweight list, mapped onto
  the framework's files where they exist.
