# Spec Delta

## Purpose

Governs what an agent that loaded `knowledge-routing-building` observably does when it builds or reworks the knowledge and routing layer of a target project's harness: the entrypoint, the knowledge files it routes to, where knowledge and project skills live, the decision of whether a procedure deserves a project skill, and the scripts that replace long inline commands. The skill ships to Claude Code, Codex, and Antigravity. Non-goals: writing the project skills themselves (handed to the skill that owns project skills), the content of the entrypoint's sync section (entropy layer), the clean-context read-back (entry skills), choosing the project's environment, checks, authority rules, or spec carrier (other layers), and writing README, CONTRIBUTING, or SECURITY, which it only comments on when they contradict the harness.

## ADDED Requirements

### Requirement: Triggering
The skill's description SHALL cause it to load for requests to create, split, trim, or reorganise a project's agent entrypoint, knowledge files, or routing between them, and for the question of whether a procedure belongs in the entrypoint, a knowledge file, or a project skill. It SHALL NOT load for writing a project skill's own content, for human-facing documentation, or for checks, permissions, and CI that other layers own.

#### Scenario: Entrypoint rewrite request
- **WHEN** the user asks "our AGENTS.md is 300 lines and agents ignore half of it, help me restructure it"
- **THEN** the skill loads

#### Scenario: Knowledge base layout request
- **WHEN** the user asks "set up a knowledge folder for agents and decide what goes in the root file versus separate files"
- **THEN** the skill loads

#### Scenario: Carrier question
- **WHEN** the user asks "should the release procedure be a skill, a doc, or just a line in the root instructions?"
- **THEN** the skill loads

#### Scenario: Claude-specific entry request
- **WHEN** the user asks "add a CLAUDE.md so Claude Code picks up the same rules as the other agents"
- **THEN** the skill loads

#### Scenario: Project skill content request
- **WHEN** the user asks "write the skill that walks an agent through our database migration steps"
- **THEN** the skill does not load; the skill that owns project skills does

#### Scenario: Human documentation request
- **WHEN** the user asks "rewrite the README so new contributors understand the repository layout"
- **THEN** the skill does not load

#### Scenario: Pre-commit routing request
- **WHEN** the user asks "route lint failures to the right fix by adding a pre-commit hook with a clear message"
- **THEN** the skill does not load; the hard-boundary layer's skill does

### Requirement: Behavior: Four-question split check per file
Before proposing any file beyond the entrypoint, the agent SHALL answer four questions for it and show the answers to the user: how and when an agent realises it needs the file, what it gains by reading it, how much unrelated content it ingests, and whether the jump cost is below inlining. A file that fails the check SHALL be inlined or dropped, never created for tidiness.

#### Scenario: Six lines every task needs
- **WHEN** a candidate knowledge file would hold six lines that every task needs
- **THEN** the agent proposes inlining those lines in the entrypoint's always-applicable block and creates no file

#### Scenario: Release-only deployment facts
- **WHEN** a candidate file holds deployment facts needed only by release tasks
- **THEN** the agent records the four answers, proposes the file, and proposes a routing row that names the release situation as its load condition

#### Scenario: Existing harness has files without a reachable condition
- **WHEN** a brownfield project has knowledge files no entrypoint line points to
- **THEN** the agent reports each as invisible and asks the user whether to route it, merge it, or delete it, rather than silently routing all of them

### Requirement: Behavior: Entrypoint shape and budget
The entrypoint SHALL be ordered: always-applicable block, when-to-read routing table by situation, validation table of recipe names, then a position reserved for the entropy layer's sync content, which this agent SHALL NOT write. A rule is always-applicable only when breaking it harms regardless of task type. With a knowledge folder the entrypoint SHALL aim at about 100 lines and SHALL NOT exceed 120; a single-file harness SHALL aim at about 200. No always-applicable rule SHALL leave for budget.

#### Scenario: Rule classified
- **WHEN** the user proposes "run the formatter before committing" and "read the schema notes before touching the ORM" for the entrypoint
- **THEN** the agent places the first in the always-applicable block and the second as a routing row, and explains the task-type test

