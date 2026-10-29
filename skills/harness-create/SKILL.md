---
name: harness-create
description: >-
  Harness creation — builds a project's first complete agent harness, from
  reading the repository to a reviewed, committed result, with every grade
  and decision confirmed by the user. Use when the user invokes it by name
  to give a repository its first AGENTS.md, knowledge files, checks,
  permissions, and specification workflow; when taking over a repository with
  history and habits that must be preserved; or when a stray CLAUDE.md or a
  few scattered rules are all the agent setup the repository has. Not for
  improving, auditing, thinning, or migrating a harness that already works
  (harness-improve), for the practice of a single layer (that layer's
  builder), or for writing README, CONTRIBUTING, or SECURITY.
license: Apache-2.0
disable-model-invocation: true
---

# Harness Create

Run one harness build for a target project from first read to close. This
skill holds the procedure and the decisions the user must take; the practice
of each layer lives in the installed skill whose description claims that
layer, and the methodology lives in the methodology manual skill. The harness
is read on every future task, so read the whole repository instead of
sampling it and spend context freely on getting each decision confirmed.
[§1.2] [§6.3]

## Rules on every step

<!-- shared:confirm-not-guess -->
Confirm, do not guess. Settle a fact from the repository when it can be
observed there (tools in use, directories, commands, history); ask the user
for everything else, and ask before choosing on any point where two readings
would lead to different work. Only a choice whose answer is plain from the
repository is made without asking.
<!-- /shared:confirm-not-guess -->

<!-- shared:recommendation-not-decision -->
A recommendation is not a decision. Present one recommended option with its
reason and the alternatives in a sentence each, then wait for the user's
choice. Challenge a choice once when the evidence contradicts it; after that
the choice binds every later step.
<!-- /shared:recommendation-not-decision -->

<!-- shared:nothing-lands-before-agreement -->
Nothing lands before agreement. Create or change no file in the target
project until the user has approved the plan that names it; an inspection
step reads and reports, it never writes.
<!-- /shared:nothing-lands-before-agreement -->

<!-- shared:plan-is-not-approval -->
An approved plan authorises the files it names and nothing else. Publishing
anything outside the repository, changing a remote setting, deleting work,
and widening what agents may do on their own are each a separate, explicit
decision by the user, taken when that step is reached.
<!-- /shared:plan-is-not-approval -->

<!-- shared:pending-decisions -->
When a step is blocked on a decision only the user can make, continue with
every step that does not depend on it and add the blocked item to a pending
decisions list. Each item states: what is blocked and why; the options; the
recommended option and its reason; which finished work each option would
change. Present the list once, at the end or when nothing else can proceed,
never one question at a time.
<!-- /shared:pending-decisions -->

Read [references/pending-decisions.md](references/pending-decisions.md) when the first item enters the list,
and write every item in its format.

<!-- shared:management-code-ownership -->
A script, hook, check, CI step, or task-runner recipe written into the target
project is the project's own management code: written for its role in the
language the project agreed to, readable first, failing with a message that
names what to fix, with no fallback that hides an unexpected error, and never
calling a script inside a skill directory. Tell the user that later fixes to
this plugin do not reach the delivered copy.
<!-- /shared:management-code-ownership -->

- **Grade layers, never the project.** Every layer gets its own grade; a
  project label ("a research repo", "production") is evidence for the
  variables, not a grade. [§6.1]
- **Route by role.** Name no builder in anything you write into the target;
  a layer goes to whichever installed skill claims it (step 6), and the
  methodology is "the methodology manual skill".
- **Deposited files stand alone.** Nothing written into the target names
  this plugin, any of its skills or agents, a path inside a skill directory,
  or a term only this plugin defines without defining it.
- **Public files are read, never written.** README, CONTRIBUTING, and
  SECURITY stay unchanged; a contradiction with the harness becomes a
  suggested edit in the closing report.
- **One agent at a time** unless the user answers in step 5 that several
  agents will write to the repository at once; only then do concurrency
  rules (worktrees, remote branches, shared-resource locks) enter the plan.
  [§4.4]

## Workflow

### 1. Investigate

