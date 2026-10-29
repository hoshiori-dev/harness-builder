# Spec Delta

## Purpose

Governs what an agent that loaded `hard-boundary-building` observably does when it builds, thickens, or thins the hard-boundary layer of a target project: the deterministic checks (formatter, secret scan, lint, typecheck, tests, architecture boundaries) that run in pre-commit hooks and in CI on GitHub or GitLab, and the soft fallbacks for what determinism cannot reach. The skill ships to Claude Code, Codex, and Antigravity. Non-goals: deciding which commands an agent may run (the authority layer), the harness self-check and sync rules (the entropy layer), labels, templates, merge method, and required-check registration on the remote (the platform lifecycle layer), the sandbox or container (the environment layer), and fixing an ordinary failing test or lint error in application code.

## ADDED Requirements

### Requirement: Triggering
The skill SHALL load, from its description alone, when the user asks to set up, grade, thicken, thin, or repair the hard checks a project runs before a commit or in CI as part of making the project workable for agents, and SHALL NOT load for a single failing check, a deployment pipeline, or a neighbouring harness layer's concern.

#### Scenario: Pre-commit and CI gates for an agent-worked repository
- **WHEN** the user says "Agents will be committing to this repo. Set up the pre-commit hooks and CI checks so nothing broken or secret can land on main."
- **THEN** the skill loads

#### Scenario: Noisy check output
- **WHEN** the user says "Every time a check fails the agent gets a wall of pytest and tsc output and loses the thread. Make our checks quieter without losing the errors."
- **THEN** the skill loads

#### Scenario: Custom boundary check with routing
- **WHEN** the user says "Add a hook that blocks imports from `app/` into `infra/` and tells whoever hits it what to do instead."
- **THEN** the skill loads

#### Scenario: Aggregator passes on a skipped job
- **WHEN** the user says "Our CI gate went green although the test job was skipped. Harden the gate that PRs depend on."
- **THEN** the skill loads

#### Scenario: Single failing test near-miss
- **WHEN** the user says "The pre-commit hook fails on `tests/test_parser.py`, fix the test."
- **THEN** the skill does not load

#### Scenario: Deployment pipeline near-miss
- **WHEN** the user says "Write a CI workflow that builds the Docker image and deploys it to staging on every tag."
- **THEN** the skill does not load

#### Scenario: Permission list near-miss
- **WHEN** the user says "Decide which git commands the agent may run without asking and which are denied outright."
- **THEN** the skill does not load

#### Scenario: Platform entities near-miss
- **WHEN** the user says "Set up the label taxonomy, the PR template, and mark the checks as required on main."
- **THEN** the skill does not load

### Requirement: Behavior: Grade is confirmed before any tool is chosen
The agent SHALL take the grade from the approved harness plan's layer table when one exists; otherwise it SHALL recommend omitted, light, medium, or thick from the project's error cost, autonomy, and team size, loosened by its environment isolation, and SHALL write nothing until the user confirms. Light: formatter and secret scan; medium: plus lint, typecheck, and tests in pre-commit and CI; thick: plus architecture boundary checks and an aggregator gate meant to become the required check.

#### Scenario: Grade assigned by the entry skill
- **WHEN** the harness plan the user approved marks the hard-boundary layer as medium
- **THEN** the agent restates what medium adds and proceeds without re-asking the grade

#### Scenario: No grade assigned
- **WHEN** the skill is loaded directly for a solo prototype with no plan
- **THEN** the agent recommends light with its reason, names the heavier grades in a sentence each, says which variable would raise it, and waits for the user's choice before touching any file

#### Scenario: Isolated environment with high error cost
- **WHEN** the project runs agents in a dev container with a network allowlist and the user names a high error cost
- **THEN** the agent's recommendation says the isolation argues for one grade looser than the error cost alone would, and lets the user pick between the two

