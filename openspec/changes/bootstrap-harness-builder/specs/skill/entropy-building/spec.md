# Spec Delta

## Purpose

Governs what an agent that loaded `entropy-building` observably does when it builds, grades, or repairs the entropy layer of a target project's harness (methodology §5 and §6.2): the correction-report rule, the single source of truth with its forward and reverse sync triggers, the project's own harness self-check wired into its task runner and CI, periodic reclamation that also thins, and the rules for session logs and canary tasks. Ships unchanged to Claude Code, Codex, and Antigravity. Non-goals: the product code's lint, tests, or CI (hard-boundary layer); finishing or linting the project skills the sync or reclamation routine may become (the skill that writes project skills; this skill only hands over the starting shape); the authority policy's pending-decisions format (authority layer); creating issue-tracker entities or labels on the remote (platform lifecycle layer); a harness that rewrites its own knowledge from failure history; running canary tasks.

## ADDED Requirements

### Requirement: Triggering
The skill's description SHALL load it when a user asks to keep a harness in sync with the code it describes, to detect stale harness content mechanically, to decide where agents record harness drift, or to set up periodic harness cleanup, and SHALL NOT load it for product-code checks, one-off fixes to a document, synchronisation between product artifacts, or branch hygiene. No prompt names the skill.

#### Scenario: Entrypoint drifts from the task runner
- **WHEN** the user says "AGENTS.md keeps describing commands that no longer exist in the justfile; set something up so the two stay in sync"
- **THEN** the skill loads

#### Scenario: Mechanical check for stale references
- **WHEN** the user says "add a CI step that fails when a path mentioned in AGENTS.md or the knowledge files no longer exists"
- **THEN** the skill loads

#### Scenario: Recording drift found during a task
- **WHEN** the user says "when an agent notices the docs contradict the code mid-task, where should that go so the next agent does not hit it again?"
- **THEN** the skill loads

#### Scenario: Long-lived harness cleanup
- **WHEN** the user says "this harness has grown for two years; give the team a routine that finds dead rules and over-thick constraints"
- **THEN** the skill loads

#### Scenario: Product lint in CI
- **WHEN** the user says "add ruff and mypy to CI so bad Python stops landing"
- **THEN** the skill does not load

#### Scenario: One-off document fix
- **WHEN** the user says "the link in AGENTS.md to the architecture doc is broken, fix it"
- **THEN** the skill does not load

#### Scenario: Product artifact synchronisation
- **WHEN** the user says "write a skill that keeps the ORM models in sync with the database migrations"
- **THEN** the skill does not load

#### Scenario: Branch hygiene
- **WHEN** the user says "clean up the stale feature branches that have already been merged"
- **THEN** the skill does not load

### Requirement: Behavior: Copies are inventoried and reduced to one source of truth
Before proposing any mechanism the agent SHALL inventory every fact the harness states in more than one place, SHALL recommend replacing each copy with a reference to one source of truth, SHALL record a ruling rule naming which place wins when two disagree, and SHALL list every copy that cannot be replaced as a mirror pair for the mechanical check. The inventory is reported before anything is written.

#### Scenario: Command described in two documents
- **WHEN** the entrypoint and a knowledge file both spell out the test command with its flags
- **THEN** the agent reports the duplicate, recommends that both name only the task-runner recipe while the flags live in the recipe, and writes nothing until the user agrees

#### Scenario: Copy that cannot become a reference
- **WHEN** the project keeps `README.md` and `README.en.md` as translations of each other
- **THEN** the pair appears in the inventory as a mirror pair with the sections that must match, and the user is asked to confirm the pair

#### Scenario: Ruling rule
- **WHEN** the inventory is presented
- **THEN** it ends with a recommended ruling rule (the code or the task runner over the document that describes it) and the user's confirmation is awaited before it lands in the entrypoint

### Requirement: Behavior: The correction-report rule lands in the entrypoint
From the medium grade up the agent SHALL write into the target's entrypoint a rule that an agent finding harness content contradicting the code MUST act in one of three ways, chosen by size of deviation and authority: fix it in the same change and say so in the commit; add it to the pending decisions list when intent or authorisation is unclear; or open a tracked issue with one fixed label. A conversation-only report SHALL be named as not acceptable. The light grade gets only the sync sentence.

