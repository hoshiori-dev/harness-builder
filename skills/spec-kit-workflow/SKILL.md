---
name: spec-kit-workflow
description: >-
  Spec-Kit carrier — runs Spec-Kit features through pull or merge requests
  and installs their check and progress-label jobs on GitHub or GitLab.
  Use when a Spec-Kit project asks whether plan.md must be approved before
  tasks.md, or what to do with a tasks.md the kit generated before
  approval; whether a request can be marked ready while a `specs/NNN-name`
  feature has unticked tasks; how to archive, lock, or validate a finished
  feature; whether the approval still holds after spec.md or plan.md
  changed; what to do with a feature directory made by hand; what a
  `spec:` label means, or asks to set one; or to add the feature check and
  progress labels to CI. Not for running the kit's own commands to create
  or implement a feature, for choosing a spec tool or whether to adopt
  spec-driven development, or for a project on OpenSpec or another
  framework.
license: Apache-2.0
compatibility: Scripts need Python 3.10+ and git; uv optional.
---

# Spec-Kit Workflow

Spec-Kit gives each feature a numbered directory under `specs/` with a
specification, a plan, and a task list, and stops there: it has no
validator, no archive, and no approval gate. This skill supplies what a
pull or merge request needs on top: which files the reviewer approves, the
lock that names the approved version, when a request is ready, and the
check and progress-label jobs that hold those rules in CI. [§4.1]

## Rules on every step

Precedence: an explicit user instruction, then the project's recorded
specification contract (`.agents/knowledge/spec-workflow.md` or the file
the agent entrypoint points to), then this skill's defaults. When the
contract settles a point differently (another lock, another completion
rule), apply the contract's rule and say that the skill's default was not
used.

<!-- shared:confirm-not-guess -->
Confirm, do not guess. Settle a fact from the repository when it can be
observed there (tools in use, directories, commands, history); ask the user
for everything else, and ask before choosing on any point where two readings
would lead to different work. Only a choice whose answer is plain from the
repository is made without asking.
<!-- /shared:confirm-not-guess -->

<!-- shared:recommendation-not-decision -->
A recommendation is not a decision. Present one recommended option with its
reason and the alternatives in a sentence each, then wait for the user's
choice. Challenge a choice once when the evidence contradicts it; after that
the choice binds every later step.
<!-- /shared:recommendation-not-decision -->

<!-- shared:nothing-lands-before-agreement -->
Nothing lands before agreement. Create or change no file in the target
project until the user has approved the plan that names it; an inspection
step reads and reports, it never writes.
<!-- /shared:nothing-lands-before-agreement -->

<!-- shared:plan-is-not-approval -->
An approved plan authorises the files it names and nothing else. Publishing
anything outside the repository, changing a remote setting, deleting work,
and widening what agents may do on their own are each a separate, explicit
decision by the user, taken when that step is reached.
<!-- /shared:plan-is-not-approval -->

<!-- shared:pending-decisions -->
When a step is blocked on a decision only the user can make, continue with
every step that does not depend on it and add the blocked item to a pending
decisions list. Each item states: what is blocked and why; the options; the
recommended option and its reason; which finished work each option would
change. Present the list once, at the end or when nothing else can proceed,
never one question at a time.
<!-- /shared:pending-decisions -->

<!-- shared:management-code-ownership -->
A script, hook, check, CI step, or task-runner recipe written into the target
project is the project's own management code: written for its role in the
language the project agreed to, readable first, failing with a message that
names what to fix, with no fallback that hides an unexpected error, and never
calling a script inside a skill directory. Tell the user that later fixes to
this plugin do not reach the delivered copy.
<!-- /shared:management-code-ownership -->

Never tick a task whose named verification has not run and passed: run it,
or ask to run it, then tick. [§4.1]

Never apply or remove a `spec:` progress label by hand. Never print an
install command for another skill.

Hand off by describing the need, never by skill name:

- Whether or at which level to adopt spec-driven development, and what a
  good specification is → the skill that teaches spec-driven development.