#### Scenario: Budget exceeded by routable content
- **WHEN** the drafted entrypoint reaches 135 lines and twenty of them describe a one-situation procedure
- **THEN** the agent proposes a knowledge file for the procedure with its four answers and routing row, asks the user, and the entrypoint lands at or under 120 lines once the user accepts the file or names which content to drop; no file is created before that answer

#### Scenario: Budget exceeded by always-applicable content
- **WHEN** the always-applicable block alone would push the entrypoint over 120 lines
- **THEN** the agent keeps every always-applicable rule, tells the user the budget cannot be met without dropping a rule, and asks which rules the user considers optional instead of removing any

#### Scenario: Sync section position
- **WHEN** the agent drafts the entrypoint before the entropy layer has run
- **THEN** the draft ends with an empty position marked for the sync content and the agent writes no sync rule, sync table, or correction-report rule itself, naming the entropy layer as its owner in the report

### Requirement: Behavior: Single entrypoint with client imports
The agent SHALL recommend `AGENTS.md` as the only rule-bearing entrypoint and a `CLAUDE.md` whose whole content is `@AGENTS.md`; it SHALL NOT copy rules into both. It SHALL recommend no subdirectory entry files, and when the user wants one, it SHALL carry no rule that must hold and SHALL NOT contradict the root.

#### Scenario: Claude Code in use
- **WHEN** the repository shows Claude Code settings and the user confirms a mixed set of agents
- **THEN** the agent writes `CLAUDE.md` containing only `@AGENTS.md` and places every rule in `AGENTS.md`

#### Scenario: Existing CLAUDE.md with its own rules
- **WHEN** a brownfield project has a `CLAUDE.md` holding rules absent from `AGENTS.md`
- **THEN** the agent lists each rule, proposes moving it into `AGENTS.md` and reducing `CLAUDE.md` to the import, and waits for the user's decision

#### Scenario: Subdirectory entry requested
- **WHEN** the user insists on a `packages/api/AGENTS.md`
- **THEN** the agent writes it with local orientation only, states in it that the root file governs, and puts no safety or commit rule in it

### Requirement: Behavior: Recommended layout for knowledge and project skills
The agent SHALL recommend, as a recommendation with its reason, `.agents/knowledge/` for knowledge files and `.agents/skills/` for project skills, with `.claude/skills` a symbolic link to `.agents/skills` when Claude Code shares the repository with other clients. It SHALL name the alternatives: a real `.claude/skills` directory when Claude Code is the only client, and a single-file harness for a lightweight project. An existing folder observable in the repository SHALL be reused without asking.

#### Scenario: Mixed clients
- **WHEN** the user confirms Claude Code and Codex both work in the repository and has no knowledge folder yet
- **THEN** the agent recommends `.agents/knowledge/` and `.agents/skills/` with `.claude/skills` linked to the latter, states why one real directory serves both clients, lists the two alternatives in a sentence each, and creates nothing until the user chooses

#### Scenario: Claude Code only
- **WHEN** the user confirms Claude Code is the only client
- **THEN** the agent presents the real `.claude/skills` directory as the fitting alternative, keeps `.agents/knowledge/` for knowledge files, and records the choice with its reason in the plan

#### Scenario: Existing folder reuse
- **WHEN** the repository already has `.agents/knowledge/` with three files
- **THEN** the agent reuses that folder without asking where knowledge should live and routes new files there

#### Scenario: Lightweight project
- **WHEN** the user prefers a single-file harness for a small project
- **THEN** the agent builds `AGENTS.md` alone under the about-200-line budget, creates no knowledge or skills folder, and does not reintroduce the folder later

### Requirement: Behavior: Knowledge files open with their load condition
Every knowledge file the agent writes SHALL begin with a line starting "Read this when" that names the situation, SHALL cover one concern, SHALL front-load facts, and SHALL have a routing row in the entrypoint whose condition matches that line.

#### Scenario: New knowledge file
- **WHEN** the agent writes a file on the project's test fixtures
- **THEN** its first line reads "Read this when …" naming fixture work, and the entrypoint's routing table has a row with the same condition

#### Scenario: Fact already self-described by code
- **WHEN** the user asks for a knowledge file listing every directory and every task-runner recipe
- **THEN** the agent declines to enumerate leaf directories and recipes, keeps a short macro-topology map of the long-lived top-level directories in the entrypoint, points at the task runner for the recipe list, and records only the "why" and "when to read" that code cannot state

