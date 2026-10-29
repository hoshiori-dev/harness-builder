---
name: authority-building
description: >-
  Authority boundary — builds, revises, or audits a project's rules for what
  coding agents may do without asking. Owns the authority layer: reversibility
  classes, the written policy, allow and deny lists for Claude Code and Codex,
  the pending decisions format, and checkpoint, squash, rollback, and push
  rules. Use when agents prompt for every shell command and the user wants
  allow and deny lists; when an agent pushed, force-pushed, commented, or
  deleted something nobody authorised and the project needs rules so it does
  not recur; when defining how agents commit checkpoints, squash drafts, and
  when they may push; when an approved harness plan hands over the authority
  layer; or when an existing policy has ask entries or allows force pushes.
  Not for a single git command question, sandbox or token scope design,
  branch protection and other platform settings, or one task's pre-authorised
  actions.
license: Apache-2.0
compatibility: Recipe tests need Python 3.10+, pytest, and just; uv optional.
---

# Authority Building

The sandbox decides what an agent *can* do; the authority layer decides what
it *may* do on its own. This skill settles that line with the user from
repository evidence, then deposits it in the target project as a policy file
whose core the agent entrypoint carries into every session, permission files
for the confirmed clients, and checkpoint recipes in the project's task
runner. [§4.2]

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

Plan approval covers the outcome, the non-goals, and the bounds of the
approach, never a list of steps; say so when the user asks what approving a
plan commits them to. [§4.2]

<!-- shared:management-code-ownership -->
A script, hook, check, CI step, or task-runner recipe written into the target
project is the project's own management code: written for its role in the
language the project agreed to, readable first, failing with a message that
names what to fix, with no fallback that hides an unexpected error, and never
calling a script inside a skill directory. Tell the user that later fixes to
this plugin do not reach the delivered copy.
<!-- /shared:management-code-ownership -->

Build to the grade the plan confirmed and never thicken it on your own:
**light** is a few allow and deny entries plus one sentence in the agent
entrypoint ("commands on neither list fall to the framework default");
**medium** adds the written policy document; **thick** adds the explicit list
of the project's irreversible actions alongside the pending decisions format,
both reported as parts of the layer. [§6.1]

Hand adjacent work to its layer by role, never by skill name: sandbox mode,
network access, and token scope to the layer owning the environment;
protecting the security hooks and the policy file to the layer owning
pre-commit and CI checks and to the layer owning platform settings (required
review on those paths before merge); branch protection and force-push
blocking to the layer owning platform settings; branch
ownership, coordinator, merger, and arbiter rules for parallel agents to the
layer owning the platform lifecycle; the per-task list of pre-authorised
irreversible actions to the layer owning the spec contract; an entrypoint
budget overrun to the layer owning knowledge and routing.

Questions arrive at any step:

- Read [references/denial-handling.md](references/denial-handling.md) when a user or an existing policy
  proposes another response to a refused action.
- Read [references/checkpoints.md](references/checkpoints.md) when a user or an existing rule proposes
  stashes, hunk-level staging, or pushing drafts for remote CI, or asks why
  hard reset is denied.
- Read [references/pending-decisions.md](references/pending-decisions.md) when the user defers a decision,
  and write each item in its format.

Vocabulary: a deposited file never names this plugin, this skill, or any
authority level ladder; it names the project's own commands and clients.

## Workflow

### 1. Inspect the repository

Read, record, write nothing. Collect: the grade the harness plan confirmed
for this layer; task runner and its recipes; test, lint, and build commands;
the commit-title style of the last 30 commits; existing permission files
(`.claude/settings*.json`, `.codex/config.toml`, `.codex/rules/`,
`.gemini/`) and any existing authority or git-workflow document; secret
scanning and other security hooks; the agent entrypoint and its line count;
whether a specification workflow exists; the clients in use; evidence of
parallel agents (several agent worktrees, per-agent remote branches).

Report the facts, then the contradictions with the methodology (ask entries,
an allowed force push, a policy that restates branch rules the platform
knowledge also carries, a stash-as-checkpoint rule), each with the fix
recommended once.

Done when: every item above is recorded as observed, absent, or "ask", and
no file in the target has changed.

### 2. Settle the decisions

Ask only what step 1 could not observe, each with one recommendation:

- **Grade**, when the plan did not confirm one: recommend medium, because a
  policy agents can read turns a refusal into a decision instead of a stall;
  light only for a short-lived prototype; thick when autonomy or team size
  is high.
- **Clients**: which the user confirms. Claude Code and Codex get generated
  permission files; any other client gets a by-hand item in the report.
- **Framework files at all**: recommend yes; on no, deposit the policy alone
  and record the choice.
