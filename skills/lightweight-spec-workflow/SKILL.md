---
name: lightweight-spec-workflow
description: >-
  Lightweight specification carrier — aligns one change before coding with
  plan mode or a per-change SPEC.md and PLAN.md in a project without a spec
  framework. Use when the user wants to agree on or approve what a change
  will do before code is touched and no spec tool is in use; when asked to
  draft, review, or plan from a SPEC.md or PLAN.md for one change; when the
  user asks whether a small fix needs a written spec or a plan is enough; when a reviewed change's
  SPEC.md must be folded, deleted, or written back before the pull request is
  marked ready; or when the spec contract names per-change documents or plan
  mode as the carrier. Not for OpenSpec changes or Spec-Kit specify and plan
  commands, deciding whether or how strictly to adopt spec-driven
  development, recording the project's spec contract, or API, protocol, and
  test specifications (OpenAPI).
license: Apache-2.0
---

# Lightweight Spec Workflow

This skill carries one change from alignment to the freeze without a
specification framework: plan mode for a small edit, a per-change `SPEC.md`
(plus `PLAN.md` when the approach needs bounding) for mid-size work. Without
it an agent starts coding on its own reading, writes goals as diffs, judges
completion from the diff, and leaves a stale `SPEC.md` behind after review.
[§4.1]

## Rules on every step

<!-- shared:confirm-not-guess -->
Confirm, do not guess. Settle a fact from the repository when it can be
observed there (tools in use, directories, commands, history); ask the user
for everything else, and ask before choosing on any point where two readings
would lead to different work. Only a choice whose answer is plain from the
repository is made without asking.
<!-- /shared:confirm-not-guess -->

Points that always need the user: the carrier, the file location, the
non-goals, the pre-authorised actions, the branch name when no change
branch exists, and the fold-or-delete choice.
Observed without asking: framework directories, existing conventions, the
recorded contract, the test command.

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

Here that means: an approved specification authorises the irreversible
actions it lists under "Pre-authorised irreversible actions" and no others.
With "none" there, work stops at a local commit. [§4.2]

<!-- shared:pending-decisions -->
When a step is blocked on a decision only the user can make, continue with
every step that does not depend on it and add the blocked item to a pending
decisions list. Each item states: what is blocked and why; the options; the
recommended option and its reason; which finished work each option would
change. Present the list once, at the end or when nothing else can proceed,
never one question at a time.
<!-- /shared:pending-decisions -->

**Handoffs by role, never by name.** Whether this project should adopt
spec-driven development, or at which level, goes to the skill that teaches
the spec-driven development methodology. Writing or changing the project's
recorded contract (every change needs a `SPEC.md`, approval mode, completion
rule, level, freeze executor) goes to the builder that owns the
specification and completion layer; never edit the project's knowledge
files for that yourself. Offer the handoff and keep drafting meanwhile. If
the user declines, continue with the four completion answers as the
contract, add the unrecorded rule to the pending decisions list, and say the
practice-level question stays open.

**Framework found means stop.** On finding `openspec/` or `.specify/` in the
repository at any step, stop, say the project already has a carrier, and
offer the carrier skill for OpenSpec or for Spec-Kit, described by that role.

## Workflow

### 1. Inspect

Record:

- framework directories (`openspec/`, `.specify/`) — any hit ends this
  workflow per the rule above;
- the recorded contract: a spec-workflow knowledge file or the entrypoint's
  rules on specifications — its level (spec-first or spec-anchored), carrier
  rule, location for per-change files, living specification, and freeze
  executor, each with the file that states it;
- the task runner's test or check recipe (`justfile`, `Makefile`,
  `package.json` scripts) — the done-check command;
- a squash or checkpoint recipe, the base branch, and the change branch.

Done when: every item is recorded as found (with file) or absent, and no
file changed.

### 2. Choose the carrier

A recorded project rule ("every change gets a `SPEC.md`") is applied without
asking; say which file stated it. Otherwise recommend by the size of the
change, give the reason, name the alternative, and wait for the choice:

- **Plan mode** for a small edit, when every item holds: one file, or a few
  lines across two; no new or changed behaviour a user or caller can observe
  beyond the fix itself; no migration, new public interface, or new
  dependency; one task, so one commit. Read
  [references/plan-mode.md](references/plan-mode.md) when the user chooses
  plan mode; that file replaces steps 3 to 5, 7, and 8; step 6 still applies.
- **`SPEC.md`** for mid-size work, plus **`PLAN.md`** when the approach needs
  bounding: several modules, a migration, an order that matters.
- **Undersized** when the change spans several features or needs a
  specification that outlives it: say the lightweight carrier is undersized,
  describe the builder that owns the specification and completion layer as
  the place to choose a framework, and propose splitting the work into
  per-change pieces meanwhile.

Done when: the user chose a carrier, or a recorded rule chose it and its
file was named.

### 3. Draft the specification

Rework [assets/SPEC.md](assets/SPEC.md) line by line for this change; rework
[assets/PLAN.md](assets/PLAN.md) only when the user wants a plan, and
otherwise keep the approach as the short "Approach" section of `SPEC.md`.
With a `PLAN.md`, delete that section from `SPEC.md`.
The specification answers four questions, each under its own heading: [§4.1]

1. **Done when** — the check command the agent runs itself (the observed
   test recipe, proposed without asking which command runs the tests), the
   acceptance scenarios exercised against the running result, and "the
   branch holds only task-level commits". [§4.3]
2. **Non-goals** — when the user offers none, propose the ones the goal
   implies, mark each as a proposal, and ask the user to confirm or strike
   each.
3. **Deliverable** — pull request, report, or deployment, plus the pending
   decisions list.