### Requirement: Behavior: Project skill warrant and handoff
For each candidate procedure the agent SHALL recommend whether it warrants a project skill, stating the condition passed or failed (recurring, non-obvious, and one of fragile, order-sensitive, or branchy), and SHALL wait for the user's choice. A failing procedure SHALL go to a cheaper carrier. A confirmed one SHALL be handed, with its trigger situations, to the skill that owns writing project skills, described by role, never by name; the agent SHALL NOT write the skill body.

#### Scenario: Single-command pre-push check
- **WHEN** the candidate is "run the type checker before pushing"
- **THEN** the agent recommends an entrypoint line, not a skill, says which condition it failed, and waits for the user's confirmation

#### Scenario: Multi-step release procedure with rollback
- **WHEN** the candidate is a ten-step release procedure with a rollback branch that broke twice last quarter and the user confirms it as warranted
- **THEN** the agent records it as warranted, names its triggers, and produces a handoff that describes the target by role, carries the definition and the trigger situations, and contains no skill name

#### Scenario: Only one incident behind the request
- **WHEN** the user wants a skill because an agent once misconfigured a cache
- **THEN** the agent recommends a knowledge line or a code comment and defers the skill until the problem recurs, while leaving the final choice to the user

### Requirement: Behavior: Process-critical skills routed explicitly
When a project skill's omission would cause harm (a pre-publish check, a migration gate), the agent SHALL add an explicit routing row in the entrypoint of the form "when doing X, load skill Y" instead of relying on description matching; auxiliary skills SHALL stay off the entrypoint.

#### Scenario: Compliance skill
- **WHEN** the project has a skill that must run before every pull request is published
- **THEN** the entrypoint's routing table names the publishing situation and that skill by name

#### Scenario: Auxiliary skill
- **WHEN** the project has a skill that formats changelog entries
- **THEN** the entrypoint carries no row for it and the agent explains that description matching suffices

### Requirement: Behavior: Inline commands versus scripts
A mechanical operation of at most two lines SHALL stay inline; anything longer, or with argument assembly or output filtering, SHALL become a script. A script owned by one project skill SHALL live under that skill's `scripts/`; a general management script SHALL live under the project's management-script directory and, when a task runner is agreed, be invoked through a recipe; without an agreed task runner the recipe SHALL join the pending decisions list.

#### Scenario: Short command
- **WHEN** the operation is a single `just test` invocation
- **THEN** the agent writes it inline and creates no script

#### Scenario: Long pipeline
- **WHEN** the operation is a seven-line shell pipeline that greps a test log for failures, used by every task
- **THEN** the agent proposes a script under the management-script directory in the agreed language that prints a pass summary or the failing files, routes to it through a recipe name, and the script meets the delivered-script contract

#### Scenario: Script used by one skill only
- **WHEN** the operation belongs to the release skill's procedure and nothing else
- **THEN** the agent places the script under that skill's `scripts/` in the handoff definition rather than in the management-script directory

#### Scenario: Management language not yet agreed
- **WHEN** a script is needed and the user has not yet agreed on a management-script language
- **THEN** the agent adds the script to the pending decisions list with the recommended language and reason, and continues with the rest of the layer

### Requirement: Behavior: Delivered scripts follow the shared script contract
Every script the agent writes into the target project SHALL run without interactive prompts, SHALL offer `--help` with a usage example, SHALL print its result on stdout and diagnostics on stderr, SHALL exit 0 on success, 1 on a finding or error, and 2 on bad arguments, SHALL be idempotent, SHALL summarise output above about 10,000 characters by default, and SHALL state only the result and the next action.

#### Scenario: Test-log script
- **WHEN** the agreed script wraps a test run of three hundred cases
- **THEN** it prints "all passed" or the failing files and assertions, exits 0 or 1 accordingly, exits 2 on an unknown flag, and prints its usage on `--help`

#### Scenario: Script run twice
- **WHEN** an agent runs the delivered script a second time without any change in the project
- **THEN** the output and the exit code are the same as the first run

