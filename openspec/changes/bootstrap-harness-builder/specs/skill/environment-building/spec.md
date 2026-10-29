# Spec Delta

## Purpose

Governs what an agent that loaded `environment-building` observably does when it builds, audits, or revises the environment and sandbox layer of a target project's harness at the grade the user confirmed: where the project's agent runs, what it can reach, which protection tier the threat model demands, which control-plane files are hard or soft read-only, and which environment variables keep every command non-interactive. The skill ships to Claude Code, Codex, and Antigravity. Non-goals: choosing an isolation technology for the user, writing lint, test, or CI recipes and the soft read-only invariant sentence (the hard-boundary layer), writing permission lists or the pending-decisions policy (the authority layer), branch protection on the remote (the platform lifecycle layer), and authoring a dev container configuration beyond what the user has chosen.

## ADDED Requirements

### Requirement: Triggering
The skill SHALL load, from a description match, when a target project's execution environment, sandbox, credential exposure, container isolation, network reach, control-plane read-only classification, or non-interactive command defaults are being built, audited, or changed as part of its agent harness, and SHALL NOT load for ordinary dev-container or Docker setup unrelated to agents, for CI gates, or for agent permission lists.

#### Scenario: Sandbox design request
- **WHEN** the user says "before I let the coding agent loose on this repo, work out what it can reach from this container and what we should lock down"
- **THEN** the skill loads

#### Scenario: Credential exposure question
- **WHEN** the user says "the agent runs with my whole ~/.aws mounted; figure out what the harness should do about secrets and the environment it runs in"
- **THEN** the skill loads

#### Scenario: Entry skill routes the layer
- **WHEN** an approved harness plan hands over "build the environment layer at the confirmed grade: isolation decision, sandbox audit, read-only control plane, non-interactive defaults"
- **THEN** the skill loads

#### Scenario: Unattended issue triage
- **WHEN** the user says "we want an agent to process incoming GitHub issues overnight with no one watching; what environment does that need?"
- **THEN** the skill loads

#### Scenario: Plain dev container setup
- **WHEN** the user says "add a devcontainer.json with Node 22 and the Postgres feature so new contributors can open this repo"
- **THEN** the skill does not load

#### Scenario: CI gate request
- **WHEN** the user says "put the type check and the secret scanner into pre-commit and the CI pipeline"
- **THEN** the skill does not load

#### Scenario: Permission list request
- **WHEN** the user says "write the allow and deny lists so the agent can run tests but never force-push"
- **THEN** the skill does not load

#### Scenario: Docker production image
- **WHEN** the user says "shrink the production Docker image and drop root in the final stage"
- **THEN** the skill does not load

### Requirement: Behavior: Confirmed grade bounds the layer
The agent SHALL take the grade the approved plan assigns to the environment layer (light: host with scoped tokens; medium: an isolated environment relied on by convention; thick: container or VM isolation, network allowlist, mount-enforced hard read-only files) as the input that bounds every option it offers. When no grade was assigned, the agent SHALL recommend one from the project's error cost and autonomy and SHALL wait for confirmation before proposing anything else.

#### Scenario: Light grade
- **WHEN** the plan grades the environment layer light
- **THEN** the agent proposes host execution with scoped tokens, records hard read-only enforcement as not applicable at this grade, and offers no container or VM option unless the user asks for one

#### Scenario: Thick grade
- **WHEN** the plan grades the environment layer thick and no isolated environment exists yet
- **THEN** the options offered are limited to isolation technologies (for example dev container or VM), and the control-plane proposal includes a network allowlist

#### Scenario: No grade assigned
- **WHEN** the skill is loaded directly with no plan and no grade
- **THEN** the agent recommends a grade with its reason, names the other grades in a sentence each, and asks nothing about isolation until the user confirms one

### Requirement: Behavior: Existing isolation is used as is
The agent SHALL first establish, from the repository and the running session, whether an isolated execution environment already exists (a dev container, VM, or equivalent in use). When one exists, the agent SHALL adopt it without proposing a replacement. When none exists and the grade is medium or thick, the agent SHALL list the isolation options the grade allows with the trade-offs of each and SHALL NOT recommend one; the user chooses.

