# Spec Delta

## Purpose

Governs what an agent that loaded the `harness-create` entry skill observably does when it creates an agent harness for a target project, whether the repository has no habits yet to preserve (greenfield) or already shows habits, history, and possibly scattered agent-facing files (brownfield): how it investigates, how it aligns goals and non-goals, which decisions it confirms with the user, when it may first write a file, how it routes each layer to a builder, how the result is read back and reviewed, and what it reports at the close. The skill ships to Claude Code, Codex, and Antigravity and is user-invoked in all three. Non-goals: improving, auditing, thinning, or migrating an existing harness (a separate entry skill); the practice of any single layer, which the layer builders hold; writing or rewriting the project's README, CONTRIBUTING, or SECURITY (a contradiction between one of them and the harness is reported as a suggestion, never edited in); writing multi-agent concurrency rules unless the user says several agents will write to the repository at once.

## ADDED Requirements

### Requirement: Triggering
The skill SHALL load only when the user invokes it by name and SHALL never load from a description match, however closely a request resembles its work. A request that would otherwise match is served by the agent's ordinary behaviour or by the model-invoked skills it reaches on its own.

#### Scenario: Invoked by name with no agent-facing files
- **WHEN** the user runs the skill by name in a repository that has code and no agent-facing files
- **THEN** the skill loads and begins by reading the repository

#### Scenario: Invoked by name in a repository with a stray CLAUDE.md
- **WHEN** the user runs the skill by name in a repository whose only agent-facing file is a `CLAUDE.md` written months ago
- **THEN** the skill loads and treats the repository as brownfield

#### Scenario: Invoked by name with a goal sentence
- **WHEN** the user runs the skill by name followed by "we want agents to be able to work unattended overnight"
- **THEN** the skill loads and carries the sentence into the goal and non-goal alignment instead of asking for the goal again

#### Scenario: Description-shaped request without invocation
- **WHEN** the user types "set up an AGENTS.md and some checks so Claude stops breaking the build" without invoking the skill
- **THEN** the skill does not load

#### Scenario: Harness vocabulary without invocation
- **WHEN** the user asks "what thickness should our hard-boundary layer be for a research repo?" without invoking the skill
- **THEN** the skill does not load

#### Scenario: Existing harness complaint without invocation
- **WHEN** the user says "our agents keep ignoring the conventions in AGENTS.md, something has drifted" without invoking the skill
- **THEN** the skill does not load

### Requirement: Behavior: Investigation reads the repository before asking and tells greenfield from brownfield
Before asking the user anything, the agent SHALL read the repository and record what it can observe (layout, stack, commands, task runner, checks, CI, hooks, branch habits, every agent-facing file, skill, and tool), SHALL classify the project as greenfield only when it shows no established habit to preserve and as brownfield when it shows any, with or without agent-facing files, and SHALL present each recorded fact as backed by evidence or as a question only the team can answer.

#### Scenario: Near-empty repository
- **WHEN** the repository holds a README, a license, and a handful of commits, with no build or test command and no CI
- **THEN** the agent reports it as greenfield, lists the little it observed, states that nothing needs preserving, and asks only what the repository cannot answer

#### Scenario: Repository with checks and no agent-facing file
- **WHEN** the repository has source code, a CI configuration, and a `justfile`, and no agent-facing file, skill, or hook
- **THEN** the agent reports it as brownfield, lists the observed stack and commands with where each was seen, treats the `justfile` and the CI checks as sources of truth to write into the harness, and the inventory reports only missing artifacts

#### Scenario: Repository with agent-facing files
- **WHEN** the repository carries an `AGENTS.md`, two project skills, and a `.claude/settings.json`
- **THEN** the agent reports it as brownfield and, for each artifact, states how a future agent finds it, when it loads, its source of truth, and what keeps it current

#### Scenario: Checks visible in justfile and CI
- **WHEN** the repository's `justfile` and CI both run `pytest` and `ruff`
- **THEN** the agent records them as the existing check set and does not ask the user which test runner or linter the project uses

