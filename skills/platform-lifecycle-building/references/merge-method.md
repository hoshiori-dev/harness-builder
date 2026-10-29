# Merge Methods

Read when asking which merge methods the repository allows, or when the
user allows more than one.

## The question

Ask every time; the probe shows what is allowed now, never what should be:

> Which merge methods may a pull (merge) request use: squash, rebase,
> merge commit? And what rule decides which one a given change uses?
> I recommend squash only.

Reason for squash only: task-level commits on the branch serve review and
bisection while the request is open, and the default branch receives one
commit per request, whose message is the request title, so the history
reads as a list of changes and every commit on it passed the checks.
Alternatives, a sentence each: rebase keeps every task commit on the default
branch, worth it only when each commit is self-contained and passes on its
own; merge commits keep the branch topology, worth it only for long-lived
branches merged as a unit (environment or release branches).

## Squash only accepted

- Remote: disable merge commits and rebase merging, enable squash, delete
  the branch on merge. Squash commit message: the request title (and body
  on GitHub). Commands are in `github.md` and `gitlab.md`.
- Knowledge (`<platform>-workflow.md`, "Branches and merging"): "Squash
  only: the pull request title becomes the commit on the default branch,
  so it follows the project's commit convention." Name the convention when
  the repository has one (read it from history or the authority policy).
- Project skill Finish step: the same rule, one line.

## Several methods allowed

Ask for the rule that picks one method per change and record it verbatim,
for example: "Squash by default; rebase only when every commit on the
branch is a task-level commit that passes the checks on its own; merge
commits only for promoting the default branch into an environment branch."
Enable exactly the methods the rule names and no other setting the rule
does not need (no required linear history unless the rule says so).