#### Scenario: User chooses a thinner grade than recommended
- **WHEN** the agent recommends thick for a multi-contributor production repository and the user chooses medium
- **THEN** the agent challenges the choice once with the evidence, then builds medium and records the choice in the deposited knowledge

#### Scenario: Layer marked omitted
- **WHEN** the approved plan marks the hard-boundary layer as omitted
- **THEN** the agent writes no hook, recipe, or CI file, leaves any existing check untouched, and records in its report why the layer is omitted and what would raise it

### Requirement: Behavior: Files to be written are agreed before the first write
Before the first write the agent SHALL present the files it will create or change together with a summary of the hook, recipe, and CI contents each will hold, and SHALL wait for the user's agreement; an approved harness plan counts as that agreement only for the files it names, and the confirmed grade is a prerequisite of the list, not a substitute for it.

#### Scenario: Direct load without a plan
- **WHEN** the skill was loaded directly, the user confirmed medium, and the tools are chosen
- **THEN** the agent lists the pre-commit configuration, the recipes, the CI file, and the knowledge file with a one-line summary of each, and no file exists in the project until the user agrees to the list

#### Scenario: Plan names only some of the files
- **WHEN** the approved harness plan names the pre-commit configuration and the checks workflow but no knowledge file
- **THEN** the agent writes the two named files and asks before creating the knowledge file, rather than treating the plan as approval for it

#### Scenario: User strikes an item from the list
- **WHEN** the user removes the CI workflow from the presented list
- **THEN** the agent writes the remaining files, does not create the workflow, and lists the missing CI check as a pending decision with its recommendation

### Requirement: Behavior: Tools are listed per language ecosystem and chosen by the user
For every check the grade calls for, the agent SHALL list the candidate tools of the project's language ecosystem with one recommendation and its reason, SHALL adopt without asking only a tool whose role is observable from the repository (a hook, recipe, or script that runs it), and SHALL ask for everything else.

#### Scenario: Formatter and linter both observable
- **WHEN** the repository's existing hook runs both `ruff check` and `ruff format`
- **THEN** the agent keeps `ruff` as the linter and the formatter without asking

#### Scenario: Linter observable, formatter not
- **WHEN** the repository has a `ruff` lint configuration and nothing that runs a formatter
- **THEN** the agent keeps `ruff` as the linter, lists the ecosystem's formatters with `ruff format` recommended, and asks the user to choose

#### Scenario: Linter not yet chosen
- **WHEN** a TypeScript repository has no linter configured and the grade is medium
- **THEN** the agent lists the ecosystem's linters with one recommended, and configures only the one the user names

#### Scenario: Task runner choice
- **WHEN** the project has no task runner
- **THEN** the agent recommends `just` as the single command surface for the checks, names `make` and package-manager scripts as alternatives, and uses whichever the user chooses for every recipe it writes

### Requirement: Behavior: Management-script language is agreed with the user
Before writing or copying any custom check, hook, or helper script for the target, the agent SHALL agree its language with the user: recommend Deno when a Deno runtime is present (explicit permissions); otherwise the popular scripting idiom of the project's community language; when neither exists, propose Deno and ask whether adding it to the agent environment is acceptable. The agent SHALL never choose a language the user says they cannot read.

#### Scenario: Deno present
- **WHEN** `deno.json` and a Deno binary exist in the target
- **THEN** the agent recommends Deno for the custom checks, citing explicit permissions, and waits for the user's confirmation

#### Scenario: Python project without Deno
- **WHEN** the target is a Python project with no Deno runtime
- **THEN** the agent recommends Python scripts and names Deno as the alternative, with the dependency it would add

#### Scenario: Go service without Deno
- **WHEN** the target is a Go service with no Deno runtime
- **THEN** the agent recommends the Go community's scripting idiom for the custom checks, names Deno as the alternative, and writes no script until the user answers

#### Scenario: No community scripting language
- **WHEN** the target holds only SQL migrations and YAML configuration with no Deno runtime
- **THEN** the agent proposes Deno, asks whether adding Deno to the agent environment is acceptable, and writes no script until the user answers

