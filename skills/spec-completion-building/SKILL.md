---
name: spec-completion-building
description: >-
  Specification and completion contract — settles and deposits how a
  target project specifies work and when a task counts as done. Owns the
  specification and completion layer. Use when a harness build or
  improvement reaches that layer; when asked how specs, approval gates, or
  the completion standard should be set up; when agents stop at "tests
  pass" or never stop and the project needs a written definition of done;
  when the agent entrypoint or knowledge base contradicts the specs on
  approval or behaviour; when spec-workflow insertion markers await
  filling; when the approval mode changes; or when existing specs have
  drifted from the code. Not for writing one spec, deciding whether to
  practise spec-driven development, or running, installing, or automating
  one spec tool.
license: Apache-2.0
compatibility: Scripts need Python 3.10+; uv optional.
---

# Specification and Completion Building

An agent without an approved goal anchors on the first code it writes, and an
agent without a checkable finish either stops at "the tests ran" or never
stops. This skill settles with the user how the target project aligns before
work starts and how it decides work is done, then deposits that as a
specification contract in the project's own words, points the entrypoint at
it, and hands the spec tool itself to the skill that owns that tool. [§4.1]

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

<!-- shared:pending-decisions -->
When a step is blocked on a decision only the user can make, continue with
every step that does not depend on it and add the blocked item to a pending
decisions list. Each item states: what is blocked and why; the options; the
recommended option and its reason; which finished work each option would
change. Present the list once, at the end or when nothing else can proceed,
never one question at a time.
<!-- /shared:pending-decisions -->

Take recorded variables, never re-ask them. The maintenance horizon, the
team size, and the autonomy level (do agents run unattended?) come from the
approved harness plan or the user's earlier answers in this build when they
are recorded there; cite that source next to every recommendation derived
from them. Ask only a variable that is neither recorded nor observable.

Never initialise, install, configure, or run the spec tool, and print no
install command. Adoption, the tool's layout, its commands, and its
automation belong to the carrier skill (step 6).

Hand adjacent work to its owner by role, never by skill name: task-runner
recipes to the layer owning hard boundaries; the harness self-check to the
layer owning entropy; the three insertion markers to the layer owning the
platform lifecycle; the authority levels that attach to the gates and the
format of pre-authorised actions to the layer owning authority; writing a
specification to the skill that owns the spec-driven development method.

Deposited files speak the project's language: no spec-tool command, no path
inside this skill, and no word this skill coined ("carrier", "layer",
"package gate", "freeze gate", "selecting fact", or the bare noun
"request"). Write the tool's name, "the spec and its design", the
platform's "pull request" or "merge request".

## Workflow

### 1. Inspect the target

Run [scripts/detect_spec_tooling.py](scripts/detect_spec_tooling.py) on
every run (`--help` lists options), from this skill's directory against the
target checkout, and keep its stderr summary line for the report:

```bash
python3 scripts/detect_spec_tooling.py --root <target>
```

(`uv run scripts/detect_spec_tooling.py --root <target>` works too.) It reads
only. Its JSON lists each spec tool found (OpenSpec, Spec-Kit, Kiro,
committed `SPEC.md`/`PLAN.md` or spec directories) with spec and change
counts and owned paths, entrypoint lines pointing at spec artifacts, and
documents that look like they restate requirements outside the tools' and
the installed skills' directories. Exit 1 means a path was unreadable:
record it and read that path by hand if permissions allow.

When neither `python3` nor `uv` exists, check the same places yourself:
`openspec/`, `.specify/`, `specs/NNN-*/`, `.kiro/`, root `SPEC.md` and
`PLAN.md`, issue and pull or merge request templates, and every markdown
file mentioning acceptance criteria. Record "inventory by hand: no Python".

Then read in full, writing nothing:

- The agent entrypoint and every knowledge file: list each sentence that
  states what the system does or restates acceptance, approval, or gate
  rules. The script cannot see a plain sentence such as "five failed logins
  lock the account".
- The approved harness plan and the earlier answers of this build: horizon,
  team size, autonomy, and whether the hard-boundary, entropy, and platform
  lifecycle layers are planned, done, or omitted.
- An existing specification contract in the knowledge base, and every file
  holding the marker `<!-- harness: spec-workflow -->` (search the tree).
