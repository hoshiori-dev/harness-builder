---
name: spec-driven-development
description: >-
  Spec-driven development — writes the specification before the code and
  runs each change through the specify-to-freeze loop. Use when the user
  wants the spec written first or a feature done spec-first; asks whether
  specs first are worth it for a project or at which level; asks whether
  the design is approved before the task list, where approval sits, or what
  a specification must answer; says what shipped no longer matches the
  spec; or wants a prototype or existing codebase brought under specs and
  approvals without a rewrite. Not for setting up a project's spec
  workflow, choosing its spec tool, or writing its contract and CI check;
  for a spec tool's own commands, such as creating or validating a change;
  for issue forms, request templates, or labels; or for defining project
  goals.
license: Apache-2.0
---

# Spec-Driven Development

A specification states, in observable behaviour, what one change must do,
what it must not do, how its completion is proven, and which irreversible
actions it may take. Spec-driven development writes it first, has it
approved before any task list or code exists, and judges the finished work
by running it, so the agreement survives the session that wrote the code.
[§4.1]

- Read [references/adoption-decision.md](references/adoption-decision.md) when the user asks whether or at which level to adopt spec-driven development.
- Read [references/adopting-existing-code.md](references/adopting-existing-code.md) when the project holds code not written from a specification (a prototype, a vibe-coded app, a brownfield codebase), before its first change enters the loop.
- Read [references/tracked-work.md](references/tracked-work.md) when a loop step meets a change request: opening the draft, reading review threads, writing the request body, marking it ready, freezing in the request, or a recorded approval mode.
- Read [references/anchoring.md](references/anchoring.md) when the user asks to code before the specification, when code exists for a change nobody approved, or when a requirement names an implementation.

## Rules on every step

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

<!-- shared:pending-decisions -->
When a step is blocked on a decision only the user can make, continue with
every step that does not depend on it and add the blocked item to a pending
decisions list. Each item states: what is blocked and why; the options; the
recommended option and its reason; which finished work each option would
change. Present the list once, at the end or when nothing else can proceed,
never one question at a time.
<!-- /shared:pending-decisions -->

**Irreversible actions need the package.** Pushing, opening or marking a
request, editing a request's body or approval line, editing an issue or any
other platform object, posting a comment, deploying, publishing, and
deleting data happen only when the approved package lists them. The one
exception is the push and draft request that publish the package itself,
which the user's confirmation in step 3 authorises. Any other irreversible
action is not performed: finish every step that does not depend on it and
add it to the pending decisions list. Local edits, branches, test runs, and
local commits are reversible and need no approval. [§4.2]

**Steps run in order.** Never start a step whose predecessor's `Done when:`
is unmet. Asked to skip ahead, name the unmet condition and the step it
belongs to, and offer to finish that step now. After every step, state which
step is done, the condition that makes it done, and the next step.

**Approver.** The person the contract names approves each gate; the user
when it names nobody. A review closes only when the approver says so.

### Project rules

Precedence: an explicit user instruction, then the project's specification
contract (the file the agent entrypoint routes specification work to,
commonly `.agents/knowledge/spec-workflow.md`), then the defaults below.

- Contract present: apply its facts, say which file stated them, re-ask none.
- Contract silent on a point that changes the work: ask once, in one batched
  question, each point with its default as the recommended option and its
  reason. Never choose silently.
- User asks to depart from the contract (for example a conversational
  closing where the contract records a recorded approval): name the
  contract's rule, recommend following it, and ask the user to confirm the
  override for this change only.
- Defaults applied: the reply lists each one and states that these are
  defaults, not project rules. Recording them as project rules is the work
  of the skill that owns the specification and completion layer; describe
  that skill to the user and edit no project knowledge file yourself.

