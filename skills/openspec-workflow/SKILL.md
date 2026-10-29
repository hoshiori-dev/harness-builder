---
name: openspec-workflow
description: >-
  OpenSpec carrier — creates, validates, and archives OpenSpec changes inside
  pull or merge requests and installs the automation that guards them on
  GitHub or GitLab. Use when a project that runs OpenSpec asks to create,
  validate, or archive a change; asks what must happen before its pull or
  merge request can merge, or how a change is approved; asks why
  spec:approved, spec:pending, or spec:archived appeared or vanished, or why
  the archive check has not reported; or wants the OpenSpec validation, the
  archive check, or the approval labels wired into CI or repaired. Not for
  choosing between spec frameworks, deciding whether to adopt spec-driven
  development or what a specification must answer, recording the project's
  spec rules, or Spec-Kit and other frameworks.
license: Apache-2.0
compatibility: Scripts need Python 3.10+ and git; check and archive need the OpenSpec CLI; uv optional.
---

# OpenSpec Workflow

This skill carries one OpenSpec change through a pull or merge request: the
approval package before the tasks, implementation, ready before archive, and
the archive inside the request after the review closes, so the default branch
never holds an unarchived change. It also installs the check, the withheld
archive check, and the `spec:*` labels that make those gates visible.

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

<!-- shared:management-code-ownership -->
A script, hook, check, CI step, or task-runner recipe written into the target
project is the project's own management code: written for its role in the
language the project agreed to, readable first, failing with a message that
names what to fix, with no fallback that hides an unexpected error, and never
calling a script inside a skill directory. Tell the user that later fixes to
this plugin do not reach the delivered copy.
<!-- /shared:management-code-ownership -->