#### Scenario: Rule as written
- **WHEN** the entrypoint section is deposited at the medium or thick grade
- **THEN** it names the three dispositions, the criterion that selects each, and that a conversation-only report does not count

#### Scenario: Issue tracker present
- **WHEN** the project has an issue tracker
- **THEN** the agent proposes one label name for drift issues that uses a namespace the platform lifecycle layer already defines (for example a `type:` label) or flags the new namespace as a pending decision for that layer, asks the user to confirm or rename it, and records the label in the rule and as an item the platform lifecycle layer or the user creates on the remote

#### Scenario: No issue tracker
- **WHEN** the project has no issue tracker and the user does not want one
- **THEN** the third disposition points at a tracked file in the repository that the reclamation routine reads, and the agent says why

### Requirement: Behavior: The sync mechanism matches the grade and the user's choice
At the light grade the agent SHALL deposit one sentence in the entrypoint that reminds agents to fix or report harness drift, and nothing more. At the medium grade the agent SHALL offer a Keep In Sync table or a sync project skill with one recommendation and its reason, and SHALL let the user choose; the chosen mechanism SHALL own each concern alone. At the thick grade the agent SHALL add the second check tier and periodic reclamation. An unconfirmed grade SHALL be asked, not assumed.

#### Scenario: Medium grade choice
- **WHEN** the entropy layer is graded medium and the harness has four concerns with linear update steps
- **THEN** the agent recommends the Keep In Sync table, names the sync skill as the alternative with when it fits (frequent, branchy, or many-artifact concerns), and waits for the choice

#### Scenario: Sync skill chosen
- **WHEN** the user chooses the sync skill
- **THEN** the agent fixes the concern, its forward trigger, its reverse checks, and its completion criterion, hands the writing of the skill to the skill that writes project skills by describing that need together with the raw starting shape it ships (concern, triggers, checks, completion criterion, checklist), does not lint or finish the skill itself, and removes the concern from any table so one mechanism owns it

#### Scenario: Grade not confirmed
- **WHEN** the approved plan grades the entropy layer but the user has never confirmed that grade in conversation
- **THEN** the agent states the planned grade with its recommendation and asks before depositing any mechanism

### Requirement: Behavior: The mechanism fills the reserved keep-in-sync section
The sentence or table SHALL fill the keep-in-sync section the knowledge and routing layer reserved in the entrypoint; the agent SHALL create no second sync section. Only a brownfield mechanism that already carries concerns (a populated sync table or a sync skill) counts as an existing mechanism, and for those concerns the agent SHALL install no second mechanism.

#### Scenario: Reserved section present
- **WHEN** the entrypoint already has an empty keep-in-sync section left by the knowledge and routing layer
- **THEN** the light-grade sentence or the medium-grade table lands inside that section and the entrypoint ends with exactly one sync section

#### Scenario: Reserved section absent
- **WHEN** the entrypoint has no keep-in-sync section at all
- **THEN** the agent adds one section at the end of the entrypoint, within the entrypoint's line budget, and reports that the knowledge and routing layer had not reserved it

#### Scenario: Existing mechanism found
- **WHEN** the target already carries a populated sync table or a sync skill that owns a concern
- **THEN** the agent installs no second mechanism for that concern, does not reopen the table-or-skill choice for it, and reports the existing one, with any contradiction between it and the inventory, for the user to decide

### Requirement: Behavior: Forward and reverse triggers with a tie-break rule
Every sync entry the agent deposits SHALL state both directions: the forward trigger (which change to the code or tooling obliges which harness update) and the reverse check (which facts to verify before editing that harness document). A standing entrypoint rule SHALL require inspecting every reverse check of a touched document and fixing or reporting every mismatch, not only the one that prompted the edit. Every entry SHALL name a tie-break rule: which side is corrected when the two disagree.

#### Scenario: Table row
- **WHEN** a Keep In Sync row covers the task-runner recipes
- **THEN** the row names the change ("a recipe is added, renamed, or removed"), the document to update, and what to run or read before editing that document, in one row

#### Scenario: Entrypoint command section edited
- **WHEN** an agent later edits the command section of the entrypoint
- **THEN** the standing rule obliges it to confirm each named recipe exists and behaves as described before the edit is finished

#### Scenario: Two sides disagree
- **WHEN** a knowledge file describes a directory layout the repository no longer has
- **THEN** the tie-break rule makes the repository the truth and the document the thing to correct, unless the user has recorded the opposite ruling for that pair

