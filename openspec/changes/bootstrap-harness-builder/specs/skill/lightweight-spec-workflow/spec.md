# Spec Delta

## Purpose
Governs what an agent that loaded the `lightweight-spec-workflow` skill observably does when a project aligns on a change without a specification framework: choosing between plan mode and a per-change `SPEC.md`/`PLAN.md`, drafting the specification so it answers the four completion questions, taking approval in the conversation, running the done-check itself, and folding, deleting, or writing back the specification at the freeze. Ships to Claude Code, Codex, and Antigravity. Non-goals: projects that run OpenSpec or Spec-Kit (their carrier skills), deciding whether or at which level to adopt spec-driven development (the methodology skill), setting or changing the project's recorded spec contract (the builder that owns the specification and completion layer), installing any platform automation, and writing API or test specifications.

## ADDED Requirements

### Requirement: Triggering
The skill SHALL load when a project without a specification framework asks to agree on a change before coding, to draft or review a per-change `SPEC.md` or `PLAN.md`, whether a change is small enough for plan mode alone, or what happens to the specification once the change is reviewed; it SHALL NOT load for a project that runs OpenSpec or Spec-Kit, for the question of whether to adopt spec-driven development at all, or for API, protocol, or test specifications.

#### Scenario: Agreement before coding, no framework
- **WHEN** the user says "before you touch the export code, write down what we're agreeing to so I can approve it; we don't use OpenSpec or anything like that"
- **THEN** the skill loads

#### Scenario: Per-change document requested
- **WHEN** the user says "draft a SPEC.md for the retry logic so we're aligned, then plan it"
- **THEN** the skill loads

#### Scenario: Small-edit question
- **WHEN** the user says "this is a two-line config fix, do we really need a written spec or is a plan enough?"
- **THEN** the skill loads

#### Scenario: Specification after review
- **WHEN** the user says "review on the export branch is done and we're about to mark the PR ready; what do we do with the SPEC.md sitting next to it?"
- **THEN** the skill loads

#### Scenario: OpenSpec project
- **WHEN** the user says "our OpenSpec change for the export is done; how do we archive it?"
- **THEN** the skill does not load

#### Scenario: Spec-Kit project
- **WHEN** the user says "run specify for the export feature and then write the plan"
- **THEN** the skill does not load

#### Scenario: Adoption question
- **WHEN** the user says "should this repo adopt spec-driven development at all, and how strictly?"
- **THEN** the skill does not load

#### Scenario: API specification
- **WHEN** the user says "write the OpenAPI spec for the export endpoint"
- **THEN** the skill does not load

### Requirement: Behavior: Carrier chosen by the size of the change
The agent SHALL recommend plan mode for a small edit and a per-change `SPEC.md` (plus `PLAN.md` when the approach needs bounding) for mid-size work, stating the reason and the alternative, and SHALL wait for the user's choice; a project rule already recorded in the repository SHALL be applied without asking. A plan presented in plan mode SHALL still answer the four completion questions. Work too large for one per-change file SHALL be named as such, not stretched onto the carrier.

#### Scenario: Mid-size change
- **WHEN** the user asks to align on a feature that touches several modules and needs a migration
- **THEN** the agent recommends `SPEC.md` beside the change with `PLAN.md` for the approach, gives the reason, names plan mode as the alternative, and writes nothing until the user chooses

#### Scenario: Small edit
- **WHEN** the user asks to align on a one-file fix with no new behaviour
- **THEN** the agent recommends plan mode, and the plan it presents names the done-check command, the non-goals, the deliverable, and the pre-authorised irreversible actions before any edit

#### Scenario: Change spanning several features
- **WHEN** the change spans several features or needs a living specification that outlives the change
- **THEN** the agent says the lightweight carrier is undersized, describes the builder that owns the specification and completion layer as the place to choose a framework, and proposes splitting the work into per-change pieces meanwhile

