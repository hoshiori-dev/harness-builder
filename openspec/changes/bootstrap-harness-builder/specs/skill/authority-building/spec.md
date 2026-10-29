# Spec Delta

## Purpose

Governs what an agent that loaded `authority-building` observably does when it
builds or revises the authority layer of a target project's harness (the
policy separating what agents may do on their own from what the sandbox lets
them do, the framework permission lists implementing it, and the checkpoint
rules for commits and pushes), shipping to Claude Code, Codex, and
Antigravity. Non-goals: the sandbox and token boundary itself (the environment
layer), branch protection, platform settings, and the branch-ownership and
coordinator rules for parallel agents (the platform lifecycle layer),
pre-commit hooks and CI checks (the hard-boundary layer), the per-task list of
pre-authorised irreversible actions inside a spec (the specification and
completion layer and its carriers), and any authority level ladder or
self-escalation vocabulary from earlier builders.

## ADDED Requirements

### Requirement: Triggering
The skill SHALL load for building, revising, or auditing a project's rules
about what coding agents may do without asking, including permission allow
and deny lists, approval timing, checkpoint and push rules, and the handover
of the authority layer from an approved harness plan. It SHALL NOT load for a
one-off question about a git command, for sandbox or token scope design, for
platform settings such as branch protection, or for the pre-authorised actions
of a single task.

#### Scenario: Permission lists for a project
- **WHEN** the user says "Agents keep asking me to approve every shell command in this repo. Set up allow and deny lists so they only stop for things that matter."
- **THEN** the skill loads

#### Scenario: Policy after an incident
- **WHEN** the user says "An agent force-pushed over a teammate's branch yesterday. Write the project rules for what agents may do on their own so it does not happen again."
- **THEN** the skill loads

#### Scenario: Checkpoint and push discipline
- **WHEN** the user says "Define how agents in this project commit checkpoints, squash drafts, and when they are allowed to push."
- **THEN** the skill loads

#### Scenario: Entry skill routes the layer
- **WHEN** an approved harness plan hands over "build the authority layer: reversibility classes, policy, permission lists, checkpoint rules"
- **THEN** the skill loads

#### Scenario: Command question near-miss
- **WHEN** the user says "What does git push --force-with-lease do differently from --force?"
- **THEN** the skill does not load

#### Scenario: Sandbox near-miss
- **WHEN** the user says "Which token scopes and network egress should the agent container be allowed?"
- **THEN** the skill does not load

#### Scenario: Branch protection near-miss
- **WHEN** the user says "Require two approvals and a green CI check before anything merges to main."
- **THEN** the skill does not load

### Requirement: Behavior: The layer is built to the confirmed grade
The skill SHALL build the authority layer to the grade the plan confirmed for
it and SHALL NOT thicken it on its own: light is a few allow and deny entries
plus one sentence in the agent entrypoint, with the rest left to the framework
default; medium is a written policy document; thick is the policy plus an
explicit list of irreversible actions and the pending decisions format. When
no grade was confirmed the skill SHALL ask, recommending medium.

#### Scenario: Light grade confirmed
- **WHEN** the plan grades the authority layer light
- **THEN** the agent proposes allow and deny entries and one entrypoint sentence stating that unlisted commands fall to the framework default, and deposits no separate policy document

#### Scenario: Thick grade confirmed
- **WHEN** the plan grades the authority layer thick
- **THEN** the deposited policy carries an explicit list of the project's irreversible actions and the pending decisions format, and the agent reports both as part of the layer

#### Scenario: Grade not recorded
- **WHEN** the agent is handed the layer without a confirmed grade
- **THEN** it asks for the grade with medium as the recommended option and its reason, and writes nothing until the user answers

### Requirement: Behavior: Actions are classified by reversibility
The skill SHALL classify every action an agent may take as reversible and
internal (done directly) or irreversible or outward (pre-authorised at plan
time or deferred to the pending decisions list), and the deposited policy
SHALL state the classification with examples from the project's own tools.
[§4.2.3]