**Precedence.** An explicit user instruction, then the project's
specification contract (the file the agent entrypoint names for spec work,
often `.agents/knowledge/spec-workflow.md`), then the defaults below. Every
reply that applies a rule says which source it came from ("the contract says
a maintainer archives", "no contract rule; the default applied").

| Point | Default when the contract is silent |
|---|---|
| Approval mode | conversational: the user states approval and the agent records it in the request description; recommend **recorded** (`spec:approved` plus the label workflow) when more than one person approves or agents run unattended |
| Design | warranted when more than one reasonable approach exists or the change touches structure, interfaces, dependencies, or files outside the record; none for a wording change |
| Archive executor | the implementer archives, after the review closes, by the tool's non-interactive archive command, and on a fork's branch a maintainer does so |

Where the contract is silent on a point the work at hand depends on, ask
with the default as the recommendation and its reason, and wait; never
choose silently. When a default applied, say so and name the skill that owns
the specification and completion layer as the way to record another rule.
If the user declines that handoff, proceed on the defaults, say which ones
applied, and list the contract update as remaining work.

**The CLI owns the tree.** Every operation the OpenSpec CLI has a command
for (init, new change, validate, archive, show, status) runs through that
command. Before the first use in a session read `openspec --help` and the
subcommand's `--help`; when a remembered command is not listed, use the one
the help lists. Never create a change directory or its `.openspec.yaml` by
hand. If `openspec` is not on PATH: say the CLI is missing, name it as the
prerequisite the project must provide, point at the tool's own
documentation without printing an install command, create nothing, and add
the blocked step to the pending decisions.

**Strict validation cadence.** Run `openspec validate --all --strict
--no-interactive` after each artifact edit, before publishing the draft,
before marking the request ready, and after archiving. Fix every error or
warning your edit caused before going on.

**Labels are read, never set.** In recorded mode `spec:pending`,
`spec:approved`, and `spec:archived` are state the label workflow keeps from
the tree and an approval record. Never add or remove one; only a person with
write permission adds `spec:approved`. When that person adds it, the
workflow records the approver, the commit, and a hash of the package (every
file of the unarchived change except `tasks.md`) in a comment; an edit to
the package changes the hash, the record no longer matches, and the workflow
drops `spec:approved` and puts `spec:pending` back until that person re-adds
the label after reading the new version. Asked to add it to your own request: decline, say a person
with write permission adds it and the workflow records it, and put the step
in the pending decisions. A conversational-mode project records approval in
the conversation and carries no `spec:*` labels; for the recorded mode, name
the skill that owns the specification and completion layer.

**The archive is the freeze.** Never edit anything under the archive
directory; a behaviour that must change gets a new change. A commit after
the archive commit means the approved version no longer exists: say so and
ask for the gate again before pushing or handing over. [§4.2]

Hand off by role, never by name: whether or how strictly to adopt
spec-driven development and what a good specification answers go to the
skill that teaches that methodology; setting or changing the approval mode,
the design rule, or the archive executor goes to the skill that owns the
specification and completion layer; the checks workflow and its gate to the
skill that owns the hard-boundary layer; remote label sync tooling to the
skill that owns the platform lifecycle layer. Answer no practice-level
question yourself.

## Workflow

Steps 1–7 carry a change; step 8 installs or repairs the automation. Enter
at the step the request names, after step 1.

### 1. Settle the rules and the tool

Read the contract, `openspec/config.yaml`, and the CLI's help. Note the
approval mode, the design rule, and the archive executor with their source;
ask for any the work depends on that is missing.

Done when: each of the three is stated with its source, and the CLI is
present (or its absence is in the pending decisions).

### 2. Decide whether the change needs a delta spec

Product behaviour gets a change with delta specs. A change to the project's
own harness, tooling, checks, workflows, or documents gets none: say no
delta spec applies and recommend no change record, because the harness is
covered by its checks and a spec would be a second copy; ask whether the
user wants a recorded design anyway. If they do: create the change with the
CLI, add `skip_specs: true` to the `.openspec.yaml` it wrote, and write a
proposal with Acceptance, a design only when the rule warrants one, tasks
only after approval, and no delta spec.

### 3. Write the approval package

Create the change with `openspec new change <name>` (or the tool's own
propose skill), then write the proposal, the delta specs, and the design when
the rule warrants one. Read
[references/artifact-roles.md](references/artifact-roles.md) when writing or
reviewing any of them. The proposal ends with `## Acceptance` holding
**Becomes true** and **Stays true**, so the end is checkable before any
code is written [§4.1]; every design Goal and Non-Goal carries a
"Checked by" clause and decisions name their rejected alternatives, with no
steps. A task list the propose step generated stays a draft: it is
after-approval material.

Done when: strict validation passes and the package meets the formats
above, with any not-yet-checkable Acceptance item named.

### 4. Publish the package and wait for the first gate

Open the draft request with the proposal, delta specs, and design; its
description links the change and states that the task list follows
approval, since approval covers the outcome and the bounds of the approach,
not the steps. [§4.2] The gate is the contract's: in recorded mode a person
with write permission adds `spec:approved`; in conversational mode the user says the
package is approved and the agent records that in the request description,
waiting for no label. Asked for the tasks before the gate closes: say they
follow the gate, name the gate that is open, and write none.

Done when: the gate the contract defines has closed.

### 5. Finish the tasks and implement

Finish `tasks.md` (each task names its verification), validate strictly, and
implement task by task. Tick a task only after its verification ran and
passed; asked to tick one whose check has not run, run it or ask for it to
be run first.

Done when: every task in `tasks.md` is ticked, each after its named
verification ran and passed, and strict validation passes.

### 6. Mark the request ready; archive nothing

When the last task is verified, validate strictly and mark the request
ready. Asked to archive and mark ready in one go: mark it ready, archive
nothing, and say the archive happens after the review closes. In recorded
mode explain the withheld check: the required archive check does not report
while a related change is unarchived on a ready request, so the merge stays
blocked with nothing red, and the archive commit is what lets it report. On a
draft the check job only warns and the required name stays unreported too,
so a success on the draft's head cannot carry over once it is marked ready;
a draft cannot merge, so the withholding blocks only once the request is
ready.

Done when: the request is ready and the change is still unarchived.

### 7. Archive after the review closes

Refuse to archive a change with an unticked task: name the open task and
archive nothing. Then follow the executor from step 1:

- **Implementer** (and the branch is not a fork's): on the request's branch,
  run this skill's script, which archives every related change, validates
  strictly, and commits:

  ```bash
  python3 <this skill's directory>/scripts/spec_changes.py archive \
    --base origin/<target> --head HEAD --message "<message in the project's convention>"
  ```

  While a task is open or a path under `openspec/` is uncommitted it exits 1
  naming it and changes nothing. When an archive, the validation, or the
  commit fails partway, it restores `openspec/` to HEAD and says so, so
  nothing stays half-archived; fix the cause and run it again. After a
  successful run, a second run exits 0 with nothing to do.
  Report the validation result and the commit. Run
  [scripts/spec_changes.py](scripts/spec_changes.py) with `--help` first when
  an option is unclear.
- **Maintainer, or a fork's branch:** archive nothing. Report the change
  ready for that person and list their step with the tool's own commands,
  since they do not have this skill's script: first confirm every task in
  each change's `tasks.md` is ticked, because `--yes` archives with open
  tasks; then per change `openspec archive <name> --yes` (add
  `--skip-specs` when its `.openspec.yaml` has `skip_specs: true`); then
  `openspec validate --all --strict --no-interactive`; then commit and push.

Done when: the archive commit is on the branch, strict validation passes on
the archived tree, and (recorded mode) the required check reports; or the
step is handed to the named person.

### 8. Install or repair the automation

1. State the platform and default branch read from the remote
   (`git remote -v`, `git symbolic-ref refs/remotes/origin/HEAD`). Ask only
   when neither can be read (recommend GitHub and the current branch) or the
   user's stated target differs from what you observed.
2. Find the project's checks workflow and its gate (GitHub) or
   `.gitlab-ci.yml` (GitLab). If there is none to join, say so and
   recommend routing to the skill that owns the hard-boundary layer to build
   it first, because the checks workflow and its gate belong there. The
   alternative, if the user agrees: create a minimal checks workflow
   (`pull_request` plus `push` to the default branch, top-level
   `permissions: {}`, a gate job) that holds the two jobs. Install nothing
   before the choice.
3. Ask whether to deposit [assets/spec_changes.py](assets/spec_changes.py)
   as the project's `scripts/spec_changes.py` with its test as is (the
   default when the agreed management language is Python) or to treat it as
   a reference implementation to rewrite in that language. Write nothing
   until the user chooses.
4. Present the plan naming every file; after approval:
   - Read [references/github.md](references/github.md) when the platform is GitHub.
   - Read [references/gitlab.md](references/gitlab.md) when the platform is GitLab.
   - Read [references/config-yaml.md](references/config-yaml.md) when
     recording the artifact rules; propose them and write them only after
     the user confirms.
5. Labels: merge the `spec:*` rows into the project's existing label file.
   When the project has a label-sync tool, print its dry-run plan of the
   additions and removals against the remote, apply it through that tool
   only after the user approves, then read the remote's labels back and
   report them. With no such tool, show the additions the merged rows imply
   against the remote (`gh label list` or the platform's label page),
   install none, name the skill that owns the platform lifecycle layer, and
   list the sync as remaining work.
6. Maintainer-only settings (the required check, rulesets, "Pipelines must
   succeed", GitLab's `SPEC_LABELS_TOKEN` and pipeline schedule) go to the pending decisions with the recommended value; continue
   with everything else. A check the platform has never observed blocks
   every request once required, so sequence a green run first.
7. GitLab: tell the user that labels and approvals take effect on the next
   pipeline on the default branch, which the schedule runs.

Decline an archive bot (no platform token can push to a fork, and that job
would be the only one with write access to contents; point at the archive
command) and comment commands (point at `status` run locally or in the check
job's log). [§3.2]

Done when: the check job is in the checks workflow and the gate's
dependencies, the label workflow (GitHub) or jobs fragment (GitLab) exists,
the label rows are merged, `scripts/spec_changes.py` and its test are the
project's own, the artifact rules are recorded, every action is SHA-pinned,
every job declares its permissions, no job holding a writable token checks
out or runs the head, and the required check and the label sync are in the
pending decisions.

### 9. Report

End with the rules applied and their source, the state of the request and
of the change record, the check's state, and the pending decisions list.

## Gotchas

- `openspec archive <name> --yes` archives a change with open tasks after a
  one-line warning; the bundled script refuses first, so prefer it over the
  bare command.
- The archive directory name carries the date, so the change link in the
  request description changes after archiving; both forms are valid.
- A tool's lowercase `design.md` is a technical design; a root `DESIGN.md`
  is a different, visual-design format. Never rename one into the other.