#### Scenario: Session already in a dev container
- **WHEN** the repository has a dev container configuration and the session is running inside it
- **THEN** the agent records that environment as the layer's base and proceeds to the threat model without offering alternatives

#### Scenario: No isolation present
- **WHEN** the repository has no container or VM configuration, the session runs on the host, and the grade is medium
- **THEN** the agent presents the options (for example dev container, VM, host with scoped tokens) each with its cost and protection in a sentence, marks none as recommended, and waits for the user's choice

#### Scenario: User chooses the host
- **WHEN** the user picks running directly on the host after seeing the options
- **THEN** the agent accepts the choice, records it as the user's decision for the environment knowledge deposited after approval, and continues; the sandbox audit still runs against the host

### Requirement: Behavior: Threat model sets the protection tier
The agent SHALL rate the project's agent on three facts: whether the lethal trifecta is present (sensitive assets, uncontrolled external input, outbound communication or state change); how reachable each content source is to an attacker (trusted repository, reputation-guarded, open-write); and whether a human is in the loop. When the trifecta is present, a source is open-write, and no human is in the loop, the agent SHALL propose the isolated tier; otherwise it SHALL rate the regular tier.

#### Scenario: Isolation rule met
- **WHEN** the project intends an unattended agent that reads issues anyone can file and holds a token that can push
- **THEN** the agent names the three conditions as met and proposes a separate restricted instance without those credentials and without main-branch write, as the recommendation for the user to confirm

#### Scenario: One condition missing
- **WHEN** the project's agent has the trifecta and reads open-write sources but a developer issues every task and reviews the result before anything leaves the machine
- **THEN** the agent rates the environment regular, places it in the middle band where source restriction is decided, explains that the missing condition is the absence of a human, and does not propose an isolated instance

#### Scenario: Trifecta incomplete
- **WHEN** the project's agent will hold no credentials and cannot write outside the repository
- **THEN** the agent states that the trifecta is incomplete and that the threat model requires no isolation, and still runs the sandbox audit

### Requirement: Behavior: Model resistance adjusts only the middle band
Within the regular tier the agent SHALL treat the middle band as the cases where sources are reputation-guarded, or open-write with a human in the loop, and SHALL use the model's injection resistance only there, to decide how much source restriction or input cleaning to apply. The agent SHALL confirm resistance per model with the user rather than inferring it from vendor reputation, and SHALL NOT let model resistance lower the isolated tier's conclusion.

#### Scenario: Strong model offered against isolation
- **WHEN** the user argues that the frontier model in use resists injection well enough to skip the isolated instance for an unattended open-source triage agent
- **THEN** the agent declines to lower the tier, explains that resistance lowers the chance of hijack while isolation lowers the loss after one, and keeps the proposal

#### Scenario: Weak retrieval sub-agent in the middle band
- **WHEN** the project runs a human-in-the-loop agent that searches the web through a lightweight sub-agent model
- **THEN** the agent recommends tighter network or input restrictions for that sub-agent and asks the user to confirm the resistance of each model named, not of the vendor

#### Scenario: Model unknown
- **WHEN** the user cannot say which model will run in the environment
- **THEN** the agent records the middle-band restriction level as a pending decision with the stricter setting recommended, and continues

### Requirement: Behavior: Five-item sandbox audit
The agent SHALL walk the user through five items: the range of sensitive assets readable or writable from the environment; host privilege leaks (for example a Docker socket or host root mount); exposure of host-local and intranet services through the network; where the framework's session logs go; and the user's explicit risk decision. For each item the agent SHALL report the finding and obtain an explicit accept-or-cut decision; it SHALL NOT mark an item accepted by silence.

#### Scenario: Host credentials mounted
- **WHEN** the audit finds the host's `~/.ssh` and `~/.aws` mounted into the container
- **THEN** the agent reports it under sensitive assets, recommends scoped tokens with the mount removed, and asks the user to accept the exposure or cut it