### Requirement: Behavior: Brownfield inventory classifies problems and preserves working choices
For a brownfield project the agent SHALL classify each existing harness artifact, if any, as stale, duplicated, contradictory, invisible, missing, or excessive, SHALL treat every working choice (task runner, lint configuration, branch habit) as a source of truth to write into the harness rather than something to replace, and SHALL present any migration it finds worthwhile as a suggestion for the team, to be executed as a separate change if accepted.

#### Scenario: Contradictory artifacts
- **WHEN** `CLAUDE.md` says commits use Conventional Commits and `CONTRIBUTING.md` shows unprefixed titles that match the git log
- **THEN** the inventory marks the `CLAUDE.md` rule as contradictory, cites both files and the log, asks the user which is intended before any plan names a commit rule, and, when the chosen rule leaves `CONTRIBUTING.md` contradicting the harness, records a suggested edit to it for the closing report without editing the file

#### Scenario: Existing Makefile
- **WHEN** the project runs its checks through a `Makefile` and the agent would have recommended another task runner
- **THEN** the plan keeps the `Makefile` as the command surface, and the runner change appears only as a suggestion the user may take up separately

#### Scenario: Specification for untouched code
- **WHEN** the user asks the harness to document specifications for a module nobody has changed in a year
- **THEN** the agent advises writing specifications only for the parts under change, explains that a specification with no change pressure rots, and records the user's decision

### Requirement: Behavior: Goals and non-goals are aligned before grading
Before asking the five variables, the agent SHALL restate the user's goal for the harness, SHALL propose the non-goals (what the harness will not police, what stays human-only, which changes to the project itself it will not make), and SHALL obtain the user's confirmation of both; the agreed goal and non-goals SHALL constrain every later grade and decision, and a goal that reaches beyond the harness SHALL be named as a non-goal with the user's answer recorded.

#### Scenario: Goal supplied with the invocation
- **WHEN** the user invoked the skill with "we want agents to be able to work unattended overnight"
- **THEN** the agent restates that goal, proposes non-goals such as not policing code style the project has never enforced, asks for confirmation of both, and does not ask for the goal again

#### Scenario: No goal supplied
- **WHEN** the user invoked the skill with no sentence about what the harness is for
- **THEN** the agent asks for the goal in one question before anything else and does not proceed to the five variables until it is answered

#### Scenario: Goal implying a project refactor
- **WHEN** the user's goal is "let agents work in the codebase once we have split the monolith into packages"
- **THEN** the agent names the split as a non-goal of the harness, offers to record it as a separate change the team may make, and records the user's answer

#### Scenario: Non-goal that constrains a layer
- **WHEN** the user confirms "no changes to CI" as a non-goal
- **THEN** every later hard-boundary row proposes only checks that run outside CI, and the grade table says the non-goal is the reason

### Requirement: Behavior: The five variables are asked only when not observable
The agent SHALL settle the five variables (error cost, maintenance horizon, environment isolation, autonomy, team size) before grading any layer, SHALL take each from the repository when it is observable there, SHALL present a value inferred from evidence rather than stated by the repository as an inference for the user to confirm or correct, and SHALL ask the user for the rest, one round covering every open variable rather than one question per turn.

#### Scenario: Session inside a declared devcontainer
- **WHEN** the session is already running inside a devcontainer declared in the repository
- **THEN** the agent records environment isolation from that fact and asks only about the variables the repository cannot show

#### Scenario: Single author in the git log
- **WHEN** the git log shows one author over the whole history
- **THEN** the agent states the inference "single maintainer" and asks the user to confirm or correct it rather than treating it as settled

#### Scenario: Three variables unobservable
- **WHEN** error cost, autonomy, and maintenance horizon cannot be observed
- **THEN** the agent asks for all three together, each with the typical answers and what each answer pushes thicker or thinner