#### Scenario: Local commit versus push
- **WHEN** the user asks whether a local commit and a push belong to the same class
- **THEN** the agent answers that a local commit is reversible and internal while a push is outward and irreversible because the remote keeps pushed objects, and the deposited policy records them as different classes

#### Scenario: Outward action without pre-authorisation
- **WHEN** a clean-context reader of the deposited policy is asked what an agent does when a step posts a tracker comment that no plan pre-authorised
- **THEN** the reader answers from the file alone: defer the comment to the pending decisions list and continue with the work that does not depend on it

#### Scenario: Specification workflow present
- **WHEN** the project has a specification workflow
- **THEN** the agent records that each spec carries a list of the irreversible actions pre-authorised for that task and hands the format to the layer that owns the spec contract, by description, never by name

### Requirement: Behavior: Approvals sit at the plan and at the handoff
The deposited policy SHALL place human approval at two points only: on the
plan, which approves the outcome and the boundaries of the approach and never
a list of steps, and on the finished work. It SHALL state that per-command
approval is not a safety mechanism and that a blocked agent continues with
everything not depending on the blocked decision. [§4.2.1, §4.2.2]

#### Scenario: Plan approval scope
- **WHEN** the user asks what they are approving when they approve a plan
- **THEN** the agent answers that the approval covers what is done, what is not done, and where the approach is bounded, not the sequence of steps, and the deposited policy says the same

#### Scenario: Agent blocked mid-task
- **WHEN** a clean-context reader of the deposited policy is asked what an agent does when one item needs a decision only the user can make
- **THEN** the reader answers from the file alone: finish every other item first and raise the decision once, at the end or when nothing else can proceed

#### Scenario: User requests per-command approval
- **WHEN** the user asks for every command to be approved by hand in a project in its running phase
- **THEN** the agent says once why this trades real safety for approval fatigue, names the sandbox as the real boundary, and writes the per-command mode only if the user still chooses it

### Requirement: Behavior: Pending decisions follow one format
The deposited policy SHALL define the pending decisions list so that every
item states what is blocked and why, the options, the recommended option with
its reason, and which finished work each option would change, presented once
rather than one question at a time, so that a user returning after hours away
can decide each item from the list alone. [§4.2.2]

#### Scenario: Field list stated
- **WHEN** a clean-context reader of the deposited policy is asked which fields a pending decisions item must carry
- **THEN** the reader lists, from the file alone, what is blocked and why, the options, the recommended option with its reason, and the finished work each option would change, and finds the rule that the list is presented once

#### Scenario: Item missing a field
- **WHEN** the user shows the agent a pending decisions item from the project that omits which finished work each option would change
- **THEN** the agent names the missing field and says the item is incomplete under the deposited policy

### Requirement: Behavior: A refusal is a decision, never routed around
The deposited policy SHALL state the two responses to a refused action: the
refusal reveals that the plan placed the work in the wrong place, so return to
the plan and choose another approach; or the refusal is a real policy
boundary, so record it as a pending decision. It SHALL state the one forbidden
move: retrying the same intent through an equivalent command, a script, or a
different tool. [§4.2.4]

#### Scenario: Denied file edit
- **WHEN** a clean-context reader of the deposited policy is asked what an agent does when an edit to a protected file is refused
- **THEN** the reader answers from the file alone: reconsider whether the logic belongs elsewhere or add a pending decision, and never write the same change through a shell redirect or script

#### Scenario: Equivalent command attempted
- **WHEN** a clean-context reader of the deposited policy is asked whether an agent denied `git push --force` may try `git push --force-with-lease` on the same branch
- **THEN** the reader answers from the file alone that this is routing around the refusal and is forbidden

#### Scenario: Three responses proposed
- **WHEN** the user or an existing policy proposes a third refusal response such as "fix the entry that blocked you"
- **THEN** the agent says that loosening a rule is outside agent authority and belongs to self-protection, and keeps the two responses and the prohibition in the policy

