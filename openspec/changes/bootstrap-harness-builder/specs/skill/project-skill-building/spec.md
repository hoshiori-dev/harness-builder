# Spec Delta

## Purpose

Governs what an agent that loaded `project-skill-building` observably does when it writes, improves, or diagnoses a project skill inside the target project: the definition and tests it fixes and gets approved before writing, the shape of the skill it produces, the pruning and lint it applies, the behavioural tests it runs, and the linter asset it delivers. Ships to Claude Code, Codex, and Antigravity. Non-goals: applying the warrant threshold (recurring, non-obvious, fragile, ordered, or branchy) that decides whether a process gets a skill (the knowledge and routing layer applies it and hands over a definition), choosing the project's skill directory layout, writing knowledge files or the entrypoint, wiring project checks into the task runner or CI, authoring the skills this plugin itself ships, and anything about another skill library.

## ADDED Requirements

### Requirement: Triggering
The description SHALL load the skill when the user asks to write, improve, review, prune, or diagnose a skill for agents in the project they are working in, including indirect phrasings about an agent instruction package misbehaving, and SHALL NOT load it for application code, human documentation, knowledge files or entrypoints, non-agent uses of the word "skill", or editing the skills this plugin itself ships.

#### Scenario: New project skill requested
- **WHEN** the user says "Our release procedure keeps going wrong when the agent runs it; turn it into a skill the agent loads when it releases"
- **THEN** the skill loads

#### Scenario: Misbehaving skill reported
- **WHEN** the user says "The agent never picks up the migration SOP we put under .agents/skills, even when I ask for a migration"
- **THEN** the skill loads

#### Scenario: Skill review requested
- **WHEN** the user says "Review .agents/skills/db-review/SKILL.md, it has grown to 700 lines and the agent skips the verification step"
- **THEN** the skill loads

#### Scenario: Entrypoint near miss
- **WHEN** the user says "Rewrite AGENTS.md so the agent knows which directories matter and which commands to run"
- **THEN** the skill does not load

#### Scenario: Application code near miss
- **WHEN** the user says "Add a skill system to the game: each character levels skills with experience points"
- **THEN** the skill does not load

#### Scenario: Human documentation near miss
- **WHEN** the user says "Write a CONTRIBUTING guide that explains our release procedure to new maintainers"
- **THEN** the skill does not load

#### Scenario: Plugin's own skill near miss
- **WHEN** the user says "Tighten the description of skills/harness-create/SKILL.md so it stops firing on unrelated requests" while working inside this plugin's repository
- **THEN** the skill does not load and the repository's own skill-quality guidance applies

### Requirement: Behavior: Definition precedes writing
Before writing or editing a skill, the agent SHALL write down the task unit covered, the trigger list including indirect phrasings, what the agent lacks that makes the skill necessary, the invocation mode, and the least capable model the skill must carry; it SHALL confirm with the user every answer the repository cannot settle, and SHALL report rather than proceed when an agent without the skill already does the task well.

#### Scenario: Value absent
- **WHEN** the requested skill would only restate steps a bare agent already performs correctly on the least capable model the project uses
- **THEN** the agent reports that finding as a recommendation to the user and to the layer that handed over the definition when there is one, and writes no skill until the user decides

#### Scenario: Invocation mode unknown
- **WHEN** the repository does not show whether the process must run on every matching task or only when a human asks
- **THEN** the agent asks the user, presenting model-invoked as the recommendation with the context cost it carries, and does not scaffold until answered

#### Scenario: Weakest model unknown
- **WHEN** nothing in the repository names the model tier agents run on
- **THEN** the agent asks for the least capable tier before judging what the skill must spell out

### Requirement: Behavior: Tests are fixed before the first edit
Before the first edit, the agent SHALL record at least three prompts that must load the skill and three near misses sharing vocabulary that must not, at least two outcome tasks with a rubric of observable requirements, the critical failures, and the passing threshold; when the host offers no clean-context subagent, it SHALL record that degradation for the final report instead of grading its own output.

#### Scenario: Tests recorded
- **WHEN** the agent moves from definition to presenting its plan
- **THEN** the trigger prompts, near misses, outcome tasks, rubric, critical failures, and threshold exist in writing, and no prompt names the skill

#### Scenario: No subagent available
- **WHEN** the host cannot dispatch a clean-context subagent
- **THEN** the agent still writes the test cases, notes that they were not run and why, and does not report the skill as tested