### Requirement: Behavior: Placement of local explanations
When the user wants to document a constraint, the agent SHALL recommend the cheapest durable carrier: a type signature when the constraint is a static invariant with readable types, an inline comment beside the code when the reason is local or temporary, and a knowledge file only for what code cannot state.

#### Scenario: Interface invariant
- **WHEN** the user wants a document saying a function must never receive an empty list
- **THEN** the agent recommends a non-empty type or a signature-level constraint and writes no knowledge entry for it

#### Scenario: Historical workaround
- **WHEN** the user wants to record why a module pins an old library version because of an upstream bug
- **THEN** the agent recommends a comment at the pin, not a knowledge file, and explains that the fact dies with the pin

### Requirement: Behavior: Confirmation and recommendations
The agent SHALL settle from the repository only what is observable there (existing entrypoints, knowledge folders, task runner, client settings) and SHALL ask the user about everything else, presenting one recommended option with its reason and alternatives in a sentence each. Nothing SHALL be written before the user approves the layer's file list.

#### Scenario: Observable fact
- **WHEN** the repository's `justfile` lists its recipes
- **THEN** the agent reads the recipe names from the file for the validation table and does not ask the user to list them

#### Scenario: User declines the recommendation
- **WHEN** the agent recommends a knowledge folder and the user prefers a single-file entrypoint for a small project
- **THEN** the agent builds the single file against the about-200-line single-file budget, states once if that budget will be strained, and does not reintroduce the folder later

#### Scenario: Blocked decision
- **WHEN** the user has not answered whether the team uses Claude Code
- **THEN** the agent writes `AGENTS.md`, adds the `CLAUDE.md` and `.claude/skills` questions to the pending decisions list with their recommendation, and creates neither

### Requirement: Behavior: Deposited artifacts reported for read-back
On completion the agent SHALL report every file it created or changed, each with its load condition and the routing row that reaches it, the entrypoint's line count against its budget, the handoffs made by role, and the pending decisions, so the entry skill's clean-context read-back has its file list. The agent SHALL NOT perform the read-back itself.

#### Scenario: Report after build
- **WHEN** the agent finishes the layer with an entrypoint and two knowledge files
- **THEN** the report lists the three paths, each file's "Read this when" condition, the matching routing rows, the entrypoint's line count against the budget, and the pending decisions

#### Scenario: Run standalone
- **WHEN** the skill was loaded directly rather than routed from an entry skill
- **THEN** the report ends by stating that the layer still awaits a clean-context read-back and lists the files to read, without the agent re-reading them in its own context

### Requirement: Outcomes
Given a project and the user's confirmed decisions, the agent SHALL leave a knowledge and routing layer whose entrypoint is within its budget, whose every knowledge file is reachable through a routing row matching its opening condition, and whose skill-or-carrier decisions are recorded with reasons and the user's confirmation.

#### Scenario: Greenfield layer
- **WHEN** the user asks for the knowledge and routing layer of a new Python service that uses `just`, pre-commit, and Claude Code plus Codex, and accepts the recommended layout
- **THEN** the result has an `AGENTS.md` of at most 120 lines ordered always-applicable, routing table, validation table, then the position the entropy layer fills; a `CLAUDE.md` containing only `@AGENTS.md`; knowledge files under `.agents/knowledge/`, each opening "Read this when" with a matching routing row; `.agents/skills/` with `.claude/skills` linked to it; recipe names rather than raw commands in the validation table; and no file created without its four-question answers shown

#### Scenario: Brownfield restructure
- **WHEN** the user hands over a repository with a 280-line `AGENTS.md`, a divergent `CLAUDE.md`, and four unreferenced docs under `docs/agents/`
- **THEN** the result has an `AGENTS.md` at or under 120 lines keeping every always-applicable rule, a `CLAUDE.md` reduced to the import with its former rules merged or listed as pending, each of the four docs routed, merged, or deleted by the user's explicit choice, and a report naming what moved where

#### Scenario: Carrier decisions
- **WHEN** the user lists six procedures and asks where each belongs
- **THEN** each procedure carries a recommended carrier (entrypoint line, knowledge file, code comment or type, or project skill) with the passed or failed condition stated, the final assignment is the one the user confirmed, and the confirmed skills are handed off to the skill that writes project skills without that skill being named