- **Deny list**: read [references/framework-rules.md](references/framework-rules.md) when presenting it;
  present the fixed list for acceptance as one block, not entry by entry.
- **Allow list**: propose every observed test, lint, build, format, and
  read-only command, and each task-runner recipe by name, one entry per
  recipe, with its evidence (file and line); the user confirms or trims.
  Never a runner wildcard (`Bash(just *)`, `["just"]`): it also allows the
  recipes that push. No push, publish, release, tracker write, or deletion
  of others' work enters it, as a raw command or inside a recipe
  (`push-one` included), however often history shows it; say that these are
  governed by pre-authorisation in the plan or spec, not by permission
  entries. [§4.2]
- **Ask entries**: none. If the user asks for one, propose allowing the
  read-only tools and classifying the outward ones by reversibility; add an
  ask entry only for a reason no allow or deny entry can serve, and record
  the entry with that reason. [§4.2]
- **Codex approval mode**, when Codex is confirmed: recommend `on-request`,
  because a command then asks only when it must leave the sandbox and the
  rules decide the rest; `never` for unattended runs. Do not ask about
  sandbox mode or network access: they belong to the environment layer.
- **Commit convention**: when history shows one, record it and propose
  nothing; otherwise recommend Conventional Commits (type prefix makes the
  squash message mechanical) and offer plain 50/72 titles.
- **Concurrency**: recommend single-agent, because parallel agents need
  branch ownership, a coordinator, and pre-authorised platform writes the
  project has not set up; when step 1 found parallel evidence, recommend
  parallel and cite that evidence. [§4.4]
- **Pairing mode**: ask whether the project is still in bootstrap or
  specification, or requires high alignment; record the phase and the
  condition on which it switches to two-ended approval. [§4.2]
- **Recipe language**: the project's task runner (`just`, `make`, npm
  scripts); ask before translating out of `just`.

Challenge each of these requests once, with its own reason; if the user
keeps it, record it as their choice with their reason, in the policy's
deviations section and in the report: [§4.2]

- **Per-command approval** in a running-phase project: it trades real
  safety for approval fatigue, and the sandbox is the real boundary. If
  kept, Claude Code gets no allow list and keeps the deny list; Codex gets
  `approval_policy = "untrusted"` and keeps the forbidden rules.
- **An allow entry for `git push`**: the policy already lets a
  pre-authorised push proceed without a prompt, and an allow entry would
  also cover pushes nobody authorised.
- **A co-author trailer or other attribution naming the agent**: the
  methodology forbids AI attribution in commits.
- **Pairing mode** outside its two legitimate sources (bootstrap or
  specification phase; a project requiring high alignment): it is outside
  them.

A third refusal response such as "fix the entry that blocked you" is
declined, not recorded: loosening a rule is outside agent authority and
belongs to self-protection, so the two responses and the prohibition stay
in the policy. [§4.2]

When revising an existing layer, recommend moving to the allow list any
prompt category the user reports as approved near 100% of the time, and
recommend tightening any allowed command that repeatedly caused rollbacks;
present both as recommendations, and recommend this one-time review over a
standing approval-rate metric, which is cost without benefit. [§4.2]

Read [references/reversibility.md](references/reversibility.md) when the user disputes a classification
or asks why a local commit and a push differ.

Done when: every bullet has a recorded answer and every challenge was made
once.

### 3. Plan the files and get approval

List the files by path with one line each: the policy (medium or thick),
one permission file per confirmed client, the recipe file or the recipes
added to the existing task-runner file, the entrypoint lines, and the
temporary clone step 6 creates and removes. State what each existing file
loses or gains. Wait for approval.

Done when: the user approved the list; until then nothing is written.

### 4. Write the policy

Skip at light grade: no policy document is written; the checkpoint and
attribution rules live in the recipe file's header comment (step 6), and
the entrypoint holds the one framework-default sentence (step 7). Otherwise
rework [assets/knowledge-authority.md](assets/knowledge-authority.md) line by line
against the settled answers; every `# CONFIGURE:` line resolved, every
section that does not apply deleted, and the project's own commands as the
examples. Read [references/denial-handling.md](references/denial-handling.md) when writing the refusal
section, [references/pending-decisions.md](references/pending-decisions.md) when writing the pending decisions
section (copy its format unchanged), and [references/reversibility.md](references/reversibility.md) when
writing the classification with the project's tools.

At thick grade the policy also carries the explicit list of this project's
irreversible actions, named as its platform's operations. When a
specification workflow exists, the policy states that each spec carries the
irreversible actions pre-authorised for that task, and the report hands the
format to the layer owning the spec contract.

Done when: a reader with only the policy file can state the reversibility
classes, the two approval points, the pending decisions fields and the
present-once rule, the two refusal responses and the prohibition, the
framework-default statement, the deny list's purpose, the checkpoint rules,
the attribution ban, the concurrency mode, the pairing scope, and the
self-protection rule.

