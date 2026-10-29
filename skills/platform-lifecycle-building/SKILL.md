---
name: platform-lifecycle-building
description: >-
  Platform lifecycle: designs, builds, migrates, or thins how work flows
  through a GitHub or GitLab repository. Owns the platform lifecycle layer:
  labels, issue forms, request templates, branching model, merge methods,
  rulesets or protected branches, the remote settings register, and the
  project skill agents follow from taking an issue to merging. Use when
  setting up or rebuilding a repository's labels, forms, branch rules, and
  agent issue-to-merge workflow; when moving a project between GitHub and
  GitLab; when labels, milestones, or boards have piled up and need cutting
  down to what is used; when deciding between GitHub Flow and develop or
  release branches, or which merge methods to allow; or when an approved
  harness plan hands over this layer. Not for one issue, pull request,
  label, or release operation, CI job authoring, local git history edits,
  or agent permission lists.
license: Apache-2.0
compatibility: Scripts need Python 3.10+ and an authenticated gh or glab; uv optional.
---

# Platform Lifecycle Building

The platform is where agent work becomes visible and irreversible: issues,
pull or merge requests, labels, and branch rules. This skill probes the
remote read-only, settles the lifecycle with the user from that evidence,
deposits the smallest set of platform objects that serves review, a project
skill agents follow for every issue and request, the knowledge behind it,
and a register of every remote setting, then applies each remote change
only as a delta the user approved. [§6.3] [§4.2]

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

A declined proposal is a decision taken, not a pending one: record the
current value kept, its owner, and the condition that reopens it, in the
settings register and the report, and continue with every step that does
not depend on it. [§4.2]

<!-- shared:management-code-ownership -->
A script, hook, check, CI step, or task-runner recipe written into the target
project is the project's own management code: written for its role in the
language the project agreed to, readable first, failing with a message that
names what to fix, with no fallback that hides an unexpected error, and never
calling a script inside a skill directory. Tell the user that later fixes to
this plugin do not reach the delivered copy.
<!-- /shared:management-code-ownership -->

Delivered automation runs only base-ref code on fork events, declares
explicit least permissions, and pins every action or image by digest.

Hand adjacent work over by role, never by skill name: the specification
carrier, its gates, and the lines that fill the insertion markers to the
skill that owns the specification and completion layer; CI jobs and secret
scanning to the skill that owns the hard-boundary layer; permission lists,
the authority policy, and the remote rules for parallel agents to the skill
that owns the authority layer; entrypoint routes to the knowledge file and
the project skill to the skill that owns the knowledge and routing layer;
linting and behavioural tests of the deposited project skill to the skill
that writes project skills.

Deposited files name the project's own paths and commands only: never this
plugin, a plugin skill, a skill directory, or a `[§x.y]` tag.

Read [references/github.md](references/github.md) when the platform is GitHub and
[references/gitlab.md](references/gitlab.md) when it is GitLab, as soon as the probe names the platform; a
migration reads both.

## Workflow

### 1. Probe the remote

Run the read-only probe, [scripts/check_platform.py](scripts/check_platform.py), against the
target: `python3 <this skill's directory>/scripts/check_platform.py --path <target>`
(`uv run` works too). Add `--repo`, `--platform`, or `--hostname` only when
`origin` does not answer them. Read locally, alongside: existing
`<platform>-workflow.md`, `platform-settings.md`, and branch or git
workflow knowledge; templates and forms; every file the probe lists under
`label_files`; the authority policy and whether it holds remote rules for
parallel agents; any specification workflow knowledge; the commit-title
convention of the last 30 commits; the scripts directory and its language.

When the probe exits 2 because it cannot tell the platform, re-run it with
`--platform` and `--hostname` when the remote URL or the user's earlier
words settle them; otherwise ask the user which platform the host runs.
The probe has no option that writes a file; never redirect its output into
the target.

When the probe exits 1, quote the tool (`gh` or `glab`) or the login
command (`gh auth login`, `glab auth login`) its stderr names, leave
installation to the user, write nothing, and ask whether to continue with
the user supplying the remote facts or to stop. Continuing marks the
settings register unverified and turns every remote write into a pending
human action with its exact command.