Read before asking. Record, each with where it was seen: layout and stack;
build, test, lint, and format commands; task runner and its recipes; checks,
CI, and hooks; branch and commit-title habits from `git log`; the remote
(`git remote -v`); whether the session runs inside an isolated environment
the repository declares (a devcontainer, a container file); and every
agent-facing file, project skill, permission file, and registered tool.

Classify the project: **greenfield** only when it shows no established habit
to preserve (no build or test command, no CI, a handful of commits);
**brownfield** when it shows any habit, with or without agent-facing files.
A single old `CLAUDE.md` makes it brownfield. Read
[references/greenfield.md](references/greenfield.md) when the project is greenfield; read
[references/brownfield.md](references/brownfield.md) when it is brownfield, and run its inventory.

Report the classification, the facts, and the open questions; the questions
are asked from step 2 on, after the goal. A command or check seen in the
task runner or CI is recorded as the existing check set and never asked
about. [§6.3]

Done when: every fact is backed by evidence (file and line, or command
output) or listed as a question only the team can answer, and no file has
changed.

### 2. Align goals and non-goals

When the invocation carried a sentence about what the harness is for,
restate it as the goal and do not ask for it again. Otherwise the goal is
the first question, asked alone in one question; nothing else proceeds
until it is answered.

Then propose the non-goals: what the harness will not police (for example
code style the project never enforced), what stays human-only, and which
changes to the project itself it will not make. A goal that reaches beyond
the harness (splitting a monolith, migrating a framework) is named as a
non-goal; offer to record it as a separate change the team may make, and
record the answer.

Ask the user to confirm the goal and the non-goals together. Every later
grade and decision must respect them, and a row they constrain says so (with
"no changes to CI" confirmed, every hard-boundary check runs outside CI and
the grade table names the non-goal as the reason).

Done when: the user confirmed one goal and a non-goal list, both recorded
for the plan.

### 3. Settle the five variables

Read [references/five-variables.md](references/five-variables.md) when settling the variables: error cost,
maintenance horizon, environment isolation, autonomy, team size. Take each
from the repository when it is observable there. A value inferred from
evidence ("one author in the whole log, so a single maintainer") is
presented as an inference for the user to confirm or correct. Ask every open
variable in one round, each with its typical answers and which layers each
answer pushes thicker or thinner. [§1.1]

Done when: all five variables have a value marked observed, confirmed
inference, or user answer.

### 4. Grade the layers

Read [references/thickness-table.md](references/thickness-table.md) when proposing grades. Build one table
of the six graded layers, named exactly: environment, knowledge and routing,
hard-boundary, authority, specification and completion, entropy. Each row:
a grade (omitted, light, medium, thick), the variables that drive it, the
evidence, and any non-goal that constrains it. For a brownfield project each
row also states what exists now; the plan fills only the difference.

Ask the user to confirm or change every row. When a change contradicts the
evidence, challenge it once, then adopt the user's grade for that row and
carry it into every later step.

**Platform lifecycle.** When `origin` points at GitHub or GitLab, add the
platform lifecycle layer below the table with these recommendations, each
confirmed: GitHub Flow; the merge methods allowed, asked every time, with
squash-only recommended; the minimal entity set (`type:`, `area:`, and
`spec:` labels, bug, feature, and task forms, one pull or merge request
template); no Projects boards or Milestones (challenge once if asked for:
they repeat state the issues and requests already hold, and an unmaintained
board misleads); releases triggered by tags. This layer takes no grade. With
no remote, or a remote that is neither, mark the layer not applicable and
ask no platform question.

Done when: every graded row carries a grade the user confirmed, and, when
the platform layer applies, each of its decisions (flow, merge methods,
entity set, no boards or milestones, tag releases) carries the user's
confirmation.

### 5. Settle the decisions inside each layer

For every layer graded above omitted, present each decision with one
recommendation and its reason, alternatives in a sentence each, and wait.
Choose without asking only what the repository answers plainly (an existing
`justfile` is the task runner; an existing secret scanner stays).

- **Entrypoint**: `AGENTS.md` with `CLAUDE.md` importing it (`@AGENTS.md`),
  about 100 lines, at most 120. [§2.1]
- **Task runner**: the one in use; otherwise `just`. Recommending another
  runner over a working one is a suggestion for a separate change, never a
  plan row.
- **Secret scanner**: betterleaks in pre-commit and CI; gitleaks or
  TruffleHog as alternatives.
