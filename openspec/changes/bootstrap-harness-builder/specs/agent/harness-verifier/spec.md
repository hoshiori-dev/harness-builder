# Spec Delta

## Purpose
Governs what the `harness-verifier` agent observably does when an entry skill dispatches it to read back a harness just built or changed in a target project: a clean-context, read-only reader that reports what an agent would load and owe from each file and where the harness contradicts itself, shipped to Claude Code only because Codex plugins carry no agents component and Antigravity loads plugin agents only from the plugin root (`.agents/knowledge/compatibility-watch.md`, W9 and W2), so in those clients the dispatching skill falls back to a fresh pass without a clean context and records the degradation. It never writes or edits a file, never reads this plugin's skill files or compares the harness against them, never overrides the thickness or budget decisions the user made, and does not replace whatever deterministic harness check the target runs (for example a `check_harness.py` at the medium or thick entropy grade).

## ADDED Requirements

### Requirement: Dispatch input
The agent SHALL run only when dispatched with a list of target-project files and optional intent lines. Its input scope SHALL be the listed files, the files they point to, the entrypoint and its import file (`CLAUDE.md`), the task-runner file the target's files name, and a names-only directory listing of the target's knowledge directory for orphan detection; the agent SHALL open nothing else and SHALL read nothing of the conversation that produced the files.

#### Scenario: Entry skill dispatches after a build
- **WHEN** the harness creation workflow reaches its read-back step and hands the agent the paths of every file it created, each followed by an intent line such as "knowledge file for the release process"
- **THEN** the agent reads the listed files in a context that contains none of the build conversation and returns one report covering every listed file

#### Scenario: Entry skill dispatches after a repair
- **WHEN** the harness improvement workflow repairs three files and hands the agent those three paths with no intent lines
- **THEN** the agent derives each file's purpose from its own content and the entrypoint route that reaches it, reports per-file facts for the three files, and raises gaps only on them, the entrypoint and its import file, the task-runner file they name, and orphans in the knowledge directory

#### Scenario: Listed file does not exist
- **WHEN** one listed path does not exist in the target project
- **THEN** the agent reports `<path>: listed for verification but not found. Fix: create it or remove it from the list` and continues with the remaining files

### Requirement: Refusals
The agent SHALL refuse two kinds of request by stating the refusal as the first line of its report and then continuing with the read-back: any request to write, fix, or edit a file, and any request to open or compare against this plugin's skill files or templates.

#### Scenario: Dispatched with a fix request
- **WHEN** the dispatching text says "verify these files and fix whatever you find"
- **THEN** the agent's first report line states that it reads only and does not edit, every finding carries its `Fix:` action, and no file in the target changes

#### Scenario: Dispatched with a plugin comparison request
- **WHEN** the dispatching text asks the agent to check the harness against the plugin's templates or skill files
- **THEN** the agent states in its first report line that it does not read the plugin's files, opens none of them, and judges the harness only against the target's own files and the intent lines

### Requirement: Behavior: Per-file report
For every listed agent-facing document (entrypoint, import file, knowledge files, project skill files) the agent SHALL report four facts: load condition, obligations placed on an agent, named source of truth, and whether every pointer resolves; the entrypoint and import file get load condition `always`. A listed machine-consumed file (task-runner, CI, pre-commit, client settings) SHALL receive only the pointer, placeholder, and budget checks.

#### Scenario: Knowledge file with a stated condition
- **WHEN** a knowledge file opens with "Read this when preparing a release" and the entrypoint routes to it under the same condition
- **THEN** the report quotes that condition as the load condition, lists the file's obligations, and names the file as the source of truth for the release steps

#### Scenario: Task-runner or CI configuration file listed
- **WHEN** the listed files include a `justfile`, `.pre-commit-config.yaml`, and `.github/workflows/checks.yml`
- **THEN** the report records for each only whether its pointers resolve and whether it carries an unfilled placeholder, and raises no `no load condition` gap for any of them

#### Scenario: Import file listed
- **WHEN** `CLAUDE.md` holding only `@AGENTS.md` is among the listed files
- **THEN** the report gives it load condition `always`, obligation "imports the entrypoint", and raises no gap for a missing "Read this when" line

### Requirement: Behavior: Load condition and source of truth
A knowledge or project skill file whose load condition neither its opening line nor any entrypoint route or skill step states SHALL be reported as a gap. A fact whose file names no source SHALL be reported as `source: none named`, not as a gap, unless another file in scope states the same fact with a different value, in which case the agent SHALL raise one gap that names both files and both values and asks the user which governs.

#### Scenario: Knowledge file without a condition
- **WHEN** a knowledge file states rules but neither its first line nor any entrypoint route says when to read it
- **THEN** the report contains `<file>: no load condition. Fix: open the file with "Read this when …" and route to it from the entrypoint under that condition`

#### Scenario: Fact with no named source
- **WHEN** a freshly written knowledge file states "releases are cut from `main` on Thursdays" and no file names where that fact is owned, and no other file states a release day
- **THEN** the report records `source: none named` for that fact and raises no gap