4. **Pre-authorised irreversible actions** — ask which push (branch and
   remote), pull request, and comments are allowed; record "none" when the
   user allows none.

Quality rules, applied before presenting: [§4.1]

- A goal describes observable behaviour, never the diff. Rewrite an
  implementation goal into the behaviour it produces ("add a unique index on
  email" becomes "a second sign-up with the same email is rejected with the
  stated response") and move the implementation into the "Implementation
  notes" of `PLAN.md`. Without a `PLAN.md`, offer one to hold the note; when
  the user declines, keep the note out of `SPEC.md` and record it in the
  commit body of the task that implements it.
- Every goal has at least one scenario a reader who has not seen the code
  can judge.
- At least one scenario covers a failing or boundary input; add one when
  every scenario describes success.

Done when: each of the four headings carries content for this change; every
goal has a scenario and at least one scenario is a failure path; every
proposed non-goal is confirmed or struck; no `{{…}}` placeholder,
`# CONFIGURE:` line, how-to-use line, or empty heading remains. A draft missing an answer is flagged to the user,
never presented for approval.

### 4. Get approval

Present the specification (and plan) in the conversation; write it uncommitted
to the agreed location only when the user asks for a file to review. Fix the
branch now: the current branch when it is not the base branch; otherwise
propose a branch name and ask. Fix the location now: the project's convention when one exists; otherwise propose
`changes/<branch-name>/` at the repository root (one place reviewers look,
named after the branch, emptied by the freeze), ask before creating it, and
say once that files placed there are the project's own. Never a system
temporary directory.

Wait for an explicit approval. When the user asks for changes, revise and
present again; commit nothing and write no code. [§4.1]

Done when: the user's own words approve this version of the draft.

### 5. Implement within the approved scope

When the agreed branch does not exist yet, create it from the base branch
before the first commit. The first commit, on that branch, includes the
`SPEC.md` (and `PLAN.md`) at the agreed location.

Record each task's start commit when the task begins. Commit a checkpoint
whenever a sub-step is verified. At the end of each task, squash its draft
commits into one task-level commit without an interactive rebase: use the
project's squash recipe when step 1 found one; otherwise
`git reset --soft <task-start-commit>` then one `git commit`. That reset
covers only the task just finished, so run it at each task's end, never
later across several tasks. [§4.3]

Take only the irreversible actions the specification lists. Never push a
draft commit: a pre-authorised push happens only after the task's drafts are
squashed into its task-level commit, as a single named ref. [§4.3]

The scope is now fixed. A request for behaviour outside it is named as
outside the approved scope, with an amendment or a follow-up change
proposed; continue the approved work until the user decides, and apply an
amendment only once approved. [§4.2]

### 6. Run the done-check yourself

1. Run the specification's check command and read its exit code.
2. Exercise every scenario against the running result (run the program,
   send the request, call the function); never judge a scenario from the
   diff. A scenario needing an environment you cannot reach is reported as
   unverified, with the reason, and listed in the deliverable, never marked
   passed. [§4.1]
3. List the branch's commits (`git log --oneline <base>..HEAD`). When draft
   commits of the last task remain, squash them as step 5 does. When an
   earlier task still has draft commits, report it as a failing item and ask
   the user how to proceed; never split staged changes by file or hunk. Push
   nothing until the branch holds only task-level commits. [§4.3]

On a failing check or scenario, name the failing output, do not declare
completion, and either fix it within the specification or raise the gap to
the user.

Done when: the check exited 0, every scenario is passed or reported as
unverified, the branch holds only task-level commits, and the report names
the command, each scenario's result, and the commits.

### 7. Deliver

Produce the deliverable the specification names, within its pre-authorised
actions. The pull request or report links or quotes the specification and
carries the pending decisions list. A remote step the specification did not
authorise (push, pull request, comment) goes to that list instead; the local
work still finishes.

### 8. Freeze

The freeze happens on the change's branch, after the gate owner closes
deliberation on the implementation and before the request is marked ready.
Asked to freeze while review is still open, say the freeze follows the close
of deliberation, leave the file, and offer to put the request up for review
instead.

**Disposition, by the recorded level, without asking the level:**

- **spec-first**: recommend folding the lasting content (behaviour, the
  reason for a decision) into the project's documentation, name deletion as
  the alternative, and act on the user's choice.
- **spec-anchored**: propose the edit that writes the accepted behaviour into
  the living specification the contract names and removes the per-change
  `SPEC.md`, and say which contract entry requires it.
- **No contract**: say spec-first is the default for a project without a
  spec framework, name spec-anchored as the alternative, ask the user to
  confirm for this change, and describe the methodology skill as the place
  to settle the level for the project.
- **User declines folding and deletion**: leave the file, add the decision
  to the pending decisions list, and state that the file will drift from
  the code.

**Executor, as the contract names it:**

- **No contract**: say that a person performs the freeze by default, then
  follow the person branch.

- **A person**: present the fold, deletion, or update as an exact proposed
  edit, commit nothing, and mark the request ready only after the person has
  made it.
- **The agent**: commit the edit on the branch before marking the request
  ready, and name that commit in the deliverable.

A commit landing after the freeze commit makes the freeze stale: before
pushing, say so, name the commit, and ask whether deliberation reopens.

Done when: the disposition is committed by its executor (or kept and
recorded as pending), no commit follows it, and only then is the request
marked ready.

## Gotchas

- `git reset --soft` rewrites history; run it only on commits not yet
  pushed. The log will not say where a task started, so the squash depends
  on the start commit recorded in step 5.
- "Ready" here means the request leaves review for merging; a draft pull
  request under review is not ready, so the freeze can still follow it.
