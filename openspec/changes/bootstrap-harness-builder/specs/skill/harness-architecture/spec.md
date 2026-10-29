# Spec Delta

## Purpose

Governs what an agent that loaded `harness-architecture` observably does: it is the methodology manual behind every harness layer, answering questions about why a harness is shaped as it is, where a rule belongs, what an existing harness gets wrong, and how agents share a repository, and it ships model-invoked to Claude Code, Codex, and Antigravity. Non-goals: it is not the build workflow (investigation, planning, approval, construction, read-back, and cleanup belong to the user-invoked entry skills), it writes no file into a target project, it does not author project skills, and it does not carry the spec-driven development loop.

## ADDED Requirements

### Requirement: Triggering
The skill description SHALL cause the skill to load for questions answered without changing the project: why a harness is shaped a certain way, where in principle a rule or fact for coding agents should live, what is wrong with an existing entrypoint or knowledge layout, or how several agents share a repository. It SHALL NOT load for a request to build, move, split, or restructure harness files (a layer's builder or an entry skill owns that), for human documentation, or for application code.

#### Scenario: Placement question
- **WHEN** the user says "we have a rule that every migration needs a rollback script; should that go in AGENTS.md, a knowledge file, or a skill?"
- **THEN** the skill loads

#### Scenario: Reasoning question
- **WHEN** the user says "our CLAUDE.md is 400 lines and the agent still ignores half of it; why does this keep happening?"
- **THEN** the skill loads

#### Scenario: Existing harness critique
- **WHEN** the user says "look at our .agents folder and tell me what an agent would get wrong working from it"
- **THEN** the skill loads

#### Scenario: Concurrency question
- **WHEN** the user says "two agents keep overwriting each other's labels on the same PR; how should we split the work?"
- **THEN** the skill loads

#### Scenario: Full build request
- **WHEN** the user says "set up everything an agent needs to work in this repo: entrypoint, checks, permissions, the lot"
- **THEN** the skill does not load, because the user-invoked entry skill owns the build

#### Scenario: Entrypoint restructure request
- **WHEN** the user says "our AGENTS.md is 300 lines and agents ignore half of it, help me restructure it"
- **THEN** the skill does not load; the knowledge and routing layer's builder does

#### Scenario: Placement change request
- **WHEN** the user says "move the style guide out of AGENTS.md into a knowledge file and fix the routing"
- **THEN** the skill does not load; the knowledge and routing layer's builder does

#### Scenario: Single-layer build request
- **WHEN** the user says "write the permission allowlist for this repo"
- **THEN** the skill does not load; the authority layer's builder does

#### Scenario: Human documentation
- **WHEN** the user says "our README is out of date; rewrite the getting-started section for new contributors"
- **THEN** the skill does not load

#### Scenario: Application code rule
- **WHEN** the user says "add a lint rule so nobody imports the database module from the API layer"
- **THEN** the skill does not load

### Requirement: Behavior: Reasoning grounded in the methodology
When asked why a harness practice holds or whether it applies, the agent SHALL answer from the methodology, tagging each point with its section (`[§x.y]`), and SHALL trace the trade-off to the five variables (error cost, maintenance horizon, environment isolation, autonomy, team size) rather than to a project type.

#### Scenario: Prototype CI question
- **WHEN** the user asks "this is just a research prototype, why would we need any CI at all?"
- **THEN** the answer names which of the five variables would make a hard boundary worth its cost (for example a data pipeline whose error cost is high), tags the sections it draws on, and gives no verdict based on the label "prototype" alone

#### Scenario: Over-long entrypoint
- **WHEN** the user asks why agents ignore rules in a 400-line entrypoint
- **THEN** the answer explains attention dilution and the per-task minimal-complete-context rule from context economics, states the entrypoint budget and that always-applicable constraints come first, and tags the sections

#### Scenario: Fact the code can state
- **WHEN** the user asks whether to list every directory and its purpose in the entrypoint
- **THEN** the answer says the file system is the source of truth for topology, that the entrypoint records only what code cannot state (why, and when to read what), and that a copied fact is a future contradiction

### Requirement: Behavior: Placement by loading mode
When asked where a rule, fact, or procedure should live, the agent SHALL classify it by when it is needed (every task, by task type, by location, by action, or by description-matched auxiliary flow), SHALL recommend one placement with its reason and name the alternatives, and SHALL state the framework caveat whenever the recommended mode depends on the framework.

#### Scenario: Always-applicable rule
- **WHEN** the user asks where a rule whose violation is costly on every task (a secret-handling rule, a commit discipline) should live
- **THEN** the agent recommends the always-applicable block at the top of the root entrypoint, not a subdirectory file, a knowledge file, or a skill

#### Scenario: Flow-critical procedure
- **WHEN** the user asks whether a pre-release compliance check can be a description-triggered skill
- **THEN** the agent says description matching is probabilistic, that a flow-critical skill must be routed explicitly from the entrypoint by scenario, and keeps description matching for auxiliary flows only

#### Scenario: Subdirectory entrypoint
- **WHEN** the user wants to put a must-follow constraint in a subdirectory's entrypoint file
- **THEN** the agent states that subdirectory loading differs across frameworks, that such a file may never load, that it must carry no required constraint and must not contradict the root, and asks which frameworks the team uses before relying on location or action loading

### Requirement: Behavior: Single source of truth and adjudication
When the agent finds or is asked about a fact recorded in more than one place, it SHALL state the entropy law (a wrong or stale harness is worse than none), SHALL recommend one source with every other place referring to it, and SHALL require an adjudication rule naming which copy wins when they disagree, preferring code over documents as the source.

#### Scenario: Duplicated command list
- **WHEN** the entrypoint, a knowledge file, and a README each list the test command with different flags
- **THEN** the agent names the task-runner recipe as the source, recommends the documents name only the recipe, and says which copy is authoritative until the duplicates are removed

#### Scenario: Copy request for the Claude entrypoint
- **WHEN** the user asks whether `CLAUDE.md` should copy `AGENTS.md` for safety
- **THEN** the agent recommends an import reference and explains it as an instance of one fact in one place, not a framework trick

#### Scenario: Existing harness contradicts the methodology
- **WHEN** an existing harness deliberately keeps two copies of a rule and the user asks the agent to leave it
- **THEN** the agent records the contradiction with the section it violates and the mirror check that would compensate, and does not rewrite the files

### Requirement: Behavior: Audit of an existing harness
When asked what an existing harness gets wrong, the agent SHALL read the harness before judging it, SHALL run the project's own harness self-check when one exists and quote its findings rather than re-deriving them, SHALL report each finding as a file, a gap classified as stale, duplicated, contradictory, invisible, missing, or excessive, and a fix, SHALL check that every knowledge file has a reachable load condition, and SHALL change no file.

#### Scenario: Invisible knowledge file
- **WHEN** a knowledge file exists that no entrypoint or routing table points to
- **THEN** the report names the file, classifies it as invisible, and proposes the routing line or the deletion

#### Scenario: Constraint without a current cause
- **WHEN** a lint rule or skill exists for a problem the repository no longer has
- **THEN** the report classifies it as excessive and proposes removing it, because an unused constraint only slows the agent

#### Scenario: Project self-check present
- **WHEN** the repository has a `check_harness.py` or a task-runner recipe that runs one
- **THEN** the agent runs it, the report quotes its output, and the manual findings add only what that output does not cover

#### Scenario: Project self-check absent
- **WHEN** the repository has an entrypoint and knowledge files but no harness self-check
- **THEN** the report lists the absent self-check as a missing finding for the entropy layer and still covers every file by hand

#### Scenario: Audit requested without a harness
- **WHEN** the repository has no entrypoint, no knowledge files, and no agent configuration
- **THEN** the agent reports that there is nothing to audit, states what the code already describes on its own, and points the user to the user-invoked creation entry rather than inventing findings

### Requirement: Behavior: Multi-agent rules on request
The agent SHALL treat a single agent as the default and SHALL state the concurrency rules only when the user describes or asks about more than one agent working at once: read-only work may share a workspace, writing work needs an isolated worktree or container, shared resources are namespaced, each agent owns its remote branch, platform writes go through one coordinator and are pre-authorised, and merge ownership is named.

#### Scenario: Parallel writers
- **WHEN** the user asks how to run three agents fixing different modules at once
- **THEN** the agent recommends one worktree and one remote branch per agent, lists the shared resources to check (ports, databases, lock files, caches, rate limits), and asks who merges and who adjudicates conflicts

#### Scenario: Platform writes
- **WHEN** parallel agents comment on and label the same issue
- **THEN** the agent recommends that only one coordinator writes to platform objects, that the others produce results, and that these irreversible writes are pre-authorised

#### Scenario: Single agent
- **WHEN** the user asks "where should our one coding agent keep its scratch notes?"
- **THEN** the agent answers the placement question and does not raise worktrees, remote-branch ownership, or coordinators

### Requirement: Behavior: Section map and handoff
When a question turns into a request to build or change a layer, or the user asks which part of the methodology covers a topic, the agent SHALL name the methodology sections, the harness layer that owns the topic, and the skill that owns that layer; SHALL direct the user to invoke the creation or improvement entry by name for a build; and SHALL NOT perform the build itself.

#### Scenario: Build request after a question
- **WHEN** after an explanation the user says "ok, set that up for us"
- **THEN** the agent names the entry skill the user must invoke, states that an approved plan precedes any file, and creates nothing

#### Scenario: Section lookup
- **WHEN** the user asks "which part of the method covers permission lists?"
- **THEN** the agent names the authority section, the authority layer, and the skill that owns that layer, and writes no permission file

### Requirement: Behavior: Recommendations, not decisions
On any question with more than one defensible answer, the agent SHALL give exactly one recommended option with its reason and the alternatives in a sentence each, SHALL wait for the user's choice, and SHALL confirm with the user any fact the repository cannot show (framework in use, team size, autonomy, error cost) before the recommendation depends on it.

#### Scenario: Unknown framework
- **WHEN** the recommended placement depends on whether subdirectory entrypoints load, and the repository does not show which agent frameworks the team uses
- **THEN** the agent asks which frameworks are in use instead of assuming one

#### Scenario: User declines the recommendation
- **WHEN** the user picks an alternative the agent argued against
- **THEN** the agent challenges once with the evidence, then answers every later question within the user's choice

### Requirement: Outcomes
Given a reasoning, placement, or audit task, the agent SHALL produce an answer a reader can check against the methodology: section-tagged, grounded in the five variables, with one recommendation per decision, and with findings in file-gap-fix form.

#### Scenario: Placement review of a draft entrypoint
- **WHEN** the user pastes a 180-line draft `AGENTS.md` that mixes safety rules, a directory listing, a style guide, a release procedure, and a sync reminder, and asks what belongs where
- **THEN** the answer keeps the safety rules and commit discipline at the top as always-applicable, routes the style guide to a knowledge file with a load condition, says the directory listing is stated by the file system, states whether the release procedure meets the project-skill threshold (recurring, non-obvious, and fragile, ordered, or branching) and where it does recommends an explicitly routed project skill, keeps the sync reminder in the entrypoint as a keep-in-sync line, tags each move with its section, and reports the resulting line count against the 100-line target

#### Scenario: Audit of a brownfield harness
- **WHEN** the user points at a repository whose `CLAUDE.md` duplicates `AGENTS.md` with two differing commands, whose `docs/agents/` holds four files no entrypoint mentions, which carries a skill for a migration finished last year, and which has no harness self-check
- **THEN** the report lists a contradictory finding with an adjudication, four invisible findings each with a routing line or deletion, one excessive finding proposing removal, and one missing finding for the absent self-check, each as file, gap, fix; changes no file; and ends by naming the improvement entry for the repair

#### Scenario: Concurrency design question
- **WHEN** the user describes a nightly job in which four unattended agents each fix one package and open pull requests
- **THEN** the answer prescribes one worktree and remote branch per agent, a coordinator for platform writes, pre-authorisation of those writes, namespaced test resources, a named merge owner, and tags the sections, without building anything