### Requirement: Behavior: Six-layer grade table confirmed layer by layer
The agent SHALL produce a table of the six graded layers, named as the builders declare them (environment, knowledge and routing, hard-boundary, authority, specification and completion, entropy), each with a proposed grade among omitted, light, medium, thick, the variables that drive it, and the evidence, and SHALL ask the user to confirm or change every row before proceeding; a grade SHALL never be chosen for the project as a whole.

#### Scenario: Mixed project
- **WHEN** a research repository contains a data pipeline the user says must not break
- **THEN** the table grades hard-boundary and entropy thicker than the other layers, names error cost and maintenance horizon as the reason, and waits for row-by-row confirmation

#### Scenario: User lowers a grade
- **WHEN** the user changes the authority layer from medium to light
- **THEN** the agent challenges the change once if the evidence contradicts it, then adopts light for that row and carries it into every later step

#### Scenario: Short-lived prototype
- **WHEN** the user states the project will be discarded within a quarter
- **THEN** the table proposes entropy as omitted or light and says why, instead of recommending a self-check in CI

### Requirement: Behavior: Platform lifecycle layer is proposed when the project is hosted
When the remote is on GitHub or GitLab, the agent SHALL propose the platform lifecycle layer alongside the six graded layers, presenting its decisions with recommendations (GitHub Flow; merge methods asked each time, squash-only recommended; minimal entity set; no Projects or Milestones; tag-triggered releases), SHALL confirm each with the user, and SHALL route the layer by its ownership phrase like the others; with no hosted remote the layer SHALL be marked not applicable and nothing asked.

#### Scenario: Remote on GitHub
- **WHEN** the repository's `origin` points at GitHub
- **THEN** the plan carries a platform lifecycle section with squash-only recommended, the merge-method question put to the user, the minimal entity set listed, and the layer assigned to the installed skill that owns it

#### Scenario: No hosted remote
- **WHEN** the repository has no remote, or its remote is a bare server that is neither GitHub nor GitLab
- **THEN** the plan marks the platform lifecycle layer not applicable, and the agent asks no merge-method or label question

#### Scenario: User asks for Projects boards
- **WHEN** the user asks the harness to set up Projects boards and Milestones
- **THEN** the agent challenges once with the reason the minimal set omits them, then records the user's choice and carries it into the plan

### Requirement: Behavior: Each layer decision is presented with a recommendation and confirmed
For every decision inside a layer (entrypoint shape, carrier, task runner, secret scanner, lint tools, deny list, approval mode, concurrency rules) the agent SHALL present one recommended option with its reason and the alternatives in a sentence each, and SHALL wait for the user's choice; it SHALL choose without asking only when the repository answers plainly; except for environment isolation when none exists, where it SHALL list the options with their costs and recommend none.

#### Scenario: Environment without isolation
- **WHEN** no isolated environment exists and the five variables place the project at medium risk
- **THEN** the agent lists the isolation options with their costs and lets the user choose instead of recommending one

#### Scenario: Single agent stated
- **WHEN** the user states that one agent at a time works in the repository
- **THEN** the plan contains no multi-agent concurrency rules (worktrees, remote branches, shared-resource locks) and says the single-agent setup is why

### Requirement: Behavior: Management-script language is agreed with the user
The agent SHALL always put the management-script language to the user and SHALL never infer it, because the user must be able to read the scripts; it SHALL recommend Deno when the repository already carries a Deno environment, otherwise the scripting practice of the project's language community, and otherwise Deno with the question whether Deno may be added to the agent environment; it SHALL also ask whether the plugin's Python reference scripts are used as they are or rewritten.

#### Scenario: Deno environment present
- **WHEN** the repository already carries a `deno.json`
- **THEN** the agent recommends Deno, names its explicit permission management as the reason, and still waits for the user's choice before planning any script

#### Scenario: No Deno and community scripts in Python
- **WHEN** the project has no Deno environment and its language community writes scripts in Python
- **THEN** the agent recommends Python for management scripts, lists Deno as the alternative with its permission-management advantage, and does not write a script until the user picks

