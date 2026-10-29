---
name: environment-building
description: >-
  Environment and sandbox — builds or audits where a project's coding agent
  runs and what it can reach. Owns the environment layer: the isolation
  decision, the protection tier, the five-item sandbox audit, read-only
  control-plane files, and non-interactive command defaults. Use when
  working out what an agent can reach from its container or host and what to
  lock down; when host credentials (~/.ssh, ~/.aws, broad tokens) are
  exposed to an agent; when an agent will run unattended on issues, pull
  requests, or web content anyone can write; when deciding whether an agent
  needs a restricted instance, a network allowlist, or read-only security
  files; when agent commands hang on a pager or prompt; or when an approved
  harness plan hands over the environment layer. Not for a dev container or
  Docker image unrelated to agents, CI or pre-commit gates, or agent allow
  and deny lists.
license: Apache-2.0
---

# Environment Building

Framework rules are aids an agent that runs code can write around; the real
boundary is the environment it runs in and the tokens it holds. This skill
settles that environment with the user at the confirmed grade: where the
agent runs, which protection tier the threat model demands, an explicit
decision on each of the five sandbox exposures, which control-plane files
are hard or soft read-only, and the variables that keep every command
non-interactive. It deposits one environment knowledge file and a variables
block in the project's task runner. [§3.3]

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

<!-- shared:management-code-ownership -->
A script, hook, check, CI step, or task-runner recipe written into the target
project is the project's own management code: written for its role in the
language the project agreed to, readable first, failing with a message that
names what to fix, with no fallback that hides an unexpected error, and never
calling a script inside a skill directory. Tell the user that later fixes to
this plugin do not reach the delivered copy.
<!-- /shared:management-code-ownership -->

<!-- shared:pending-decisions -->
When a step is blocked on a decision only the user can make, continue with
every step that does not depend on it and add the blocked item to a pending
decisions list. Each item states: what is blocked and why; the options; the
recommended option and its reason; which finished work each option would
change. Present the list once, at the end or when nothing else can proceed,
never one question at a time.
<!-- /shared:pending-decisions -->

The grade bounds every option offered; never add a mechanism of a thicker
grade on your own. [§6.1]

| Grade | Isolation | Hard read-only files | Network |
|---|---|---|---|
| light | host, credentials limited to scoped tokens | enforcement not applicable | open |
| medium | an isolated environment, relied on by convention | listed, kept by convention | open |
| thick | container or VM isolation | enforced at the mount or OS layer | allowlist |

Hand adjacent work to its layer by describing the layer, never by naming a
skill: lint, typecheck, and test recipes, the task-runner choice, and the
soft read-only invariant sentence to the layer that owns hard-boundary
checks; allow and deny lists and which actions need pre-authorisation to
the layer that owns authority; branch protection and remote token settings
to the layer that owns the platform lifecycle; an entrypoint over budget to
the layer that owns knowledge and routing.

When the user reverses a confirmed choice after the files landed, update the
knowledge file and the variables block (and the dev container file when the
choice touched it), and name every piece of finished work the reversal
changed.

## Workflow

### 1. Inspect

Read, record, write nothing. Collect:

- the grade the approved plan assigned to this layer, if any;
- isolation: a dev container configuration, `Vagrantfile`, VM or cloud
  workspace configuration in the repository; whether this session runs
  inside one (`/.dockerenv`, `REMOTE_CONTAINERS`, `CODESPACES`);
- reach: mounts, `runArgs`, forwarded ports, and network mode read from
  the container configuration and from `/proc/self/mountinfo`; credential
  directories and token variables present in the session (names only,
  never values); a forwarded SSH agent or git credential helper;
- the clients in use and where each writes session logs;
- control-plane files: security hooks and secret scanner, sandbox and
  container configuration, permission files, linter, type-check, test, and
  build configuration;
- the task runner, its existing exported variables, and whether the test
  command enters watch mode by default;
- the agent entrypoint, its line count, and the knowledge directory.

Read [references/devcontainer.md](references/devcontainer.md) when a dev container configuration exists or
the session runs in a container, to read its reach correctly.

Done when: every item is recorded as observed, absent, or "ask", and no
file in the project has changed.

### 2. Settle the grade

