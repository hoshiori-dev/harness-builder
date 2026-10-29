Read this when about to push, publish, release, comment, label, change a remote setting, or delete anything you did not write; when an action is refused; and whenever unsure whether an action is yours to take.

# Agent Authority Policy

Set by {{OWNER}} on {{DATE}}. <!-- # CONFIGURE: {{OWNER}} and {{DATE}}: who set this policy and when. -->
The sandbox decides what an agent *can* do; this file decides what it *may*
do on its own. The two are independent and this file is the narrower one.

## Reversibility is the key

Classify every action before taking it:

- **Reversible and internal**: edit files, create a branch or worktree, run
  checks, commit locally, squash unpushed commits. Do it; no question.
- **Irreversible or outward**: push, open or update a pull request, post a
  comment, add or remove a label, change an issue or pull request state,
  release, publish, change a remote setting, delete anything the user wrote.
  Take it only when the approved plan or the task's spec pre-authorised it;
  otherwise add it to the pending decisions list below and continue with the
  work that does not depend on it.

A local commit can be rewritten or dropped. A pushed commit cannot be erased
from the remote: a force push moves the branch pointer and the old objects
stay addressable. The two are different classes.

### Irreversible actions in this project

{{IRREVERSIBLE_ACTIONS}} <!-- # CONFIGURE: {{IRREVERSIBLE_ACTIONS}}: thick grade only. List this project's irreversible actions as its platform's operations (for example `gh pr ready`, `gh pr comment`, `gh release create`, `just publish`); delete this section at medium grade. -->

{{SPEC_SENTENCE}} <!-- # CONFIGURE: {{SPEC_SENTENCE}}: keep when a specification workflow exists, delete otherwise: "Each spec carries a list of the irreversible actions pre-authorised for that task; an action on that list proceeds without a prompt, every other outward action is deferred." -->

## Approval at both ends, not per command

Human approval sits at two points: on the plan and on the finished work.
Approving a plan approves what is done, what is not done, and where the
approach is bounded; it never approves a sequence of steps. Per-command
approval is not a safety mechanism: it exhausts the reviewer, protects
nothing the sandbox does not already protect, and destroys the unattended
time that is the point of using an agent.

When one item needs a decision only the user can make, finish every other
item first and raise the decision once, at the end or when nothing else can
proceed.

## Pending decisions

Each item carries five fields: what is blocked; why the decision is the
user's; the options, one sentence each; the recommended option and its
reason; which finished work each option would change. The list is presented
once, never one question at a time, so that a user returning after hours
away can decide every item from the list alone.

```markdown
### 1. <short title>
- Blocked: <step or action>
- Why: <reason the user must decide>
- Options:
  - A. <option>
  - B. <option>
- Recommended: <A or B>, because <reason>.
- Impact on finished work:
  - A: <what changes, or none>
  - B: <what changes, or none>
```

## A refusal is a decision

When a permission rule, a hook, or the platform refuses an action, it means
one of two things:

1. The plan put the work in the wrong place. A refused edit to a protected
   file usually means the logic belongs elsewhere: return to the plan and
   choose another approach.
2. A real policy boundary was reached: record it as a pending decision and
   continue with the rest.

Forbidden: retrying the same intent through an equivalent command, a script,
a different tool, or a shell redirect. Denied `git push --force`, then
`git push --force-with-lease` on the same branch, is routing around. A
refused edit, then the same change through `cat >` or `sed -i`, is routing
around. A failing test, linter, or secret scan is not a refusal; it is a
defect to fix.

## Permission lists

The framework permission lists ({{PERMISSION_FILES}}) <!-- # CONFIGURE: {{PERMISSION_FILES}}: the client permission files this project uses, for example `.claude/settings.json` and `.codex/rules/authority.rules`; or "none; this policy alone" when the user declined framework files. -->
name what is known safe (allow) and what is known dangerous (deny). Commands on neither list
fall to the framework's default judgement; the sandbox makes a wrong default
survivable. On a client whose default is to ask, a recurring prompt for a
safe command is a reason to widen the allow list, not to add an ask entry.
The lists carry no ask entries. <!-- # CONFIGURE: when the owner kept an ask entry, write instead "The lists carry one ask entry, <entry>, kept by <owner> because <reason>; add no other." -->