### 5. Write the permission files

Read [references/framework-rules.md](references/framework-rules.md) when writing any client permission
file. Rework [assets/claude-settings.jsonc](assets/claude-settings.jsonc) into strict JSON for Claude Code
and [assets/codex-config.toml](assets/codex-config.toml) plus [assets/codex-authority.rules](assets/codex-authority.rules) for
Codex, each holding exactly the confirmed allow and deny entries and no ask
entries except those recorded in step 2 with the user's reason. The Codex
`config.toml` holds only the confirmed `approval_policy`; a kept
per-command deviation is written as step 2 states. For any other confirmed
client, write nothing and put the entries
to transcribe in the report. An existing file loses its contradicting
entries only where the user accepted the fix in step 2.

Done when: each written file parses; it contains the confirmed allow, deny,
and recorded ask entries and no others; and no allow entry matches an
outward command or a recipe that pushes, publishes, releases, or writes to
a tracker, wildcards included, except a push allow kept as a recorded
deviation.

### 6. Write the checkpoint recipes

Read [references/checkpoints.md](references/checkpoints.md) when writing or translating the recipes.
Rework [assets/checkpoint-recipes.just](assets/checkpoint-recipes.just) into the agreed task runner:
`checkpoint`, `squash-task`, `rollback`, and `push-one`, with the project's
commit convention, draft prefix, and remote, keeping its header comment.

Exercise each recipe once, never in the target's own working tree: it still
holds this layer's uncommitted files and may hold the user's changes, which
`checkpoint` and `rollback` would commit or reset away.

1. Record the target's `git status --porcelain`, `git branch --list`, and
   `git stash list`.
2. Clone it: `git clone --quiet <target> <tmpdir>`.
3. Run the target's reworked recipe file against the clone
   (`just --justfile <target>/justfile --working-directory <tmpdir> <recipe>`;
   `make -f <target>/Makefile -C <tmpdir> <target>`; otherwise copy the file
   into the clone).
4. In the clone: `push-one` on the base branch; on a new branch,
   `checkpoint` then `push-one`, both `push-one` runs exiting 1 without
   pushing; a second `checkpoint`; `squash-task` from the branch start;
   `rollback` to the branch start. Never run the push path: a push is
   outward and the approved plan did not authorise it.
5. Remove the clone: `rm -rf <tmpdir>`, as the approved plan named.

Report every output. Tell the user the project owns the copy and later
plugin fixes do not reach it. [§4.3]

Done when: every recipe ran once with its output reported; nothing reached
a remote; the clone is gone; the target's status, branch list, and stash
list match the record from item 1; and `git reset --hard` and
`git clean -fd` stay on the deny list.

### 7. Route the entrypoint

At medium and thick grade, add the policy's core to the entrypoint's
always-applicable block, so every session carries it, then one route line:
the policy path with the load condition "before pushing, taking any outward
action, and when an action is refused". The core, in the project's words:

```markdown
Act alone only on reversible, internal work. A push, comment, label,
release, or other outward action needs pre-authorisation in the plan or the
spec; otherwise add it to the pending decisions list and continue. Never
retry a refused action by another route. Loosening the authority policy, a
permission list, or a security hook is outside agent authority: propose the
change and wait.
```

At light grade, add only the sentence "Commands on neither permission list
fall to the framework's default judgement." If the additions push the
entrypoint past its budget, add them anyway, report the overrun as a
finding for the layer owning knowledge and routing, and trim nothing
yourself.

Done when: at medium and thick grade, the entrypoint holds the core and
names the policy with that condition; at light grade, it holds the one
framework-default sentence, no policy file exists, and the recipe file's
header comment states the checkpoint and attribution rules.

### 8. Report and hand off

Report: every file written or changed; each decision the user deferred, in
the pending decisions format (read [references/pending-decisions.md](references/pending-decisions.md) when any
decision was deferred); each deviation from the methodology the user kept, with
their reason; by-hand items (permission entries for clients without a
generated file; blocking force pushes on the remote, described to the layer
owning platform settings; protecting the security hooks and the policy
file, described to the layer owning pre-commit and CI checks and to the
layer owning platform settings as required review on those paths); the
needs handed to
the platform lifecycle layer when concurrency was confirmed; at thick grade,
the irreversible-actions list and the pending decisions format, named as
parts of the layer; and the statement that the project owns the deposited
recipes and permission files.

Done when: every item is in the report and no skill is named in it.

## Gotchas

- Claude Code matches rules on command text: `git -C . push` and `bash -c
  'git push'` escape a `Bash(git push *)` deny. Add the spellings the
  repository's history shows and do not chase the rest.