#### Scenario: No Deno and no community scripting practice
- **WHEN** the project has neither a Deno environment nor a scripting practice in its community language
- **THEN** the agent recommends Deno and asks whether the user allows adding Deno to the agent environment before planning any script in it

### Requirement: Behavior: Plan approval precedes every file, and approval covers only what the plan names
The agent SHALL deposit no file in the target project before the user approves a plan grouped by layer that names every file to be created or changed, the grade and reasons per layer, the decisions taken, and the open assumptions; the plan SHALL contain no placeholder, fill instruction, or inapplicable row; and publishing, changing remote settings, deleting work, and widening agent autonomy SHALL each be a separate decision taken when that step is reached, never implied by the approval.

#### Scenario: Write attempted before approval
- **WHEN** the user asks "just drop in an AGENTS.md draft so I can see it" before the plan is approved
- **THEN** the agent shows the draft in the conversation and writes nothing to the repository until the plan is approved

#### Scenario: Plan approved
- **WHEN** the user approves the plan
- **THEN** the files created afterwards are exactly those the plan names

#### Scenario: Plan presented for a project without a hosted remote
- **WHEN** the agent presents the plan for a repository with no GitHub or GitLab remote
- **THEN** the plan contains no platform row, no placeholder, and no fill instruction

#### Scenario: Remote action after approval
- **WHEN** the approved plan includes a label set for the platform and the build reaches that step
- **THEN** the agent shows the labels as a dry run and asks for a separate go-ahead before applying them to the remote

### Requirement: Behavior: Layers are routed to builders by their ownership phrase
The agent SHALL assign each planned layer, platform lifecycle included, to the installed skill whose description states "Owns the <layer> layer" using the layer name the builders declare (the six names of the grade table plus platform lifecycle), SHALL load that skill and let it run the layer and hand back, SHALL name no builder itself, and when no skill claims a layer SHALL say so, build it from the methodology manual, and record the gap.

#### Scenario: Installed builder claims the layer
- **WHEN** the plan includes the authority layer and an installed skill's description says it owns the authority layer
- **THEN** the agent loads that skill for the layer, and the files it leaves behind contain no reference to the builder

#### Scenario: Builder renamed
- **WHEN** the skill owning the entropy layer has been renamed but still carries the ownership phrase
- **THEN** routing succeeds without any change to the entry skill

#### Scenario: No builder claims a layer
- **WHEN** no installed skill description claims the hard-boundary layer
- **THEN** the agent tells the user, builds the layer from the manual's references, and lists the missing builder in the closing report

### Requirement: Behavior: Checkpoints are commits
During the build the agent SHALL commit at each verified checkpoint (typically one layer), SHALL write the messages in the convention the plan recorded, SHALL add no AI attribution, and SHALL push nothing unless the user decided so for that step.

#### Scenario: Layer finished
- **WHEN** a layer's files exist and its checks pass locally
- **THEN** the agent commits them with a message in the recorded convention and does not stash or rely on session-only undo

#### Scenario: Pre-commit failure at a checkpoint
- **WHEN** the secret scan in pre-commit rejects a checkpoint commit
- **THEN** the agent removes or fixes the flagged content and retries; it does not bypass the hook

### Requirement: Behavior: Every artifact is read back in a clean context
After building, the agent SHALL have each new or changed artifact read by the plugin's read-only verifier agent given only the target project's files and the intent line, SHALL fix every gap it reports and re-read until the reading matches the intent; when no subagent can be dispatched, the agent SHALL do the same reading itself in a fresh pass and SHALL record that degradation in the closing report.

#### Scenario: Verifier reports a gap
- **WHEN** the verifier reports that a knowledge file is unreachable from the entrypoint
- **THEN** the agent adds the route to the entrypoint, re-runs the verifier on both files, and continues only on PASS

