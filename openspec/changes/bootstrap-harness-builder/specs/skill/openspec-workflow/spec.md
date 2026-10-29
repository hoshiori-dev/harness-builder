# Spec Delta

## Purpose

Governs what an agent that loaded `openspec-workflow` observably does when a project runs OpenSpec changes through pull or merge requests, shipping to Claude Code, Codex, and Antigravity: creating, validating, and archiving changes through the tool's commands, the approval package, the spec-less marker, the archive inside the request after the review closes, the withheld archive check and `spec:*` labels, and the GitHub or GitLab automation installed from its assets. Non-goals: choosing a carrier, teaching spec-driven development, setting the project's specification contract, comment commands on requests, remote label sync tooling, and any job that archives on a person's behalf.

## ADDED Requirements

### Requirement: Triggering
The skill SHALL load when a project that runs OpenSpec asks to create, validate, or archive a change, how a change is approved or archived before its pull or merge request merges, what the `spec:*` labels or the archive check mean, or how to install or repair that automation on GitHub or GitLab; it SHALL NOT load for choosing between carriers, for what a specification must answer or whether to adopt the practice, or for a project on another framework.

#### Scenario: Archive question
- **WHEN** the user says "our OpenSpec change is implemented; what has to happen before this PR can merge?"
- **THEN** the skill loads

#### Scenario: Label question
- **WHEN** the user says "the PR lost its spec:approved label after I edited the proposal; is that expected?"
- **THEN** the skill loads

#### Scenario: Automation install
- **WHEN** the user says "wire the openspec validation and the approval labels into this repository's CI"
- **THEN** the skill loads

#### Scenario: Change creation
- **WHEN** the user says "create a new OpenSpec change called export-csv and validate it"
- **THEN** the skill loads

#### Scenario: Carrier choice
- **WHEN** the user says "should this library use OpenSpec or Spec-Kit?"
- **THEN** the skill does not load

#### Scenario: Methodology question
- **WHEN** the user says "before we code the export feature, what does its spec have to answer so we know when it is done?"
- **THEN** the skill does not load (the methodology skill does)

#### Scenario: Other framework
- **WHEN** the user says "how do Spec-Kit features get approved before the PR merges?"
- **THEN** the skill does not load

### Requirement: Behavior: Contract first, confirm before choosing
The agent SHALL apply precedence of an explicit user instruction, then the project's specification contract named by its entrypoint, then this skill's defaults; where the contract is silent on a point that changes the work (approval mode, when a design is warranted, archive executor), the agent SHALL ask with one recommended option and its reason, and SHALL NOT choose silently.

#### Scenario: Contract names a different executor
- **WHEN** the project's contract says a maintainer archives and the skill's default says the implementer does
- **THEN** the agent follows the contract and says which rule it applied

#### Scenario: Contract silent on the design rule
- **WHEN** the agent cannot find whether the project requires a design for the change at hand
- **THEN** it recommends the default rule with its reason, names the alternative, and waits for the user's choice before publishing the package

### Requirement: Behavior: Archive executor default
Absent a contract rule, the agent SHALL state the default executor identically to the methodology skill: the implementer archives, after the review closes, by the tool's non-interactive archive command, and on a fork's branch a maintainer does so; it SHALL say in its reply that the default applied and name the specification and completion layer builder by role as the way to record a different rule.

#### Scenario: No contract
- **WHEN** the project has no specification contract and the review of the request has closed
- **THEN** the agent says the implementer default applied, archives through the tool's command, and names the layer builder by role for recording another rule

#### Scenario: Fork branch
- **WHEN** the request comes from a fork and no contract names an executor
- **THEN** the agent says a maintainer runs the archive on the fork's branch, archives nothing itself, and lists the step for that person

### Requirement: Behavior: Tool commands verified, no hand-made trees
The agent SHALL run every operation the OpenSpec CLI has a command for through that command, reading the current `--help` before the first use in a session, and SHALL NOT create a change directory or its metadata by hand.

#### Scenario: Renamed command
- **WHEN** the agent's remembered command name is absent from the CLI's `--help`
- **THEN** it uses the command the help lists and does not write the change directory itself

#### Scenario: CLI missing
- **WHEN** the OpenSpec CLI is not on PATH
- **THEN** the agent reports that the CLI is missing, names it as the prerequisite the project must provide and points at the tool's own documentation without printing an install command, creates no change directory, and adds the blocked step to the pending decisions list

### Requirement: Behavior: The approval package precedes the tasks
The agent SHALL open the draft pull or merge request with the proposal, the delta specs, and the design when the project's rule warrants one, and SHALL treat the task list as after-approval material even when the tool generated it, finishing it only after the first gate the contract defines has closed: the `spec:approved` label in recorded mode, the user's stated approval in conversational mode.

