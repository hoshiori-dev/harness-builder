# Spec Delta

## Purpose

Governs what an agent that loaded `platform-lifecycle-building` observably does, for Claude Code, Codex, and Antigravity, when it builds, repairs, or thins the platform lifecycle layer of a target project hosted on GitHub or GitLab: the minimal set of labels, forms, and templates, the branching model and allowed merge methods, the remote settings register, the project skill agents follow for every issue, pull request, or merge request, and the remote writes that put those in place. Non-goals: choosing the specification carrier or its approval gates (the builder owning the specification and completion layer fills the insertion markers this skill leaves), CI checks and secret scanning (the hard-boundary layer), permission lists and the authority policy (the authority layer), hosting platforms other than GitHub and GitLab, infrastructure-as-code for platform settings, and running a single issue or pull request operation in a project whose lifecycle already exists.

## ADDED Requirements

### Requirement: Triggering
The skill SHALL load when a user asks to design, set up, rebuild, migrate, or thin a repository's lifecycle on GitHub or GitLab (labels, issue forms, templates, branching, merge rules, rulesets or protected branches, the agents' issue-to-merge workflow) and SHALL NOT load for a single operation on an existing issue, pull request, label, or release, for CI job authoring, or for git operations that touch no platform object.

#### Scenario: Whole lifecycle on GitHub
- **WHEN** the user says "Set up how work flows through this GitHub repo: labels, issue forms, a PR template, branch rules, and what agents do from taking an issue to merging"
- **THEN** the skill loads

#### Scenario: Migration between platforms
- **WHEN** the user says "We are moving this project from GitHub to our self-hosted GitLab; rebuild the merge request templates, labels, and protected branch rules there"
- **THEN** the skill loads

#### Scenario: Thinning an over-built lifecycle
- **WHEN** the user says "Our repo has forty labels, three milestones nobody updates, and a Projects board; cut this down to what agents and reviewers actually use"
- **THEN** the skill loads

#### Scenario: Merge policy decision
- **WHEN** the user says "Should agents open PRs against main directly or should we use develop and release branches? Decide and configure the merge settings"
- **THEN** the skill loads

#### Scenario: One label added
- **WHEN** the user says "Add a `needs-triage` label to this repository"
- **THEN** the skill does not load

#### Scenario: One pull request handled
- **WHEN** the user says "Open a PR for the branch I just pushed and request a review from the backend team"
- **THEN** the skill does not load

#### Scenario: CI job authored
- **WHEN** the user says "Write a GitHub Actions workflow that runs pytest on every pull request"
- **THEN** the skill does not load

#### Scenario: Local git question
- **WHEN** the user says "Squash my last four commits into one before I push"
- **THEN** the skill does not load

### Requirement: Behavior: Read-only probe before any question
Before asking the user anything, the agent SHALL run the shipped platform probe against the target's remote and SHALL ask only for what the probe and the repository cannot show: intent, team size, governance. Owner type, plan tier, and visibility SHALL be evidenced separately and never assumed from one another. A missing or unauthenticated CLI SHALL stop the probe with the missing piece named, never a guessed inventory.

#### Scenario: Authenticated GitHub remote
- **WHEN** the target's `origin` is a GitHub repository and `gh` is authenticated
- **THEN** the agent reports owner type, plan, visibility, existing labels, rulesets or branch protections, and templates before its first question, and does not ask the user for any of those facts

#### Scenario: CLI absent
- **WHEN** neither `gh` nor `glab` is installed, or the installed one is not logged in
- **THEN** the agent names the missing tool (`gh` or `glab`) or the login command (`gh auth login` / `glab auth login`), leaves installation to the user, writes no file, and asks whether to continue with the user supplying the remote facts or to stop

#### Scenario: Personal account on a free plan
- **WHEN** the probe shows a personal-account owner on a free plan with a private repository
- **THEN** the agent names which proposed settings that combination cannot enforce (such as rulesets on private repositories) before proposing them, and records each as a convention with its owner instead of silently dropping it

### Requirement: Behavior: Minimal entity set and the deletion test
The agent SHALL recommend the minimal entity set as its starting point: `type:` and `area:` labels plus the reserved `spec:` namespace, bug / feature / task issue forms, one pull or merge request template, and no Projects, boards, or Milestones. Every entity beyond it SHALL pass the deletion test, stated to the user as what management ability is lost without it, before it is created. [§6.2]