#### Scenario: User refuses the proposed language
- **WHEN** the user declines Deno and names a language the agent did not list
- **THEN** the agent writes the checks in the user's language and records the choice in the deposited knowledge

### Requirement: Behavior: Delivered scripts follow the management-code contract
Every script the agent writes or copies into the target SHALL run with no interactive prompt, SHALL offer `--help` with a usage example, SHALL put data on stdout and diagnostics on stderr, SHALL exit 0 on pass, 1 on a finding or error, and 2 on bad arguments, SHALL be idempotent, and when written in Python SHALL run under plain `python3` with the standard library unless the user accepts a dependency.

#### Scenario: Boundary check passes
- **WHEN** a delivered boundary check runs on a tree with no violation
- **THEN** it prints nothing on stderr, prints its result on stdout, and exits 0

#### Scenario: Bad argument
- **WHEN** a delivered script is run with an unknown flag
- **THEN** it prints usage on stderr and exits 2 without touching any file

#### Scenario: Python chosen on a machine without uv
- **WHEN** the agreed language is Python and the target environment has no uv
- **THEN** the delivered script runs with `python3` alone and the recipe that calls it does not require uv

### Requirement: Behavior: Native quiet output is configured and log parsers are challenged
The agent SHALL configure every check with the tool's own quiet or compact flags so a failure reaches the agent as errors rather than full logs, SHALL NOT propose or silently add an output parser, filter, or wrapper for a tool that lacks such flags, and SHALL challenge a request for one once with the quiet-flag or scoped-command alternative; after that the user's choice binds.

#### Scenario: Test runner with quiet flags
- **WHEN** the project runs `pytest`
- **THEN** the deposited recipe runs it with its quiet and short-traceback options, and the configuration carries no post-processing of the output

#### Scenario: Tool without a quiet mode
- **WHEN** a check the user chose prints full logs and offers no compact flag
- **THEN** the agent accepts the native output, records the trade-off in one sentence in the deposited knowledge, and writes no parser

#### Scenario: User asks for a log filter
- **WHEN** the user asks the agent to write a script that strips the noise from a tool's output
- **THEN** the agent explains once why it recommends against the filter and offers the quiet flags or a scoped command instead, and writes nothing until the user answers

#### Scenario: User insists on the log filter
- **WHEN** the user has heard the alternatives and still wants the filter
- **THEN** the agent writes it as project-owned management code in the agreed language and records the maintenance trade-off in the deposited knowledge and the report

### Requirement: Behavior: Pre-commit stays within a seconds budget and scans secrets on every commit
The agent SHALL agree a seconds budget for the pre-commit hook with the user, SHALL place at least the formatter and a secret scan in it so every checkpoint commit is scanned, SHALL recommend betterleaks for the scan with gitleaks and TruffleHog named as alternatives, and SHALL move any check that cannot meet the budget to CI or to a task-end recipe rather than into the hook.

#### Scenario: Light grade hook
- **WHEN** the grade is light and the project has a CI platform
- **THEN** the hook runs only the formatter and the secret scan, and the same scan runs in CI; when no CI platform is known the agent asks which one will host the project before writing a CI file

#### Scenario: Slow test suite
- **WHEN** the grade is medium and the test suite takes minutes
- **THEN** the tests go to CI and a scoped fast recipe, the hook keeps format, secret scan, and the checks that fit the budget, and the agent tells the user why the tests are not in the hook

#### Scenario: Secret scanner unavailable
- **WHEN** the recommended scanner cannot be installed in the target's environment
- **THEN** the agent offers the alternative scanners with their install path and writes no hook until the user chooses one

#### Scenario: User declines every scanner
- **WHEN** the user declines every scanner the agent offered
- **THEN** the agent delivers the hook with the remaining checks, marks it as incomplete in the deposited knowledge and the report, says the light grade is not met, and lists the missing scan as the first pending decision with the recommended scanner