#### Scenario: User accepts an exposure
- **WHEN** the user says the Docker socket stays mounted because the project builds images
- **THEN** the agent records the item as an accepted risk with the user's reason for the environment knowledge deposited after approval and does not raise it again

#### Scenario: Session logs collected centrally
- **WHEN** the team plans to ship agent session logs to a shared store
- **THEN** the agent names it as a privacy decision because logs carry file contents and command output, and requires an explicit decision before recording it

#### Scenario: Audit left incomplete
- **WHEN** the user ends the conversation with two items undecided
- **THEN** the agent lists those two items in the pending decisions with the recommended option for each, and the deposited knowledge marks them as undecided rather than accepted

### Requirement: Behavior: Control-plane protection spectrum
For the runtime phase the agent SHALL classify each control-plane file as hard read-only (security rules, sandbox configuration, secret-scanning hooks) or soft read-only (linter, type-check, test, build configuration), as recommendations the user confirms per file. Hard read-only is enforced at the mount or OS layer at the thick grade and recorded as a convention below it. The soft read-only invariant sentence belongs to the hard-boundary layer; this layer SHALL point to it, not restate it.

#### Scenario: Classifying the control plane
- **WHEN** the repository has a pre-commit configuration with a secret scanner, a linter configuration, and a dev container configuration
- **THEN** the agent proposes the secret scanner hook and the dev container configuration as hard read-only and the linter configuration as soft read-only, each as a recommendation the user confirms per file

#### Scenario: Soft read-only classification
- **WHEN** the user confirms the test configuration as soft read-only
- **THEN** the deposited knowledge lists the test configuration under soft read-only and points to the hard-boundary layer's knowledge for the invariant wording, and the agent hands "invariant sentence covers the test configuration" to the hard-boundary layer by describing that layer

#### Scenario: Hard read-only below the thick grade
- **WHEN** the layer is graded medium and the user confirms the secret scanner hook as hard read-only
- **THEN** the deposited knowledge lists the hook under hard read-only enforced by convention, and names mount-level enforcement as the step hardening to thick would add

#### Scenario: Opaque security rule
- **WHEN** the user wants the security rule logic unreadable by the project's agent
- **THEN** the agent agrees on the condition that every denial message says it is a policy boundary, not a transient fault, and names the alternative path or the person who decides

### Requirement: Behavior: Non-interactive environment variables
The agent SHALL set the environment variables that keep every command the harness runs non-interactive (such as `CI=true`, `PAGER=cat`, and `GIT_PAGER=cat`) in the project's task runner, and SHALL name in the environment knowledge any per-command flag a recipe still needs. Editing the lint, typecheck, or test recipes themselves belongs to the hard-boundary layer. The variables block is the project's own management code and SHALL be delivered as the project's copy.

#### Scenario: Task runner present
- **WHEN** the project already uses `just`
- **THEN** the agent adds the non-interactive variables to the justfile after the user approves the snippet and tells the user the delivered copy is theirs to maintain

#### Scenario: No task runner agreed
- **WHEN** the project has no task runner and the user has not chosen one
- **THEN** the agent installs nothing, hands the task-runner choice to the hard-boundary layer by describing that layer, and records the variables as a pending decision with `just` as the recommended carrier and the variables listed in the environment knowledge

#### Scenario: Watch-mode test command
- **WHEN** the project's test command enters watch mode by default
- **THEN** the environment knowledge names the run-once flag, and the agent hands "run-once flag for the test recipe" to the hard-boundary layer by describing that layer instead of editing the recipe itself

### Requirement: Behavior: Deposited knowledge and entry route
After the user approves the plan for this layer, the agent SHALL deposit one environment knowledge file whose first line states when to read it, recording the grade, the isolation decision, the protection tier, the five audit decisions with their reasons, the control-plane classification, and the non-interactive rules, and SHALL add a route to it in the project's agent entrypoint while that entrypoint stays at or under 120 lines. Before approval the agent SHALL write nothing into the project.