Report the facts before the first question: owner type, plan, and
visibility as three separate facts (each `unknown` is asked, never
inferred from another); default branch; merge methods; labels; rulesets or
protected branches; templates; branches, tags, and environments; open
milestones; boards (`null` on GitHub means the token lacks `read:project`:
ask the user to grant it or to name the boards); label files. Name now every likely setting the plan and
visibility cannot enforce (rulesets on a private repository of a personal
free account, required approvals on GitLab Free).

Done when: every probe key is reported or marked unknown, nothing the
probe showed is asked, and no file has changed.

### 2. Ask what the probe cannot show

In one round: the intent (new setup, rebuild, migration, thinning); team
size and who reviews and merges; governance (who owns each remote setting
and approves its change); whether one agent works at a time or several in
parallel; whether outside contributors open requests from forks.

Done when: each has an answer or is on the pending decisions list.

### 3. Settle the decisions

One recommendation each, in this order:

- **Entity set.** Read [references/necessity.md](references/necessity.md) when proposing the set,
  when the user asks for more, or when the probe found surplus. Recommend
  the minimal set (`type:` and `area:` labels, the `spec:` namespace
  reserved, bug / feature / task forms, one request template) and list
  Projects, boards, and Milestones among the objects deliberately not
  created. Every extra passes the deletion test first; removing surplus is
  a separate decision. [§6.2]
- **One label file.** The committed label file is the only label
  definition: the specification carrier later appends its `spec:` rows to
  it, and the sync reads only it. When two label files exist, show both,
  recommend merging into the one the sync reads, and run no `--prune` until
  one remains.
- **Branching model and releases.** Read [references/branching.md](references/branching.md) when
  recommending either: GitHub Flow for a new project, a GitLab Flow variant
  only on evidence, an existing git-flow kept [§6.3]; tag-triggered
  releases, with no release automation configured until the user chooses.
- **Merge methods.** Read [references/merge-method.md](references/merge-method.md) when asking: ask
  which methods are allowed and the rule for each, recommend squash only,
  and apply the answer to both the remote setting and the knowledge.
- **Default-branch protection.** Recommend changes only through requests,
  force pushes and deletion refused. Where the plan or tier cannot enforce
  it, propose it as a convention in `platform-settings.md` with its owner
  and the plan change that would enforce it.
- **Label sync.** Recommend the delivered workflow or CI job where the
  platform can run it (on GitLab: a project access token and an image with
  `python3` and `glab`); otherwise a named person runs the script.
- **Management code.** Use the language the harness plan agreed; when none
  was agreed, ask, offering the Python reference implementations as they
  stand or a rewrite in the project's language.
- **Parallel agents.** Read [references/remote-state.md](references/remote-state.md) when more than one
  agent works at a time; with one agent, nothing about it is written. [§4.4]

When existing knowledge, a template, or a remote setting contradicts a
decision just taken, quote the existing line or value with its path beside
the decision, ask which stands, and change neither until answered.

Done when: every bullet has an answer, a recorded decline, or a pending
decisions item, and every contradiction found is answered or pending.

### 4. Plan the files and the remote deltas

List each local file by its target path with one line (the Files table in
the platform reference), and what each existing file gains or loses. List
the remote deltas separately, saying that approving the plan does not
approve them: each is shown and approved when step 6 reaches it. Say that
the delivered scripts and automation become the project's own. Wait for
approval.

Done when: the user approved the file list; nothing is written before.

### 5. Write the local files

Rework each asset line by line against the settled answers: every
`# CONFIGURE:` line resolved (a line holding only a placeholder is replaced
whole), fill guidance deleted, sections that do not apply deleted.