#### Scenario: Propose generated the task list
- **WHEN** the tool's propose step produced the proposal, delta specs, design, and task list together on a recorded-mode project
- **THEN** the agent publishes the first three as the package, states on the request that the task list follows approval, and finishes it only after `spec:approved` is present

#### Scenario: Conversational mode
- **WHEN** the project's contract names conversational approval and the user says the package is approved
- **THEN** the agent finishes the task list, waits for no label, and records the approval in the request's description

#### Scenario: Tasks asked before the gate
- **WHEN** the user asks for the task list while the package is still under review
- **THEN** the agent says the tasks follow the gate, names the gate that is open, and writes none

### Requirement: Behavior: Spec-less harness change
For a change to the project's own harness, tooling, checks, workflows, or documents the agent SHALL say no delta spec applies, SHALL recommend no change record unless the user wants a design recorded, and when a record is wanted SHALL set `skip_specs: true`, write a proposal with Acceptance and a design only when the project's rule warrants one, and write tasks after approval.

#### Scenario: CI-only edit
- **WHEN** the change edits only the project's CI workflow
- **THEN** the agent says no delta spec applies, recommends no change record with its reason, and asks whether a recorded design is wanted

#### Scenario: Record wanted
- **WHEN** the user asks for a change record for a CI-only edit
- **THEN** the change carries `skip_specs: true`, a proposal with Acceptance, a design when the project's rule warrants one (otherwise the agent asks with the recommended rule), tasks after approval, and no delta spec

### Requirement: Behavior: Strict validation cadence
The agent SHALL run the tool's strict validator after each artifact edit, before publishing the draft, before marking the request ready, and after archiving, and SHALL fix every reported error or warning attributable to its edit before continuing.

#### Scenario: Validator fails before publish
- **WHEN** the strict validator reports a scenario heading at the wrong level
- **THEN** the agent fixes the artifact and re-validates before pushing the draft

#### Scenario: Validator passes after archive
- **WHEN** the archive command has moved the change under the archive directory
- **THEN** the agent runs the strict validator on the archived tree and reports the result before committing

### Requirement: Behavior: Acceptance and design format
The agent SHALL end every proposal with an `## Acceptance` section holding **Becomes true** and **Stays true** lists of checkable items, and SHALL give each design Goal and Non-Goal a "Checked by" clause and list decisions with their rejected alternatives and no steps.

#### Scenario: Proposal without acceptance
- **WHEN** the agent reviews a proposal that ends at its Impact section
- **THEN** it adds the Acceptance section with both lists before publishing and names the items that are not yet checkable

#### Scenario: Design with steps
- **WHEN** a design lists the order in which files are edited
- **THEN** the agent moves the order to the task list and leaves the design with bounds, decisions, and rejected alternatives

### Requirement: Behavior: Configuration carries the artifact rules
The agent SHALL record the proposal, specs, design, and tasks rules in the project's OpenSpec configuration so the tool's own skills apply them, proposing the rules and writing them only after the user confirms.

#### Scenario: Configuration without rules
- **WHEN** the automation is installed in a project whose OpenSpec configuration has no artifact rules
- **THEN** the agent proposes the rules for proposal, specs, design, and tasks in that configuration and the user confirms before they are written

#### Scenario: Existing rules contradict
- **WHEN** the configuration already carries an artifact rule that contradicts the Acceptance format
- **THEN** the agent shows both rules, recommends one, and changes nothing until the user chooses

### Requirement: Behavior: Ready first, archive after the review closes
When the last task is verified the agent SHALL mark the pull or merge request ready and archive nothing; after the review closes, when the contract or the default names the implementer as executor, it SHALL archive every related change on the request's branch through the tool's non-interactive archive command, validate strictly, and commit; otherwise it SHALL report the change ready for the named executor and archive nothing.

#### Scenario: Asked to archive and mark ready together
- **WHEN** the implementation is finished and the user asks to archive and mark the request ready in one go
- **THEN** the agent marks it ready, archives nothing, and says the archive happens after the review closes

#### Scenario: Review closed with the implementer as executor
- **WHEN** the review has closed and the contract names the implementer
- **THEN** the agent archives every related change on the branch through the archive command, validates strictly, and commits

#### Scenario: Review closed with a maintainer as executor
- **WHEN** the review has closed and the contract names a maintainer
- **THEN** the agent reports the change ready for that maintainer, names the archive command, and archives nothing

