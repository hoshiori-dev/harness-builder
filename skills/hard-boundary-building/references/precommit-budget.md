# Pre-commit Budget

Read when agreeing the pre-commit budget with the user, when deciding
whether a check goes in the hook, or when an existing hook runs longer than
the budget.

## Why the hook stays fast

The hook runs on every checkpoint commit an agent makes. A slow hook gets
bypassed with `--no-verify`, and the secret scan must never be bypassed: a
squash keeps whatever a draft commit contained, so the scan has to run on
every commit, not only before a release. Heavy verification belongs in CI
and in the task-end recipe. [§4.3]

## Agreeing the budget

Recommend 10 seconds for a typical commit (a handful of staged files),
because that is short enough that neither a person nor an agent is tempted
to skip it. Alternatives: 5 seconds for a tight checkpoint loop; 30 seconds
for a project whose typecheck cannot be scoped and the user wants it local
anyway. Record the agreed number in the knowledge file.

## Placing each check

| Check | Hook | CI | Task-end recipe |
|---|---|---|---|
| Formatter | always, on staged files | yes | yes |
| Secret scan | always, on staged files | yes, on the added commits | yes |
| Lint | when it fits, on staged files | yes | yes |
| Typecheck | when the whole-project run fits | yes | yes |
| Tests | only a suite that fits the budget | yes, the full suite | yes |
| Boundary check | on staged files | yes | yes |

A check that does not fit goes to CI and to the task-end recipe (`just
check`), never into the hook. Tell the user which checks left the hook and
why, in the conversation and in the report.

Whenever tests leave the hook, deliver a scoped fast recipe (one file,
module, or the files changed since the base branch) that returns in
seconds, and route it in the knowledge file so the agent verifies every
small change without waiting for CI. [§4.3]

## Measuring

Time each candidate command in check-only mode on a typical change
(`time ruff check <files>`, `time tsc --noEmit --pretty false`) once the
user agreed; ask for the test-suite duration rather than running a long
suite unasked. After writing the hook, time
`pre-commit run --files <the delivered files>` against the budget and
report the number.

## An existing hook over budget

Propose moving the slow checks to CI and a scoped recipe, with the measured
or reported time as evidence. Change the hook only after the user agrees.
If the user declines, leave the hook as it is and add the move to the
pending decisions list with the recommendation and the time it costs per
commit.