### Requirement: Behavior: Framework rules follow deny-fixed, allow-confirmed, no-ask
The skill SHALL recommend a fixed deny list (`git reset --hard`, `git push
--force`, `git push --all/--mirror/--tags`, `git clean -fd`, `git branch -D`,
`rm -rf` at the repository root, edits to the authority file and security
hooks), SHALL propose an allow list from the project's observed commands for
the user to confirm, and SHALL add no ask entries unless the user names an
irreplaceable reason. [§4.2.5]

#### Scenario: Allow list proposed from the repository
- **WHEN** the repository's task runner and test commands are observable
- **THEN** the agent proposes them as allow entries with the evidence for each and waits for the user to confirm or trim before writing any permission file

#### Scenario: Ask entry requested
- **WHEN** the user asks to put a whole MCP server or tool family under ask
- **THEN** the agent proposes instead to allow its read-only tools and classify its outward tools by reversibility, adding an ask entry only if the user states a reason no allow or deny entry can serve

#### Scenario: Framework files declined
- **WHEN** the user declines framework permission files
- **THEN** the agent deposits the written policy alone, records the choice, and does not write any client permission file

### Requirement: Behavior: Unlisted commands fall to the framework default
The deposited policy SHALL state that commands on neither list fall to the
framework's default judgement, with the sandbox making a wrong default
survivable, and that on a client whose default is to ask the remedy is a wider
allow list, not ask entries. It SHALL describe the deny list as protection
against a careless collaborator's mistakes, with the sandbox and tokens as the
real boundary. [§4.2.5]

#### Scenario: Deny list purpose stated
- **WHEN** a clean-context reader opens the deposited policy
- **THEN** it finds the deny list described as protection against a careless collaborator's mistakes, with the sandbox and tokens named as the real boundary, not as a defence against an attacker, and finds the statement that unlisted commands fall to the framework default and that an ask-by-default client calls for a wider allow list

#### Scenario: Unlisted command queried
- **WHEN** a clean-context reader of the deposited policy is asked whether an agent may run a command on neither list
- **THEN** the reader answers from the file alone that the framework's default decides, that the sandbox absorbs a wrong default, and that a recurring prompt for it is a reason to widen the allow list

### Requirement: Behavior: Irreversible outward commands never enter the allow list
The allow list SHALL contain no irreversible or outward command (push,
publish, release, tracker comment, label or state change, deletion of others'
work), however often the repository shows it in use; such commands are
pre-authorised in the plan or the spec or deferred to the pending decisions
list, and the policy SHALL say so. [§4.2.3]

#### Scenario: Push and release in daily use
- **WHEN** the git log and task runner show `git push` and a release command in daily use
- **THEN** the agent leaves them out of the proposed allow list and says they are governed by pre-authorisation, not by permission entries

#### Scenario: User asks to allow the push
- **WHEN** the user asks to add `git push` to the allow list so agents stop stalling
- **THEN** the agent explains once that the policy already lets a pre-authorised push proceed without a prompt and that an allow entry would also cover pushes nobody authorised, and records the user's choice if they keep it as a deviation

### Requirement: Behavior: Permission files are produced per confirmed client
Framework permission files SHALL be written only for clients the user
confirms. For Claude Code and Codex the agent SHALL produce the client's
permission configuration from the confirmed lists; for any other confirmed
client it SHALL record the policy alone and list that client's permission
configuration as a by-hand item in the closing report, with the entries to
transcribe.

#### Scenario: Claude Code and Codex confirmed
- **WHEN** the user confirms Claude Code and Codex as the project's clients
- **THEN** the project gains one permission configuration per client, each holding exactly the confirmed allow and deny entries and no ask entries

#### Scenario: Client without a shipped format
- **WHEN** the user confirms Antigravity as a client
- **THEN** the agent writes no permission file for it, and the report lists its permission configuration as a by-hand item naming the confirmed allow and deny entries

### Requirement: Behavior: Checkpoints are commits with task-level squashing
The deposited rules SHALL state that checkpoints are commits, never stashes or
session-only undo; that drafts inside a task are squashed non-interactively
into one commit per task when the task ends; that a non-atomic task is split
at the plan level, not by hunk; that drafts never leave the machine; that a
push names a single ref; and that "no draft commits on the branch" is part of
task completion. [§4.3]