### Requirement: Behavior: Nothing lands before the user approves the definition and tests
The agent SHALL present the definition, trigger list, test cases with rubric and threshold, its recommendations on every open choice, and the files it intends to create or change, and SHALL create or change no file in the target project until the user approves or amends that set; an approved set authorises those files and nothing else.

#### Scenario: Definition presented
- **WHEN** the definition and test cases are recorded
- **THEN** the agent shows them to the user together with its recommendations and the intended file locations, and asks for agreement before scaffolding

#### Scenario: Approval not yet given
- **WHEN** the definition and tests are recorded but the user has not yet answered
- **THEN** no file under the project's skill directory exists or has changed, and the agent waits or continues only with reading and reporting

#### Scenario: User amends the tests
- **WHEN** the user replaces one near miss and lowers the passing threshold before approving
- **THEN** the agent records the amended cases as the tests of record, restates the set once, and scaffolds only after the user confirms the amended set

### Requirement: Behavior: The produced skill has the agreed shape
The delivered skill SHALL be a directory whose `SKILL.md` frontmatter `name` equals the directory name in lowercase letters, digits, and single hyphens, with a third-person description that opens on the skill's leading word, gives most of its length to triggers with one trigger per branch, names what it is not for, and restates nothing from the body; `scripts/`, `references/`, and `assets/` SHALL exist only when a file goes in.

#### Scenario: Description inspected
- **WHEN** a reviewer reads the delivered description
- **THEN** it is third person, starts with the capability's leading word, contains a "Use when" clause covering direct and indirect phrasings, a "Not for" clause, and no sentence that also appears in the body

#### Scenario: Empty bundle directory
- **WHEN** the skill needs no script, reference, or asset
- **THEN** the delivered directory contains only `SKILL.md`

#### Scenario: Host-specific field
- **WHEN** the user wants the skill to load only when invoked by name
- **THEN** the agent writes the host's switch for that, tells the user it is outside the Agent Skills specification and which host honours it, and lists hosts where the skill would still load by description

### Requirement: Behavior: Body follows the information hierarchy
The delivered body SHALL put ordered steps first, with a `Done when:` criterion only where the boundary is checkable and changes how the step is executed or judged; rules every branch needs inline; branch-specific material in `references/` files each linked at first mention with a precise load condition; one default per decision presented as a recommendation.

#### Scenario: Completion criteria checked
- **WHEN** a reviewer reads every `Done when:` in the delivered skill
- **THEN** each can be judged done or not done from observable evidence, and steps with no meaningful boundary carry none

#### Scenario: Reference pointer wording
- **WHEN** the delivered skill links a reference file
- **THEN** the sentence states the condition under which to read it, never "see references/"

#### Scenario: Two equal options found
- **WHEN** the draft presents two approaches as equally valid at one decision
- **THEN** the agent picks one as the recommended default and reduces the other to a single sentence

### Requirement: Behavior: Scripts bundled with a project skill obey the script rules
A script the agent writes into a project skill SHALL never prompt interactively, offer `--help` with a usage example, print data on stdout and diagnostics on stderr, exit 0 on success, 1 on a finding or error, and 2 on bad arguments, be idempotent, pin dependency versions, summarise output above about 10,000 characters by default, and be named in a `compatibility` frontmatter line.

#### Scenario: One-off logic
- **WHEN** a step needs logic that would differ from run to run
- **THEN** the agent writes it as an inline instruction, not a bundled script

#### Scenario: Script interface inspected
- **WHEN** a reviewer runs the delivered script with `--help`, with bad arguments, and twice on the same input
- **THEN** it prints a usage example, exits 2 with usage on stderr, and produces identical output with no interactive prompt on both runs

### Requirement: Behavior: Script language defaults to Python with PEP 723
The agent SHALL recommend Python with PEP 723 inline metadata, standard library first and runnable on plain `python3` without uv, for every bundled script, unless the project's community language is TypeScript or the user chooses otherwise; the choice SHALL be confirmed with the user before the script is written.

#### Scenario: Python-ecosystem project
- **WHEN** the target project's community language is Python and the user agrees to the recommendation
- **THEN** the delivered script carries PEP 723 inline metadata, prefers the standard library, and runs on plain `python3` when it has no dependencies