#### Scenario: Project rule already recorded
- **WHEN** the project's knowledge states that every change gets a `SPEC.md`
- **THEN** the agent follows that rule without re-asking and says which file stated it

#### Scenario: Framework detected during work
- **WHEN** the agent finds an OpenSpec or Spec-Kit directory in the repository while drafting
- **THEN** it stops, says the project already has a carrier, and offers the matching carrier skill by description instead of continuing

### Requirement: Behavior: The specification answers the four completion questions
The drafted specification SHALL state how completion is judged (acceptance scenarios, a check command the agent can run itself, and the task-end condition that no draft commits remain on the branch), what is explicitly not done, what is delivered (pull request, report, or deployment, plus a pending decisions list), and which irreversible actions are pre-authorised (branch pushed, pull request or comments allowed). A draft missing any answer SHALL be flagged, never presented for approval.

#### Scenario: Draft presented for approval
- **WHEN** the agent presents a `SPEC.md` for approval
- **THEN** a reader finds a done-check command with the no-draft-commits condition, a non-goals list, a deliverable statement, and a pre-authorised actions list, each under its own heading

#### Scenario: User supplies no non-goals
- **WHEN** the user describes the goal and says "no exclusions come to mind"
- **THEN** the agent proposes the non-goals it infers from the goal, marks them as proposals, and asks the user to confirm or strike each before approval

#### Scenario: No irreversible action authorised
- **WHEN** the user authorises no push, pull request, or comment for the change
- **THEN** the specification records "none" under pre-authorised actions and the agent stops at a local commit, adding any remote step to the pending decisions list

### Requirement: Behavior: Scenarios are judgeable and describe behaviour
Every goal in the specification SHALL have at least one scenario a reader who has not seen the code can judge, at least one scenario across the specification SHALL cover a failure or edge path, and goals SHALL describe observable behaviour, not the diff. The agent SHALL rewrite a goal phrased as an implementation into the behaviour it produces and SHALL add a failure-path scenario when the draft has none.

#### Scenario: Goal phrased as implementation
- **WHEN** the user writes "add a unique index on email" as a goal
- **THEN** the agent rewrites the goal as the observable behaviour (a duplicate email is rejected with the stated response) and keeps the index as a note under the plan, not the specification

#### Scenario: No failure path
- **WHEN** every scenario in the draft describes success
- **THEN** the agent adds at least one scenario for a failing or boundary input before presenting the draft

### Requirement: Behavior: Approval is given in the conversation and fixes the scope
The agent SHALL present the draft specification (and plan, when one exists) in the conversation, or write it to the agreed location uncommitted, SHALL wait for an explicit approval, and SHALL make no code change before it. After approval the scope SHALL be fixed: a later request outside it SHALL be raised as an amendment to approve first, not silently absorbed. An approved plan SHALL NOT be read as authorising any action beyond those the specification lists.

#### Scenario: Approval given
- **WHEN** the user replies that the specification is approved
- **THEN** the agent begins implementation and the first commit includes the `SPEC.md` beside the change

#### Scenario: Approval withheld
- **WHEN** the user asks for changes to the draft
- **THEN** the agent revises the specification, presents it again, commits nothing, and writes no code

#### Scenario: Scope added mid-implementation
- **WHEN** the user asks for an extra behaviour not in the approved specification
- **THEN** the agent names it as outside the approved scope, proposes an amendment or a follow-up change, and continues the approved work until the user decides

### Requirement: Behavior: The specification is committed beside the change
Once approved, a `SPEC.md` or `PLAN.md` SHALL be committed in the change's branch next to the work it governs (in a location the project's conventions name, or a per-change directory the agent proposes) and SHALL be referenced from the pull request or report; after approval it SHALL NOT be left as an uncommitted file or placed in a system temporary directory.

#### Scenario: Location unspecified
- **WHEN** the project has no convention for where specifications live
- **THEN** the agent proposes one location with its reason, asks before creating it, and says once that the files placed there are the project's own