- Setting or changing the project's rules (approval mode, completion rule,
  lock, request shape) → the skill that owns the specification and
  completion layer.
- A checks workflow or aggregator gate that does not exist yet → the skill
  that owns the hard-boundary layer.

When the user declines a handoff, apply the contract as it stands, or these
defaults where it is silent (every task ticked before ready, gates closed in
conversation, the lock declared on the request), say which you applied, and
name the contract update as remaining work.

## Workflow

Step 1 runs for every request; then go to the step the question reaches.

### 1. Read the project

Read, write nothing. Record: the specs directory and its feature
directories; `.specify/` and the project's copy of the kit's scripts and
templates; the contract's approval mode, gate owner (the person who approves
the specification and plan), completion rule, lock, request shape, and
level (spec-first or spec-anchored); the platform (GitHub or GitLab from the
remote URL); the checks workflow and its aggregator gate; the label file;
whether `scripts/spec_kit_features.py` already exists and the project's
agreed management-script language.

The touched features of a request are the feature directories its diff
touches. Report them with the bundled
[scripts/spec_kit_features.py](scripts/spec_kit_features.py) (read-only;
without uv, run it with `python3`):

```bash
uv run --script <this skill's directory>/scripts/spec_kit_features.py --root <project root> status --base origin/main --head HEAD
```

`<this skill's directory>` is the directory holding this file, never the
project. Never run the project's own `scripts/spec_kit_features.py` for
this session's reports: that is the deposited copy for the jobs, and it
has no `show` or `related`.

Its subcommands are `related`, `status`, `show`, `check`, and `labels`; run
`--help` for options. For a request by number, take its refs from
`gh pr view <n> --json baseRefOid,headRefOid` (on GitLab, `glab mr view <n>`)
and `git fetch` both before passing them.

Done when: every item above is recorded as observed, absent, or "ask", and
nothing in the project changed.

### 2. The approval package

A draft request opens with the feature's `spec.md` and `plan.md`; together
they are what the reviewer approves. `tasks.md` is after-approval material
even when the kit generated it early: keep it out of the review and draft
a note for the request marking it as after-approval. Post the note only
when the contract or the request's pre-authorised actions allow posting;
otherwise hand the draft to the user or list the post under pending
decisions. [§4.2]

The plan bounds the approach (constraints, preferences, rejected
alternatives) and lists no steps, because approving steps approves a method
without bounding the result. When a plan reads as an ordered procedure, say
so, recommend recasting it under the kit's plan headings as approach,
constraints, preferences, and rejected alternatives, and edit it only after
the user agrees. [§4.2]

Read [references/layout.md](references/layout.md) when validating a
feature directory, when a feature was made by hand, or before saying what
the kit's feature script did (numbered directory, branch or no branch).
Validation is a heading check against the kit's templates; say that no
programmatic validator exists.

Done when: the user knows which files are under review and which are not,
any after-approval note is posted, held by the user, or under pending
decisions, and any plan rewrite is either agreed or declined.

### 3. Lock the approved version

The kit archives nothing, so the lock is a declaration on the request.
When the gate owner closes the review, draft it:

```text
Review closed: specs/<feature>/spec.md and specs/<feature>/plan.md are
approved unchanged at <commit>. Tasks may proceed; a later change to either
file reopens the review.
```

`<commit>` is the head commit the gate owner reviewed. Post it only when
the contract or the request's pre-authorised actions
allow posting; otherwise hand the draft to the user or list the post under
pending decisions. Say that nothing mechanical enforces the declaration.
[§4.2]

Before every push or handover, look for a spent lock:
`git log --oneline <commit>..HEAD -- specs/<feature>/spec.md specs/<feature>/plan.md`.
Any output means the approved version no longer exists: say so and ask for
the gate again before pushing or handing over.

When the user wants to skip the declaration, say once that the approval
would then follow the branch with no version to name, then follow the
user's choice.

Done when: the declaration names a commit, and either it is posted or the
user holds the draft or it is under pending decisions.