### Requirement: Behavior: Open task blocks archive
The agent SHALL refuse to archive a change whose task list has an unticked item, naming the open task, and SHALL refuse to tick a task whose verification did not run.

#### Scenario: Open task
- **WHEN** the user asks to archive a change whose task list has an unticked item
- **THEN** the agent refuses, names the open task, and archives nothing

#### Scenario: Tick without verification
- **WHEN** the user asks to tick a task whose named verification has not run
- **THEN** the agent declines, runs or asks to run the verification, and ticks only after it passes

### Requirement: Behavior: Archived record is immutable and the approval is spent by later commits
The agent SHALL never edit a change under the archive directory, and SHALL say that a commit after the archive commit spends the approval, asking for the gate again before pushing or handing over.

#### Scenario: Edit to an archived change
- **WHEN** the user asks to fix a typo in an archived change's proposal
- **THEN** the agent declines, says the archived record is immutable, and offers a new change if the behaviour must change

#### Scenario: Commit after the archive
- **WHEN** a fix is pushed after the archive commit
- **THEN** the agent says the approved version no longer exists and asks for the gate again before handing over

### Requirement: Behavior: Labels are read, never set by hand
When the project runs the recorded approval mode, the agent SHALL read `spec:pending`, `spec:approved`, and `spec:archived` as state the installed workflow maintains from the tree and an approval record, SHALL NOT apply or remove any of them, and SHALL explain that only a person with write permission adds `spec:approved` and that an edit to the package returns the request to `spec:pending`.

#### Scenario: Label lost after an edit
- **WHEN** the user asks why `spec:approved` disappeared after a proposal edit
- **THEN** the agent says the recorded package hash no longer matches, that the workflow returned `spec:pending`, and that a maintainer re-adds the label after reading the new version

#### Scenario: Asked to add the label
- **WHEN** the user asks the agent to add `spec:approved` to its own request
- **THEN** the agent declines, says the label is added by a person with write permission and recorded by the workflow, and marks the step pending

#### Scenario: Conversational-mode project asks about labels
- **WHEN** a project in conversational approval mode asks which label marks approval
- **THEN** the agent says the project records approval in conversation and carries no `spec:*` labels, and names the layer builder by role if the user wants the recorded mode

### Requirement: Behavior: The archive check is withheld, not failed
When the project runs the recorded mode, the agent SHALL explain the archive check as a required check that is withheld while a related change is unarchived on a ready request, so the merge stays blocked with nothing red, and the archive commit is what lets it report.

#### Scenario: Ready request with unarchived change
- **WHEN** a ready request still carries an unarchived related change
- **THEN** the agent explains that the required check has not reported, the merge stays blocked, nothing is red, and the archive commit is what releases it

#### Scenario: Draft with unarchived change
- **WHEN** a draft request carries an unarchived related change
- **THEN** the agent says the check warns on a draft and withholds only once the request is ready

### Requirement: Behavior: Platform and branch observed, not asked
When asked to install the automation, the agent SHALL state the platform and default branch it read from the repository's remote and SHALL ask only when neither can be read or when the user's stated target differs from what was observed.

#### Scenario: Remote readable
- **WHEN** the repository's remote names a GitHub repository with `main` as the default branch
- **THEN** the agent states both facts and asks no question about them

#### Scenario: Remote absent
- **WHEN** the repository has no remote configured
- **THEN** the agent asks for the platform and target branch with GitHub and the current branch as the recommendation

### Requirement: Behavior: Check job joins the existing checks workflow
On GitHub the agent SHALL add the check job from its assets to the project's existing checks workflow and the gate's dependencies, SHALL create a checks workflow only when none exists and the user agrees, and SHALL produce the label workflow and merge the `spec:*` label rows into the project's existing label file rather than creating a second file.

#### Scenario: GitHub install
- **WHEN** the user asks to install the automation in a GitHub repository whose base has a checks workflow with a gate
- **THEN** the agent adds the check job to that workflow and the gate's dependencies, adds the label workflow, and merges the `spec:*` rows into the existing label file

#### Scenario: No checks workflow to join
- **WHEN** the repository has no checks workflow or gate for the check job to join
- **THEN** the agent says so, recommends that the hard-boundary layer be built first by describing the need, and installs nothing until the user decides

#### Scenario: GitLab install
- **WHEN** the user asks to install the automation in a GitLab project
- **THEN** the agent produces the CI jobs fragment and merges the label rows into the project's label file, and states that labels take effect on the next pipeline

