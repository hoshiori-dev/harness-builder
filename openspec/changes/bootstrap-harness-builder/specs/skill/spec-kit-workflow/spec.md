# Spec Delta

## Purpose

Governs what an agent that loaded `spec-kit-workflow` observably does when a project runs Spec-Kit features through pull or merge requests: the approval package (specification and plan, tasks after approval), completion as every task of every touched feature ticked because the kit archives nothing, the lock as a declaration on the request naming a commit, the `spec:` progress labels, and the GitHub or GitLab automation it produces for the project. Ships to Claude Code, Codex, and Antigravity. Non-goals: running the kit's own commands to create or implement one feature, choosing a carrier or deciding whether to adopt spec-driven development, setting the project's specification contract, any `/spec` comment command, and projects on OpenSpec or a lightweight carrier.

## ADDED Requirements

### Requirement: Triggering
The skill SHALL load when a project that runs Spec-Kit asks how a feature's specification and plan pass approval, what must be complete before a request is ready, what locks a feature when nothing is archived, what the progress labels mean, or to install the feature check and labels; it SHALL NOT load for running the kit's own commands on one feature, for choosing a spec tool, or for a project on another framework.

#### Scenario: Approval order question
- **WHEN** the user says "does the plan.md of our Spec-Kit feature need to be approved before we write tasks.md?"
- **THEN** the skill loads

#### Scenario: Readiness question
- **WHEN** the user says "our specs/004-export feature has two unticked tasks; can I mark the PR ready?"
- **THEN** the skill loads

#### Scenario: Automation install request
- **WHEN** the user says "add a progress label and a feature check to CI for our Spec-Kit repository"
- **THEN** the skill loads

#### Scenario: Kit command request
- **WHEN** the user says "run the specify command to start the export feature and fill in the spec"
- **THEN** the skill does not load

#### Scenario: Tool choice question
- **WHEN** the user says "should this project use Spec-Kit or OpenSpec for its specs?"
- **THEN** the skill does not load

#### Scenario: Other framework
- **WHEN** the user says "our OpenSpec change is implemented; how do we archive it and label the PR?"
- **THEN** the skill does not load