#### Scenario: Entity set proposed
- **WHEN** the agent reaches the entity decision for a repository with no labels or templates
- **THEN** it presents the minimal set as the recommendation, lists Projects and Milestones among objects deliberately not created, and asks the user to confirm or extend

#### Scenario: Extra entity requested
- **WHEN** the user asks for `priority:` labels in addition to the minimal set
- **THEN** the agent asks what would be lost without them, records the answer beside the labels, and adds them only after the user confirms

#### Scenario: Existing surplus
- **WHEN** the probe finds labels, milestones, or a board that no open item uses
- **THEN** the agent lists each with the deletion test applied and proposes removal as a separate decision, deleting nothing without the user's explicit yes

### Requirement: Behavior: One committed label file is the label source
The committed label file this layer deposits SHALL be the project's single label definition: the specification carrier adds its concrete `spec:*` rows to that file and keeps no parallel label file, the delivered sync reads only that file, and pruning SHALL never be the default, so no sync deletes labels another step defined.

#### Scenario: Carrier labels added later
- **WHEN** the specification carrier is installed after this layer and needs `spec:pending`, `spec:approved`, and `spec:archived`
- **THEN** the deposited knowledge directs it to append those rows to the existing label file, and the next label sync creates them from that file with no second file and no second sync

#### Scenario: Second label file found
- **WHEN** the probe finds two label definition files in the target
- **THEN** the agent shows both, recommends merging them into the one the sync reads, and runs no sync with `--prune` until one file remains

### Requirement: Behavior: Branching model recommended from evidence
The agent SHALL recommend GitHub Flow (short-lived branches off the default branch, merged through a pull or merge request) for a new project, SHALL propose a GitLab Flow variant only on evidence of environment branches or release maintenance, and SHALL never propose git-flow for a project that does not already use it.

#### Scenario: New repository
- **WHEN** the target has one branch and no release history
- **THEN** the agent recommends GitHub Flow with its reason, names the GitLab Flow variants as alternatives in a sentence each, and waits for the choice

#### Scenario: Environment branches in use
- **WHEN** the probe shows `staging` and `production` branches with deployments attached
- **THEN** the agent recommends the GitLab Flow environment-branch variant and records the evidence it relied on

#### Scenario: Existing git-flow
- **WHEN** the target already uses `develop` and `release/*` branches
- **THEN** the agent keeps git-flow unless the user asks to change it, and states once that it does not recommend git-flow for new work

### Requirement: Behavior: Tag-triggered releases recommended
The agent SHALL recommend releases triggered by pushing a version tag and SHALL recommend against a release-management bot, naming the bot alternative in a sentence, and SHALL configure no release automation until the user has chosen.

#### Scenario: Release automation asked
- **WHEN** the user asks how releases should be cut
- **THEN** the agent recommends a tag-triggered release workflow with its reason, names a release-management bot as the alternative in one sentence, and writes nothing until the user picks one

#### Scenario: Bot chosen
- **WHEN** the user chooses the release-management bot
- **THEN** the agent challenges the choice once with its reason, then records the choice and plans the bot's configuration as the user's decision

### Requirement: Behavior: Merge methods are asked, squash-only recommended
The agent SHALL ask which merge methods the repository allows and the rule for each, SHALL recommend allowing squash only, and SHALL apply the answer both to the remote setting and to the deposited knowledge so agents and the platform enforce the same rule.

#### Scenario: User accepts the recommendation
- **WHEN** the user accepts squash-only
- **THEN** the planned remote change disables merge commits and rebase merging, and the deposited knowledge says the pull request title becomes the squashed commit message and must follow the project's commit convention

#### Scenario: User allows several methods
- **WHEN** the user allows squash and rebase
- **THEN** the agent asks for the rule that picks one per change (for example rebase only when every commit is task-level), records it, and proposes no setting the rule does not need

### Requirement: Behavior: Default-branch protection recommended
The agent SHALL recommend protecting the default branch so changes land only through pull or merge requests with force pushes and deletion refused, SHALL propose a required check only after that check has run green on the default branch, and where the probed plan and visibility cannot enforce the rule SHALL propose recording it as a convention with an owner. The recommendation waits for the user's choice.