- **Lint and type-check tools**: the ones in use; otherwise recommend the
  ecosystem's most widely used linter and type checker for the detected
  language (for example Ruff and mypy for Python, ESLint and `tsc` for
  TypeScript), because agents and their training data know them best; give
  the alternatives in a sentence each and wait for the choice.
- **Specification carrier**: the one in use; otherwise recommend by project
  shape: OpenSpec for a library, infrastructure, or existing code, because
  its change folders track deltas against what already exists; Spec-Kit for
  a greenfield application built feature by feature, because it plans each
  feature from specification to tasks; a lightweight carrier (plan mode or
  one `SPEC.md`) for a small single-person project, because the other two
  cost more ceremony than one maintainer needs. Name the other two as the
  alternatives in a sentence each. Recommend spec-anchored specifications
  when the project is maintained beyond one release cycle, spec-first
  otherwise. Specifications are written only for parts under change. When asked for
  specifications of code nobody is changing, advise against it, because
  nothing forces such a document to track the code and it rots from the day
  it is written; record the user's decision. [§6.3]
- **Deny list**: recommend this fixed list, accepted as one block: `git
  reset --hard`, `git push --force`, `git push --all`, `--mirror`, and
  `--tags`, `git clean -fd`, `git branch -D`, `rm -rf` at the repository
  root, and rewriting the permission files and security hooks; each
  destroys work or disables a guard that cannot be restored by the agent.
  The alternative is a written policy with no framework permission files.
- **Allow list**: list the project's observed test, lint, build, format, and
  read-only commands and each task-runner recipe by name, with evidence;
  the user confirms or trims. No ask entries, no runner wildcard, and no
  push, publish, release, or deletion: those are pre-authorised in the
  plan or spec, or go to the pending decisions list. [§4.2]
- **Approval mode**, when Codex is a client: recommend `on-request`, because
  a command then asks only when it must leave the sandbox; `never` for
  unattended runs as the alternative.
- **Commit convention**: the one history shows, unless an inventory item
  marked it contradictory; then ask which is intended before the plan names
  a commit rule. With no history, recommend Conventional Commits, with plain
  50/72 titles as the alternative. No AI attribution.
- **Concurrency**: ask "Will several agents write to the repository at
  once?" Recommend one agent at a time, so the plan carries no concurrency
  rules and says why; the alternative adds worktrees, remote branch rules,
  and shared-resource locks. Record the answer. [§4.4]
- **Handoff files**: recommend `.agents/handoff/` listed in `.gitignore`,
  because the agent finds it in the repository and git never carries it;
  the system temporary directory is the alternative, which leaves the
  repository untouched but is lost on reboot.
- **Environment isolation, when none exists**: list the options (devcontainer,
  a disposable VM or cloud workspace, the host with scoped tokens) with
  their costs and recommend none; the user chooses. When an isolated
  environment exists, use it. [§3.2]
- **Management-script language**: always ask, never infer; the user must be
  able to read the scripts. Recommend Deno when the repository carries a
  Deno environment (`deno.json`), citing its explicit permission
  management; otherwise the scripting practice of the project's language
  community, with Deno as the alternative; otherwise Deno, asking whether
  Deno may be added to the agent environment. Also ask whether the plugin's
  Python reference scripts are used as they are or rewritten. Plan no
  script before the answer.

Done when: every decision for every planned layer has the user's choice
recorded, or sits in the pending decisions list.

### 6. Plan and get approval

Assign each planned layer, platform lifecycle included, to its builder:
list the installed skills' descriptions and pick the one containing
`Owns the <layer> layer` with that layer's name. When none does, tell the
user that the layer will be built from the methodology manual skill's
references and record the gap; when two do, ask which to use.

Rework [assets/harness-plan.md](assets/harness-plan.md) line by line into the plan: goal and
non-goals, the five variables, the grade table, then one section per layer
graded above omitted, in build order, with the decisions taken, every file
to be created or changed by path, and the skill assigned; then human-only actions, open
assumptions, and suggestions for separate changes. Remove every
`# CONFIGURE:` comment, placeholder, fill instruction, and inapplicable
row; with no hosted remote the plan has no platform section at all.