### Requirement: Behavior: Precedence and confirmation
The agent SHALL apply an explicit user instruction first, then the project's recorded specification contract, then the skill's defaults; SHALL settle from the repository only what is observable there (the specs directory, the kit's files, the platform); and SHALL present every default as a recommendation with its reason and wait for the user's choice rather than deciding.

#### Scenario: Contract contradicts a default
- **WHEN** the project's contract names a different lock than a declaration on the request
- **THEN** the agent applies the contract's lock and says the skill's default was not used

#### Scenario: Request shape unknown
- **WHEN** the contract does not record whether a feature's specification and implementation travel in one request or two
- **THEN** the agent recommends the combined shape with its reason, names the split shape as the alternative, and asks before configuring anything

### Requirement: Behavior: The approval package is the specification and the plan
The agent SHALL treat a feature's `spec.md` and `plan.md` together as the approval package a draft request opens with, SHALL treat `tasks.md` as after-approval material even when the kit generated it, and SHALL require the plan to bound the approach (constraints, preferences, rejected alternatives) rather than list steps, proposing any rewrite of the user's plan and editing it only after the user agrees.

#### Scenario: Reviewer's set
- **WHEN** the user asks what the reviewer is handed at the approval gate
- **THEN** the agent answers the specification and the plan, and says the task list follows the approval

#### Scenario: Plan written as steps
- **WHEN** the plan reads as an ordered implementation procedure
- **THEN** the agent says the plan lists steps instead of bounding the approach, recommends recasting it as approach, constraints, preferences, and rejected alternatives under the kit's template headings with its reason, and edits the plan only after the user agrees

#### Scenario: Tasks generated early
- **WHEN** the kit has already generated `tasks.md` before the specification is approved
- **THEN** the agent marks it as after-approval material on the request and keeps it out of the review

### Requirement: Behavior: No validator, so headings are checked and said so
Because the kit ships no programmatic validator, the agent SHALL check a feature directory against the kit's template headings, SHALL say that this is a heading check and no programmatic validation exists, and SHALL check what the project's installed kit version of the feature script does (numbered directory, branch or no branch) before asserting it to the user.

#### Scenario: Validation asked
- **WHEN** the user asks to validate a feature directory
- **THEN** the agent lists the template headings that are present and missing and states that no programmatic validator exists

#### Scenario: Hand-made feature directory
- **WHEN** a feature directory was created by hand rather than through the kit
- **THEN** the agent warns that the kit's later steps may not find what they read and recommends recreating it through the kit

#### Scenario: Branch assumption
- **WHEN** the user assumes the kit's feature script created a branch for the feature
- **THEN** the agent reads the project's copy of the feature script before answering, and when it creates no branch says so and points the user to the project's branching rule

### Requirement: Behavior: Completion is every task ticked, because the kit archives nothing
The agent SHALL state that Spec-Kit has no archive operation; for a request that carries implementation (the combined shape, or the split shape's implementation request) SHALL treat it as ready only when every task of every touched feature is ticked, counting a missing task list or one with no checkbox as not started; SHALL refuse to tick a task whose verification did not run; and on a spec-anchored project SHALL name the project's own rule for updating the living specification.

#### Scenario: Ready with an open task
- **WHEN** the user asks to mark the request ready while a touched feature's task list has an open item
- **THEN** the agent refuses, names the feature and the task, and, when the check job is installed, says it would fail

#### Scenario: Feature without a task list
- **WHEN** a touched feature has its specification and plan but no `tasks.md`
- **THEN** the agent treats the feature as not started, admits it on a draft request or a split-shape specification request, and refuses to mark an implementation request ready until the task list exists and is fully ticked

#### Scenario: Archive asked
- **WHEN** the user asks how to archive the finished feature
- **THEN** the agent says the kit archives nothing, completion is the fully ticked task list, and a spec-anchored project updates its living specification per its recorded rule

#### Scenario: Tick without verification
- **WHEN** the user asks to tick a task whose named verification has not run
- **THEN** the agent declines, runs or asks to run the verification, and ticks only after it passes

### Requirement: Behavior: The lock is a declaration naming the commit
Because the kit has no archive, the agent SHALL record the lock as a declaration on the request, written when the gate owner (the person the project's contract names as approving the specification and plan) closes the review, stating that the review closed with both files unchanged and naming the commit they stand at; SHALL treat any later change to either as a new approval round; and SHALL detect a spent lock (a commit after the named one touching either file) before pushing or handing over.

#### Scenario: Review closes
- **WHEN** the gate owner closes the review of the specification and the plan
- **THEN** the agent drafts the declaration naming the commit, posts it only when the contract or the request's pre-authorised actions allow posting and otherwise hands the draft to the user or lists the post under pending decisions, and says that nothing mechanical enforces it

#### Scenario: Spent lock
- **WHEN** the specification changed in a commit after the one the declaration names
- **THEN** the agent says the approved version no longer exists and asks for the gate again before pushing or handing over

#### Scenario: Declaration skipped
- **WHEN** the user wants to skip the declaration
- **THEN** the agent says the approval would then follow the branch with no version to name, challenges once, and follows the user's choice

### Requirement: Behavior: Progress labels are read, never applied by hand
The agent SHALL explain the three progress labels (`spec:not-started`, `spec:in-progress`, `spec:done`) as derived from the touched features' task lists by the installed automation, SHALL never apply or remove one by hand, and SHALL say that a request touching no feature carries none.

#### Scenario: Label asked
- **WHEN** the user asks why the request carries `spec:in-progress`
- **THEN** the agent explains that a touched feature has both ticked and open tasks and that the label changes on the next run, not by hand

#### Scenario: Manual label requested
- **WHEN** the user asks the agent to set `spec:done` on the request
- **THEN** the agent declines, says the label is workflow-owned, and points at the open task that keeps it from changing

### Requirement: Behavior: The automation is produced per platform, fork-safe
When asked to install the automation, after the user has confirmed the request shape and the files to produce, the agent SHALL produce for the observed platform a check job joining the existing checks workflow and its gate and a progress-label job, every privileged job running on the base ref, reading the head as data, with explicit least permissions and SHA-pinned actions; SHALL add the three labels to the label file; SHALL install no comment command; and SHALL say nothing installed pushes.

#### Scenario: GitHub install
- **WHEN** the user asks to install the automation in a GitHub repository whose base has a checks workflow with a gate
- **THEN** the agent lists the files it would add or change and writes only after the user agrees; the check job then joins that workflow and the gate's dependencies, the label workflow carries explicit permissions and SHA-pinned actions, the three labels are in the label file, and the agent says nothing installed archives or pushes

#### Scenario: Split shape, no ticked task
- **WHEN** a ready request on a split-shape project carries the specification and the plan with no ticked task
- **THEN** the produced check admits it, and fails a later request of the same project that ticked one task and left the rest open

#### Scenario: Privileged job needing head documents
- **WHEN** a produced job that runs with a writable token needs a touched feature's documents
- **THEN** it checks out the base and reads the head through the deposited script's API snapshot, and no produced step fetches or checks the head out

#### Scenario: GitLab install
- **WHEN** the user asks to install the automation in a GitLab project
- **THEN** the agent produces the jobs fragment and label rows, states that the label takes effect on the next pipeline, and refuses running a fork's pipeline in the parent project as a workaround

#### Scenario: No checks workflow to join
- **WHEN** the repository has no checks workflow or gate for the check job to join
- **THEN** the agent says so, recommends that the hard-boundary layer be built first by describing the need, and installs nothing until the user decides

### Requirement: Behavior: Remote writes are dry-run, approved, applied, read back
The agent SHALL show the label additions and removals a sync of the label file would make on the remote before any write, SHALL apply them only after the user approves that plan, and SHALL read the remote back afterwards and report the difference; when the token cannot write or a platform action needs a maintainer (required check, ruleset), the agent SHALL list it under pending decisions and continue with the rest of the install.

#### Scenario: Label sync
- **WHEN** the project's label file holds the three progress labels and the remote lacks them
- **THEN** the agent prints the additions and removals, waits for approval, applies them, and reports the labels the remote holds afterwards

#### Scenario: Token cannot write labels
- **WHEN** the agent's token cannot create labels on the remote
- **THEN** the agent lists the label sync under pending decisions with the exact delta, finishes the file-level install, and applies nothing by another route

#### Scenario: Required check needs a maintainer
- **WHEN** marking the feature check required needs repository settings the agent cannot change
- **THEN** the agent lists the exact setting under pending decisions with the recommended value and continues

### Requirement: Behavior: Deposited script is the project's own management code
The agent SHALL deposit the management script as the project's own `scripts/spec_kit_features.py`, the path the produced jobs call, SHALL confirm with the user whether to use it as is or rewrite it in the project's agreed management language, and SHALL tell the user that later fixes to the plugin do not reach the delivered copy.

#### Scenario: Script deposited
- **WHEN** the automation is installed
- **THEN** the project holds its own copy with its test, the produced jobs call that path, and the handoff says the copy is the project's and is not kept identical to the plugin's

#### Scenario: Project language differs
- **WHEN** the project's agreed management language is not Python
- **THEN** the agent offers its Python script as a reference implementation to rewrite, and writes nothing until the user chooses

### Requirement: Behavior: Handoffs by description
The agent SHALL route whether or at which level to adopt spec-driven development and what a good specification is to the skill that teaches spec-driven development and specification quality, and setting or changing the project's rules (approval mode, completion rule, lock, request shape) to the skill that owns the specification and completion layer, each by describing the need, never by an install command; when the user declines a handoff, it SHALL apply the contract or the defaults and say so.

#### Scenario: Adoption question
- **WHEN** the user asks whether the project should adopt spec-driven development at all
- **THEN** the agent describes the question for the skill that teaches spec-driven development to pick up and prints no install command

#### Scenario: User declines the contract handoff
- **WHEN** the user wants the ticked task list recorded as the project's completion rule but declines the layer builder
- **THEN** the agent installs the automation with the defaults, says so, and names the contract update as remaining work

### Requirement: Outcomes
Given a repository that runs Spec-Kit, the agent SHALL produce the observable results below without the user naming any file, job, or label.

#### Scenario: Ready check on a touched feature
- **WHEN** the user asks "is PR 17 ready?" in a repository where `specs/003-import/tasks.md` holds `- [x] T001`, `- [ ] T002`, and `- [ ] T003`
- **THEN** the agent answers no, names `003-import` and tasks T002 and T003, says completion is every task ticked because the kit archives nothing, and does not tick anything

#### Scenario: Automation installed end to end
- **WHEN** the user asks to add the Spec-Kit request automation to a GitHub repository with a checks workflow and an aggregator gate
- **THEN** the agent confirms the request shape and lists the files before writing, and the repository then gains a check job in that workflow listed in the gate's dependencies, a label workflow with explicit permissions and every action SHA-pinned, three `spec:` label rows, `scripts/spec_kit_features.py` with its test, no comment-command workflow, no placeholder left in `.github/`, no step that fetches or checks out the head in a privileged job, and a handoff stating that the label delta was applied after approval and read back, or listed under pending decisions when the token could not write

#### Scenario: Lock recorded after review
- **WHEN** the reviewer approves the specification and plan of `specs/005-billing` at commit `a1b2c3d` and the user asks what to do next
- **THEN** the agent produces a declaration for the request stating the review closed with both files unchanged at `a1b2c3d`, says tasks may now proceed, and says a later edit to either file reopens the gate

### Requirement: Script: scripts/spec_kit_features.py
The bundled script SHALL resolve a request's touched features from `--base` and `--head` git refs and offer `related`, `status`, `show`, `check`, and `labels`, none editing the working tree. It SHALL be stdlib-only Python 3.10+ under uv and plain `python3`, offer `--help` with a usage example, print data on stdout (JSON with `--json`) and diagnostics on stderr, summarise output above about 10,000 characters unless `--full` or `--output` is passed, be idempotent, and exit 0/1/2.

#### Scenario: Help
- **WHEN** the script runs with `--help`
- **THEN** it prints usage naming the five subcommands and a usage example and exits 0

#### Scenario: Representative run
- **WHEN** a touched feature has its specification, plan, and a fully ticked task list and `check --base <base> --head <head>` runs
- **THEN** it exits 0, and `status --json` with the same refs reports the feature as done

#### Scenario: Open task when ready
- **WHEN** a touched feature has an open task and `check` runs without `--draft`
- **THEN** it exits 1 naming the feature and the task, and with `--draft` it exits 0 and prints the task as a warning on stderr

#### Scenario: Missing plan
- **WHEN** a touched feature has a specification but no plan
- **THEN** `check` exits 1 and names the feature and the missing file

#### Scenario: Missing task list
- **WHEN** a touched feature has a specification and a plan but no `tasks.md`
- **THEN** `check --draft` and `check --shape split` on a specification request exit 0 reporting the feature as not started, and `check` on a ready implementation request exits 1 naming the feature and the missing file

#### Scenario: Long show output
- **WHEN** `show` would print more than about 10,000 characters of feature documents
- **THEN** it prints a summary with the sizes and says how to get the whole text, and prints it whole with `--full` or writes it with `--output`

#### Scenario: Repeated run
- **WHEN** the identical `check` and `status` commands run a second time
- **THEN** the output is identical and nothing in the tree changes

#### Scenario: Bad arguments
- **WHEN** the script is invoked with an unknown option, or `show --feature` names a feature the request does not touch
- **THEN** it exits 2 and prints a diagnostic naming the option or listing the touched features

#### Scenario: Plain interpreter
- **WHEN** the script runs through `python3` on a machine without uv
- **THEN** it behaves identically to a run through `uv run --script`

### Requirement: Script: assets/spec_kit_features.py
The deposited script SHALL offer `snapshot`, `check`, `status`, and `labels`, none editing the tree, reading the head from `--base`/`--head` refs or from a `--snapshot` document built from the platform API without fetching or checking out the head. It SHALL meet the bundled script's interface rules: stdlib-only Python 3.10+ under uv or `python3`, `--help` with a usage example, stdout data, stderr diagnostics, long output summarised unless `--full` or `--output`, idempotent, exits 0/1/2.

#### Scenario: Help
- **WHEN** the script runs with `--help`
- **THEN** it prints usage naming the four subcommands and a usage example and exits 0

#### Scenario: Snapshot versus git refs
- **WHEN** `snapshot` runs against a request and `status`, `check`, and `labels` run against the resulting document
- **THEN** their output is identical to the same subcommands run with `--base` and `--head` over a clone of that request

#### Scenario: Partial read
- **WHEN** `snapshot` reaches a file, byte, or API-call cap, meets a truncated tree, or finds a document it cannot decode as text
- **THEN** it exits 1 naming the path or endpoint and writes no document

#### Scenario: Snapshot for another specs directory
- **WHEN** a snapshot built for a different specs directory is passed with `--snapshot`
- **THEN** every subcommand refuses it with exit 1 naming both directories instead of matching against no feature

#### Scenario: Split shape with no ticked task
- **WHEN** `check --shape split` runs on a ready request whose touched feature has no ticked task
- **THEN** it exits 0, and exits 1 once the same feature has one ticked and one open task

#### Scenario: Missing task list in the snapshot
- **WHEN** the snapshot holds a feature with a specification and a plan and no `tasks.md`
- **THEN** `check --shape split` on a specification request and `check --draft` exit 0, `check` on a ready implementation request exits 1 naming the missing file, and `labels` computes `spec:not-started`

#### Scenario: Labels with a stale current label
- **WHEN** `labels --current spec:not-started` runs on a request whose touched feature has every task ticked
- **THEN** it prints `spec:done` to add and `spec:not-started` to remove, and `labels --taxonomy` prints exactly the three managed `spec:` names

#### Scenario: Long snapshot output
- **WHEN** `snapshot` would print a document longer than about 10,000 characters to stdout
- **THEN** it prints a summary naming the feature count and size unless `--full` is passed, and `--output <path>` writes the whole document to that path

#### Scenario: Repeated run
- **WHEN** the identical `check` command runs a second time against the same snapshot
- **THEN** the output is identical and nothing in the tree changes

#### Scenario: Bad arguments
- **WHEN** the script is invoked with an unknown option or with neither refs nor a snapshot
- **THEN** it exits 2 and prints a diagnostic naming what is missing