| Point | Default (recommended when the contract is silent) |
|---|---|
| Level | spec-first; spec-anchored when maintenance past one release is observable (tagged releases spanning more than one release cycle), citing that history |
| Carrier | the spec tool in use; else the lightweight carrier (a per-change file or plan mode) for this change. Choosing or changing the project's spec tool goes to the skill that owns the specification and completion layer |
| Request shape | none: with conversational approval and no contract naming a platform request, both reviews close in the conversation and no request is opened. Combined (specification and implementation in one request, opened as a draft) only when the contract or the user puts review on a request |
| Approval | conversational, on the complete package, at both gates |
| Design | warranted by the rule in step 3 |
| Freeze executor | the implementer; on a fork, the person who holds the branch |
| Scope | domains describe the product; harness, tooling, checks, workflows, and documents are spec-less changes |

A request for a domain covering build scripts or other tooling is declined:
domains describe the product. Offer the carrier's spec-less change kind.

### Carriers

Hand tool work to the carrier skill by role, never by an install command:
creating, validating, and archiving records and the request automation go
to the carrier skill for the tool the project runs (the carrier skill for
OpenSpec, the carrier skill for Spec-Kit); with no spec tool, the choice
between a per-change file and plan mode goes to the lightweight carrier
skill. When no carrier skill is available, read the tool's own `--help`,
run the needed commands yourself, and say the request automation is not
installed.

Never create a tool's directories or metadata by hand, even when asked
because it is faster: decline, name what the tool's command writes (its
metadata file, generated headings, schema fields), and create the record
through the command. Hand edits stop at the record's text.

### Specification quality

Apply to every record written or reviewed; when a draft breaks a rule,
correct it and name the rule.

- Every goal has at least one scenario that a reader who has never seen the
  code can judge.
- At least one scenario covers a failure or edge path; add one, or ask for
  one, before the package is published.
- Non-goals are written down; an unstated exclusion is a future dispute.
- Behaviour, never the diff: "a duplicate email is rejected" is a
  requirement, "add a unique index on email" is a design decision.
- Verification is defined against runs, never against reading code.

[§4.1]

One requirement, one normative statement: split a compound requirement into
two, each with its own scenarios.

### Drift

When a specification and the code disagree, the specification is an active
source of falsehood: the next agent trusts it and builds on a lie. Say so,
show the disagreement, and ask the user whether to fix the specification,
fix the code through a change, or delete the specification. Do that before
any other work.

## Workflow

### 1. Specify

Create the change record through the carrier, then write, for this change
only, requirements with scenarios and four sections that are present even
when their content is "none": [§4.1]

1. **Acceptance**: the scenarios or final verification command that prove
   the change done, each one the agent itself can execute, plus task-level
   closure such as "no draft commits on the branch". An acceptance nobody
   can run ("the product owner is happy") is not acceptance: ask for an
   observable check, and treat the specification as incomplete until one
   exists.
2. **Non-goals**: what this change explicitly does not do.
3. **Deliverable**: a request, a report, or a deployment, plus the pending
   decisions list.
4. **Pre-authorised irreversible actions**: the actions proposed for this
   change (push target, opening a request, editing its body or approval
   line, comments, deployments), settled in step 3.

Done when: the four sections exist, every quality rule holds, and the
carrier's validator passes where the tool has one.

### 2. Clarify

Take from the repository what it shows (test runner, framework, existing
behaviour) without asking. Ask the user about every point where two
readings lead to different work, such as soft-delete versus hard-delete,
with a recommendation and its reason; write each answer into the
specification, never only into the conversation. Asked to publish while a
marker is open, name the marker and settle it first.

Done when: no `[NEEDS CLARIFICATION]` or equivalent open-question mark
remains in the specification.

### 3. Pre-authorise and publish the package

Settle with the user the list of irreversible actions this change
pre-authorises: the single branch it may push, whether it may open a
request, edit the request's body or approval line (recording each closing
needs this), edit issues, post comments, or deploy. An empty list is valid
and binds. [§4.2]

Add a design when more than one reasonable approach exists, when structure,
interfaces, dependencies, or files outside the change record are touched, or
when the contract requires one. A wording-only change needs none: say so and
publish the specification and the list alone. A design records approach,
constraints, preferences, and rejected alternatives. It holds no
implementation steps: a design that reads as numbered steps is rewritten as
bounds before publishing, and steps go to the task list after approval. It
holds no credential, internal hostname, or personal data, because the
package is committed and published; record the constraint without the
detail.