The deny list (`git reset --hard`, `git push --force`, `git push
--all/--mirror/--tags`, `git clean -fd`, `git branch -D`, `rm -rf` at the
repository root, edits to this file, the permission files, and the security
hooks) protects against a careless collaborator's mistakes, not an attacker.
An agent that runs code can spell around it; the sandbox and the scoped
tokens are the real boundary.

No push, publish, release, tracker write, or deletion of others' work is an
allow entry, as a raw command or inside a task-runner recipe, however
routine; recipes are allowed one by one, never through a runner wildcard: those actions proceed when the plan or the
spec pre-authorised them and are deferred otherwise.

## Checkpoints are commits

<!-- # CONFIGURE: `just` below is the task runner; write the project's own (`make`, `npm run`) and its recipe names. -->
- Commit after every verified sub-step; never a stash (unnamed, addressed by
  stack position, conflicts on pop, invisible in `git log`) and never a
  session-only undo.
- A finished task is one atomic commit. Draft commits made inside a task are
  squashed into it when the task ends, non-interactively:
  `just squash-task <task-start> "<message>"` resets softly to the task
  start and commits once. Squash per task, not per pull request.
- A task that holds two independent changes goes back to the plan and is
  split there; commits are not carved out of a mixed diff by hunk.
- Draft commits never leave the machine. Push only after the task's commit
  exists, and push one explicit ref: `just push-one`. `--all`,
  `--mirror`, and `--tags` are denied. Only unpushed history is rewritten;
  pushed history is reverted.
- A draft pushed to get remote CI is a publication and passes the same gate
  as a real push; the local fast validation loop comes first.
- Squashing changes no content: secret scanning runs on every checkpoint
  commit, not only before publication.
- "No draft commit on the branch" is part of every task's completion;
  `just push-one` refuses while one exists.
- To discard a failed approach run `just rollback <ref>`: it commits a
  checkpoint if the tree is dirty, prints that commit's SHA, then resets.
  `git reset --hard` itself stays denied because it would destroy
  uncommitted work; the recipe guarantees the precondition.

Commit messages follow {{CONVENTION}}. <!-- # CONFIGURE: {{CONVENTION}}: the commit convention, for example "Conventional Commits: `<type>(<scope>)?: <subject>`, lowercase imperative subject, no trailing period, at most 72 characters" or "a 50-character imperative title, no type prefix, body wrapped at 72". -->
No AI or tool attribution in any commit: no co-author trailer, tool name, or
model name.

## Concurrency

{{CONCURRENCY}} <!-- # CONFIGURE: {{CONCURRENCY}}: single-agent: "One agent works on this repository at a time; no parallel-agent rule applies." Parallel: "Several agents work in parallel. Every platform write by a parallel agent (comment, label, state, push) is outward and irreversible, so it is pre-authorised or deferred like any other. Branch ownership, the coordinator role, who merges, and who arbitrates conflicts are defined in <platform knowledge file> and not restated here." -->

## Pairing mode

Step-by-step approval is legitimate only while a project is being
bootstrapped or its specifications are being established with the user
present, or in a project requiring high alignment (strict security,
per-line accountability). Approval fatigue applies in pairing mode too; a
present human is not a reason to ask about every command.
{{PAIRING}} <!-- # CONFIGURE: {{PAIRING}}: "Not in use; this project is in its running phase." Or: "In use during <phase, e.g. the bootstrap of this harness / the specification of <feature>> because <the user is present and leading / strict security requires per-line accountability>; approvals happen in the conversation. The project switches back to approval at the plan and at the handoff when <condition, e.g. the first specification is approved>." -->

## Deviations recorded by the owner

{{DEVIATIONS}} <!-- # CONFIGURE: {{DEVIATIONS}}: delete this section when the user kept no deviation. Otherwise record each as "<choice> by <owner> on <date>, because <their reason>; the methodology recommends <recommendation>." -->

## This file protects itself

Loosening this policy, a permission list, or a security hook is outside
every agent's authority, including when it would unblock the current
task and including when a denied command turns out to be required by the
approved plan. Do not edit the rule: propose the change with its reason and
wait.

Maintenance happens when the harness is improved, as a one-time review: a
prompt category approved near 100% of the time moves to the allow list; an
allowed command that repeatedly caused rollbacks is tightened. No standing
metric is kept.