Present the plan in the conversation; it is not written into the target
unless the plan itself names it. When the user asks to see a draft file
before approval, show it in the conversation and write nothing. When the
user rejects the plan or stops, write nothing, make no commit, and summarise
the investigation, the goal, and the grade table so the work can resume.

Done when: the user approved the plan as presented.

### 7. Build layer by layer

Build in this order, skipping layers graded omitted: environment, knowledge
and routing, hard-boundary, authority, platform lifecycle, specification and
completion, entropy. On a greenfield project, the knowledge and routing
checkpoint documents only commands that already exist; the hard-boundary
checkpoint adds each command it creates to the entrypoint. For each layer:

1. Load the skill the plan assigned (when it is gone, repeat the lookup
   from step 6; a renamed skill still carrying the phrase is the same
   builder); a layer with none is built from the methodology manual skill's
   references. Give it the plan's grade, decisions, and file list for its
   layer so it does not ask them again, let it run, and continue here when
   it hands back.
2. Create only files the plan names. A file the plan did not name needs the
   user's approval of a plan amendment first.
3. A remote action the plan includes (label sync, a push) is shown as a
   dry run and applied only after a separate go-ahead at that step. Never
   apply branch protection, secret scanning, push protection, or any other
   repository setting: each goes to the plan's human-only actions and step
   10 item 3.
4. Checkpoint: once the layer's files exist and its checks pass locally,
   stage the explicit paths and commit with a message in the recorded
   convention, no AI attribution. Never stash or rely on session-only undo.
   When a hook rejects the commit, fix or remove the flagged content and
   commit again; never bypass the hook. Push nothing unless the user decided
   so for this step. [§4.3]

When a decision blocks a layer, finish every layer that does not depend on
it and add the item to the pending decisions list.

Done when: every planned layer is built and committed, or blocked with an
item in the pending decisions list.

### 8. Read back in a clean context

Hand every new or changed artifact to the plugin's read-only verifier agent
(`harness-verifier`), giving only target-project paths and one intent line
each, never this skill's content. Fix every gap it reports, then re-run it
on the fixed file and every file the fix touched; continue only on PASS.
When the client cannot dispatch it, use any clean-context subagent with the
same input; when none can be dispatched, read the files yourself in a fresh
pass from the entrypoint, as an agent that never saw this build, and record
the read-back as degraded. [§3.4]

Done when: the latest read-back of every artifact is PASS, or the degraded
pass found no gap.

### 9. Review the finished harness

Review in this order, fixing as you go:

- **Vocabulary**: every term only this plugin defines (pending decisions
  list, grade names, layer names) is defined where it is used, or the
  sentence is rewritten plainly.
- **Self-containment**: search the deposited files for plugin and skill
  names, skill-directory paths, and the ownership phrase. A CI step,
  hook, or recipe calling a script inside a skill directory is replaced by
  the project's own copy, and the user is told later plugin fixes do not
  reach it.
- **Mechanics**: every rule reachable from the entrypoint; entrypoint within
  budget; links resolve; every documented command runs; each sync concern
  owned in both directions. [§5.3]
- **Checklist**: read [references/final-checklist.md](references/final-checklist.md) when walking the
  closing checklist, and walk it item by item.

Re-read every fixed file under step 8 and commit the fixes as a checkpoint.

Done when: every pass is clean and every checklist item is passed, marked
not applicable with the grade that omits it, or in the pending decisions
list.

### 10. Close

Report, in this order:

1. Every artifact created or changed, with its role and validation result.
2. The pending decisions list, once, in its format.
3. Every platform or remote action left for a human, each with the exact
   setting to apply (for example branch protection on the default branch
   requiring the named checks; secret scanning and push protection on).
4. Every public file that contradicts the harness, with a suggested edit;
   none of them changed.
5. Missing builders, a degraded read-back, and the suggestions for separate
   changes recorded in the plan.

Done when: the report holds all five parts, names no skill, and `git status`
shows nothing uncommitted from this build.

## Gotchas

- A fact the code already states (a command, a directory) copied into a
  knowledge file is a copy that will go stale; route to the recipe or file
  instead. [§1.3]
- A self-hosted GitLab has its own hostname in `origin`. Before marking the
  platform lifecycle layer not applicable, check for `.gitlab-ci.yml` or
  `.gitlab/`; treat the remote as GitLab only on that evidence, and
  otherwise mark the layer not applicable without asking.