### Requirement: Behavior: The harness self-check is deposited as the project's own management code
From the medium grade up the agent SHALL deposit a project-owned harness self-check where the project's management scripts live, configured from observed facts, wired into a task-runner recipe and the CI checks, with tier 1 always on and tier 2 only at the thick grade or on request. The Python it ships is a reference implementation: the agent SHALL ask whether the project keeps it or has it rewritten in its agreed management language, and SHALL say the project owns the copy.

#### Scenario: Configuration from observation
- **WHEN** the repository has `AGENTS.md`, a `justfile`, `.agents/knowledge/`, and the mirror pair from the inventory
- **THEN** the deposited script's settings name those paths and that pair without asking, and the agent asks only about what the repository does not show

#### Scenario: Script lands
- **WHEN** the script lands
- **THEN** a task-runner recipe runs it, the CI checks run that recipe, and the agent runs the recipe once and reports its output before declaring the step done

#### Scenario: Project scripts in another language
- **WHEN** the project's agreed management language is TypeScript on Deno
- **THEN** the agent offers a port with the same rules and messages, recommends it, writes the recipe in whichever language the user confirms, and introduces uv as a project dependency only after asking

#### Scenario: Script in a skill directory
- **WHEN** a project already calls a script inside a skill directory from its CI
- **THEN** the agent reports it as a defect and proposes a project-owned copy, accepting the duplication as deliberate

### Requirement: Behavior: Periodic reclamation thins as well as updates
At the thick grade the agent SHALL install a reclamation routine, as a dated section or a project skill that lists what to hunt (stale or dead content, contradicted or duplicated rules, unreachable content, triggers that cannot fire, over-thick constraints), the thinning signal "what this constraint blocks no longer occurs", a cadence anchored to a team rhythm, and a `Last run:` absolute date. Each finding gets a disposition; deletion needs evidence or approval.

#### Scenario: Section deposited
- **WHEN** the reclamation routine lands as a section
- **THEN** it carries the checklist with thinning signals, the anchor event, the cadence, and `Last run:` with an absolute date or "never"

#### Scenario: Skill form chosen
- **WHEN** the user wants the reclamation routine as a project skill
- **THEN** the agent hands the skill that writes project skills the described need together with the raw starting shape it ships (what to hunt, thinning signals, cadence, `Last run:`, dispositions), and does not lint or finish the skill itself

#### Scenario: Long-lived project graded medium
- **WHEN** the project is long-lived but the confirmed entropy grade is medium
- **THEN** the agent recommends raising the entropy grade to thick, asks, and installs reclamation only after the user confirms the higher grade

#### Scenario: Thinning candidate
- **WHEN** a run finds a lint rule written for a bug fixed two years ago that has blocked nothing since
- **THEN** the finding is reported with the disposition "thin" and the evidence, and the rule is removed only after the user approves

#### Scenario: Cleanup prompted by an agent failure
- **WHEN** repeated agent failures on one instruction prompt a cleanup
- **THEN** the routine reports the failure pattern and a recommendation and makes no automatic edit to knowledge, because that would need controls this harness does not have

### Requirement: Behavior: Session logs are secrets and canaries are manual
The agent SHALL treat framework session logs as secrets: they stay out of the repository and shared drives, analysis happens locally or after redaction, and any centralised collection is presented to the user as an exposure-surface decision, never configured silently. Canary tasks SHALL be described as a manual, on-demand practice for large projects that opt in; the agent SHALL never wire them into CI and SHALL NOT propose them at the light grade.

#### Scenario: Observation requested
- **WHEN** the user asks to track which tool calls fail most often
- **THEN** the agent proposes a local analysis of the session logs, records the secret-handling rule where the harness keeps observation guidance, and asks before any log leaves the machine

#### Scenario: Canaries asked for CI
- **WHEN** the user asks to run representative agent tasks after every harness change in CI
- **THEN** the agent declines the CI wiring, explains the credential and cost reasons, and offers a manual canary list the team triggers after major harness refactors

### Requirement: Behavior: Delivery is agreed first and verified last
The agent SHALL write nothing until the user has approved the list of artifacts (entrypoint sections, knowledge section or skill request, script, recipe, CI job), SHALL present one recommendation per decision and wait, SHALL continue past a blocked decision by adding it to the pending decisions list, and before handing back SHALL confirm the rule is reachable from the entrypoint, the recipe runs, and the CI job references it, reporting any failure instead of fixing it silently.