#### Scenario: Project in another ecosystem
- **WHEN** the target project is a Go service with no Deno runtime
- **THEN** the agent recommends Python with PEP 723 metadata as the default, names Go as the alternative in one sentence, and writes the script only after the user confirms

#### Scenario: TypeScript project
- **WHEN** the target project's community language is TypeScript
- **THEN** the agent recommends Deno when a Deno runtime is already present, citing its explicit permissions, and otherwise the project's existing TypeScript runtime idiom; it names the other as the alternative in one sentence, asks before adding any runtime to the agent environment, and writes the script only after the choice

### Requirement: Behavior: Three pruning passes against the weakest model
After writing or touching any part of a skill, description included, the agent SHALL run three passes in order: deduplicate so each meaning has one home, delete lines that no longer bear on the skill, and delete whole sentences that would not change behaviour on the least capable model the skill must carry.

#### Scenario: Restated rule
- **WHEN** the draft states one rule in the description and again in the body
- **THEN** the agent keeps the copy where the hierarchy ranks it and removes the other

#### Scenario: No-op sentence
- **WHEN** a sentence tells the agent to do what the least capable supported model already does unprompted
- **THEN** the agent deletes the sentence whole rather than rewording it

### Requirement: Behavior: Lint runs before tests and every warning gets a verdict
The agent SHALL run the shipped linter over the skill after pruning, through uv when available and plain `python3` otherwise, SHALL fix every error, and SHALL apply each warning or state why it does not apply before moving to behavioural tests.

#### Scenario: Error reported
- **WHEN** the linter exits 1 on the draft
- **THEN** the agent fixes the named findings and re-runs until it exits 0

#### Scenario: Warning kept
- **WHEN** the linter warns about a description over 900 characters and the triggers are all distinct branches
- **THEN** the agent records why the length stays and proceeds

#### Scenario: uv missing
- **WHEN** `uv` is not installed in the environment
- **THEN** the agent runs the linter with `python3` and gets the same findings

### Requirement: Behavior: Behavioural tests run in clean contexts at the floor tier
When clean-context subagents are available, the agent SHALL run every trigger prompt and near miss at least twice and each outcome task once on the least capable model tier the skill claims, in an isolated worktree with the candidate exposed to skill discovery, observe loading through host telemetry or a neutral `SKILLS_LOADED` line, grade outputs with a subagent that produced none of them, and revise the instruction rather than the prompt on failure.

#### Scenario: Trigger case contradicts expectation
- **WHEN** two valid attempts on a near miss show the skill loaded
- **THEN** the agent rewrites the description, re-prunes, re-lints, and re-runs the affected cases

#### Scenario: Isolation unavailable
- **WHEN** no worktree can be created for the run
- **THEN** the agent runs in the best available environment, keeps outputs out of version control, and records the degradation with the results

#### Scenario: Floor tier cannot complete
- **WHEN** a solver on the claimed tier fails the task with the skill loaded
- **THEN** the agent strengthens the instruction or asks the user to raise the claimed tier; it does not escalate the solver silently

### Requirement: Behavior: Diagnosis starts from the symptom
For an existing skill, the agent SHALL map the observed symptom to its cause before editing: never or wrongly triggers to the description; stopped early or shallow work to a missing or weak completion criterion; an unopened reference to its pointer wording; contradictions to duplication or stale layers; length to sprawl; then apply the smallest general fix and run pruning, lint, and tests.

#### Scenario: Reference never opened
- **WHEN** session evidence shows the agent needed a reference it never read
- **THEN** the agent sharpens the pointer's load condition first and inlines the material only if a sharpened pointer still fails

#### Scenario: Shallow step
- **WHEN** the agent read one file where the step required a sweep
- **THEN** the fix makes the completion criterion exhaustive or plants a stronger word, not an extra paragraph

### Requirement: Behavior: Delivered linter is the project's own management code
When the agent delivers the linter into the target project, it SHALL confirm with the user whether the shipped Python is used as is or rewritten in the project's agreed language, place it where the project keeps management scripts, tell the user that later changes to this plugin do not reach the copy, and leave wiring into the project's check or CI to the layer that owns the harness self-check, whose confirmed grade decides whether the structural tier is installed.

#### Scenario: Linter delivered as is
- **WHEN** the user accepts the Python reference implementation
- **THEN** the copy sits in the project's management scripts directory with its test beside it, no project file calls into a skill directory, and the report names the harness self-check layer as the owner of wiring it into the project's check once the grade allows the structural tier

