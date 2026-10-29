# Spec Delta

## Purpose

Governs what an agent that loaded `spec-completion-building` observably inventories, asks, recommends, and deposits for a target project's specification and completion layer: the specification level, the carrier, the completion answers and quality rules every spec must carry, the two approval gates and their mode, the spec-less rule for harness changes, the fast feedback and worktree discipline, and the gitignored handoff directory. Ships to Claude Code, Codex, and Antigravity. Non-goals: writing a specification, deciding whether a project adopts spec-driven development at all, running or installing a spec tool's commands, installing platform automation, writing the task-runner recipes the hard-boundary layer owns, and the authority levels that attach to the gates.

## ADDED Requirements

### Requirement: Triggering
The skill SHALL load when a harness build or improvement reaches the specification and completion layer, when a project asks how its specs, completion standard, or approval gates should be set up or aligned with its harness, when specs and harness contradict, or when insertion markers left for the specification workflow await filling; it SHALL NOT load for writing one spec, choosing whether to practise spec-driven development, running one tool's commands, or installing one tool's automation.

#### Scenario: Harness build reaches the layer
- **WHEN** an entry skill building a harness says "next layer: decide how this project specifies work and when a task counts as done"
- **THEN** the skill loads

#### Scenario: Completion standard request
- **WHEN** the user says "agents keep stopping after 'tests pass' or never stop; define what done means for a change in this repo and where that rule lives"
- **THEN** the skill loads

#### Scenario: Harness contradicts the spec tool
- **WHEN** the user says "our AGENTS.md and our openspec specs disagree about approval; make the harness say one thing"
- **THEN** the skill loads

#### Scenario: Markers awaiting fill
- **WHEN** the user says "the platform layer left three spec-workflow markers in the PR template, the workflow skill, and the GitHub knowledge file; fill them from the spec contract we already recorded"
- **THEN** the skill loads

#### Scenario: Writing one specification
- **WHEN** the user says "write the spec for the export endpoint before we implement it"
- **THEN** the skill does not load

#### Scenario: Adoption question
- **WHEN** the user says "is spec-driven development worth it for a two-week prototype?"
- **THEN** the skill does not load

#### Scenario: Tool command request
- **WHEN** the user says "archive the finished OpenSpec change and add the spec status labels to the repository"
- **THEN** the skill does not load

### Requirement: Behavior: Inventory before any question
Before asking anything, the agent SHALL run the bundled read-only inventory script against the target checkout, record its summary, and read the entrypoint and knowledge files in full for behaviour statements and requirement-restating documents; it SHALL write nothing to the project during inspection and SHALL not ask the user for any fact the inventory settled.

#### Scenario: Tool already present
- **WHEN** the inventory finds an `openspec/` directory with active changes
- **THEN** the agent records OpenSpec as the carrier in use and asks no carrier question

#### Scenario: Restating document found
- **WHEN** the inventory lists a `docs/requirements.md` with acceptance criteria outside the tool's directories
- **THEN** the agent lists it as a source-of-truth conflict to resolve with the user (spec, pointer, or deletion) and changes nothing until the plan is approved

#### Scenario: Script cannot run
- **WHEN** neither `uv` nor `python3` is available in the target environment
- **THEN** the agent performs the inventory by reading the tree itself, records the degradation, and still asks nothing the tree answers

### Requirement: Behavior: Recorded variables are not re-asked
When the approved harness plan or the user's earlier answers in the build record the maintenance horizon, the team size, or the autonomy level, the agent SHALL take them from there and SHALL ask none of them again; it SHALL ask only a variable that is neither recorded nor observable, and SHALL cite the source of each taken value in the recommendation it derives from it.

#### Scenario: Variables already in the plan
- **WHEN** the approved plan records "maintained for years, three committers, agents run unattended at night"
- **THEN** the agent derives the level, gate mode, and defaults from those three answers, cites the plan as their source, and asks the user only about points the plan leaves open