#### Scenario: Knowledge file deposited
- **WHEN** the user approves the environment plan
- **THEN** the project gains one environment knowledge file opening with a "Read this when..." line that holds every decision above, and the entrypoint routes to it with a load condition

#### Scenario: Entrypoint over target but under cap
- **WHEN** adding the route leaves the entrypoint above the 100-line target but at or under 120 lines
- **THEN** the agent adds the route, reports the overrun to the user as a finding for the knowledge and routing layer, and does not trim other routes itself

#### Scenario: Entrypoint at the cap
- **WHEN** adding the route would push the entrypoint over 120 lines
- **THEN** the agent leaves the entrypoint unchanged, lists "route to environment knowledge" as a pending decision with a recommended row to merge or move, hands the overrun to the knowledge and routing layer by describing that layer, and names the knowledge file as temporarily unreachable in its closing report

#### Scenario: Inspection before approval
- **WHEN** the agent has completed the audit but the user has not yet approved the plan
- **THEN** no file in the project has been created or changed

### Requirement: Behavior: Confirmation and handoff
The agent SHALL settle from the repository only what is observable there (configuration files, mounts, tools in use), SHALL ask the user on every other point, and SHALL present each recommendation with its reason and the alternatives. At the end it SHALL report what it deposited, the pending decisions, and the findings it hands to other layers by description, for the entry skill's clean-context read-back.

#### Scenario: Observable fact
- **WHEN** the dev container configuration lists its mounts
- **THEN** the agent reads the mounts from the file and does not ask the user to list them

#### Scenario: Finding for another layer
- **WHEN** the audit shows the project's agent holds a token that can push to the default branch
- **THEN** the agent records the scoped-token recommendation under the sensitive-assets audit item, hands "push as an irreversible action needing pre-authorisation" to the authority layer and "default-branch protection" to the platform lifecycle layer by describing each layer, not by naming a skill, and lists both in its closing report

#### Scenario: User reverses a confirmed choice
- **WHEN** the user later changes an accepted audit item to cut
- **THEN** the agent updates the deposited knowledge and the related variables block, and names the finished work the reversal changed

### Requirement: Outcomes
Given a target project, the confirmed grade, and the user's answers, the agent SHALL leave the environment layer in a state a reader can verify without seeing the skill: the result matches the confirmed grade, the isolation decision is the user's, every audit item carries an explicit decision, control-plane files are classified, the non-interactive variables are in place, and the knowledge is reachable from the entrypoint.

#### Scenario: Pair-programmed project in an existing dev container
- **WHEN** the plan grades the layer medium for a repository with a dev container the session runs in, a pre-commit secret scanner, a linter configuration, a justfile, trusted-repository sources only, and a developer who reviews every result
- **THEN** the result uses the existing container unchanged, rates the regular tier naming the missing conditions, records five accepted-or-cut audit items with reasons, classifies the secret scanner as hard read-only by convention and the linter as soft read-only pointing to the hard-boundary knowledge for the invariant, adds the non-interactive variables to the justfile, proposes no network allowlist, and leaves one knowledge file routed from the entrypoint; the rubric fails if any option was chosen for the user, any audit item lacks a decision, or a thick-grade mechanism was added

#### Scenario: Unattended triage on the host
- **WHEN** the plan grades the layer thick for a maintainer with no container who wants an agent to process public issues overnight
- **THEN** the result lists container and VM isolation options without a recommendation and records the user's pick, proposes a restricted instance without credentials or main-branch write and records the user's answer, includes a network allowlist in the control-plane proposal, and places the model-resistance question in the middle band only; the rubric fails if model resistance was used to drop the isolated proposal or if an isolation option was presented as recommended

#### Scenario: User declines the whole audit
- **WHEN** the user of a project with a justfile says to skip the sandbox audit and just document the environment
- **THEN** the result deposits the knowledge file with the audit section marked as declined by the user on that date, lists the five items as pending decisions with recommendations, and still adds the non-interactive variables to the justfile; the rubric fails if any item is recorded as accepted