When the plan assigned a grade, take it. If the plan grades the layer
omitted, report that this layer builds nothing and stop. Otherwise
recommend one from the project's error cost and autonomy only, with the
reason, and name the other two in a sentence each: thick when the agent
will run unattended or a mistake reaches production, customer data, or
money; medium when a developer works with the agent but it holds
credentials or a mistake is costly to undo; light when nothing sensitive is
reachable and a mistake is cheap to undo. Propose nothing else (isolation,
tier, audit, control plane) until the user confirms a grade; every later
step depends on it. [§6.1]

Done when: the grade is confirmed by the plan or by the user, and nothing
after this step has been proposed before that confirmation.

### 3. Decide the isolation

- **An isolated environment exists and the session uses it**: record it as
  the layer's base and go to step 4. Offer no alternative.
- **A configuration exists but this session runs outside it**: ask whether
  agents work inside it; on yes, adopt it as above; on no, treat it as none
  in use and follow the branch for the grade below, listing the existing
  configuration among the options without recommending it.
- **Light grade, none exists**: propose the host with scoped tokens, naming
  each token to scope and the scopes it keeps, for the user to confirm;
  record the confirmation as the user's decision in the knowledge file.
  Offer no container or VM unless the user asks for one.
- **Medium grade, none exists**: list dev container, VM, and host with
  scoped tokens.
- **Thick grade, none exists**: list isolation technologies only: local dev
  container, cloud-hosted dev container, VM.

For each option in a medium or thick list give its cost and protection in
one sentence, recommend none, and wait. When the user picks the host,
accept it, record it as the user's decision, and continue; the audit in
step 5 runs against the host. When the user picks a dev container, plan
only what the choice requires; the file is listed in step 8 and written in
step 9. [§3.3]

Done when: the base is recorded, and as the user's decision whenever
options were listed or the host was proposed.

### 4. Rate the threat model

Rate three facts, from the repository where observable, otherwise by asking:

1. **Trifecta**: the agent can reach sensitive assets, ingests content it
   does not control, and can communicate outward or change state.
2. **Source reachability**, per content source: trusted repository,
   reputation-guarded, or open-write (issues, pull request comments, search
   results, arbitrary pages).
3. **Human in the loop**: a person issues each task and reviews the result
   before anything leaves the machine.

All three (trifecta present, an open-write source, no human) → the
**isolated tier**: recommend a separate restricted instance without the
sensitive credentials and without write to the main branch or the
configuration, for the user to confirm. Any one missing → the **regular
tier**; name the missing condition. Trifecta incomplete → say no isolation
is required; the audit still runs. [§3.2]

The **middle band** of the regular tier is reputation-guarded sources, or
open-write sources with a human in the loop. Only there does model
resistance to injection set how much source restriction or input cleaning
to apply; trusted-repository-only sources need no restriction. Model
resistance never lowers the isolated tier. Read [references/threat-model.md](references/threat-model.md) when
rating the middle band, when the user disputes the tier, or when proposing
the restricted instance.

Done when: each of the three facts is recorded with its evidence, the tier
is named with the conditions met or missing, and any middle-band setting is
confirmed per model or listed as pending.

### 5. Run the sandbox audit

Walk the five items with the user against the confirmed base: sensitive
assets, host privilege leaks, local and intranet exposure, session-log
destination, and the explicit risk decision. For each, report the finding,
recommend accept or cut with the reason, and record the user's answer and
reason. Silence is not acceptance. An accepted item is recorded with the
user's reason and not raised again. [§3.3]

Read [references/sandbox-audit.md](references/sandbox-audit.md) when walking the items, and when the user
leaves items undecided or declines the audit.

Done when: each of the five items carries accepted, cut, undecided, or
declined, with a reason for every accepted or cut item, and every undecided
or declined item is on the pending decisions list with its recommendation.

### 6. Classify the control plane

For each control-plane file found in step 1, recommend hard read-only
(security rules, sandbox and container configuration, secret-scanning
hooks, permission files) or soft read-only (linter, type-check, test, build
configuration), and get the user's confirmation per file. At thick grade
the proposal adds mount-level enforcement of each hard read-only file and a
network allowlist; below thick it records hard read-only as kept by
convention and names mount-level enforcement as the step hardening to
thick would add (at light, enforcement is recorded as not applicable). For
soft read-only files, point to the hard-boundary layer's knowledge for the
invariant wording and hand "the invariant sentence covers this file"
(naming it) to that layer; do not write the sentence here. [§3.3]