### Requirement: Behavior: Custom checks fail with a routing message
Every project-specific hook, boundary check, or lint rule the agent writes SHALL fail with a message that names what is wrong and what to do instead (the replacement, or the document or example to read), SHALL never hide an unexpected error behind a fallback, and SHALL follow the management-code ownership rules the project agreed to.

#### Scenario: Architecture boundary violated
- **WHEN** a delivered boundary check finds an import from `app/` into `infra/`
- **THEN** its message names the file and line, the forbidden direction, the allowed alternative, and the knowledge file that states the rule

#### Scenario: Check cannot read its input
- **WHEN** a delivered check cannot open a file it expected
- **THEN** it exits with a distinct error that names the file, not a pass

#### Scenario: Custom check deposited
- **WHEN** a custom check is deposited
- **THEN** the agent tells the user the project owns it and that later fixes to the plugin do not reach the copy

### Requirement: Behavior: The CI gate is what thick adds and treats skipped as failure
For the thick grade the agent SHALL deliver one aggregator job that depends on every check job and fails when any needed job failed, was cancelled, or was skipped, so a single check name can become the required check; for medium it SHALL deliver independent check jobs and no aggregator. The agent SHALL say that registering checks as required on the remote belongs to the platform lifecycle layer or a human.

#### Scenario: Medium grade workflow
- **WHEN** the grade is medium
- **THEN** the delivered workflow holds one job per check with no aggregator, and the agent says the gate is what the thick grade would add

#### Scenario: Needed job skipped
- **WHEN** the grade is thick and a path filter skips the test job on a pull request
- **THEN** the gate job fails and names the skipped job

#### Scenario: All jobs green
- **WHEN** the grade is thick and every needed job succeeds
- **THEN** the gate job succeeds and is the only name the agent proposes for the required check

#### Scenario: Thick grade on GitLab
- **WHEN** the platform is GitLab and the grade is thick
- **THEN** the delivered pipeline contains a final stage that fails on any earlier failure or skip, and the agent notes that marking it required is a project-settings action outside this layer

### Requirement: Behavior: Check configuration is declared soft read-only
The deposited knowledge SHALL state once, for the configuration files this layer delivers, that lint, type, test, or build rules may not be weakened nor assertions deleted to make a failing check pass, while adjustments that keep the invariant and proposals to the user stay open. When the environment layer already records that invariant, the agent SHALL link to it instead of writing a second copy, and SHALL name the hard read-only files (secret scan hook, security rules) as a separate class.

#### Scenario: Knowledge deposited
- **WHEN** the hard-boundary knowledge is deposited and no other knowledge file states the soft read-only invariant
- **THEN** it contains the sentence, names the configuration files it covers, and the agent tells the user that the layer owning the environment should adopt this sentence as its source

#### Scenario: Environment layer already states the invariant
- **WHEN** a knowledge file from the environment layer already carries the control-plane spectrum with the soft read-only sentence
- **THEN** the hard-boundary knowledge links to that sentence and lists only the configuration files it adds under it, and no second copy of the sentence exists in the project

#### Scenario: Agent later tempted to relax a rule
- **WHEN** a future session hits a lint failure in business code
- **THEN** the deposited knowledge leaves it three routes, fixing the code, an adjustment that keeps the invariant, or a proposal to the user, and forbids the fourth: weakening the rule or deleting an assertion to pass

### Requirement: Behavior: Verifier fallback covers what determinism cannot
For a check the user wants that no deterministic tool can express (business-logic consistency, privacy review beyond pattern matching), the agent SHALL offer an explicit self-check step at a fixed position in the workflow and, when the client supports subagents, a clean-context verifier before commit, stating that both are soft boundaries whose compliance is not total.

#### Scenario: PII review requested
- **WHEN** the user wants new code reviewed for personal data handling before each pull request
- **THEN** the agent adds a named self-check step to the deposited workflow and offers a clean-context verifier subagent as the stronger option