#### Scenario: User declines the script
- **WHEN** the user declines the self-check at the medium grade
- **THEN** the agent records the refusal and its risk as a pending decision, deposits the rest, and does not reintroduce the script

#### Scenario: Blocked label decision
- **WHEN** the user has not answered which drift label to use when the rest of the layer is ready
- **THEN** the agent lands everything that does not depend on the label, adds the label to the pending decisions list with options and a recommendation, and does not invent a name

#### Scenario: Verification fails
- **WHEN** the deposited check fails in the target on first run
- **THEN** the agent reports each finding as the script printed it and asks whether to fix the harness content or adjust the configuration, rather than editing the check to pass

### Requirement: Outcomes
Given an approved plan that grades the entropy layer, the agent SHALL leave the target with the mechanisms that grade requires, each reachable from the entrypoint and exercised once, and SHALL leave a pending decisions list for everything the user did not settle.

#### Scenario: Medium grade with a table
- **WHEN** the task is "build the entropy layer at medium grade for this repository (justfile, AGENTS.md, .agents/knowledge, README.md and README.en.md)", the user confirms the grade, chooses the table, and keeps the Python reference implementation
- **THEN** the entrypoint gains the correction-report rule with three dispositions, a ruling rule, a Keep In Sync table whose rows each name the change, the document, and the reverse check, filling the one keep-in-sync section, and the standing reverse rule; `scripts/check_harness.py` exists with the four paths and the README pair configured, a recipe runs it, CI runs the recipe, and the agent's report shows the run's output and the pending decisions

#### Scenario: Thick grade for a long-lived project
- **WHEN** the task is "entropy layer at thick grade; the team ships monthly" and the user confirms the grade
- **THEN** in addition to the medium result the check enables the second tier (skill frontmatter, entrypoint budget), a reclamation section or skill carries the checklist with thinning signals, a monthly cadence anchored to the release, and `Last run:` with a date, and the report says canaries are a manual option and session logs stay local

#### Scenario: Light grade
- **WHEN** the task is "entropy layer at light grade for a three-month prototype" and the user confirms the grade
- **THEN** the entrypoint's keep-in-sync section gains one sentence that reminds agents to fix or report harness drift and nothing else; no three-disposition rule, script, recipe, CI job, or reclamation routine is created; and the report says what the project would add if it outlives the prototype

### Requirement: Script: check_harness.py
The delivered `check_harness.py` SHALL run with no prompt, SHALL offer `--help` with a usage example, SHALL print its findings as JSON on stdout (each with file, rule, problem, and fix) and diagnostics on stderr, SHALL exit 0 with no finding, 1 with findings, and 2 on bad arguments or an unusable configuration, SHALL be read-only and idempotent, SHALL run under uv and under plain `python3` with the standard library only, and SHALL call no script inside a skill directory.

#### Scenario: Tier 1 finding
- **WHEN** the entrypoint names a recipe the task runner lacks and a knowledge file is not reachable from the entrypoint
- **THEN** stdout holds two findings naming each file, the missing recipe or the unreachable file, and the fix, and the exit code is 1

#### Scenario: Mirror pair out of step
- **WHEN** a configured mirror pair differs in a section that must match
- **THEN** the finding names both files, the section, and that one must be edited to match the other, and the exit code is 1

#### Scenario: Configured path missing
- **WHEN** a path in the settings block does not exist
- **THEN** the script reports the setting and the path and exits 2 rather than skipping the check

#### Scenario: Second tier disabled
- **WHEN** the settings block leaves the second tier off
- **THEN** skill frontmatter and the entrypoint budget are not checked, stderr says the tier is off, stdout holds only the tier 1 findings list, and tier 1 still runs

#### Scenario: Second tier enabled
- **WHEN** the second tier is on and the entrypoint exceeds its configured line budget
- **THEN** a finding names the entrypoint, the line count, the budget, and the fix, and the exit code is 1

#### Scenario: Clean repository
- **WHEN** every check passes
- **THEN** stdout holds an empty findings list, the run leaves the repository unchanged, and the exit code is 0 on a second run as well

#### Scenario: Bad argument
- **WHEN** the script is run with an unknown flag
- **THEN** it prints usage on stderr and exits 2