#### Scenario: Enforceable repository
- **WHEN** the probe shows a public repository, or an organisation plan that supports rulesets or protected branches
- **THEN** the agent recommends a default-branch ruleset or protected-branch rule allowing changes only through requests and refusing force pushes, shows it as a dry-run delta, and applies nothing before approval

#### Scenario: Rule not enforceable
- **WHEN** the probe shows a private repository on a personal free plan
- **THEN** the agent says the ruleset cannot be enforced there, proposes the same rule as a convention in `platform-settings.md` with its owner and the plan change that would enforce it, and asks the user to confirm

#### Scenario: Protection declined
- **WHEN** the user declines any protection
- **THEN** the agent records the decline as a decision taken (current value kept, owner, the condition that reopens it), and the deposited knowledge states that the default branch accepts direct pushes

### Requirement: Behavior: Templates and knowledge carry three insertion markers
The delivered pull or merge request template, the project skill's finish step, and the platform knowledge file SHALL each contain the `<!-- harness: spec-workflow -->` marker once where the specification workflow adds its lines; issue forms carry none. The agent SHALL hand off to the builder whose description owns the specification and completion layer by that description, never by a skill name.

#### Scenario: Specification layer not yet built
- **WHEN** the target carries no specification workflow knowledge
- **THEN** the three delivered files each carry the marker once, the handoff names the specification and completion layer as the next step, and no spec-specific line is written

#### Scenario: Specification layer already built
- **WHEN** the target already has a specification workflow knowledge file naming its gates
- **THEN** the agent still writes the three markers and reports that the specification layer must be re-run to fill them, rather than copying gate lines itself

#### Scenario: Marker already present
- **WHEN** the existing knowledge file or request template already contains the marker
- **THEN** the agent keeps the existing marker, adds none, and each of the three files still carries it once

### Requirement: Behavior: Project skill deposited with publish gate and red-run digest
The agent SHALL deposit a project skill named `github-project-workflow` or `gitlab-project-workflow` under which agents take work, open requests as drafts, pass the publish gate before any remote or publishable write, finish with no draft commits left on the branch, and digest red runs instead of reading full logs. The publish gate SHALL require a clean-context review of the exact payload ending in the verbatim line `SAFE TO PUBLISH: YES` and SHALL treat any other last line as NO.

#### Scenario: Project skill delivered
- **WHEN** the plan approving the project skill is confirmed
- **THEN** the deposited skill opens pull or merge requests as drafts, requires the payload (title, body, commit messages, diff) assembled in files outside the repository and reviewed before publishing, and makes "no draft commits remain on the branch" part of finishing

#### Scenario: No subagent available for the review
- **WHEN** the client in the target cannot dispatch a clean-context subagent
- **THEN** the deposited skill states the file-only fallback: re-read every payload file from disk against the same checklist and write `Review mode: file-only (not clean-context)` directly above the verdict

#### Scenario: Pipeline turns red
- **WHEN** a pull or merge request's checks fail
- **THEN** the deposited skill directs the agent to run the delivered digest script and read its JSON instead of fetching full logs, and to fix on the same branch