#### Scenario: No subagent support
- **WHEN** the client has no subagent mechanism
- **THEN** the agent delivers only the explicit self-check step and records the degradation in the deposited knowledge

### Requirement: Behavior: Platform branch and handoffs
The agent SHALL ask or observe whether the remote is GitHub or GitLab and deliver only that platform's CI files; for any other host it SHALL say CI files are out of scope and deliver the hook and recipes. It SHALL hand entropy checks, permission lists, and required-check registration to the layers that own them by describing the work rather than naming a skill, and SHALL end with a report listing every deposited file, the pending decisions, and the remote actions a human must take.

#### Scenario: Platform observed from the remote
- **WHEN** `git remote -v` shows a GitLab host
- **THEN** the agent delivers `.gitlab-ci.yml` content and no `.github/workflows/` file

#### Scenario: No remote configured
- **WHEN** the repository has no remote
- **THEN** the agent asks which platform will host it, and delivers only the hook and recipes until the user answers

#### Scenario: Unsupported host
- **WHEN** `git remote -v` shows a Bitbucket or Gitea host
- **THEN** the agent says CI files for that host are outside what it delivers, deposits the hook and recipes, and lists the CI checks as a pending decision with the jobs they should run

#### Scenario: Handoff by description
- **WHEN** the harness plan includes a harness self-check in CI
- **THEN** the agent leaves a slot for it among the CI jobs (and in the gate's dependencies at thick) and states that the layer owning entropy delivers the check, without naming a skill

#### Scenario: Final report
- **WHEN** the layer is built
- **THEN** the report lists every file written, the budget and grade chosen, the pending decisions, and the remote actions (branch protection, required check) a human must perform

### Requirement: Outcomes
Given a target repository and an approved grade, the agent SHALL leave the project with a hard-boundary layer that an independent reader can run and judge against the grade without opening the skill.

#### Scenario: Medium grade on a Python GitHub repository
- **WHEN** the user asks for the hard-boundary layer at medium for a Python service on GitHub, confirms ruff, pyright, pytest, betterleaks, `just`, and Python as script language, and approves the list of files
- **THEN** the repository gains a pre-commit configuration that runs the formatter, the secret scan, lint, and typecheck within the agreed budget, `just` recipes for lint, typecheck, the full test suite, and a scoped fast test, a checks workflow with one quiet-flagged job per check and a secret-scan job and no aggregator, a knowledge file that states or links the soft read-only invariant, and a report whose pending decisions name any remote setting left for a human; no delivered file references a path inside the plugin

#### Scenario: Thick grade on a TypeScript GitHub repository
- **WHEN** the user asks for thick on a multi-contributor TypeScript repository, confirms the tools, a boundary rule between `app/` and `infra/`, Deno for the custom check, and approves the list of files
- **THEN** the repository gains the medium set plus a boundary check whose failure message names the file, the rule, and the alternative, and a workflow whose check jobs converge on one gate job that fails on a failed, cancelled, or skipped job; the report names that gate as the one check to register as required and says a human or the platform layer registers it

#### Scenario: Light grade on a research prototype
- **WHEN** the user asks for the hard-boundary layer at light for a short-lived experiments repository and declines any CI file
- **THEN** the repository gains only a formatter and a secret scan in the pre-commit hook, a one-line recipe to run them, and a sentence in the knowledge that names the grade; no lint, typecheck, test, or gate configuration is added, the missing CI secret scan is a pending decision with the recommended workflow, and the agent records that the grade can be raised later through hardening

#### Scenario: Existing hooks contradict the agreed grade
- **WHEN** the repository already has a pre-commit hook that runs the full test suite for several minutes and the agreed grade is medium with a seconds budget
- **THEN** the agent proposes moving the tests to CI and a scoped recipe, changes the hook only after the user agrees, and leaves the hook untouched with the item on the pending decisions list if the user declines