Read [references/control-plane.md](references/control-plane.md) when classifying, when writing the
allowlist or mount enforcement, when the user wants the security rules
unreadable by the agent, or when a client has its own sandbox setting.

Done when: every control-plane file has a classification the user
confirmed, and the thick-grade proposal contains the allowlist.

### 7. Set the non-interactive defaults

The variables are `CI=true`, `PAGER=cat`, `GIT_PAGER=cat`, and
`GIT_TERMINAL_PROMPT=0`, plus any ecosystem variable the project's tools
read. [§4.3]

- **Task runner in use**: plan to add the missing variables from
  [assets/justfile-env-snippet.just](assets/justfile-env-snippet.just), translated when the runner is not
  `just`; keep variables the file already exports.
- **No task runner agreed**: install nothing; hand the task-runner choice
  to the hard-boundary layer; add a pending decision with `just` as the
  recommended carrier, and list the variables in the knowledge file.
- **A recipe still needs a flag** (a test command that watches by default,
  a tool that prompts): name the flag in the knowledge file and hand "the
  run-once flag for the test recipe" (or the recipe concerned) to the
  hard-boundary layer. Do not edit the recipe.

Done when: the variables have a carrier in the plan or a pending decision,
and every needed per-command flag is named.

### 8. Plan and get approval

List every file with one line each: the knowledge file (in the project's
knowledge directory; recommend `.agents/knowledge/environment.md` when none
exists), the task-runner lines, the entrypoint route, any container
configuration change the user chose in steps 3, 5, or 6, and any client
sandbox setting the user confirmed in step 6 with the file that holds it.
State what each existing file gains or loses.

For the task-runner change, show the exact lines to add: the snippet from
step 7 reworked, its `# CONFIGURE:` line resolved or deleted, and every
variable the file already exports removed. Wait for approval of the list
and of that text.

Done when: the user approved the list and the exact task-runner lines;
until then nothing is written.

### 9. Write the files

Rework [assets/knowledge-environment.md](assets/knowledge-environment.md) line by line from the recorded
answers: every `# CONFIGURE:` line resolved, every section that does not
apply deleted, the project's own paths and commands as the examples. Add
the task-runner lines exactly as approved. Read
[references/devcontainer.md](references/devcontainer.md) when writing a dev container configuration
the user chose.

Then route the entrypoint: one line naming the knowledge file with its load
condition. Count the lines the entrypoint would have with the route added:

- at or under 100: add the route;
- over 100 but at or under 120: add the route and report the overrun as a
  finding for the knowledge and routing layer; trim nothing yourself;
- over 120: leave the entrypoint unchanged, add "route to environment
  knowledge" as a pending decision with a recommended row to merge or move,
  hand the overrun to the knowledge and routing layer, and name the
  knowledge file as temporarily unreachable in the report.

Done when: the knowledge file opens with its "Read this when" line and holds
the grade, the base and who chose it, the tier, the five audit items with
decisions and reasons, the control-plane classification, and the
non-interactive rules; it contains no `{{`; the task-runner lines contain
no `# CONFIGURE:` and no `{{ECOSYSTEM_VARIABLES}}`; and the route is in
place or pending.

### 10. Report

Report: each file written or changed; the pending decisions list; each
finding handed to another layer, with the layer described (for example a
token that can push to the default branch hands "push as an irreversible
action needing pre-authorisation" to the authority layer and "default-branch
protection" to the platform lifecycle layer); every by-hand step left to
the user, such as revoking or rescoping a token; and the ownership notice
for the delivered copy.

Done when: every item is in the report and no skill is named in it.

## Gotchas

- A dev container without a `~/.ssh` mount can still push: VS Code's Dev
  Containers extension forwards the host's SSH agent (`SSH_AUTH_SOCK`) and
  a git credential helper into the container. Check both under sensitive
  assets.
- `CI=true` also switches some tools into CI behaviour (a frozen lockfile on
  install, no colour, no update prompt). Name any recipe it changes in the
  knowledge file.