### Requirement: Behavior: Knowledge and settings register deposited
The agent SHALL deposit `<platform>-workflow.md` (label semantics, branch and merge rules, the project skill's route) and `platform-settings.md` (every remote setting with its current value, its target value, its owner, and the readback command) under the target's knowledge directory, each opening with its "Read this when…" line, and SHALL append to an existing file of that name rather than creating a second.

#### Scenario: Knowledge file already present
- **WHEN** the target already has `.agents/knowledge/github-workflow.md`
- **THEN** the agent adds its sections to that file and creates no parallel planning file

#### Scenario: Setting the platform cannot enforce
- **WHEN** a planned rule (for example required reviews) is unavailable on the probed plan
- **THEN** `platform-settings.md` records it as a convention with its owner and the trigger that would upgrade it to a setting

### Requirement: Behavior: Remote writes run dry-run, approval, apply, readback
Every remote write (labels, settings, rulesets, protected branches) SHALL be shown as a dry-run delta first, applied only after the user approves that exact delta, and read back from the platform afterwards with the readback recorded. An approved plan SHALL NOT count as approval of a remote write. A required check SHALL be named in a ruleset only after it has run green on the default branch.

#### Scenario: Label sync
- **WHEN** the approved label file differs from the repository's labels
- **THEN** the agent prints the create / update / skip plan, applies it only after the user approves, and shows the post-apply listing matching the file

#### Scenario: User declines the apply
- **WHEN** the user declines a dry-run delta
- **THEN** nothing is written remotely, the decline is recorded in the report and in `platform-settings.md` as a decision taken (current value kept, owner, the condition that reopens it) and not in the pending decisions list, and the build continues with every step that does not depend on it

#### Scenario: New required check
- **WHEN** a workflow or pipeline job is to become a required check
- **THEN** the agent sequences the job first, confirms a green run on the default branch, and only then proposes the ruleset or protected-branch entry, saying that a check the platform has never observed blocks every request

### Requirement: Behavior: Multi-agent remote rules point at the authority policy
When the target runs more than one agent concurrently, the platform knowledge SHALL name the authority policy as the single source of the remote rules (one remote branch per agent, platform writes through one coordinator, each such write pre-authorised) and SHALL add only platform mechanics: which coordinator role writes labels, comments, and states, and the per-agent branch pattern. It SHALL restate none of the rules; with a single agent it SHALL write none of this. [§4.4]

#### Scenario: Single agent
- **WHEN** the user states one agent works at a time
- **THEN** the deposited knowledge contains no coordinator or per-agent-branch rule

#### Scenario: Authority policy already carries the rules
- **WHEN** the user states several agents work in parallel worktrees and the deposited authority policy already holds the remote rules
- **THEN** the platform knowledge references that policy by path for the rules, names the coordinator role for platform writes and the per-agent branch pattern, and repeats no rule sentence

#### Scenario: Authority policy not yet built
- **WHEN** concurrency is stated but the target has no authority policy
- **THEN** the platform knowledge points at the authority policy's agreed path, the agent lists the missing policy as a handoff to the builder owning the authority layer, and writes the rules into no file of its own

### Requirement: Behavior: Delivered scripts and automation belong to the target
Scripts and workflows delivered to the target SHALL come from the skill's assets as reference implementations, SHALL be reworked line by line against project facts (placeholders resolved only on their marked lines, unneeded parts removed) or rewritten in the management language the user agreed to, SHALL never call back into a skill directory, and the agent SHALL say later plugin fixes do not reach the delivered copy.

#### Scenario: Ownership stated
- **WHEN** any script or workflow is delivered
- **THEN** the agent tells the user the target owns the copy and that later plugin fixes do not reach it, and the delivered file names no path into a skill directory

#### Scenario: Python reference accepted
- **WHEN** the user accepts the Python reference implementations as the project's management scripts
- **THEN** the reworked copies land under the project's own scripts path with their tests, no `{{` placeholder left, and no path into a skill directory

#### Scenario: Reference implementation reworked
- **WHEN** the user asks for the digest script in the project's own management language
- **THEN** the agent treats the Python asset as the reference implementation, confirms the rewrite with the user, and delivers no Python copy beside it

### Requirement: Behavior: Delivered automation is fork-safe and least-privileged
Delivered automation SHALL execute only base-ref code on fork events, SHALL declare explicit least permissions, and SHALL pin actions or images by digest.

#### Scenario: Label sync workflow delivered
- **WHEN** the user accepts automated label sync
- **THEN** the delivered workflow runs on default-branch changes to the label file, declares `issues: write` (or the GitLab equivalent token scope) as its only write, does not prune by default, and never checks out or runs head code from a fork

### Requirement: Behavior: Existing harness contradicts the plan
When the target's existing knowledge, templates, or settings contradict a decision the user has just taken, the agent SHALL show the contradiction with both values before writing, and SHALL let the user choose which stands.

#### Scenario: Knowledge says rebase, user chose squash
- **WHEN** the existing `github-workflow.md` states rebase merging and the user has chosen squash-only
- **THEN** the agent quotes the existing line, asks which rule stands, and changes neither the file nor the remote until answered

### Requirement: Outcomes
Given an approved plan, the agent SHALL leave the target with a complete platform lifecycle layer whose local files, remote state, and knowledge agree, and SHALL end with a report, the readbacks, and a pending decisions list holding only questions the user has not answered.

#### Scenario: New public GitHub repository, single maintainer
- **WHEN** the user runs the skill on a fresh public GitHub repository with no labels or templates, confirms every recommendation, accepts the Python reference implementations, and approves each dry-run
- **THEN** the repository has exactly the `type:` / `area:` labels listed in the committed label file (which reserves the `spec:` namespace for the carrier's rows), three issue forms, one PR template carrying the `<!-- harness: spec-workflow -->` marker once, squash as the only merge method, a default-branch ruleset admitting changes only through pull requests and refusing force pushes, `github-workflow.md` carrying the marker once and `platform-settings.md` with readbacks recorded, `github-project-workflow` with the verbatim `SAFE TO PUBLISH: YES` gate and the marker once in its finish step, and the label-sync and run-digest scripts under the project's own path with no reference to the plugin

#### Scenario: GitLab project with surplus entities
- **WHEN** the user runs the skill on a GitLab project carrying thirty labels and two stale milestones, keeps the minimal set, and declines to delete the milestones
- **THEN** unused labels are listed with the deletion test and removed only where the user said yes, the milestones remain with the decline recorded in `platform-settings.md` and the report as a decision taken with its reopening condition, the pending decisions list holds no milestone item, the merge request template and `gitlab-project-workflow` are deposited with their markers, protected-branch rules were applied from an approved delta and read back, and the report names every remote action still awaiting a human

#### Scenario: Probe cannot run
- **WHEN** the user runs the skill in a repository whose remote is unreachable from the agent's environment
- **THEN** the agent writes local files only after the user supplies the remote facts, records every remote write as a pending human action with its exact command, and the knowledge file marks the settings register as unverified

### Requirement: Script: check_platform.py
The script SHALL probe the target's remote read-only through `gh` or `glab`, print one JSON object on stdout (platform, owner type, plan, visibility, default branch, labels, rulesets or protected branches, templates present), write diagnostics to stderr, offer `--help` with an example, exit 0 on a complete probe, 1 when the CLI is missing, unauthenticated, or fails, and 2 on bad arguments, run identically under `uv run` and plain `python3`, and change nothing.

#### Scenario: GitHub remote probed
- **WHEN** run with `--repo OWNER/REPO` against an authenticated `gh`
- **THEN** stdout is a single JSON object with `"platform": "github"` and the listed keys, and exit status is 0

#### Scenario: Platform auto-detected
- **WHEN** run without `--platform` in a repository whose `origin` points at a GitLab host
- **THEN** the script uses `glab`, reports `"platform": "gitlab"`, and runs no `gh` command

#### Scenario: CLI unauthenticated
- **WHEN** the CLI reports no login
- **THEN** the script exits 1 with a stderr line naming the login command, and prints no partial JSON

#### Scenario: Repeated run
- **WHEN** run twice in a row
- **THEN** both outputs are identical and the remote shows no change

### Requirement: Script: sync_labels.py
The delivered script SHALL read a JSON label file, compare it with the repository's labels through the platform CLI, print a create / update / skip (and, with `--prune`, delete) plan as JSON on stdout, change nothing without `--apply`, be idempotent, offer `--help`, and exit 0 on a plan or clean apply, 1 on an invalid file or CLI failure, 2 on bad arguments.

#### Scenario: Dry run
- **WHEN** run with `--file labels.json --repo OWNER/REPO` and no `--apply`
- **THEN** stdout is the plan JSON and the repository's labels are unchanged

#### Scenario: Apply then rerun
- **WHEN** run with `--apply` and then again with `--apply`
- **THEN** the second run's plan contains only skips and exits 0

#### Scenario: Invalid colour in the file
- **WHEN** a label entry has a colour that is not six hex digits
- **THEN** the script exits 1 naming the file, the index, and the fix, before any plan is printed

### Requirement: Script: run_log_digest.py
The delivered script SHALL digest one failed CI run or pipeline into a single JSON object on stdout (run id, status, conclusion, failed jobs with failed steps and the last N log lines each), never fetch full logs, offer `--help`, and exit 0 when a digest is produced (an empty failed list on a green run), 1 when the CLI is missing or fails, 2 on bad arguments.

#### Scenario: Red run digested
- **WHEN** run with `--repo OWNER/REPO --run-id ID --tail 40` on a run with two failed jobs
- **THEN** stdout lists both jobs with their failed steps and at most 40 log lines each, and nothing else is printed to stdout

#### Scenario: Green run
- **WHEN** the run concluded successfully
- **THEN** the digest has an empty failed-jobs list and the exit status is 0

#### Scenario: Job without a log
- **WHEN** a failed job never started and the CLI returns no log for it
- **THEN** the job still appears with an empty log tail and the CLI's message in its error field