#### Scenario: User declines delivery
- **WHEN** the user does not want a linter in the project
- **THEN** the agent still lints the skill from the plugin's copy, records the decision, and leaves no linter in the project

### Requirement: Behavior: Process-critical skills are routed by the entrypoint owner
When the finished skill is process-critical, the agent SHALL hand the explicit routing of it to the layer that owns the entrypoint by describing that layer rather than naming a skill, and SHALL NOT edit the entrypoint itself.

#### Scenario: Process-critical skill finished
- **WHEN** a skill the project cannot afford to miss is delivered
- **THEN** the report says the entrypoint must name it by scenario and names the layer responsible, without claiming to have edited the entrypoint

### Requirement: Behavior: User-only decisions go to the pending list
A decision only the user can make SHALL enter a pending decisions list presented once, with options, recommendation, and affected work, rather than blocking the parts of the work that do not depend on it.

#### Scenario: Blocked on a user decision
- **WHEN** the user is unreachable about the script language
- **THEN** the agent finishes every part not depending on it and lists the choice, options, recommendation, and affected work in one pending decisions list

### Requirement: Outcomes
Given a skill task in a target project, the agent SHALL leave a skill that a reviewer can accept on the rubric below without seeing this skill: tests written and approved first, a conforming description, checkable completion criteria, conditioned pointers, lint exit 0 with warnings reasoned, and a test report or recorded degradation.

#### Scenario: New release skill
- **WHEN** asked to create a skill for a project's release procedure, in a project whose agreed skills directory already exists, with subagents available
- **THEN** the result contains a `<name>/SKILL.md` under that skills directory with `name` equal to its directory, a description under 1024 characters opening on the leading word with "Use when" and "Not for" clauses, numbered steps with a checkable `Done when:` on the verification step, every reference linked with a load condition, lint exit 0, and a report listing trigger results, outcome scores against the pre-declared rubric, solver tier, and any degradation

#### Scenario: Existing skill that never triggers
- **WHEN** asked to fix a skill the agent never loads, without subagents
- **THEN** the result changes the description to carry the words users actually say and indirect phrasings, changes the body only by what the three pruning passes remove, lints clean, and reports the test cases written and the reason they were not run

### Requirement: Script: lint_skill.py
The asset `lint_skill.py` SHALL lint one skill directory or `SKILL.md` given by `--skill PATH`, print human-readable findings or, with `--json`, a JSON array of findings each carrying location, level, reason, and suggestion on stdout, exit 0 with no errors, 1 when a finding is an error or the skill file is missing, and 2 on bad arguments, offer `--help` with a usage example, be idempotent, and run under `uv run` and plain `python3`, using the standard library with PyYAML optional.

#### Scenario: Clean skill
- **WHEN** run on a skill whose frontmatter, structure, links, reachability, description budget, body size, and script hygiene pass
- **THEN** stdout reports the skill as passing and the exit code is 0

#### Scenario: Findings in JSON
- **WHEN** run with `--json` on a skill whose `name` differs from its directory and whose reference link target does not exist
- **THEN** stdout is a JSON array with one error per finding, each stating what is wrong and how to fix it, and the exit code is 1

#### Scenario: Description budget tiers
- **WHEN** run on three skills whose descriptions are 700, 950, and 1100 characters long
- **THEN** the first gets a mild warning (above 600), the second a strong warning (above 900), the third an error (above 1024), and only the third run exits 1

#### Scenario: Warnings only
- **WHEN** run on a skill whose description exceeds 900 characters but has no error
- **THEN** the warning is printed, stderr counts the warnings, and the exit code is 0

#### Scenario: Missing skill file
- **WHEN** run with `--skill` pointing at a directory that contains no `SKILL.md`
- **THEN** stderr says the file does not exist and the exit code is 1

#### Scenario: Bad arguments
- **WHEN** run without `--skill`, or with an existing path that is neither a directory nor a file named `SKILL.md`
- **THEN** stderr names the usage and the exit code is 2

#### Scenario: Repeated run
- **WHEN** run twice on the same unchanged skill
- **THEN** both runs print identical findings and exit codes and no file is modified

#### Scenario: Without PyYAML
- **WHEN** run with `python3` on a machine lacking uv and PyYAML
- **THEN** the simple key-value frontmatter is still parsed and the findings match those of the uv run