### 4. Readiness

A request that carries implementation (the combined shape, or the split
shape's implementation request) is ready only when every task of every
touched feature is ticked. A feature with no `tasks.md`, or one with no
checkbox, has not started: admit it on a draft or on the split shape's
specification request, and refuse to mark an implementation request ready
until its task list exists and is fully ticked. [§4.1]

```bash
uv run --script <this skill's directory>/scripts/spec_kit_features.py --root <project root> check --base origin/main --head HEAD --shape <combined|split> [--draft]
```

Pass `--shape` from the contract's request shape and `--draft` when the
request is a draft. When the contract does not record the shape, ask
before giving a verdict that depends on it: recommend combined, because
one request carries one approval and one lock.

When the answer is no, name each feature and each open task, say that
completion is every task ticked because the kit archives nothing, tick
nothing, and say the installed check job would fail when it exists. Asked
how to archive a finished feature: there is no archive; completion is the
fully ticked task list, and on a spec-anchored project the living
specification is updated by the project's recorded rule; name that rule or
say it is missing.

Done when: the user has a yes or a no that names every unfinished task.

### 5. Progress labels

The installed automation derives one label per request from the touched
features' task lists: `spec:not-started` (no task ticked), `spec:in-progress`
(some ticked, some open), `spec:done` (all ticked). A request touching no
feature carries none. The label changes on the next run, never by hand:
asked to set one, decline, say the label is workflow-owned, and name the
open task that keeps it from changing.

### 6. Install the automation

Only when the user asks. First confirm:

- **Request shape**, when the contract does not record it: recommend
  combined (specification, plan, and implementation in one request),
  because one request carries one approval and one lock; the alternative is
  split (a specification request first, implementation requests after),
  which suits review by a different person or a long implementation.
- **Script language**: the produced jobs call `scripts/spec_kit_features.py`.
  Always ask whether to use the Python asset as is or rewrite it in the
  agreed language. Recommend as is when the agreed language is Python, because
  the jobs and the test are written for it; when it is another language,
  offer the asset as a reference implementation to rewrite; when no
  language is recorded, ask for it and do not assume Python. Write nothing
  until the user chooses.
- **A checks workflow with a gate**. When none exists, say so, recommend
  building the hard-boundary layer first (hand off as above), and install
  nothing until the user decides.

Then list every file to add or change and wait for agreement.

- Read [references/github.md](references/github.md) when the platform is GitHub.
- Read [references/gitlab.md](references/gitlab.md) when the platform is GitLab.

Follow its table and fork-safety rules. Deposit
[assets/spec_kit_features.py](assets/spec_kit_features.py) and its
`_test.py` sibling as the project's `scripts/` copies and run the test.
Install no comment-command workflow. [§3.2]

Done when: the listed files exist, no `{{NAME}}` placeholder remains
(`grep -rn '{{[A-Z]'` over the written CI files prints nothing), the
deposited test passes, every privileged job checks out only the base, and
no produced step fetches or checks out the head in one. On GitLab, where
no job runs on the base ref, the label token is under pending decisions
with that deviation stated.

### 7. Sync the labels and hand over

Show the label additions and removals a sync of the label file would make
on the remote, apply them only after the user approves that delta, then
read the remote back and report the difference. When the token cannot
write, or a setting needs a maintainer (required check, ruleset, "Pipelines
must succeed"), list it under pending decisions with the exact delta or
setting and its recommended value, apply nothing by another route, and
finish the rest. [§4.2]

The handoff states: the files written; that nothing installed archives or
pushes; that the deposited script is the project's own copy and is not
kept identical to this skill's; on GitLab, that a label applies on the next
pipeline; whether the label delta was applied and read back or is pending;
the pending decisions list.

Done when: the handoff carries every item above.

## Gotchas

- The kit's core feature script creates a directory, not a branch; a
  harness that says "the tool creates the branch" sends agents onto the
  wrong ref.
- The kit's `converge` step appends tasks; it is not an archive, and a
  converged feature with open tasks is not done.