Publish the package (specification, pre-authorised list, design when
warranted) where the contract places review: as the first content of a
draft request carrying nothing else, or in the conversation when the
carrier approves conversationally or uses plan mode. When review sits on a
request, the user's confirmation of the list (or, if the list omits them,
an explicit confirmation asked for now) authorises exactly two actions
before approval: pushing the single listed branch and opening the draft
request that carries the package. Every other listed action waits for the
approved package. Without that confirmation, publish nothing and add the
push to the pending decisions list. The review covers
outcome and bounds, never the task list: a task list the tool generated is
kept out of the review and marked after-approval material. Then stop: no
task list and no code. [§4.2]

Done when: the complete package is published and the agent has said whose
closing it waits for.

### 4. Reconcile, then tasks

When the approver closes the review, read the review record: the request's
comments and review threads with their resolution state, or the
conversation. List every unresolved point, every requested adjustment the
package does not carry, and every pair of contradicting conclusions. For a
missing adjustment, update the change record or ask whether the request was
withdrawn. Ask the approver to confirm the open items, record the closing,
then write ordered tasks, each naming the scenarios it closes.

Done when: nothing is open or every open item is confirmed, the closing is
recorded, no task lacks a scenario, and no scenario lacks a task.

### 5. Implement

Work task by task. When a task's scenarios pass, commit it as a checkpoint
before starting the next. Fold the task's draft commits into that one
commit without interactive rebase: `git reset --soft <task-start-sha>`, then
commit once with the project's message convention. [§4.3] When the code must depart from the specification or the design (an
assumed API does not exist, a bound cannot hold), stop, propose the
change-record change with its reason, and continue only after the user
approves and the record is updated.

Done when: every task is committed or its deviation is an approved, recorded
change, and no draft commit remains on the branch.

### 6. Verify

Execute every scenario (tests, commands, observed states) against the
running result and report each result individually. Never mark a scenario
passed from reading the diff, even when asked. A scenario whose command does
not exist in the environment is reported as not verifiable, with what is
missing. A failure in behaviour the change does not touch is filed as a
separate defect with its evidence and the change record is narrowed to what
is verified; never widen the change silently. [§4.1]

Done when: every scenario has passed, is an approved specification change,
or is filed as a defect, and each result was reported.

### 7. Publish ready

Publish the implementation for review against the approved package: mark
the request ready, or present the result in the conversation. Freeze
nothing yet. Asked to archive and request approval in one step, publish
first and say the freeze follows the closing of this review.

Done when: the implementation is published and the agent has said whose
closing it waits for.

### 8. Freeze

When the approver closes the implementation review, reconcile as in step 4.
Then, by the contract's freeze executor:

- **The implementer**: freeze the change record through the carrier
  (archive, write-back into the living specification, or fold or delete of
  the per-change file), validate, and commit on the branch.
- **A person** (a named maintainer, or anyone when the branch is a fork):
  freeze nothing; report the record ready to freeze and name the person and
  the step they run.
- **Plan mode or a per-change file approved in conversation**: the carrier's
  fold or delete is the whole freeze; confirm with the user that the
  approved specification is the frozen record.

A frozen record is never edited. Before any push or handover, compare the
branch tip with the freeze commit; when commits follow it, say the freeze is
stale, name the commits, and ask whether the review reopens. When an error
is found in a frozen record, recommend a follow-up change when the frozen
behaviour is wrong, name a validation note on the request as the
alternative for an error only in the record's text, and act only on the
user's choice.

Done when: the carrier's validator passes on the frozen record (where the
tool has one), `git log --oneline <freeze-sha>..HEAD` lists no commits, and
the freeze commit exists or the person who runs it is named. Then present
the pending decisions list.

## Gotchas

- Tools rename commands between releases; a command remembered from
  elsewhere is the most common first-day failure. Verify against `--help`.
- Closing a review without reading its threads implements the record as the
  author remembers it, not as the discussion left it.