#### Scenario: Squash rule stated
- **WHEN** a clean-context reader of the deposited rules is asked how an agent finishes a task that has three draft commits
- **THEN** the reader answers from the files alone: run the non-interactive recipe that resets softly to the task start and commits once under the project's message convention

#### Scenario: Stash suggested
- **WHEN** the user or an existing rule proposes stashing work before trying a different approach
- **THEN** the agent recommends committing a checkpoint instead, explains why stashes are the worst mechanism for agents, and the deposited rules say the same

#### Scenario: Remote CI needed for a draft
- **WHEN** a clean-context reader of the deposited rules is asked whether an agent may push unfinished work to get remote CI
- **THEN** the reader answers from the files alone that such a push is a publication passing the same gate as a real push and that the local fast validation loop comes first

### Requirement: Behavior: Rollback is a recipe, hard reset stays denied
A rollback recipe SHALL check that the working tree is clean or create a
checkpoint commit first, and the raw destructive command (`git reset --hard`,
`git clean -fd`) SHALL stay on the deny list; the precondition is guaranteed
by the recipe, not by a reminder. [§4.3]

#### Scenario: Failed approach discarded
- **WHEN** a clean-context reader of the deposited rules is asked how an agent discards a failed approach
- **THEN** the reader answers from the files alone: run the rollback recipe, which verifies a clean tree or commits a checkpoint before resetting, while `git reset --hard` itself remains denied

#### Scenario: Deny entry questioned
- **WHEN** the user asks why hard reset is denied if agents are expected to roll back
- **THEN** the agent answers that the deny entry protects uncommitted work and the recipe makes rollback safe by committing first, and keeps both

### Requirement: Behavior: Commit convention is confirmed and AI attribution is forbidden
The skill SHALL confirm the commit-message convention, recommending
Conventional Commits and offering plain 50/72 titles without a type prefix,
unless the repository's history already shows one in use, in which case it
SHALL record that convention without proposing another. The deposited rules
SHALL forbid AI attribution (co-author trailers, tool names, model names) in
commit messages. [§4.3]

#### Scenario: Convention observable in history
- **WHEN** the git log shows unprefixed 50/72 titles
- **THEN** the agent records that convention, does not propose Conventional Commits, and the deposited rules state that commits carry no AI attribution

#### Scenario: No convention observable
- **WHEN** the repository has few commits and no consistent title style
- **THEN** the agent asks which convention to adopt, recommending Conventional Commits with its reason and offering plain 50/72, and writes the recipes only after the answer

#### Scenario: Attribution requested
- **WHEN** the user asks for a co-author trailer naming the agent on every commit
- **THEN** the agent says once that the methodology forbids AI attribution, and records the user's choice as a deviation if they keep it

### Requirement: Behavior: Deposited recipes and permission files belong to the target
The checkpoint recipes and permission files written into the target SHALL be
reworked against project facts and written in the task runner and language the
user agreed to, SHALL never call into a skill directory, and the agent SHALL
tell the user that later plugin fixes do not reach the delivered copy. The
shipped recipes are a reference implementation, not a file to copy.

#### Scenario: Project uses another task runner
- **WHEN** the project uses make rather than just
- **THEN** the agent asks before translating the recipes into make targets and delivers none in just syntax

#### Scenario: Recipes deposited
- **WHEN** the recipes land in the project's task runner
- **THEN** the agent runs each once and reports the output, and tells the user that the project owns the copy and later plugin fixes do not reach it

### Requirement: Behavior: Deposited authority knowledge and entry route
After the user approves the plan for this layer, the agent SHALL deposit one
authority knowledge file whose first line states when to read it and SHALL add
a route to it, with that load condition, in the project's agent entrypoint.
When the route would exceed the entrypoint budget the agent SHALL add it,
report the overrun to the layer owning knowledge and routing, and SHALL NOT
trim other routes itself. Before approval it SHALL write nothing.

#### Scenario: Knowledge file deposited
- **WHEN** the user approves the authority plan at the medium grade or above
- **THEN** the project gains one authority knowledge file opening with a "Read this when..." line, and the entrypoint routes to it with a load condition naming pushes, outward actions, and refusals