### Requirement: Behavior: Privileged jobs are fork-safe
Every produced job that runs with a writable token SHALL check out the base and read the head only as data through the deposited script's snapshot, SHALL declare explicit least permissions, and SHALL use actions pinned by SHA; the check job SHALL run on the read-only request trigger and may check out the head.

#### Scenario: Label workflow reads the head
- **WHEN** the produced label workflow needs a request's change documents
- **THEN** it checks out the base, reads the head through the deposited script's snapshot, and no step in it fetches or checks out the head

#### Scenario: Unpinned action
- **WHEN** an asset or existing workflow references an action by tag
- **THEN** the agent replaces the tag with the commit SHA and the tag as a comment before committing

#### Scenario: Asked for an archive bot
- **WHEN** the user asks for a job that archives the request's changes automatically
- **THEN** the agent declines, says no platform token can push to a fork and the job would be the only one holding write access to contents, and points at the archive command

#### Scenario: Asked for comment commands
- **WHEN** the user asks for slash commands on the request that show a change's documents
- **THEN** the agent declines, points at the deposited script's `status` run locally or in the check job as the replacement, and installs no comment-triggered workflow

### Requirement: Behavior: Deposited script is the project's own management code
The agent SHALL deposit the asset script as the project's own `scripts/spec_changes.py` with its test, the path the produced jobs call, SHALL confirm with the user whether to use it as is or rewrite it in the project's agreed management language, SHALL write nothing until the user chooses, and SHALL tell the user that later fixes to the plugin do not reach the delivered copy.

#### Scenario: Script deposited
- **WHEN** the automation is installed on a project whose agreed management language is Python
- **THEN** the project holds its own copy with its test, the produced jobs call that path, and the handoff says the copy is the project's and is not kept identical to the plugin's

#### Scenario: Project language differs
- **WHEN** the project's agreed management language is not Python
- **THEN** the agent offers the asset as a reference implementation to rewrite, and writes nothing until the user chooses

### Requirement: Behavior: Label definitions shown, remote sync delegated
The agent SHALL show the label additions and removals its merged definitions imply against the remote, SHALL apply them only through the project's existing label-sync tool after the user approves and read the result back, SHALL install no sync tool of its own, and when the project has none SHALL route the sync to the skill owning the platform lifecycle layer by description and list it as remaining work.

#### Scenario: Project has a sync tool
- **WHEN** the project's label file now carries the `spec:*` rows and the remote lacks them
- **THEN** the agent prints the plan the project's own tool produces, waits for approval, applies it through that tool, and reports the labels the remote holds afterwards

#### Scenario: Project has no sync tool
- **WHEN** the project has no label-sync tool
- **THEN** the agent shows the implied additions, installs none, names the platform lifecycle layer builder by role, and lists the sync as remaining work

### Requirement: Behavior: Maintainer-only platform actions go to pending decisions
Maintainer-only platform actions (marking the archive check required, rulesets) SHALL go to the pending decisions list with the recommended value, and the agent SHALL continue with every step that does not depend on them.

#### Scenario: Required check needs a maintainer
- **WHEN** marking the archive check required needs repository settings the agent cannot change
- **THEN** the agent lists the exact setting under pending decisions with the recommended value and continues with the rest of the install

#### Scenario: Check never run on the default branch
- **WHEN** the user asks to name the check as required before it has run on the default branch
- **THEN** the agent says a check the platform has never observed blocks every request, and sequences a green run first

### Requirement: Behavior: Handoffs by description
The agent SHALL route whether or at which level to adopt spec-driven development and what a good specification is to the skill that teaches that methodology, and setting or changing the project's rules (approval mode, design rule, archive executor) to the skill that owns the specification and completion layer, each described rather than installed; when the user declines, it SHALL proceed on the contract or the defaults and say so.

#### Scenario: Practice question
- **WHEN** the user asks whether the project should adopt spec-driven development at all
- **THEN** the agent offers the methodology skill by its role and answers no practice-level question itself

#### Scenario: User declines the contract handoff
- **WHEN** the user wants a different archive executor recorded but declines the layer builder
- **THEN** the agent installs the automation with the defaults, says which defaults applied, and lists the contract update as remaining work

### Requirement: Outcomes
Given an end-to-end task, the agent SHALL leave the pull or merge request, the change record, and the automation in the state the project's rules describe.

#### Scenario: Change carried from proposal to merge-ready
- **WHEN** asked to take an implemented OpenSpec change through to a mergeable pull request on a recorded-mode project with the automation installed and the implementer as executor
- **THEN** the request was marked ready before any archive, the archive commit landed on the branch after the review closed, strict validation passes on the archived tree, no label was set by hand, and the final report names the required check as reporting

