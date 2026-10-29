# Checkpoints

Read when writing the checkpoint rules of a policy, writing or translating
the checkpoint recipes, or when a user or an existing rule proposes stashes,
hunk-level staging, or pushing drafts for remote CI, or asks why hard reset
is denied when agents are expected to roll back. [§4.3]

## Rules the deposited files carry

- **Checkpoints are commits.** Commit after every verified sub-step. Never a
  stash: it is addressed by stack position, may conflict on pop, has no name,
  and does not appear in `git log`. Never a session-only undo: invisible to
  humans, gone across sessions.
- **One task, one atomic commit.** A verified sub-step is a task of the plan
  or the spec's task list; its commit is written to the project's commit
  convention.
- **Drafts inside a task are squashed when the task ends**, non-interactively:
  `git reset --soft <task-start>` then one commit. The unit is the task, not
  the pull request; do not postpone squashing to "before the PR is ready"
  when the drafts' meaning is already out of context.
- **A non-atomic task goes back to the plan.** A task found to hold two
  independent changes is split at the plan level and committed separately;
  commits are not carved out of a mixed diff by hunk.
- **Drafts never leave the machine.** Push only after the task's commit
  exists, and push one explicit ref (`git push origin HEAD`). `--all`,
  `--mirror`, and `--tags` are denied. Only unpushed history is rewritten;
  pushed history is reverted.
- **A draft pushed for remote CI is a publication.** It passes the same gate
  as a real push; the local fast validation loop comes first.
- **Squashing changes no content.** Secret scanning runs on every checkpoint
  commit, not only before publication, because a stray credential folds into
  the task commit unchanged.
- **"No draft commit on the branch" is part of task completion**, so the
  squash does not depend on anyone remembering it.
- **Rollback is a recipe; the raw command stays denied.** The recipe verifies
  a clean tree or commits a checkpoint first, then resets; `git reset --hard`
  and `git clean -fd` remain on the deny list because they protect
  uncommitted work. The precondition is guaranteed by the recipe, not by a
  reminder.
- **No AI attribution** in commit messages: no co-author trailers, tool names,
  or model names.

## Recipes

`assets/checkpoint-recipes.just` is the reference implementation; it is
reworked into the project's task runner and convention, never copied: the
draft prefix, the base branch, the commit-subject regex, and the remote name
each set from the settled answers, and the header comment kept, since it
carries the checkpoint and attribution rules into the project at every
grade.

| Recipe | Does | Refuses when |
|---|---|---|
| `checkpoint <msg>` | stages everything, commits `<draft-prefix>: <msg>` | the tree is clean |
| `squash-task <start> <msg>` | `reset --soft <start>`, one commit `<msg>` | `<start>` is not an ancestor of HEAD, any commit in `<start>..HEAD` is already on the upstream, or `<msg>` breaks the convention |
| `rollback <ref>` | commits a checkpoint if the tree is dirty, prints its SHA, then `reset --hard <ref>` | `<ref>` does not resolve |
| `push-one` | `git push origin HEAD` | a draft-prefixed commit exists between the base branch and HEAD, or the branch is the base branch |

The draft prefix (`checkpoint` in the asset) is what makes "no draft commit
on the branch" machine-checkable; `push-one` enforces it.

## Commit convention

Observed in history: record it, propose nothing. Not observable: recommend
Conventional Commits (`<type>(<scope>)?: <subject>`, lowercase imperative,
no trailing period, subject at most 72 characters) because the type makes the
squash message mechanical; offer plain 50/72 titles without a prefix. Write
the chosen rule into the policy and into the `squash-task` check; for
plain 50/72 the subject regex is `^[A-Z]$|^[A-Z].{0,48}[^.]$` (at most 50
characters, no trailing period).

## Translating to another task runner

Ask first. Keep the refusal conditions and the messages that name what to
fix; `make` targets take arguments through variables (`make squash-task
START=<sha> MSG="..."`), npm scripts through a small Python or shell file the
script calls. Deliver nothing in `just` syntax to a project that does not use
`just`.