#### Scenario: Variable missing from the plan
- **WHEN** the plan records the horizon and team size but not whether agents run unattended
- **THEN** the agent asks only the autonomy question, with one recommendation, and re-asks neither recorded variable

### Requirement: Behavior: Level recommended by maintenance horizon
The agent SHALL ask the specification level with one recommendation derived from the maintenance horizon: spec-anchored (specs kept as the living description) when the project is maintained past one release, spec-first (spec used to build, then archived) otherwise; it SHALL present the alternative in one sentence and SHALL record the user's choice and its selecting fact.

#### Scenario: Long-lived library
- **WHEN** the user states the library will be maintained for years
- **THEN** the agent recommends spec-anchored, names the horizon as the reason, and offers spec-first as the alternative

#### Scenario: User overrules
- **WHEN** the user chooses spec-first against a spec-anchored recommendation
- **THEN** the agent challenges once with the evidence, then records spec-first and designs every later step around it

### Requirement: Behavior: Carrier recommended by project shape
The agent SHALL recommend exactly one carrier by applying these rules in order and stopping at the first match: a carrier already in use is kept without asking unless the user asks to change it; a solo small project gets the lightweight carrier (committed per-change SPEC.md/PLAN.md or plan mode); a project with existing code gets OpenSpec; an application delivered feature by feature from zero gets Spec-Kit. The alternatives SHALL be named in one sentence each.

#### Scenario: Greenfield application
- **WHEN** a team project has no code and the user describes an app delivered feature by feature
- **THEN** the agent recommends Spec-Kit, names OpenSpec and the lightweight carrier as alternatives in one sentence each, and waits for the choice

#### Scenario: Existing code with no tool
- **WHEN** a repository maintained by several people holds code and the inventory finds no spec tool
- **THEN** the agent recommends OpenSpec and cites "existing code" as the selecting fact

#### Scenario: Solo maintainer with a small existing codebase
- **WHEN** the user is the only maintainer of a small repository that already holds code and no spec tool
- **THEN** the agent recommends the lightweight carrier alone, cites "solo small project" as the selecting fact, and names OpenSpec as the alternative in one sentence

#### Scenario: Spec-Kit already in use for a library
- **WHEN** the inventory finds `.specify/` in a library repository
- **THEN** the agent keeps Spec-Kit without asking, notes the shape mismatch, and offers a migration to OpenSpec as a separate change the user may decline, never folded into this build

### Requirement: Behavior: Completion answers and quality rules enter the contract
The deposited contract SHALL state the four completion answers (how done is judged by a check the agent runs itself; what is not done; what is delivered, pending decisions included; which irreversible actions are pre-authorised) and the four quality rules (at least one judgeable scenario per goal, and at least one scenario in the spec covering a failure or edge path; non-goals written; behaviour, not diff; verification against run results) so that a clean-context reader names all eight.

#### Scenario: Clean-context read of the contract
- **WHEN** an agent that has never seen the skill reads only the deposited contract and is asked what a new spec must contain
- **THEN** it names all four completion answers and all four quality rules, and states the failure-path rule as one scenario per spec, not one per goal

#### Scenario: Lightweight carrier chosen
- **WHEN** the carrier is per-change SPEC.md/PLAN.md or plan mode
- **THEN** the contract lists the same four answers and four rules as the headings every per-change specification or plan must carry, in project terms, without referring to any template

### Requirement: Behavior: Gates and approval mode by team size
The agent SHALL record two gates: the approval package (spec plus design when warranted) is approved before any task list is written; the request is marked ready when the last task is verified, and the record is frozen inside the request after the deliberation closes, by the implementer or a person on a fork. The mode SHALL be recommended from team size: conversational for solo or pairing; recorded (`spec:approved` label, package fingerprint, awaiting-archive check) otherwise.

#### Scenario: Solo project
- **WHEN** the user is the only committer and reviews in conversation
- **THEN** the agent recommends conversational closing of both gates and records that tasks follow the first closing and the freeze follows the review of the ready request