#### Scenario: Automation installed in a fresh GitHub repository
- **WHEN** asked to install the OpenSpec request automation in a GitHub repository whose base has a checks workflow and a label file but no spec automation
- **THEN** the checks workflow gains the check job listed in the gate's dependencies, a label workflow exists, the `spec:*` rows are merged into the existing label file, `scripts/spec_changes.py` and its test are the project's own, OpenSpec artifact rules are recorded; every action is SHA-pinned, every job declares its permissions, no job holding a writable token checks out or runs a request's head, the check job runs on the read-only request trigger, no comment-triggered workflow exists, and the required-check setting and the remote label sync appear in the pending decisions

#### Scenario: Harness-only change
- **WHEN** asked to run a CI-only change through the workflow and the user wants a change record
- **THEN** the change carries `skip_specs: true`, a proposal with Acceptance, a design when the project's rule warrants one (otherwise the agent asked with the recommended rule), tasks written after approval, and no delta spec was created

### Requirement: Script: spec_changes.py
The bundled script SHALL offer `related`, `status`, `check`, and `archive` over `--base` and `--head` git refs, print JSON on stdout and diagnostics on stderr, summarise output above about 10,000 characters unless `--full` or `--output` is given, support `--help` with an example, exit 0 on success, 1 on a finding or failure, 2 on bad arguments, be idempotent, and run stdlib-only under `uv run` and plain `python3` 3.10+; `check` and `archive` SHALL need the OpenSpec CLI.

#### Scenario: Help
- **WHEN** the script runs with `--help`
- **THEN** it prints usage naming the four subcommands with an example and exits 0

#### Scenario: Representative archive
- **WHEN** a related change with every task ticked exists at the head and `archive --base <base> --head HEAD` runs
- **THEN** the change moves under the archive directory, the main specs carry its delta, strict validation passes, and `check` with the same refs then exits 0

#### Scenario: Repeated archive
- **WHEN** the identical `archive` command runs a second time
- **THEN** nothing changes and it exits 0

#### Scenario: One open and one complete change
- **WHEN** one related change has an open task and another is complete
- **THEN** `archive` exits 1, names the open task, and archives neither

#### Scenario: Uncommitted tree
- **WHEN** `archive` runs while a path the tool writes is uncommitted
- **THEN** it exits 1 naming the path and changes nothing

#### Scenario: Long status output
- **WHEN** `status` would print more than about 10,000 characters
- **THEN** it prints a summary naming the omitted documents and the `--full` and `--output` options, and `--full` prints everything

#### Scenario: Bad arguments
- **WHEN** the script runs with an unknown option
- **THEN** it exits 2 and prints a diagnostic naming the option

### Requirement: Script: assets/spec_changes.py
The deposited script SHALL offer `snapshot`, `check`, `status`, and `labels`, none editing the tree, reading changes from `--base`/`--head` or from a `--snapshot` document built from the platform API without checking out the head, refusing any partial read; `check` SHALL print an archive verdict after strict validation and `labels` the `spec:*` state and label changes. It SHALL meet the bundled script's interface rules: summarised long output, `--help`, exit codes 0/1/2, uv or `python3`.

#### Scenario: Help
- **WHEN** the script runs with `--help`
- **THEN** it prints usage naming the four subcommands with an example and exits 0

#### Scenario: Unarchived change on a ready request
- **WHEN** `check --base <base> --head HEAD` finds an unarchived related change and `--draft` is absent
- **THEN** it exits 1 with a JSON verdict naming the change, which the installed workflow reports under the awaiting-archive name

#### Scenario: Draft with unarchived change
- **WHEN** `check --draft` finds an unarchived related change
- **THEN** it prints a warning naming the change and exits 0

#### Scenario: Package edited after approval
- **WHEN** `labels` reads an approval record whose package hash differs from the current package
- **THEN** it reports the removal of `spec:approved` and the addition of `spec:pending`

#### Scenario: Partial snapshot
- **WHEN** `snapshot` reaches a cap, meets a truncated tree, or cannot decode a document as text
- **THEN** it exits 1 naming the path and writes no document

#### Scenario: Snapshot and clone compared
- **WHEN** `status` and `labels` run against a snapshot and against a clone with `--base` and `--head`
- **THEN** their output is identical

#### Scenario: Long snapshot output
- **WHEN** `snapshot` collects documents whose combined printed size exceeds about 10,000 characters
- **THEN** stdout carries a summary naming the document count and `--output <file>` writes the whole snapshot to that file

#### Scenario: Repeated run
- **WHEN** the identical `check` and `status` commands run twice
- **THEN** the output is identical and nothing in the tree changes