#### Scenario: Client without agents
- **WHEN** the build runs in a client whose plugins carry no agents
- **THEN** the agent performs the read-back itself in a fresh pass and the closing report names the read-back as degraded

### Requirement: Behavior: Final review covers vocabulary, self-containment, mechanics, and the checklist
Before closing, the agent SHALL review the deposited harness for terms only this plugin defines and left undefined, for any dependency on the plugin (names, paths, phrases), for mechanics (every rule reachable from the entrypoint, entrypoint within budget, links resolve, documented commands run, each sync concern owned in both directions), and SHALL walk the methodology's closing checklist item by item, fixing and re-reading what the review changes.

#### Scenario: Leaked term
- **WHEN** a deposited knowledge file uses "pending decisions list" without saying what one contains
- **THEN** the review defines the term in that file or rewrites the sentence plainly, and the file is re-read

#### Scenario: Plugin dependency
- **WHEN** a deposited CI step invokes a script by a path inside a skill directory
- **THEN** the review replaces it with the project's own copy and tells the user later plugin fixes do not reach that copy

#### Scenario: Checklist item fails
- **WHEN** the checklist item on handoff hygiene finds the handoff directory is not in `.gitignore`
- **THEN** the agent adds the ignore rule, commits it as a checkpoint, and records the item as passed

### Requirement: Behavior: Close with a report, a pending decisions list, and the human platform actions
At the close the agent SHALL report every artifact changed with its role and validation result, SHALL present the pending decisions list once (each item: what is blocked and why, options, recommended option with reason, which finished work each option would change), SHALL list every platform or remote action that remains for a human, and SHALL list every public file (README, CONTRIBUTING, SECURITY) that contradicts the harness with a suggested edit, having changed none of them.

#### Scenario: Blocked decision mid-build
- **WHEN** the user is away when the merge method must be chosen
- **THEN** the agent finishes every layer that does not depend on it and the closing list carries the merge-method item with squash as the recommended option

#### Scenario: Platform settings in the plan
- **WHEN** the plan included branch protection and secret scanning on the platform
- **THEN** the closing report lists each as an action for a human with the exact setting to apply, and the agent has changed neither

#### Scenario: Public file contradicting the harness
- **WHEN** `CONTRIBUTING.md` describes a review workflow the approved harness replaces
- **THEN** the agent leaves `CONTRIBUTING.md` unchanged and the closing report lists the contradiction with a suggested edit for the team

### Requirement: Outcomes
Run end to end on a real repository, the skill SHALL leave a harness whose entrypoint is within budget, whose knowledge files are reachable, whose checks run, and whose every decision was confirmed by the user, with nothing written before plan approval.

#### Scenario: Python service with checks, one author, long horizon, attended sessions
- **WHEN** the skill runs on a Python service with `pytest` and `ruff` configured, one author, no agent-facing files, already developed in a devcontainer, and the user states the service is maintained for years, that a bad change costs a day of cleanup but no data, that sessions are attended, and then confirms the recommended rows
- **THEN** the repository gains an `AGENTS.md` of at most 120 lines with an always-applies block, routing table, and validation commands; a `CLAUDE.md` that only points at it; reachable knowledge files; a pre-commit configuration that runs formatting, secret scanning, and the existing `ruff` and `pytest`; a harness self-check that passes; commits at each layer with no AI attribution; and the transcript shows the plan approved before the first write and every layer grade confirmed

#### Scenario: Brownfield repository with a stale CLAUDE.md
- **WHEN** the skill runs on a repository whose `CLAUDE.md` names a test command that no longer exists and whose `Makefile` runs the real checks
- **THEN** the inventory marks the command stale with the evidence, the plan keeps the `Makefile`, the new entrypoint points at the working command, the stale rule is removed in a checkpoint commit, and the closing report lists the artifacts changed and any decision left pending

#### Scenario: User declines the plan
- **WHEN** the user rejects the plan after the grade table and asks to stop
- **THEN** the repository has no new or changed file, no commit was made, and the agent summarises the investigation and the table so the work can resume later
