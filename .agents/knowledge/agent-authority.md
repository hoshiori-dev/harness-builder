# Agent Authority Policy

Read before pushing, marking a pull request ready, posting a comment, adding
or removing a label, releasing, or changing a remote setting, when an action
is refused, and whenever unsure whether an action is yours to take.

Set by the repository owner on 2026-10-29. The sandbox decides what an agent
*can* do; this file decides what it *may* do. The two are independent, and
this file is the narrower one.

## Reversibility is the key

Classify every action before taking it:

- **Reversible and internal** (edit files, create a branch, run checks,
  commit locally, create a worktree): do it, no question asked.
- **Irreversible or outward** (push, mark ready, comment, label, close,
  release, change a remote setting, delete anything the user wrote): take it
  only when the plan or the task's pre-authorised list names it; otherwise
  queue it as a pending decision and continue with the rest.

Local commits can be rewritten; pushed commits cannot be erased from GitHub
(unreachable objects stay addressable), so the two are not the same class.

## Approval at both ends, not per command

Approval happens when a plan is agreed and when the work is handed over, not
on each command. A plan approval covers the result and the bounds of the
approach, never a list of steps. When a step is blocked on a decision only a
human can make, do the parts that do not depend on it and add the item to the
pending decisions list: what is blocked and why, the options, the recommended
option with its reason, and which finished work each option would change.
Present the list once, when nothing else can proceed or at the end.

Pre-authorised in every change here, once the plan or the issue says so: push
to the issue branch, open and update the draft pull request, mark it ready
after the self-review below, post the `Ready for review` comment. Never
pre-authorised: approving, merging, adding `spec:approved`, tagging, creating
or editing a release, changing a remote setting, force-pushing, pushing to
another agent's branch.

## A refusal is a decision

When a command, hook, or permission refuses an action, read the refusal as
one of three things and act accordingly: the approach is in the wrong place
(go back to the plan and choose another approach); a policy boundary was
reached (record it as a pending decision); or a check found a defect (fix the
defect). Never route around a refusal with an equivalent command, a script,
or a loosened rule.

## Permission lists

Framework permission lists (`.claude/settings.json` and its equivalents) name
what is known safe and what is known dangerous and leave the rest to the
framework's default. They carry no "ask" entries: a prompt on every command
exhausts the reviewer and protects nothing. The deny list guards against a
careless collaborator, not an attacker; an agent that can run code can bypass
it, which is why the sandbox and the scoped tokens are the real boundary.

## Self-review before ready

Ready means the pull request is worth a human reviewer's time. With
`just check` green and the checklist ticked, read the whole diff once against
the issue and the spec and ask: does it do all of what was asked and nothing
else; is anything wrong (a bug, a false sentence, a hand-edited generated
file, a loosened check, a secret); would the maintainer have to ask a
question the body could answer? Act only on findings that change correctness,
scope, or reviewability. One pass, then `gh pr ready`.

## Handoff

After `gh pr ready`, post one comment headed `Ready for review` naming what
changed, what the self-review changed, where to start reading, and the
behavioural test results when a skill changed, and report the same in the
session. CODEOWNERS requests every listed owner except the author, so when
the agent works through the maintainer's own account the comment is the
request.

## Gates

| Gate | Meaning | Owner |
|---|---|---|
| Proposal approval | the maintainer closes the proposal discussion on the PR and adds `spec:approved`; the `pr-labels` workflow records the approved commit | maintainer |
| Review admission | the self-review passes; the draft becomes ready | agent |
| Integration | squash merge into `main` | maintainer |
| Release | tag `vX.Y.Z` pushed | maintainer |

The `pr-labels` workflow accepts `spec:approved` only from an account with
write permission and withdraws it when the approved package changes. It
cannot tell the maintainer from an agent working through the maintainer's
account: that line is this policy. An agent never adds `spec:approved`.

## Pairing mode

The initial build of this repository and any later session the maintainer
runs side by side with the agent are pairing mode: approvals happen in the
conversation, and the pending decisions list is short because the human is
present. Pairing mode changes who answers, not what needs an answer.

## This file protects itself

Loosening this policy, a check, a hook, a workflow, or a permission list is
outside every agent's authority, including when it would unblock the current
task. Propose the change in the pull request and wait.