- The task runner and the test runner: a scoped fast check (single file,
  module, or diff) and whether the runner accepts a file path.
- A harness self-check the entropy layer deposited (a recipe or CI job that
  checks the harness itself).
- `.gitignore`, for a handoff or scratch directory.
- When specs exist: each requirement against the code it names. Read
  [references/spec-drift.md](references/spec-drift.md) when one disagrees with
  the code or with another spec.

When a contract already exists, ask nothing it records (level, carrier,
gates) and plan in step 3 only what this run changes:

- **Markers to fill**: run step 5 from the contract as it stands.
- **A recorded value the user changes**: update every contract passage that
  depends on it, then refresh every marker block that states it (step 5).
  For a gate-mode change that is the gate-mode line and the whole
  recorded-or-conversational paragraph below the gates. Lines that do not
  depend on the value stay unchanged.
- **A pending item now settled by an observed fact** (the entropy layer
  deposited a harness self-check, the hard-boundary layer added a scoped
  recipe, markers now exist): fill that item, refresh any marker block it
  affects, and drop it from the pending list. Re-ask nothing.

Change the contract on nothing else.

Done when: the summary line (or the by-hand note) is recorded; every tool,
restating document, behaviour sentence, marker, scoped command, self-check,
and contradiction is listed with its path; each of the three variables is
marked with its source or as unknown; and no file in the target changed.

### 2. Settle the decisions

Ask everything still open in one numbered round, each with one
recommendation and its source or selecting fact. A variable from step 1
still unknown comes first, recommended from the evidence (a scheduled agent
job or bot-opened pull requests suggest unattended runs; none suggests
attended).

1. **Level.** Recommend spec-anchored (specs stay the living description of
   the system) when the project is maintained past one release; otherwise
   spec-first (a spec builds the change, then is archived). Name the
   horizon as the reason.
2. **Carrier.** Apply in order and stop at the first match: a carrier
   already in use is kept without asking; a solo, small project gets the
   lightweight carrier (committed per-change `SPEC.md`/`PLAN.md`, or plan
   mode); a project with existing code gets OpenSpec; an application
   delivered feature by feature from zero gets Spec-Kit. Read
   [references/carrier-choice.md](references/carrier-choice.md) when
   presenting the alternatives, when the carrier in use does not fit the
   project's shape, or when it is none of the three. [§4.1]
3. **Gate mode.** Two gates always exist; recommend their mode from team
   size and autonomy: conversational for a solo maintainer or a pair in the
   conversation; recorded otherwise, and whenever agents work with no one in
   the conversation. Read
   [references/approval-gates.md](references/approval-gates.md) before
   asking, and when the user asks for a job that archives or approves.
4. **Spec-less changes.** Confirm that a change to the project's own
   harness, tooling, checks, workflows, or documents carries no spec.