#### Scenario: Unattended agents
- **WHEN** the user says agents will open pull requests overnight with no one in the conversation
- **THEN** the agent recommends the recorded mode, states that the label is removed when the package changes after approval, and records that a commit after the freeze reopens the deliberation

#### Scenario: Automation offered as the archiver
- **WHEN** the user asks for a job that archives the record on merge
- **THEN** the agent declines, records the implementer (or a maintainer on a fork's branch) as the executor, and adds the request to the pending decisions list only if the user insists

### Requirement: Behavior: Harness changes are spec-less
The contract SHALL state that a change to the project's own harness, tooling, checks, workflows, or documents carries no spec, naming the carrier's marker for such a change where the carrier has one, and naming the harness self-check as the covering check only where the entropy layer provides one; where none exists the contract SHALL state the rule in words, name no check, and the agent SHALL list the self-check reference as pending with the entropy layer as its precondition.

#### Scenario: CI change asked about
- **WHEN** a clean-context agent reads only the contract of a project whose entropy layer deposited a harness self-check and is asked whether editing the CI workflow needs a spec
- **THEN** it answers no and names that self-check as the check covering the change

#### Scenario: Carrier without a marker
- **WHEN** the carrier is the lightweight one
- **THEN** the contract states the spec-less rule in words and names no marker

#### Scenario: Project without a harness self-check
- **WHEN** the entropy layer is light, omitted, or not yet built when this layer runs
- **THEN** the contract states the spec-less rule, names no check, the self-check reference appears in the pending decisions list with the entropy layer as its precondition, and a re-run after that layer deposits a check fills the reference

### Requirement: Behavior: Fast feedback and worktree cleanup are recorded
The agent SHALL record in the contract the scoped validation command (single file, module, or diff, running in seconds) that the hard-boundary layer or the project already provides, together with the rule that every exploratory worktree or branch is removed once its evaluation ends; where no scoped command exists it SHALL name the gap for the hard-boundary layer by description, or list it as pending when that layer is omitted or already done, and SHALL never invent a command.

#### Scenario: Scoped recipe already present
- **WHEN** the hard-boundary layer deposited a task-runner recipe for a scoped fast test
- **THEN** the contract names that recipe as the fast scoped check and the full run as the task-end check, and the agent writes no recipe of its own

#### Scenario: Test runner supports a path filter
- **WHEN** no recipe exists but the project's test runner accepts a file path
- **THEN** the contract names that invocation as the fast scoped check and the full run as the task-end check

#### Scenario: No fast path
- **WHEN** the only check is a ten-minute full build
- **THEN** the agent names the gap for the layer that owns task-runner recipes, by description, and lists it as a pending decision with options and a recommendation only when that layer is omitted or already done, instead of writing a command it has not run

### Requirement: Behavior: Handoff directory is gitignored
The agent SHALL recommend `.agents/handoff/` as the location for session handoff and scratch notes, SHALL add it to `.gitignore` once the plan is approved, and SHALL record in the contract that such files never enter version control because they carry logs and credentials more often than code does.

#### Scenario: Default accepted
- **WHEN** the user accepts the recommendation
- **THEN** `.gitignore` gains the handoff directory and the contract names the path and the reason

#### Scenario: User prefers the system temp directory
- **WHEN** the user declines a repository directory
- **THEN** the agent records the system temporary directory as the location, changes `.gitignore` not at all, and the contract states the same rule for that location

### Requirement: Behavior: Contract deposited and platform markers filled
After approval the agent SHALL deposit the spec-workflow knowledge file in the project's own vocabulary, naming level, carrier, gates with mode, scope, fast check, and handoff location, and SHALL point the entrypoint at it with a read condition. Where the three `<!-- harness: spec-workflow -->` markers exist it SHALL insert text matching the settled gates and mode after each marker, closed by an end marker so a re-run replaces that block; otherwise it SHALL record the fill as pending.

#### Scenario: Platform layer present
- **WHEN** the three markers exist in the target project
- **THEN** each gains, between the marker and an end marker, text matching the settled gates and mode, the marker itself stays as the anchor, and a second run on the unchanged contract changes nothing

#### Scenario: Platform layer absent
- **WHEN** no marker exists in the target project
- **THEN** the contract is deposited, the entrypoint pointer is added, and the marker fill is listed as pending with the platform layer named as its precondition

#### Scenario: Contract already deposited and markers fresh
- **WHEN** the target already carries the deposited contract and the platform layer has since left three unfilled markers
- **THEN** the agent fills the markers from the contract's recorded gates and mode, asks nothing the contract records (level, carrier, gates), and changes the contract only on a user request

#### Scenario: Gate mode changed after fill
- **WHEN** the user switches the recorded mode from conversational to recorded after the markers were filled
- **THEN** the agent updates the contract, replaces the text between each marker and its end marker in all three files, and changes nothing else in those files

#### Scenario: Vocabulary leak
- **WHEN** the deposited contract is checked after writing
- **THEN** it contains no tool command, no script path inside the plugin, and no term the skill alone defines

### Requirement: Behavior: Tool adoption handed to the carrier skill
The agent SHALL NOT initialise, install, or configure the spec tool itself; it SHALL hand adoption, the tool's layout, and its automation to the skill that owns the chosen carrier (OpenSpec, Spec-Kit, or the lightweight per-change documents and plan mode), described by its role, and SHALL print no install command. Only where the chosen approach is none of the three SHALL it record the by-hand executor and list the automation as remaining work.

#### Scenario: OpenSpec chosen
- **WHEN** the user settles on OpenSpec
- **THEN** the handoff names the carrier skill by what it owns (OpenSpec changes, archive, status labels) and the agent runs no tool initializer

#### Scenario: Every tool declined
- **WHEN** the user refuses every spec framework and keeps hand-written per-change spec documents
- **THEN** the agent records the lightweight carrier and hands off to the skill that owns per-change SPEC.md/PLAN.md and plan-mode alignment, described by that role, installing nothing

#### Scenario: Unsupported framework in use
- **WHEN** the inventory finds a specification framework that is neither OpenSpec, Spec-Kit, nor hand-written documents, and the user keeps it
- **THEN** the agent records the implementer as the executor of every gate and the structural check the project adopts, lists the framework's automation as remaining work, and hands off nothing

### Requirement: Behavior: Drifted specs are repaired without blocking the build
When the inventory finds existing specs that contradict the code or each other, the agent SHALL report each contradiction with its two sources, SHALL ask once whether to fix or delete each spec with one recommendation, SHALL apply a decision the user gives, and when the user defers SHALL record each unresolved contradiction in the pending decisions list and deposit the contract with the drift noted, naming the specs that are not yet authoritative; it SHALL NOT back-fill specs for untouched code.

#### Scenario: Spec contradicts code
- **WHEN** a main spec requires behaviour the code observably no longer has
- **THEN** the agent lists the spec, the code location, and the two options (fix the spec, delete it) with a recommendation, and applies the user's answer before the layer is reported done

#### Scenario: Decision deferred
- **WHEN** the user says the contradiction will be settled later
- **THEN** the agent adds it to the pending decisions list with both options and the recommendation, deposits the contract with that spec named as not yet authoritative, and continues every step that does not depend on it

#### Scenario: Back-fill requested
- **WHEN** the user asks for specs covering every existing module
- **THEN** the agent recommends covering only behaviour future changes touch, names the codebase map as the carrier for the rest, and records the user's final choice

### Requirement: Behavior: Read-back in a clean context
After depositing, the agent SHALL have the contract read back by a clean-context subagent that answers the layer's questions (level, carrier, where a new spec goes, who approves which gate and how it is recorded, when the draft opens, who freezes, what harness changes carry) from project files alone; without a subagent it SHALL perform the read itself in a fresh pass and record the degradation.

#### Scenario: Subagent available
- **WHEN** a subagent can be spawned
- **THEN** it answers every question from the deposited files, and each gap it reports is fixed before the layer is reported done

#### Scenario: No subagent
- **WHEN** the client offers no subagent
- **THEN** the agent re-reads the deposited files from the top, answers the same questions, and the final report says the read-back was not clean-context

### Requirement: Outcomes
Given a target project and a user who answers questions, the agent SHALL leave the project with a deposited specification contract, an entrypoint pointer, a gitignored handoff directory, and a recorded handoff, with every decision traceable to the user, the approved plan, or an observed fact.

#### Scenario: Existing TypeScript library on GitHub with no spec tool
- **WHEN** the user runs the layer on a maintained library with several committers and accepts every recommendation
- **THEN** the contract records spec-anchored, OpenSpec, conversational or recorded gates matching the stated team size, ready before freeze with the implementer as freezer, the four completion answers and four quality rules, the spec-less rule for harness changes, a scoped test command the runner or the hard-boundary layer provides, and `.agents/handoff/` gitignored; the entrypoint points at the contract with a read condition; the carrier handoff names no command; and a clean-context reader answers who approves, when tasks are written, and who freezes

#### Scenario: Solo greenfield script collection
- **WHEN** a solo user with a small repository declines every spec framework
- **THEN** the contract records spec-first and the lightweight carrier, conversational gates, the same four answers and rules as the headings every per-change specification or plan must carry, the handoff names the skill that owns per-change documents and plan mode by role, no tool is installed, no marker fill is attempted, and the pending decisions list is empty or names only the scoped check and the self-check reference when the project has neither

#### Scenario: Brownfield with contradicting specs
- **WHEN** the inventory finds Spec-Kit directories whose specs disagree with the code and an AGENTS.md that restates acceptance criteria, and the user defers one fix-or-delete decision
- **THEN** the run keeps Spec-Kit, lists each contradiction and the restated passage for the user's decision, applies the decisions given, deposits the contract naming the deferred spec as not yet authoritative with that item on the pending decisions list, and the final contract leaves the entrypoint pointing at the specs instead of restating them

### Requirement: Script: detect_spec_tooling.py
Read-only inventory of a checkout: `--root <dir>` (default `.`), `--max-candidates <n>` (default 40), `--help` with an example; stdout SHALL be one JSON object listing spec tools found, entrypoint lines pointing at spec artifacts, and requirement-restating documents outside the found tools' directories and installed skill trees (`.agents/skills/`, `.claude/skills/`, plugin skill directories; symlinks followed once); summary on stderr; exit 0/1/2 (ok/inspection failure/bad arguments).

#### Scenario: Repository with OpenSpec
- **WHEN** the script runs with `--root` on a checkout holding `openspec/specs` and `openspec/changes`
- **THEN** stdout JSON lists a tool entry for OpenSpec with its spec and change counts and owned paths, and the exit code is 0

#### Scenario: Nothing found
- **WHEN** the script runs on a checkout with no spec tool and no requirement-shaped document
- **THEN** stdout JSON has an empty tools list and empty candidate list, stderr says "tools: none", and the exit code is 0

#### Scenario: Bad root
- **WHEN** `--root` names a path that is not a directory
- **THEN** stderr says what is wrong and how to fix it, nothing is written to stdout, and the exit code is 2

#### Scenario: Unreadable subdirectory
- **WHEN** a directory under `--root` cannot be read because of its permissions
- **THEN** stderr names that path and the error, stdout holds either no output or a JSON object marked as partial, and the exit code is 1

#### Scenario: Run without uv
- **WHEN** the script is started with plain `python3` on a machine without `uv`
- **THEN** it runs with the standard library alone and prints the same JSON as under `uv run`

#### Scenario: Repeated run
- **WHEN** the script runs twice on an unchanged checkout
- **THEN** both outputs are identical and `git status --porcelain` shows no new file

#### Scenario: Skill tree with acceptance headings
- **WHEN** `.agents/skills/` holds skill files with "Acceptance criteria" headings and `.claude/skills/` is a symlink to it
- **THEN** none of those files appears among the requirement-restating candidates and the symlink is not reported a second time
