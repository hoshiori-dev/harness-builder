# Spec Delta

## Purpose

Governs what an agent that loaded the `spec-driven-development` skill observably does when it decides whether a project works spec-first and when it runs a change through the specify-to-freeze loop: the completion answers and quality rules every specification carries, the approval package that precedes tasks and code, the project rules it takes from the specification contract or asks for when absent, and how tool work is handed to a carrier skill. Ships to Claude Code, Codex, and Antigravity; non-goals: recording a project's spec rules (the specification and completion layer builder), running a spec tool's commands or automation (the carrier skills), defining a project's goals, and building platform forms or CI. Terms used below: the approver is the person the contract names to approve a gate (the user by default); a review is the discussion of a package or an implementation and closes when the approver says so; the change record is the change's specification, design, and task files wherever the carrier keeps them.

## ADDED Requirements

### Requirement: Triggering
The skill SHALL load from its description for requests to decide whether or at which level a project adopts spec-driven development, to work spec-first, to run or explain the specify-to-freeze loop, to judge what a specification must answer or where approval sits, or to bring existing code under the discipline; it SHALL NOT load for building a project's spec rules or harness, for a tool's own change command, or for platform intake and CI work.

#### Scenario: Spec-first request for a feature
- **WHEN** the user says "write the spec first for the CSV export, then we'll implement"
- **THEN** the skill loads

#### Scenario: Question about the approval boundary
- **WHEN** the user asks "should the design be approved before we write the task list, or after?"
- **THEN** the skill loads

#### Scenario: Adoption question
- **WHEN** the user asks "is writing specs first worth it for a two-week prototype?"
- **THEN** the skill loads

#### Scenario: Prototype entering the discipline
- **WHEN** the user says "this app was vibe-coded over a weekend; how do we get it under written specs and approvals before we add features, without rewriting it?"
- **THEN** the skill loads

#### Scenario: Drift between spec and code
- **WHEN** the user says "what we shipped no longer matches what the spec says; what do we do first?"
- **THEN** the skill loads

#### Scenario: Harness build request
- **WHEN** the user says "set up our spec workflow: choose OpenSpec or Spec-Kit, write the contract, add the CI check"
- **THEN** the skill does not load (the specification and completion layer builder does)

#### Scenario: Tool command request
- **WHEN** the user says "create a new OpenSpec change called export-csv and validate it"
- **THEN** the skill does not load (the carrier skill does)

#### Scenario: Platform intake request
- **WHEN** the user says "add issue forms and a PR template so every spec change is labelled"
- **THEN** the skill does not load

### Requirement: Behavior: Adoption and level are recommended, never decided
Asked whether or at which level a project adopts spec-driven development, the agent SHALL recommend one answer with the fact that selects it and the alternative in one sentence, SHALL wait for the user's choice, and SHALL route recording the choice as a project rule to the specification and completion layer builder by role; it SHALL recommend spec-anchored when the project is maintained past one release and spec-first otherwise, and SHALL NOT answer that specs are never worth it.

#### Scenario: Short-lived prototype
- **WHEN** the user asks whether writing specs first is worth it for a prototype to be thrown away in two weeks
- **THEN** the agent recommends spec-first at the lightest carrier, names the two-week horizon as the selecting fact, names spec-anchored as the alternative, and asks before treating either as decided

#### Scenario: Long-lived library
- **WHEN** the user says the library will be maintained for years and asks how strictly to adopt the discipline
- **THEN** the agent recommends spec-anchored with the horizon as its reason, and when the user agrees describes the layer builder that records the rule rather than editing the project's knowledge files itself

#### Scenario: User declines the recorded rule
- **WHEN** the user chooses a level but declines to have it recorded in the project
- **THEN** the agent runs the current change at the chosen level and lists the unrecorded rule in the pending decisions list

### Requirement: Behavior: The loop runs in eight ordered steps with checkable boundaries
The agent SHALL run every change through specify, clarify, pre-authorise and publish the package, reconcile then tasks, implement, verify, publish ready, freeze, in that order, and SHALL NOT start a step whose predecessor's completion condition is unmet; when asked to skip ahead it SHALL name the unmet condition and the step it belongs to.