#### Scenario: Pull request or report opened
- **WHEN** the agent opens the pull request or writes the report the specification named as deliverable
- **THEN** that deliverable links or quotes the specification and lists any pending decisions

### Requirement: Behavior: The agent runs the done-check itself
Before declaring the change complete the agent SHALL run the final check command the specification names, SHALL execute the acceptance scenarios against the running result, not judge them from the diff, and SHALL verify that the branch holds only task-level commits; a failing check, scenario, or remaining draft commit SHALL be reported with the failing item named, and the change SHALL NOT be declared complete.

#### Scenario: Check passes
- **WHEN** the done-check command exits 0, every scenario is exercised, and the branch holds only task-level commits
- **THEN** the agent reports completion naming the command, each scenario's result, and the commits on the branch

#### Scenario: Check fails
- **WHEN** the done-check command exits non-zero
- **THEN** the agent names the failing output, does not declare completion, and either fixes within the specification or raises the gap to the user

#### Scenario: Scenario cannot be exercised
- **WHEN** a scenario needs an environment the agent cannot reach
- **THEN** the agent says which scenario is unverified and why, and lists it in the deliverable instead of marking it passed

#### Scenario: Draft commits remain on the branch
- **WHEN** unsquashed draft commits from a task remain on the branch at the done-check
- **THEN** the agent does not declare completion, squashes them per task non-interactively (soft reset to the task's start, then one commit per task), pushes nothing until done, and only then reports completion

### Requirement: Behavior: Freeze disposition follows the recorded level
The agent SHALL read the project's level from its recorded specification contract and apply it without asking: at spec-first it SHALL recommend folding the lasting content into documentation, with deletion as the alternative, and act on the user's choice; at spec-anchored it SHALL propose updating the living specification the contract names and removing the per-change file. With no contract it SHALL state spec-first as the default, ask the user to confirm it, and name the level question as open.

#### Scenario: Contract records spec-first
- **WHEN** the project's contract records spec-first and the deliberation on the implementation has closed
- **THEN** the agent recommends folding into documentation, names deletion as the alternative, asks no level question, and acts only on the user's choice

#### Scenario: No contract recorded
- **WHEN** no contract declares the project's level and the deliberation on the implementation has closed
- **THEN** the agent says spec-first is the default for a project without a spec framework, names spec-anchored as the alternative, asks the user to confirm for this change, and describes the methodology skill as the place to settle the level for the project

#### Scenario: Contract records spec-anchored
- **WHEN** the project's contract names a living specification
- **THEN** the agent proposes the edit that writes the accepted behaviour into that specification and removes the per-change `SPEC.md`, and says which contract entry required it

#### Scenario: User keeps the file
- **WHEN** the user declines both folding and deletion
- **THEN** the agent leaves the file, records the decision in the pending decisions list, and states that the file will drift from the code

### Requirement: Behavior: The freeze happens inside the request by the named executor
The fold, deletion, or living-specification update SHALL happen on the change's branch after the gate owner closes deliberation on the implementation and before the request is marked ready, performed by whoever the contract names as freeze executor; with no contract the agent SHALL say a person performs it by default. When the executor is a person the agent SHALL propose the exact edit and wait rather than commit it; a commit after the freeze SHALL be named as making it stale.

#### Scenario: Contract names a person
- **WHEN** the contract records that a person freezes and the deliberation has closed
- **THEN** the agent presents the fold or deletion as a proposed edit, commits nothing, and marks the request ready only after the person has made the edit

#### Scenario: Contract names the agent
- **WHEN** the contract records that the agent freezes in the request
- **THEN** the agent commits the fold, deletion, or update on the branch before marking the request ready and names that commit in the deliverable

#### Scenario: Asked to freeze before deliberation
- **WHEN** the user asks to delete the `SPEC.md` while the implementation is still under review
- **THEN** the agent says the freeze follows the close of deliberation, leaves the file, and offers to mark the request ready for review instead

#### Scenario: Commit after the freeze
- **WHEN** a commit lands on the branch after the fold or deletion and before the push
- **THEN** the agent says the freeze is stale, names the commit, and asks whether the deliberation reopens before pushing

### Requirement: Behavior: Committed specification carries no scaffold text
A committed `SPEC.md` or `PLAN.md` SHALL contain no placeholder marker, no how-to-use or instruction text, and no heading without content for this change; every section SHALL be written for the change at hand.

#### Scenario: Specification committed from a starting shape
- **WHEN** the agent commits a `SPEC.md` it produced from a starting shape
- **THEN** the file contains no placeholder markers, no how-to-use text, and only headings that carry content for this change

#### Scenario: Plan not wanted
- **WHEN** the user wants `SPEC.md` but declines `PLAN.md`
- **THEN** the agent commits only `SPEC.md` and keeps the approach as a short section within it

### Requirement: Behavior: Methodology and contract questions are handed off by description
The agent SHALL route adoption and level questions to the skill that teaches the methodology, and changes to the project's recorded contract (approval mode, completion rule, level, freeze executor) to the builder that owns the specification and completion layer, each described rather than named; when the user declines, the agent SHALL continue the carrier work with the four completion questions as its default contract and say the practice-level question stays open.

#### Scenario: Adoption question during work
- **WHEN** the user asks mid-drafting whether this project should do spec-driven development at all
- **THEN** the agent describes the methodology skill as the place for that question and offers to continue the draft meanwhile

#### Scenario: Contract change requested
- **WHEN** the user wants "every change needs a SPEC.md" written into the project's rules
- **THEN** the agent describes the layer builder that records the contract, offers it, and does not edit the project's knowledge files itself

#### Scenario: Handoff declined
- **WHEN** the user declines the offered skill
- **THEN** the agent finishes the specification with the four questions as the contract and lists the unrecorded rule in the pending decisions

### Requirement: Behavior: Confirm, do not guess
For every point where two readings would lead to different work (carrier, location, non-goals, pre-authorised actions, fold-or-delete choice) the agent SHALL ask the user, attaching one recommendation with its reason; facts observable in the repository (framework directories, existing conventions, the recorded contract, the test command) SHALL be settled without asking. A blocked decision SHALL be added to the pending decisions list while unblocked work continues.

#### Scenario: Test command observable
- **WHEN** the repository's task runner defines a test recipe
- **THEN** the agent proposes that recipe as the done-check command without asking which command runs the tests

#### Scenario: User unavailable for a decision
- **WHEN** the user leaves the branch-to-push question unanswered and other work remains
- **THEN** the agent finishes the local implementation, does not push, and presents the question in the pending decisions list at the end

### Requirement: Outcomes
Given a project with no specification framework, the agent SHALL carry a change from alignment to the freeze so that a reviewer finds an approved specification answering the four questions, an executed done-check on a branch of task-level commits, and a disposition of the specification file made inside the request.

#### Scenario: Feature carried end to end
- **WHEN** the user asks to add rate limiting to an API in a repository with a `justfile` test recipe and no spec tooling, and approves the drafted specification
- **THEN** the branch holds a committed `SPEC.md` with a done-check command, non-goals, deliverable, pre-authorised actions, and at least one failure-path scenario; the agent ran the done-check and reported each scenario; the branch holds only task-level commits; no push happened unless the specification authorised it; and the agent proposed the file's disposition after deliberation closed and before the request was marked ready

#### Scenario: Small fix in plan mode
- **WHEN** the user asks to fix a typo in a configuration key and agrees to plan mode
- **THEN** no `SPEC.md` is created, the plan presented before editing names the check command, the non-goals, the deliverable, and the authorised actions, and the agent runs the check after the edit

#### Scenario: Specification rejected twice
- **WHEN** the user rejects the first two drafts for missing non-goals and for a goal phrased as implementation
- **THEN** no code is written before the third draft is approved, and the approved draft contains confirmed non-goals and behaviour-phrased goals