- GitHub: [issue-form-bug.yml](assets/github/issue-form-bug.yml), [issue-form-feature.yml](assets/github/issue-form-feature.yml),
  [issue-form-task.yml](assets/github/issue-form-task.yml), [issue-template-config.yml](assets/github/issue-template-config.yml),
  [pull-request-template.md](assets/github/pull-request-template.md), [labels.json](assets/github/labels.json),
  [workflow-labels-sync.yml](assets/github/workflow-labels-sync.yml), [codeowners](assets/github/codeowners) (only when it passed the
  deletion test), [project-skill.md](assets/github/project-skill.md), [knowledge-github-workflow.md](assets/github/knowledge-github-workflow.md),
  [platform-settings.md](assets/github/platform-settings.md).
- GitLab: [issue-template-bug.md](assets/gitlab/issue-template-bug.md), [issue-template-feature.md](assets/gitlab/issue-template-feature.md),
  [issue-template-task.md](assets/gitlab/issue-template-task.md), [merge-request-template.md](assets/gitlab/merge-request-template.md),
  [labels.json](assets/gitlab/labels.json), [ci-labels-sync.yml](assets/gitlab/ci-labels-sync.yml), [project-skill.md](assets/gitlab/project-skill.md),
  [knowledge-gitlab-workflow.md](assets/gitlab/knowledge-gitlab-workflow.md), [platform-settings.md](assets/gitlab/platform-settings.md).
- Both: [sync_labels.py](assets/sync_labels.py) and [run_log_digest.py](assets/run_log_digest.py) with their
  `_test.py` files, into the project's scripts path; remove the other
  platform's code, then run the tests there. A rewrite in another language
  replaces the Python copy instead of sitting beside it.

The project skill is `github-project-workflow` or `gitlab-project-workflow`.
Keep its publish gate's rules; read [references/publish-gate.md](references/publish-gate.md) when reworking
the gate or before the build makes any publishable write. [§4.2]

The knowledge file and the register go into the target's knowledge
directory, each opening with its "Read this when…" line. When a file of
that name exists, add the sections to it; never create a second planning
or label file. The register holds every remote setting with current value,
target value, status, owner, readback command, and trigger, including each
decline and each convention the platform cannot enforce.

The request template, the project skill's Finish step, and the knowledge
file each carry `<!-- harness: spec-workflow -->` exactly once; issue forms
carry none. Keep a marker already present and add none beside it. Write no
specification line yourself, even when a specification workflow already
exists: report that its layer must be re-run to fill the markers.

Done when: `grep -rnE '\{\{[A-Z_]+\}\}'` over the delivered files prints
nothing; each of the three files counts the marker once; no delivered file
names a skill directory or this plugin; the delivered tests pass.

### 6. Apply the remote writes, one delta at a time

Order: labels (forms rely on them), merge methods, branch protection, then
any required check. For each delta: show the current value and the exact
command or payload (for labels, the sync's dry-run plan), apply it only
after the user approves that exact delta, then read it back from the
platform and record the readback in the register. [§4.2]

- Declined: nothing is written remotely; go on with the next delta.
- Remote unreachable or the user's own rights insufficient: record the
  delta as a pending human action with its exact command.
- A job becoming a required check: sequence the job first, confirm a green
  run on the default branch, and only then propose the ruleset or
  protected-branch entry, saying that a check the platform has never
  observed blocks every request.

Done when: every planned delta is applied with its readback recorded,
declined and recorded, or listed as a pending human action with its
command.

### 7. Report and hand off

Report: every file written or changed; each applied delta with its
readback; each decision taken by decline; every remote action still
awaiting a human, with its command; the pending decisions list holding only
questions the user has not answered; that the project owns the delivered
scripts and automation and later plugin fixes do not reach them. Hand off
by role as the Rules state; the three insertion markers are named as the
next step, and a missing or incomplete authority policy is handed off only
when agents run in parallel.

Done when: every item above is in the report.

## Gotchas

- `"available": false` in the probe is an HTTP 403: either the plan and
  visibility lack the feature or the caller lacks admin rights. Settle which
  from the plan and visibility facts before telling the user it cannot be
  enforced.
- GitLab protects the default branch at creation but lets maintainers push:
  "protected" in the probe does not mean "changes only through requests".