5. **Fast check.** Confirm the scoped command found in step 1 as the fast
   check and the full run as the task-end check. With none found, name the
   gap to the layer owning hard boundaries by description ("a seconds-long
   test or type check for one file or the diff"); when that layer is omitted
   or already done, add it to the pending list instead. Propose only a
   command found in the repository; it is run once in step 4 before it is
   written down. [§4.3]
6. **Handoff location.** Recommend `.agents/handoff/`, gitignored, because
   handoff notes carry logs and credentials more often than code does; the
   alternative is the system temporary directory. [§4.3]
7. **Restating documents and drift.** For each restating document: make it
   a spec, a pointer to the spec, or delete it; recommend the pointer. For
   each drifted spec, fix or delete: read
   [references/spec-drift.md](references/spec-drift.md) when presenting
   them, or when the user asks for specs covering every module. [§5.1]

The user overrules a recommendation: challenge once with the evidence, then
design every later step around the choice. A deferred item goes to the
pending list with its options and recommendation, and every step that does
not depend on it continues.

Done when: each of the seven has an answer recorded with who gave it (user,
plan, or observed fact), or sits on the pending list.

### 3. Plan the files and get approval

List every file by path with what it gains or loses: the contract
(`.agents/knowledge/spec-workflow.md`, or the project's knowledge directory),
the entrypoint pointer line, the `.gitignore` line (none when the user chose
the temporary directory), each marker file, and each restating document or
spec the user decided to change or delete. Wait for approval.

Done when: the user approved the list; nothing is written before.

### 4. Deposit the contract

Rework [assets/knowledge-spec-workflow.md](assets/knowledge-spec-workflow.md)
line by line: resolve every `# CONFIGURE:` line, delete every section that
does not apply.
Read [references/contract-design.md](references/contract-design.md) when reworking it.
Read [references/completion-boundary.md](references/completion-boundary.md) when writing its
completion section.

- Fast check: run the recorded scoped command once on one file before
  writing it down; a command that fails goes to the pending list instead.
- Spec-less rule: name the carrier's marker for such a change only when the
  project already records one; name the harness self-check only when the
  entropy layer deposited it. Otherwise state the rule in words, name no
  check, and put the self-check reference on the pending list with the
  entropy layer as its precondition.
- Drift: name every spec whose decision was deferred as not yet
  authoritative.
- Add one line to the entrypoint's routing: the contract's path with the
  condition "before starting a change that alters behaviour, and before
  writing or approving a spec". Replace each behaviour sentence the user
  chose to move with a pointer to the spec.
- Append [assets/gitignore-handoff.txt](assets/gitignore-handoff.txt) to
  `.gitignore` when the repository directory was chosen and the line is not
  already there.
- Apply each restating-document and drift decision the user gave.

Done when: the contract names level, carrier, both gates with their mode,
who freezes, scope, fast and task-end checks, worktree cleanup, and the
handoff location; `grep -n '{{' <contract>` returns nothing; it contains no
spec-tool command, no path into this skill, no coined word, and no bare
"request" where the platform's "pull request" or "merge request" belongs; and the
entrypoint points at it with a read condition and restates none of it.

### 5. Fill the markers

For each file holding `<!-- harness: spec-workflow -->`, write the text for
that file between the marker and an end marker
`<!-- /harness: spec-workflow -->` on its own line.
Read [references/approval-gates.md](references/approval-gates.md) when writing each block.
When an end marker already follows, replace only the lines between the two.
Change nothing else in the file. With no marker in the target, check the
plan's status for the platform lifecycle layer: planned or not yet built,
add "fill the spec-workflow markers" to the pending list with that layer as
its precondition; omitted, record nothing and attempt no fill.

Done when: each marker is followed by text matching the contract's gates and
mode and one end marker; the marker lines are unchanged; and a second fill
on the unchanged contract produces no diff.

### 6. Hand off the carrier

Hand adoption, layout, and automation to the skill that owns the chosen
carrier, described by what it owns: for OpenSpec, the skill that owns
OpenSpec changes, archiving, and status labels; for Spec-Kit, the skill
that owns Spec-Kit features and their task completion; for the lightweight
carrier, the skill that owns per-change `SPEC.md`/`PLAN.md` and plan-mode
alignment. Pass it the settled level, gate mode, and spec-less rule; ask it
to add its spec-less marker to the contract. For any other framework the
user keeps, record the implementer as the executor of every gate and the
structural check the project adopts, list the framework's automation as
remaining work, and hand off nothing.

Done when: the handoff names an owner by role and no command, or the by-hand
executor and remaining work are recorded.

### 7. Read back in a clean context

Give a clean-context subagent only the target's file paths (contract,
entrypoint, marker files) and have it answer from them alone: the level; the
carrier; where a new spec goes; what a new spec must contain (all four
completion answers and four quality rules); who approves each gate and how
it is recorded; when the draft request opens and when tasks are written;
who freezes the record and what a later commit means; what a harness change
carries; the fast check. Fix every gap it reports and ask again. Without a
subagent, re-read the files from the top in a fresh pass, answer the same
questions, and record "read-back not clean-context".

Done when: every question is answered from project files alone and every
gap the read-back found is fixed.

### 8. Report

Report the files written or changed; each decision with its source (user,
plan, observed fact); the carrier handoff; gaps named to other layers; the
pending decisions list, presented once; and every degradation (inventory by
hand, read-back not clean-context).

Done when: every decision in the contract traces to the user, the plan, or
an observed fact, and the report names no skill.

## Gotchas

- Acceptance criteria copied into an issue template or the entrypoint are
  the most common contradiction: the copy drifts while the spec moves. The
  copy becomes a link to the spec's scenarios.
- Freezing a record early to turn the awaiting-archive check green freezes
  a version nobody reviewed. Leave the check red until the review closes.
