# Agent Authority Policy

Read before marking work ready, requesting review, approving, merging,
releasing, or changing a remote setting, and whenever unsure whether an action
is yours to take.

Level: H1 (agents prepare and admit to review, humans integrate), set by the
repository owner on 2026-10-27, raised from H0 the same day. A repository
created from this template keeps H1 until its owner edits this file.

## What agents may do

Take issues; propose OpenSpec changes; implement; run `just check` and
`just clients-validate`; create and update draft pull requests; self-review
the finished change (below) and, when it passes, mark the draft ready and
request the maintainer's review; fix review findings; archive a change on the
branch after the maintainer approved it; prepare release notes.

## What agents may not do without a human

Approve; merge; push tags; create or edit releases; change labels on the gate
(`spec: approved`); change remote settings; move or weaken any gate in this
file or in the checks.

## Self-review before ready

Ready means the pull request is worth a human reviewer's time, not that it is
perfect. With `just check` green and the checklist ticked, read the whole diff
once against the issue and the spec and ask:

- Does it do what the issue and the spec ask, all of it and nothing else?
- Is anything wrong: a bug, a false statement in a document, a check or a
  generated file edited by hand, a secret or private data in the diff?
- Would the maintainer have to ask a question the PR body could answer?

Act on a finding only when it changes correctness, scope, or reviewability.
Do not reopen style, naming, or structure that the checks accept, and do not
refactor adjacent code; such thoughts become at most an optional follow-up
note in the PR. One pass, then `gh pr ready`: the maintainer's review is the
second pair of eyes, not a second self-review.

## Handoff to the reviewer

Marking ready is not yet a handoff. After `gh pr ready`, the agent posts one
comment on the PR headed `Ready for review` that names what changed, what the
self-review changed, and where to start reading, and reports the same in the
session. CODEOWNERS requests a review from every listed owner except the PR
author, so when the agent works through the maintainer's own account nobody
is requested automatically: the comment and the session report are the
handoff, and the maintainer's queue is
`gh pr list --search "is:open draft:false review:none"`. A repository with a
second maintainer lists that account in `.github/CODEOWNERS`, which makes the
request automatic.

## Gates

| Gate | Meaning | Owner |
|---|---|---|
| Proposal approval | the maintainer closes the proposal discussion on the PR and adds `spec: approved`; the `pr-labels` workflow records the approved commit | maintainer |
| Review admission | the self-review above passes; the draft becomes ready and the maintainer's review is requested | agent (the implementer) |
| Integration | squash merge into `main` | maintainer |
| Release | tag `vX.Y.Z` pushed | maintainer |

The `pr-labels` workflow accepts `spec: approved` only from an account with
write permission, records the approved commit, and withdraws the label when the
change is edited afterwards. It cannot tell the maintainer from an agent
working through the maintainer's account: that line is this policy, not the
script. An agent never adds `spec: approved`.

## Escalation: stop and hand to a human when

- the change needs a file outside the issue's scope, or touches a check,
  hook, workflow, or this policy;
- acceptance criteria cannot be judged from the spec and the issue;
- a required check is unavailable or flaky;
- a client behaves differently from `.agents/knowledge/client-matrix.md`;
- there is no rollback path (anything published outside the repository).

No self-escalation: an agent never raises its own level or waives a gate; a
change to this file is itself a gated change.