#### Scenario: Entrypoint has no room
- **WHEN** adding the route would push the entrypoint past its line budget
- **THEN** the agent adds the route, reports the budget overrun as a finding for the knowledge and routing layer, and does not trim other routes itself

#### Scenario: Inspection before approval
- **WHEN** the agent is still gathering the project's commands and existing rules
- **THEN** it reads and reports only and creates no file in the target project

### Requirement: Behavior: Concurrency is asked with single-agent as the default
The skill SHALL ask whether several agents will work concurrently,
recommending single-agent operation unless the repository shows evidence of
parallel agents (several agent worktrees or per-agent remote branches), and
SHALL write any parallel-agent rule only when the user confirms concurrency;
otherwise the policy SHALL record single-agent operation. [§4.4]

#### Scenario: Concurrency not in scope
- **WHEN** the user confirms that one agent works at a time
- **THEN** the deposited policy records single-agent operation and contains no parallel-agent rule

#### Scenario: No evidence of parallel agents
- **WHEN** the repository shows one worktree and no per-agent branches
- **THEN** the agent asks about concurrency with single-agent operation as the recommended answer and its reason

#### Scenario: Evidence of parallel agents
- **WHEN** the repository shows several agent worktrees and per-agent remote branches
- **THEN** the agent asks about concurrency with parallel operation as the recommended answer and the evidence for it

### Requirement: Behavior: Parallel-agent rules stay with the platform layer
When concurrency is confirmed, the policy SHALL state only the authority-side
rule (every platform write by a parallel agent is outward and irreversible, so
it is pre-authorised or deferred) and SHALL point to the platform knowledge
for branch-ownership, coordinator, merger, and arbiter rules without restating
them; the agent SHALL hand those rules to the layer owning the platform
lifecycle by description. [§4.4]

#### Scenario: Concurrency confirmed
- **WHEN** the user confirms parallel agents on the same repository
- **THEN** the deposited policy states that each parallel agent's platform writes are pre-authorised or deferred, points to the platform knowledge for branch ownership, coordinator, merger, and arbiter, restates none of them, and the agent describes those rules as a need for the layer owning the platform lifecycle without naming a skill

#### Scenario: Existing policy restates the branch rules
- **WHEN** the project's existing authority policy already carries one-branch-per-agent and coordinator rules and the platform knowledge carries them too
- **THEN** the agent reports the duplicate, recommends keeping the platform knowledge as the single source and replacing the policy's copy with a pointer, and changes nothing until the user chooses

### Requirement: Behavior: Pairing mode is a scoped exception
The deposited policy SHALL recognise step-by-step approval as legitimate only
during bootstrap and specification phases or in projects requiring high
alignment such as strict security or per-line accountability, SHALL state when
the project switches back to two-ended approval, and SHALL note that approval
fatigue applies in pairing mode too. [§4.2.6]

#### Scenario: Bootstrap phase
- **WHEN** the project is still establishing its specifications with the user present
- **THEN** the policy records pairing mode for that phase and the condition on which the project switches to two-ended approval

#### Scenario: Pairing requested for a routine project
- **WHEN** the user asks for pairing mode in a mature project with no alignment constraint
- **THEN** the agent states once that this is outside the two legitimate sources and records the choice if the user keeps it

### Requirement: Behavior: The policy protects itself and is maintained by ask rate
The deposited policy SHALL live in a file agents read on every session, SHALL
state that loosening the policy file, the permission lists, or the security
hooks is outside any agent's authority, even to unblock the current task, and
SHALL carry a maintenance rule: when harness improvements are made, an ask
category approved near 100% of the time moves to allow, and an allowed command
that repeatedly caused rollbacks is tightened; no standing metric is kept.
[§4.2.7]

#### Scenario: Rule in the way
- **WHEN** a clean-context reader of the deposited policy is asked what an agent does when a rule blocks its current task
- **THEN** the reader answers from the file alone: do not edit the rule; propose the change with its reason and wait

