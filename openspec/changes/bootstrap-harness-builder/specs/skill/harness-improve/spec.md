# Spec Delta

## Purpose

Governs what an agent that loaded `harness-improve` observably does when a project already has a harness and the user wants it audited, repaired, thinned, hardened, migrated to another spec carrier or platform, or re-layered; the skill is user-invoked and ships to Claude Code, Codex, and Antigravity. Non-goals: creating a harness where none exists (the creation entry skill's work), building any single layer itself (the layer builders do that), fixing application tests or CI that are not harness, and writing or rewriting README, CONTRIBUTING, or SECURITY.

## ADDED Requirements

### Requirement: Triggering
The skill SHALL load only when the user invokes it by name, as a user-invoked skill of the client, and SHALL NOT load from a description match, however closely a request resembles its subject.

#### Scenario: Invoked by name with no further text
- **WHEN** the user runs the skill by name with no arguments in a repository that has an `AGENTS.md`
- **THEN** the skill loads and begins its audit of the existing harness

#### Scenario: Invoked by name with a complaint
- **WHEN** the user runs the skill by name followed by "agents keep running the old test command, something in here is stale"
- **THEN** the skill loads and treats the complaint as a lead for the audit, not as its only scope

#### Scenario: Invoked by name with a restructuring goal
- **WHEN** the user runs the skill by name followed by "we are moving from Spec-Kit to OpenSpec and from GitLab to GitHub"
- **THEN** the skill loads and records the stated migration as the user's goal, to confirm after the audit rather than to act on before it

#### Scenario: Invoked by name on a repository with no harness
- **WHEN** the user runs the skill by name in a repository that has no agent-facing file, skill, hook, or check
- **THEN** the skill loads, reports that there is nothing to audit, names the creation entry skill as the right tool, and writes nothing

#### Scenario: Audit asked for in plain words
- **WHEN** the user writes "audit our harness and tell me what is stale or duplicated" without invoking the skill by name
- **THEN** the skill does not load, whatever other skill the request matches

#### Scenario: Thinning asked for in plain words
- **WHEN** the user writes "our AGENTS.md is 300 lines and the pre-commit takes a minute, slim it down" without invoking the skill by name
- **THEN** the skill does not load

#### Scenario: Hardening asked for in plain words
- **WHEN** the user writes "the prototype is going to production, harden the harness: lint, tests, CI, the lot" without invoking the skill by name
- **THEN** the skill does not load

### Requirement: Behavior: Audit before any change
Before proposing anything, the agent SHALL inventory every project-visible harness artifact and record for each its discovery path, load trigger, source of truth, and update mechanism; SHALL follow entrypoint pointers the way a future agent would; and SHALL run the project's own harness self-check when one exists. The audit reads and reports; it writes nothing.

#### Scenario: Inventory of an existing harness
- **WHEN** the repository holds `AGENTS.md`, `CLAUDE.md`, `.agents/knowledge/`, two project skills, a pre-commit config, and CI workflows
- **THEN** the report lists every one of them, and for each names how an agent reaches it, what makes it load, which file or tool is its source of truth, and what keeps it current, with "none" written where one is missing

#### Scenario: Harness self-check present
- **WHEN** the repository contains a `check_harness.py` or a task-runner recipe that runs one
- **THEN** the agent runs it and quotes its findings in the audit report instead of re-deriving them by hand

#### Scenario: Harness self-check absent
- **WHEN** the repository has no harness self-check
- **THEN** the audit records its absence as a finding for the entropy layer and still completes the inventory

### Requirement: Behavior: Defects and excess are classified
The agent SHALL classify every audit finding as stale, duplicated, contradictory, invisible, missing, or excessive, SHALL cite the evidence for each, SHALL attach to each a proposed disposition the user accepts or changes, and SHALL present the classified list to the user as one report before asking the repair-or-rebuild question. [§6.3]

#### Scenario: Stale command
- **WHEN** `AGENTS.md` documents `npm test` and the repository has only `pnpm` lockfiles and a `pnpm test` script
- **THEN** the finding is classified stale, cites both files, names `package.json` as the source of truth, and proposes updating the documented command

#### Scenario: Excess with no current cause
- **WHEN** a lint rule, a one-off migration skill, or a routing entry guards against something no longer present in the repository
- **THEN** the finding is classified excessive and proposed for thinning, with the vanished cause named

#### Scenario: Knowledge nothing reaches
- **WHEN** a knowledge file exists but no entrypoint, skill, or pointer refers to it
- **THEN** the finding is classified invisible, and the proposed disposition is reconnect or remove, never leave unchanged

#### Scenario: User changes a disposition
- **WHEN** the user keeps a constraint the report proposed for thinning and names what it still catches
- **THEN** the finding stays in the report with the user's disposition and reason, and no later step removes that constraint

### Requirement: Behavior: Drift is fixed before other work
When the audit finds a specification that contradicts the code or a harness that contradicts itself, the agent SHALL propose fixing or deleting it as the first item of the plan, and SHALL NOT build, thin, harden, or migrate on top of it until the user has decided its disposition. [§5.1]

#### Scenario: Drifted specification
- **WHEN** a spec under the project's spec directory describes an interface the code no longer has
- **THEN** the plan's first item is to update or delete that spec, and every later item is marked as depending on it

#### Scenario: Two rules disagree
- **WHEN** `AGENTS.md` says commits use plain 50/72 titles and a knowledge file mandates Conventional Commits
- **THEN** the agent asks the user which is the source of truth, and the plan keeps that copy and removes or updates the other before any other change

#### Scenario: User wants the new feature first
- **WHEN** the user asks to add a new layer before the drifted spec is handled
- **THEN** the agent states once why drift comes first, and if the user still declines, records the drift as a pending decision and proceeds without building on the contradicted content

### Requirement: Behavior: Repair or rebuild is the user's decision
After the classified report, the agent SHALL present repair and rebuild as options with one recommendation and its reason, and SHALL wait for the user's choice; it SHALL recommend keeping every working choice as the source of truth and SHALL offer tooling migrations as separate changes, not folded into the repair. [§6.3]

#### Scenario: Scattered but working harness
- **WHEN** the audit finds a usable entrypoint, correct commands, and a few stale pointers
- **THEN** the agent recommends repair, states that rebuild would discard working conventions, and asks before doing either

#### Scenario: User chooses rebuild
- **WHEN** the user picks rebuild against the recommendation
- **THEN** the agent challenges once with the evidence, then plans the rebuild, keeping the project's task runner, lint configuration, and branching habit as given facts

#### Scenario: Migration surfaced during audit
- **WHEN** the audit shows the project would gain from switching task runners
- **THEN** the agent lists the switch as a separate recommended change for the team to decide, and the repair plan does not depend on it

### Requirement: Behavior: Restructuring kinds are named and bounded
The agent SHALL classify the agreed work as one or more of hardening, thinning, carrier or platform migration, or re-layering, and SHALL state for each the boundary of what changes and what is preserved. [§6.2]

#### Scenario: Hardening a prototype
- **WHEN** the user says the prototype becomes a long-lived product
- **THEN** the plan covers recording the stable structure in the entrypoint, adding type, lint, and test gates as soft read-only invariants while locking the security control plane (sandbox configuration, secret-scan hooks) hard read-only, and clearing exploration leftovers with a sync mechanism, each confirmed with the user

#### Scenario: Thinning an overweight harness
- **WHEN** the agreed work is thinning
- **THEN** every removal names the constraint, the thing it used to catch, and the evidence it no longer occurs, and nothing is deleted that still catches something

#### Scenario: Carrier migration
- **WHEN** the agreed work is moving from one spec carrier to another
- **THEN** the plan freezes or archives in-flight changes in the old carrier, states which specs move and which are deleted as covering unchanged code, and installs the new carrier's automation only after the user approves

#### Scenario: Platform migration
- **WHEN** the agreed work is moving from GitLab to GitHub or the reverse
- **THEN** the plan lists the labels, templates, workflows, and settings to recreate and marks every remote write as needing its own approval

#### Scenario: Re-layering
- **WHEN** the agreed work is redistributing an existing harness across the six layers, such as authority rules written inside `AGENTS.md` and a completion rule enforced only by a lint hook
- **THEN** the plan names for each moved rule its old home, its new home in the layer that owns it, the entrypoint pointer that replaces it, and the copy to delete; no rule is dropped in the move, and the grade of both layers involved is re-stated

### Requirement: Behavior: Affected layers are re-graded
Grades cover the six methodology layers (environment and sandbox, knowledge and routing, hard boundary, authority, specification and completion, entropy); the platform lifecycle layer is routed to its builder but not graded. For every graded layer the agreed work touches, the agent SHALL state the current and proposed grade among omitted, light, medium, and thick with the justifying variable, and SHALL ask the user to confirm each changed grade; untouched layers keep theirs unasked. [§6.1]

#### Scenario: One layer moves
- **WHEN** thinning removes architecture checks from CI
- **THEN** the hard-boundary layer is shown moving from thick to medium with the reason, the other five graded layers are listed as unchanged, and the user confirms the move

#### Scenario: Observable grade
- **WHEN** a layer's grade is plain from the repository, such as an existing dev container for the environment layer
- **THEN** the agent states it as observed rather than asking

#### Scenario: Platform migration touches no graded layer
- **WHEN** the agreed work is only a platform migration
- **THEN** the report shows the six graded layers unchanged and states that the platform lifecycle layer is being rebuilt without a grade

### Requirement: Behavior: Plan approval precedes every file
The agent SHALL write an improvement plan that names every file to add, change, or delete, the disposition and source of truth per finding, the re-graded layers, and the verification per item; SHALL show it in the conversation or write it only to the project's ignored handoff directory; and SHALL change no file under version control until the user approves it. An approved plan authorises the files it names and nothing else.

#### Scenario: Plan presented
- **WHEN** the audit report and dispositions are agreed
- **THEN** the user sees a plan listing each file with its action, the finding it resolves, the source of truth, and how the change is verified, and no tracked file has changed yet

#### Scenario: Action outside the plan
- **WHEN** executing the approved plan would require deleting a branch, changing a remote setting, or widening agent permissions
- **THEN** the agent stops that item, asks for a separate explicit decision, and continues with the other items

#### Scenario: User declines the plan
- **WHEN** the user rejects the plan
- **THEN** the agent revises or ends the work, and no tracked file in the target project has changed

### Requirement: Behavior: Layers are routed to builders by their ownership phrase
For each layer the approved plan changes, the agent SHALL hand the work to the installed skill whose description states "Owns the <layer> layer" for that layer, passing the audit findings and the approved dispositions for that layer, SHALL load it and let its workflow run the layer and hand back, and SHALL name no builder itself; when no installed skill's description claims the layer, the agent SHALL say so and perform that layer's items itself from the plan, recording the gap.

#### Scenario: Knowledge layer repair
- **WHEN** the plan updates stale pointers in the entrypoint and reconnects an invisible knowledge file
- **THEN** the skill whose description owns the knowledge and routing layer performs the change and receives the exact findings, and the files left behind contain no reference to the builder

#### Scenario: Builder renamed
- **WHEN** the skill owning the entropy layer has been renamed but its description still carries the ownership phrase
- **THEN** routing succeeds without any change to the entry skill

#### Scenario: No builder claims a layer
- **WHEN** no installed skill's description claims the layer the plan changes
- **THEN** the agent performs that layer's items itself following the plan and reports the gap to the user in the closing report

### Requirement: Behavior: Checkpoints are commits
The agent SHALL commit once per verified layer, SHALL write each message in the convention the audit found the project using or the plan recorded, SHALL add no AI attribution, and SHALL push nothing unless the user decided so for that step. [§4.3]

#### Scenario: Layer passes its checks
- **WHEN** a layer's changes are in place and the project's checks pass locally
- **THEN** the agent commits them with a message in the recorded convention and no attribution trailer, and does not rely on stashes or session-only undo

#### Scenario: Push implied but not approved
- **WHEN** the plan was approved without a decision on pushing and a layer's commit is made
- **THEN** the commit stays local, and pushing appears as its own question or pending decision

#### Scenario: Pre-commit rejection at a checkpoint
- **WHEN** the secret scan in pre-commit rejects a checkpoint commit
- **THEN** the agent removes or fixes the flagged content and retries; it does not bypass the hook

### Requirement: Behavior: Read-back in a clean context
After the builders finish, the agent SHALL have the changed harness read back by a clean-context reader that has not seen the plan, SHALL fix every reported gap or record it as a pending decision, and SHALL record a degradation when no subagent is available and it re-reads the files itself in a fresh pass.

#### Scenario: Verifier available
- **WHEN** the client offers a read-only verifier agent
- **THEN** every changed file and the entrypoint are read back, and the result lines are quoted in the final report

#### Scenario: No subagent available
- **WHEN** the client has no subagent facility
- **THEN** the agent re-reads every changed file as a future agent would, resolves every pointer, and the final report states that read-back was done without a clean context

#### Scenario: Read-back finds a dangling pointer
- **WHEN** the read-back reports a pointer to a deleted file
- **THEN** the pointer is fixed or removed before the work is reported done

### Requirement: Behavior: Final review covers vocabulary, self-containment, mechanics, and the checklist
Before closing, the agent SHALL review every changed file for terms only this plugin defines and left undefined, for any dependency on the plugin (names, paths, phrases, scripts invoked from a skill directory), for mechanics (every rule reachable from the entrypoint, entrypoint of at most 120 lines, links resolve, documented commands run, each sync concern owned in both directions), and SHALL walk the methodology's closing checklist item by item, fixing and re-reading what the review changes.

#### Scenario: Leaked term
- **WHEN** a repaired knowledge file uses "pending decisions list" without saying what one contains
- **THEN** the review defines the term in that file or rewrites the sentence plainly, and the file is re-read

#### Scenario: Plugin path left in a file
- **WHEN** a hardened CI step or task-runner recipe invokes a script by a path inside a skill directory
- **THEN** the review replaces it with the project's own copy and tells the user that later plugin fixes do not reach that copy

#### Scenario: Checklist item fails
- **WHEN** the checklist item on entropy finds a Keep In Sync entry whose counterpart file does not name the pair
- **THEN** the agent adds the reverse entry, commits it as a checkpoint, and records the item as passed

### Requirement: Behavior: Close with pending decisions
The agent SHALL finish with a report of what changed and why, the before-and-after grade per touched layer, the verification run, the manual platform actions left to the user, and a single pending decisions list in which each item states what is blocked, the options, the recommendation with its reason, and which finished work each option would change.

#### Scenario: Blocked item during execution
- **WHEN** an item needs a decision only the user can make, such as which of two conflicting rules is intended
- **THEN** the agent continues with every independent item and reports the blocked one once in the closing list, not as an interruption

#### Scenario: Nothing pending
- **WHEN** every item was executed and verified
- **THEN** the closing report says so explicitly and still lists the verification commands run

### Requirement: Outcomes
Run end to end, the skill SHALL leave the project with a harness whose every remaining artifact is reachable, current, proportionate to the agreed grades, and verified, and whose changes are traceable to audit findings the user approved.

#### Scenario: Stale harness repaired
- **WHEN** the user invokes the skill on a repository whose `AGENTS.md` names two deleted directories and a renamed test command, whose knowledge file on branching nothing links to, and which has a passing `check_harness.py`
- **THEN** the result has an entrypoint of at most 120 lines naming only existing paths and the current command, the branching file reachable from the entrypoint or deleted with the user's agreement, `check_harness.py` still passing, one checkpoint commit per touched layer with no AI attribution and nothing pushed, and a closing report tracing each edit to a classified finding

#### Scenario: Prototype hardened
- **WHEN** the user invokes the skill on a prototype with a ten-line `AGENTS.md`, no checks, and a leftover `scripts/tmp_*` folder, and chooses hardening
- **THEN** the result has the hard-boundary layer re-graded with the user's confirmation, formatting and secret scanning plus the agreed lint and test gates in pre-commit and CI, the stable directory structure recorded in the entrypoint, the temporary scripts removed or kept by explicit decision, a harness self-check wired into the task runner that calls no path inside a skill directory, and a report listing every grade change

#### Scenario: Overweight harness thinned
- **WHEN** the user invokes the skill on a repository where a spec drifted from the code and three constraints guard against problems no longer present, and chooses thinning
- **THEN** the drifted spec is fixed or deleted before any other edit, each of the three constraints is removed with the vanished cause named, nothing that still catches a current problem is removed, and the touched layers show their new grades in the report