#### Scenario: Tasks requested before the package is approved
- **WHEN** the specification and design are written and the user asks for the task list next
- **THEN** the agent declines, says the task list follows the approved package, and publishes or confirms the package instead

#### Scenario: Code requested before the specification
- **WHEN** the user says "just start coding the export, we'll write the spec after"
- **THEN** the agent says the specification comes first, names the anchoring risk of code written before agreement, and offers to write the specification now

#### Scenario: Loop step completed
- **WHEN** the agent finishes any step
- **THEN** it states which step is done, the condition that makes it done, and the next step

### Requirement: Behavior: Specify answers the four completion questions
The specification the agent writes SHALL answer, for this change only: what proves it is done (acceptance scenarios or a final verification command the agent itself can run, including task-level closure such as no draft commits on the branch), what is explicitly not done, what is delivered (a request, a report, a deployment, plus the pending decisions list), and which irreversible actions are proposed for pre-authorisation, to be settled in step 3.

#### Scenario: Specification drafted
- **WHEN** the agent writes the specification for a change
- **THEN** it carries acceptance scenarios the agent can execute, a non-goals list, a deliverable statement, and a pre-authorised irreversible actions section, each present even when its content is "none"

#### Scenario: Acceptance the agent cannot run
- **WHEN** the only acceptance offered is "the product owner is happy with it"
- **THEN** the agent asks for an observable check it can execute and does not treat the specification as complete until one exists

### Requirement: Behavior: Clarify confirms rather than guesses
During clarify the agent SHALL settle from the repository what can be observed there, SHALL ask the user about everything else where two readings lead to different work, and SHALL record each answer in the specification rather than only in the conversation; the step is done when no clarification marker (a `[NEEDS CLARIFICATION]` or equivalent open-question mark in the specification) remains.

#### Scenario: Ambiguity with two readings
- **WHEN** a requirement could mean either soft-deleting or hard-deleting records
- **THEN** the agent asks the user which is meant, with a recommendation and its reason, and writes the answer into the specification

#### Scenario: Fact observable in the repository
- **WHEN** the question is which test runner the project uses and the repository shows one configured
- **THEN** the agent takes the answer from the repository and does not ask

#### Scenario: Marker left open
- **WHEN** the user asks to publish while a requirement still carries a clarification marker
- **THEN** the agent names the marker and settles it before publishing