#### Scenario: Deny entry blocks legitimate work
- **WHEN** a clean-context reader of the deposited policy is asked what an agent does when a denied command turns out to be required by the approved plan
- **THEN** the reader answers from the file alone: propose a policy change with its reason and wait, never work around the entry

#### Scenario: Ask category always approved
- **WHEN** during a harness improvement the user reports that a prompt category was always approved
- **THEN** the agent recommends moving that category to the allow list and presents it as a recommendation for the user to confirm

#### Scenario: Standing dashboard requested
- **WHEN** the user asks for a permanent metric on approval rates
- **THEN** the agent recommends a one-time review at improvement time instead and explains why a standing metric is cost without benefit

### Requirement: Behavior: Decisions are confirmed and recommendations are not decisions
The skill SHALL settle from the repository only what it can observe there,
SHALL ask the user about every other decision with one recommended option and
its reason, SHALL write nothing into the target project before the plan
naming the files is approved, and SHALL route adjacent work by describing the
layer that owns it, never by naming a skill.

#### Scenario: Existing authority rules contradict the recommendation
- **WHEN** the project already has permission files with ask entries and a policy allowing force pushes
- **THEN** the agent reports the contradiction with the methodology, recommends the fix once, and leaves the existing rules unchanged if the user keeps them

#### Scenario: Hook protection needed
- **WHEN** the policy names security hooks as protected
- **THEN** the agent describes the need to the layer owning pre-commit and CI checks and to the layer owning platform settings, without naming any skill

#### Scenario: Observable fact not asked
- **WHEN** the repository's task runner, test command, and secret-scanning hook are visible in its files
- **THEN** the agent uses them as evidence without asking and asks only about what the repository does not show

### Requirement: Outcomes
Given a target project and the user's confirmations, the agent SHALL leave,
at the confirmed grade, an authority policy reachable from the project's agent
entrypoint, the permission files for the confirmed clients, and checkpoint
recipes in the agreed task runner, and a clean-context reader SHALL be able to
state the rules from those files alone.

#### Scenario: Single-agent project on Claude Code
- **WHEN** the user runs the skill on a repository with a task runner and Conventional Commits in its history, confirms the medium grade, single-agent operation, and Claude Code as the only client, accepts the fixed deny list, confirms an allow list from the observed commands, and declines ask entries
- **THEN** the project gains a policy file linked from its entrypoint that states the reversibility classes, two-ended approval, the pending decisions format, the two refusal responses and the prohibition on routing around, checkpoint rules with no AI attribution, the framework-default statement, and self-protection; a Claude Code permission file with exactly the confirmed allow and deny entries, no ask entries, and no push or publish command; checkpoint and rollback recipes in the task runner; and a clean-context reader can answer whether an agent may push, squash, roll back, or edit the policy from these files alone

#### Scenario: Concurrent agents with existing contradicting rules
- **WHEN** the user runs the skill on a project whose existing permission file allows `git push --force`, confirms that two agents work in parallel, and accepts the recommendation to remove the force-push allowance
- **THEN** the permission file no longer allows force pushes, the policy states that every parallel agent's platform write is pre-authorised or deferred and points to the platform knowledge for branch ownership and coordination without restating it, and the report lists every changed file, any decision the user deferred in the pending decisions format, and the need to block force pushes on the remote, described to the layer owning platform settings without naming a skill

#### Scenario: Light grade on a make project
- **WHEN** the user runs the skill on a short-lived prototype using make, confirms the light grade, and confirms an allow list of its build and test targets
- **THEN** the project gains permission entries holding exactly the confirmed allow entries and the fixed deny list, one entrypoint sentence stating that unlisted commands fall to the framework default, checkpoint recipes as make targets after the user agreed to the translation, and no separate policy document

#### Scenario: User keeps the per-command mode
- **WHEN** the user asks for per-command approval on a mature project and keeps that choice after one challenge
- **THEN** the deposited policy records per-command approval as the user's explicit choice with its stated reason, the deny list and checkpoint rules are still present, and the agent's closing report names the choice as a deviation from the methodology