#### Scenario: Two files state the same fact differently
- **WHEN** the entrypoint says the test command is `just test` and a knowledge file says it is `npm test`, and no file says which one governs
- **THEN** the report contains one gap naming both files and both values, whose `Fix:` asks the user which file governs (optionally with a recommendation and its reason) and states that the other file will reference the winner once decided

### Requirement: Behavior: Pointer resolution
The agent SHALL check that every file path, relative link, `@` import, and task-runner recipe (a `just` recipe, `make` target, npm or pnpm script, or a recipe of whatever runner the target's files name) named in a listed file resolves in the target project, and SHALL report each that does not as a gap naming the pointer and the file that carries it.

#### Scenario: Recipe named but absent
- **WHEN** the entrypoint tells agents to run `just check` and the target's `justfile` defines no `check` recipe
- **THEN** the report contains ``AGENTS.md: names recipe `just check` that the justfile does not define. Fix: add the recipe or correct the name``

#### Scenario: Pointer to a missing file
- **WHEN** a knowledge file links to `.agents/knowledge/deploy.md` and no such file exists
- **THEN** the report contains a gap naming the linking file and the missing path, with a `Fix:` that creates the file or removes the link

#### Scenario: Recipe of a runner whose file is absent
- **WHEN** the entrypoint names `make lint` and `make test` and the target has no `Makefile`
- **THEN** the report contains one gap stating that the task runner the entrypoint relies on is absent, with a `Fix:` that adds the runner file the project chose or rewrites the commands

#### Scenario: Target uses a runner other than just
- **WHEN** the entrypoint names `npm run check` and `package.json` defines a `check` script
- **THEN** the pointer is reported as resolved and no gap asks for a `justfile`

### Requirement: Behavior: Entrypoint budget
The agent SHALL count the lines of the entrypoint (`AGENTS.md`, or the file an intent line names as the entrypoint) against a ceiling and target set by an intent line (`entrypoint budget: <ceiling>`) or by the target's own harness files, defaulting to 120 and 100 when neither states one; over the ceiling SHALL be a gap, between target and ceiling a note naming the count and the target. An import file holding only `@AGENTS.md` SHALL not be counted; one holding more SHALL be a gap.

#### Scenario: Entrypoint within target
- **WHEN** `AGENTS.md` is 92 lines and no budget is stated
- **THEN** the report records the count and raises no gap or note about the budget

#### Scenario: Entrypoint over the default ceiling
- **WHEN** `AGENTS.md` is 134 lines and no budget is stated
- **THEN** the report contains `AGENTS.md: 134 lines, ceiling 120. Fix: move the sections that apply only to some tasks into knowledge files and route to them`

#### Scenario: Single-file lightweight harness
- **WHEN** an intent line says "single-file harness, entrypoint budget: 200" and `AGENTS.md` is 160 lines
- **THEN** the report records the count against the 200-line ceiling and raises no budget gap

#### Scenario: Import file carries its own rules
- **WHEN** `CLAUDE.md` contains `@AGENTS.md` followed by twelve lines of rules
- **THEN** the report contains a gap naming `CLAUDE.md` as a second source of always-on rules, with a `Fix:` that moves the lines into `AGENTS.md` and leaves only the import

### Requirement: Behavior: Knowledge reachability
The agent SHALL confirm that every knowledge file in the input, and every file named in the knowledge directory listing, is reachable from the entrypoint by following pointers across one or more hops or is named by a project skill, and SHALL report each unreachable file as a gap.

#### Scenario: Reachable in two hops
- **WHEN** the entrypoint routes to `github-workflow.md`, which links to `github/checks.md`
- **THEN** `github/checks.md` is reported as reachable with its route, and no gap is raised

#### Scenario: Orphan knowledge file
- **WHEN** `.agents/knowledge/legacy-build.md` exists and no entrypoint route, knowledge file, or project skill names it
- **THEN** the report contains `.agents/knowledge/legacy-build.md: unreachable from the entrypoint. Fix: route to it from AGENTS.md under its load condition, or delete it`

#### Scenario: Reachable only through a project skill
- **WHEN** a knowledge file is named only by a project skill's step and by no entrypoint route
- **THEN** the report records the skill as the route and raises no gap

### Requirement: Behavior: Unfilled placeholders
The agent SHALL report as a gap every unfilled template token left in a listed file, where a token is `{{IDENT}}` not preceded by `$`; expressions of the form `${{ … }}` are not tokens under this check.

#### Scenario: Template placeholder left behind
- **WHEN** a knowledge file contains `{{PROJECT_NAME}}`
- **THEN** the report contains `<file>: unfilled placeholder {{PROJECT_NAME}}. Fix: replace it with the project's value`

#### Scenario: Workflow expression
- **WHEN** a listed `.github/workflows/checks.yml` contains `${{ github.sha }}` and no other double brace
- **THEN** no placeholder gap is raised for that file

### Requirement: Behavior: Undefined vocabulary
The agent SHALL report as a gap every term a listed agent-facing document uses as the name of a project artefact, list, mode, or process (for example "the pending decisions list", "spec-anchored", "soft read-only") as though the reader already knew it, when no target-project file defines it. Commands, paths, tool names, and proper nouns (`just test`, `uv`, GitHub Actions, Apache-2.0) are not terms under this check.

#### Scenario: Concept used without a definition
- **WHEN** the entrypoint tells agents to "add blocked items to the pending decisions list" and no target file says what that list is, where it lives, or what each item states
- **THEN** the report contains a gap naming the term and the file, with a `Fix:` that defines it in the authority knowledge file or inline

#### Scenario: Concept defined in the target
- **WHEN** the entrypoint says "this project is spec-anchored" and the target's spec workflow file defines what spec-anchored means
- **THEN** no gap is raised for the term

#### Scenario: Tool and command names
- **WHEN** a knowledge file names `ruff`, `just lint`, and Conventional Commits without defining any of them
- **THEN** no vocabulary gap is raised for those names

### Requirement: Behavior: Keep In Sync covers both directions
When a listed file carries a Keep In Sync section or table, the agent SHALL check that every row states both directions, which code or configuration change triggers which harness update and which harness change triggers which verification of the implementation, and SHALL report a row that states only one direction as a gap. When no such section exists the agent SHALL add a note, not a gap, unless an intent line says one is expected.

#### Scenario: Row with a forward trigger only
- **WHEN** a row says "when the justfile changes, update the Validation section" and nothing says what to verify when the Validation section changes
- **THEN** the report contains a gap naming the row, with a `Fix:` that adds the reverse check

#### Scenario: Both directions present
- **WHEN** every row names the code change that updates the harness and the harness change that must be verified against the code
- **THEN** no gap is raised for the section

#### Scenario: Section absent where the intent expects one
- **WHEN** an intent line says "entropy layer: medium, Keep In Sync table" and the entrypoint has no such section
- **THEN** the report contains a gap naming the entrypoint, with a `Fix:` that adds the table

### Requirement: Behavior: Report format
The report SHALL consist, in this order, of the optional refusal line, the per-file facts, any notes prefixed `note:`, one line per gap in the exact form `<file>: <gap>. Fix: <action>`, and a final line that is `PASS` when there are no gap lines or `FAIL (<n>)` where `<n>` equals the number of gap lines. Each distinct defect SHALL yield exactly one gap line even when several checks detect it.

#### Scenario: Gaps found
- **WHEN** the read-back finds three gaps across two files
- **THEN** the report contains exactly three gap lines in the stated form and its last line is `FAIL (3)`

#### Scenario: No gaps found
- **WHEN** the read-back finds no gap
- **THEN** the report's last line is `PASS`, and any budget note above it does not change that verdict

#### Scenario: Defect detected by two checks
- **WHEN** `CLAUDE.md` holds a full copy of the entrypoint, which both the budget check and the source-of-truth check detect
- **THEN** the report carries one gap line for it and the count in the verdict rises by one

#### Scenario: Gap without a known fix
- **WHEN** the agent finds a contradiction it cannot resolve from the files, such as two sources of truth with no rule saying which governs
- **THEN** the gap line's `Fix:` names the decision the user must take rather than choosing for them

### Requirement: Outcomes
Dispatched on a built harness, the agent SHALL return a report whose per-file facts match the files' content and whose verdict a reader can confirm by opening the named files and nothing else.

#### Scenario: Freshly built harness
- **WHEN** the agent is dispatched on a 96-line `AGENTS.md`, a `CLAUDE.md` holding only `@AGENTS.md`, four knowledge files each opening with "Read this when …" and each routed from the entrypoint, a `justfile` defining every recipe the files name, a workflow file using `${{ github.sha }}`, and a Keep In Sync table whose rows state both directions
- **THEN** the report lists each agent-facing document with its load condition, obligations, source of truth (or `source: none named`), and resolved pointers, records only pointer and placeholder results for the `justfile` and workflow, contains no gap line, and ends with `PASS`

#### Scenario: Brownfield harness with four defects
- **WHEN** the agent is dispatched with no intent lines on a 131-line `AGENTS.md` that names `just test` with no `test` recipe, a knowledge file opening with "Read this when …" that nothing routes to, and a file still containing `{{OWNER}}`, where every other pointer resolves, every term is defined, and no two files state one fact differently
- **THEN** the report contains exactly four gap lines, one for the budget, one for the recipe, one for the orphan, one for the placeholder, each naming its file and a `Fix:` action, and ends with `FAIL (4)`

#### Scenario: Intent line contradicted by the file
- **WHEN** an intent line says "`CLAUDE.md` imports `AGENTS.md`" and `CLAUDE.md` holds a full copy of the entrypoint's text instead, and no other defect is present
- **THEN** the report contains one gap naming `CLAUDE.md` as a duplicate source of truth with a `Fix:` that replaces the copy with the import, and ends with `FAIL (1)`