### Requirement: Behavior: The approval package pre-authorises irreversible actions and precedes tasks and code
In step 3 the agent SHALL settle with the user the list of irreversible actions this change pre-authorises (push target, opening a request, comments, deployments), and SHALL publish the package wherever the contract places review (the request's first content, or the conversation when the carrier approves conversationally): the specification, that list, and a design when warranted. Only the approved package authorises those actions; the review covers outcome and bounds, never the task list.

#### Scenario: Package approved with an empty pre-authorised list
- **WHEN** the user approves a package whose pre-authorised irreversible actions section says "none" and implementation later reaches the push
- **THEN** the agent does not push, finishes every local step, and adds the push to the pending decisions list with what is blocked and why, the options, the recommended option and its reason, and the finished work each option would change, presented once at the end

#### Scenario: Irreversible action not pre-authorised
- **WHEN** implementation reaches an action the approved package did not list, such as opening a pull request or posting a comment
- **THEN** the agent does not perform it, continues with every step that does not depend on it, and adds the action to the pending decisions list with what is blocked and why, the options, the recommended option and its reason, and the finished work each option would change, presented once

#### Scenario: Package published in the conversation
- **WHEN** the contract names plan mode or a conversational carrier with no request
- **THEN** the agent presents the specification, the pre-authorised list, and any design in the conversation and waits for the approver's explicit approval before writing tasks

### Requirement: Behavior: A design bounds the approach and never lists steps
The agent SHALL add a design to the package when more than one reasonable approach exists, when structure, interfaces, dependencies, or files outside the change record are touched, or when the contract requires one; the design SHALL record approach, constraints, preferences, and rejected alternatives, SHALL contain no implementation steps, and SHALL carry no credential, internal hostname, or personal data.

#### Scenario: Design written as a procedure
- **WHEN** the design reads as numbered implementation steps
- **THEN** the agent rewrites it as bounds before publishing and says steps belong to the task list after approval

#### Scenario: Wording-only change
- **WHEN** the change edits one section's wording and the contract requires no design
- **THEN** the agent says no design is warranted and publishes the specification and the pre-authorised list alone as the package

#### Scenario: Constraint carrying a private detail
- **WHEN** a technical constraint involves a credential, an internal hostname, or a person's private data
- **THEN** the agent records the constraint without the private detail, because the package is committed and published

### Requirement: Behavior: Reconcile closes the gate before tasks are written
When the approver closes the package review, the agent SHALL read the review record (the request's discussion and review threads with their resolution state, or the conversation when the carrier approves conversationally), list every unresolved point, every requested adjustment the package does not carry, and every pair of contradicting conclusions, ask the approver to confirm the open items, record the closing, and only then write ordered tasks each tied to the scenarios it closes.

#### Scenario: Nothing open at closing
- **WHEN** every review thread is resolved and every requested adjustment is in the package
- **THEN** the agent records the closing and writes the task list, with no task lacking a scenario and no scenario lacking a task

#### Scenario: Requested adjustment missing from the record
- **WHEN** a review comment asked for a scenario to change and the package still carries the old one at closing
- **THEN** the agent names the gap, updates the change record or asks whether the request was withdrawn, and writes no tasks until it is settled

#### Scenario: Tool-generated task list
- **WHEN** the carrier tool produced a task list together with the specification
- **THEN** the agent keeps it out of the package review, marks it as after-approval material, and finishes it only after the closing

#### Scenario: Conversational review
- **WHEN** the package was approved in the conversation with two adjustments requested along the way
- **THEN** the agent confirms both adjustments are in the specification before writing tasks, and names any that is not

### Requirement: Behavior: Implementation deviations change the record first
While implementing, the agent SHALL work task by task, SHALL commit a checkpoint when a task's scenarios pass, and when the code must depart from the specification or the design SHALL stop, propose the change-record change, obtain the user's approval, and update the change record before continuing.

#### Scenario: Code needs to deviate
- **WHEN** a task cannot be completed as specified because an assumed API does not exist
- **THEN** the agent stops, proposes the specification or design change with its reason, and continues only after the user approves and the change record is updated

#### Scenario: Task scenarios pass
- **WHEN** the scenarios tied to a task pass
- **THEN** the agent commits that task as a checkpoint before starting the next one

### Requirement: Behavior: Verification runs the scenarios against the result, not the diff
The agent SHALL verify by executing each scenario (tests, commands, observed states) against the running result, SHALL NOT report a scenario as passed from reading the diff, and SHALL end verification with every scenario passed, recorded as an approved specification change, or filed as a separate defect; a failure in behavior the change does not touch is filed, not absorbed.

#### Scenario: Scenario judged from the diff
- **WHEN** the user asks "the diff looks right, can we call the scenarios passed?"
- **THEN** the agent declines, runs each scenario, and reports each result individually

#### Scenario: Failure outside the change
- **WHEN** a scenario fails because of behavior the change does not touch
- **THEN** the agent files it as a separate defect with the evidence, narrows the change record to what is verified, and does not widen the change silently

#### Scenario: Verification command unavailable
- **WHEN** the acceptance command named in the specification does not exist in the environment
- **THEN** the agent reports the scenario as not verifiable, says what is missing, and does not mark it passed

### Requirement: Behavior: Publish ready, then freeze where the carrier records it
After verification the agent SHALL publish the implementation for review against the approved package (request marked ready, or the result presented in the conversation); when the approver closes that review it SHALL reconcile as at the first gate, then freeze the change record where the carrier records it (archive, write-back, or fold or delete of a per-change file) when the contract names the agent as freeze executor, and otherwise report the record ready to freeze and name the person.

#### Scenario: Asked to freeze and request approval in one step
- **WHEN** the implementation is finished and the user asks to archive and ask for approval together
- **THEN** the agent publishes the implementation for review first, freezes nothing, and says the freeze comes after that review closes

#### Scenario: Agent is the freeze executor
- **WHEN** the contract names the implementer as freeze executor and the implementation review closes
- **THEN** the agent freezes the change record on the branch through the carrier, validates, and commits

#### Scenario: A person is the freeze executor
- **WHEN** the contract names a maintainer as freeze executor or the branch belongs to a fork
- **THEN** the agent freezes nothing, reports the change record ready to freeze, and names the person and the step they run

#### Scenario: Plan-mode carrier at freeze
- **WHEN** the carrier is plan mode or a per-change file approved in the conversation and the change is accepted
- **THEN** the agent performs no second freeze step beyond the carrier's fold or delete, and confirms with the user that the approved specification is the frozen record

### Requirement: Behavior: A freeze is spent by later commits and never edited
A commit after the freeze commit SHALL be named as making the freeze stale before any push or handover, and a frozen change record SHALL NOT be edited; when an error is found in it the agent SHALL recommend a follow-up change when the frozen behaviour is wrong and a validation note on the request when only the record's text is wrong, and SHALL confirm with the user before acting.

#### Scenario: Commit after the freeze
- **WHEN** the agent is about to push or hand over and a commit exists after the freeze commit
- **THEN** it says the freeze is stale, names the commits, and asks whether the review reopens

#### Scenario: Defect found after the freeze
- **WHEN** review finds that a frozen record describes behaviour the code does not have
- **THEN** the agent recommends a follow-up change with its reason, names the validation note as the alternative for a text-only error, and does not edit the frozen record

### Requirement: Behavior: Specification quality rules are applied to every record
The agent SHALL write and review specifications so that every goal has at least one scenario a reader who has never seen the code can judge, at least one scenario covers a failure or edge path, non-goals are written down, behavior is described and never the diff, and verification is defined against runs; it SHALL correct a draft that breaks a rule and name the rule.

#### Scenario: Implementation written as a requirement
- **WHEN** a draft requirement says "add a unique index on email"
- **THEN** the agent rewrites it as observable behavior such as a duplicate email being rejected, and says the index is a design decision

#### Scenario: Requirement without a failure path
- **WHEN** every scenario in a draft covers the success path
- **THEN** the agent adds or requests at least one failure or edge scenario before the package is published

#### Scenario: Compound requirement
- **WHEN** one requirement carries two normative statements
- **THEN** the agent splits it into two requirements, each with its own scenarios

### Requirement: Behavior: Project rules come from the contract, asked once when absent
The agent SHALL apply precedence of an explicit user instruction, then the project's specification contract, then the defaults below, for level, carrier, request shape, approval mode, design rule, freeze executor, and spec scope; it SHALL re-ask nothing the contract states, and where the contract is silent on a point that changes the work it SHALL ask once, batched, each point with its default as the recommended option and its reason, and SHALL NOT choose silently.

#### Scenario: Contract present
- **WHEN** the project's knowledge base carries a specification contract and the user starts a change
- **THEN** the agent applies its facts, says which file stated them, and re-asks none of them

#### Scenario: No contract
- **WHEN** the project has no specification contract and the user asks what happens after the draft is published
- **THEN** the agent asks one batched question covering the silent points, each with the default recommended and its reason, proceeds on the answers, and names the specification and completion layer builder by role as the way to record them

#### Scenario: Contract contradicts a default
- **WHEN** the contract records a recorded-approval mode and the user asks to proceed on a conversational closing alone
- **THEN** the agent names the contract's recorded mode, asks the user to confirm overriding it for this change with following the contract as the recommendation, and proceeds on the user's answer

#### Scenario: Domain requested for tooling
- **WHEN** the user asks for a spec domain covering the build scripts
- **THEN** the agent declines, says domains describe the product, and offers the carrier's spec-less change kind for harness work

### Requirement: Behavior: Declared defaults for the silent points
The recommended defaults SHALL be: level spec-first, or spec-anchored when maintenance past one release is observable; carrier the one in use, else the lightweight one (per-change file or plan mode); request shape combined (specification and implementation in one request), or none when approval is conversational; approval conversational on the complete package; design per the design requirement; freeze executor the implementer (a person on a fork); scope the product, harness changes spec-less.

#### Scenario: Defaults stated in the reply
- **WHEN** the agent runs a change in a project with no contract after the user accepts every recommendation
- **THEN** its reply lists each default it applies and states that these are defaults, not project rules

#### Scenario: Maintenance horizon observable
- **WHEN** the repository shows tagged releases spanning more than one release cycle
- **THEN** the agent recommends spec-anchored and cites the release history as the selecting fact

#### Scenario: No request shape
- **WHEN** the project has no contract, no spec tool, and the user approves the package in the conversation
- **THEN** the loop runs with both reviews closed in the conversation, no draft request is required, and the freeze is the carrier's fold or delete of the per-change file

### Requirement: Behavior: Tool work is handed to the carrier skill by description
When the project runs a specification tool the agent SHALL route creating, validating, archiving, and the request automation to the carrier skill for that tool; with no tool in use it SHALL route per-change file or plan-mode work to the lightweight carrier skill; each by role, never by an install command or another library. When no carrier is available it SHALL run the loop with commands verified from the tool's own help, create no tool directory by hand, and say the automation is not installed.

#### Scenario: Carrier available
- **WHEN** the project runs OpenSpec and the user asks how to archive the change in the pull request
- **THEN** the agent hands the step to the OpenSpec carrier skill by role and prints no install command

#### Scenario: No tool in use
- **WHEN** the project has no spec tool and the user wants the specification written down before coding
- **THEN** the agent hands the per-change file or plan-mode choice to the lightweight carrier skill by role

#### Scenario: Carrier unavailable
- **WHEN** no carrier skill for the project's tool is available
- **THEN** the agent reads the tool's help, runs the needed command itself, and says the request automation is not installed

#### Scenario: Hand-written record offered
- **WHEN** the user asks the agent to write the change directory and metadata by hand because it is faster
- **THEN** the agent declines, names the metadata the tool's command produces, and creates the record through the command

### Requirement: Behavior: Existing code enters the discipline without backfilling
When the project already contains code not written from a specification, the agent SHALL specify only the behavior the next change touches, SHALL observe actual behavior by running the software rather than inferring it from code, SHALL ask the user to rule on each unexplained behavior (requirement, non-goal, or defect) rather than promoting it, and SHALL refuse to write specifications for code nobody is changing.

#### Scenario: Full backfill requested
- **WHEN** the user asks to write specs for the whole existing codebase before any change
- **THEN** the agent declines, explains that specs for untouched code rot immediately, and offers to specify the next change plus an as-built map that claims no requirement

#### Scenario: Unexplained prototype behavior
- **WHEN** the running prototype exhibits behavior no document explains
- **THEN** the agent lists it and asks the user whether it is a requirement, a non-goal, or a defect, without deciding on its own

#### Scenario: Spec and code disagree
- **WHEN** an existing specification contradicts what the code does
- **THEN** the agent says the specification is an active source of falsehood, and fixes or deletes it with the user's decision before other work

### Requirement: Outcomes
Given an end-to-end task, the agent that loaded the skill SHALL produce a specification carrying the four completion answers, a package approved before tasks, verification run against the result, and a freeze where the carrier records it, with every decision confirmed with the user and every unauthorised irreversible action listed as pending.

#### Scenario: Feature added to a project with a contract
- **WHEN** the user asks, in a repository whose contract names OpenSpec, conversational gates, and the implementer as freeze executor, to "add rate limiting to the public API, spec first"
- **THEN** the result is a change record with requirements, failure scenarios, non-goals, a deliverable, and pre-authorised actions; a draft request carrying only the package; tasks written only after the user closes the review; each scenario executed with its result reported; and the record archived in the request after the second closing, with no push the approved package did not authorise

#### Scenario: Change in a project without a contract
- **WHEN** the user asks, in a repository with no specification contract and no spec tool, to "do the password-reset flow spec first"
- **THEN** the agent asks one batched question with the defaults recommended, names the layer builder by role, hands the per-change file or plan-mode choice to the lightweight carrier by role, writes a specification with the four completion answers and at least one failure scenario, has it approved in the conversation before any task or code, verifies by running the scenarios, and lists any irreversible action it did not perform as a pending decision

#### Scenario: Prototype handed over
- **WHEN** the user asks to "bring this weekend prototype under specs and add login"
- **THEN** the agent runs the prototype, asks the user to rule on each unexplained behavior, writes a specification only for the login change, produces an as-built map that claims no requirement, and writes no specification for untouched modules
