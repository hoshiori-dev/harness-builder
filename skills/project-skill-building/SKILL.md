---
name: project-skill-building
description: >
  Writes and repairs the skills a project keeps for its own agents, so each
  recurring procedure loads on the right task and runs the same way every
  time. Use when a recurring procedure should become something the agent loads
  by itself ("turn our release steps into a skill", "the agent keeps getting
  the migration SOP wrong"); when a project skill misbehaves: never loads,
  loads on the wrong task, skips or rushes a step, works shallowly, ignores
  its references, or has grown long; when asked to review, prune, or diagnose
  a SKILL.md; or when the knowledge and routing layer hands over a skill
  definition to write. Not for AGENTS.md, CLAUDE.md, or knowledge files (the
  knowledge and routing layer handles those), human documentation, application
  features that happen to be called skills, or the skills this plugin itself
  ships.
license: Apache-2.0
compatibility: Scripts need Python 3.10+; uv optional.
---

# Project Skill Building

A project skill is a self-contained procedure the agent loads on demand:
the release steps, a migration, a review nobody may skip. Knowledge files
hold facts and architecture; a skill holds a workflow, and its description is
permanent context cost on every turn, so each one must earn its place by
supplying what the agent lacks or by making one process run the same way
every time. [§2.3] Every judgement below (what the agent lacks, what counts
as obvious, what is a no-op) is made against the least capable model tier the
skill must carry, never the model at hand.

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

<!-- shared:management-code-ownership -->
A script, hook, check, CI step, or task-runner recipe written into the target
project is the project's own management code: written for its role in the
language the project agreed to, readable first, failing with a message that
names what to fix, with no fallback that hides an unexpected error, and never
calling a script inside a skill directory. Tell the user that later fixes to
this plugin do not reach the delivered copy.
<!-- /shared:management-code-ownership -->

Hand work off by role, never by skill name. This skill never edits the
entrypoint, and whether a process deserves a skill at all was settled by the
layer responsible for knowledge and routing before the definition arrived
here. [§2.3]

## Workflow

Creating a skill runs steps 1 to 11. Improving, reviewing, pruning, or
diagnosing an existing skill starts at step 12, which routes back into the
sequence.

### 1. Define

Write down: the task unit the skill covers (one coherent unit; too narrow
collides with neighbours, too broad triggers unreliably); the trigger list,
including indirect phrasings that never name the domain; what the agent lacks
that makes the skill necessary; the invocation mode; the least capable model
tier the skill must carry. When nothing in the repository names the model
tier, ask before judging what the skill must spell out; when nothing shows
whether the process runs on every matching task or only when a human asks,
present model-invoked as the recommendation with the context cost it carries
and wait. Read [references/value.md](references/value.md) when deciding
whether the skill adds anything a bare agent lacks, or which instruction
pattern (checklist, validation loop, template, gotcha) fits the process.

Done when: all five answers are written, and either the value answer is
non-empty or the finding "a bare agent on the floor tier already does this
well" has been reported as a recommendation to the user (and to the layer that
handed over the definition, when one did) with no skill written.

### 2. Fix the tests

Before the first edit, record: at least three prompts that must load the
skill and three near misses that share vocabulary but must not, each with
its expected load decision; at least two outcome tasks with a rubric of
observable requirements; the critical failures; the passing threshold. No
prompt names the skill.
Read [references/testing.md](references/testing.md) when writing these cases
or when the host can dispatch clean-context subagents. When it cannot, record
that degradation for the final report: the cases are written, not run, and
the skill is never called tested; the authoring agent never grades its own
output.

Done when: every item above exists in writing with its expected result, and
the subagent availability is recorded.

### 3. Present and get approval

Show the user, in one message: the definition, the trigger list, the test
cases with rubric and threshold, a recommendation on every open choice
(invocation mode, script language, and the linter delivery: delivered or not,
as is in Python or rewritten in the agreed language, and where it will live),
and the exact files to create or change, with paths, including the linter and
its test file when delivery is recommended. Wait. When the user amends
anything, record the amended cases as the tests of record, restate the whole
set once, and wait again. The approved set authorises those files and nothing
else. When only some open choices are answered, the user may approve the set
except those choices: work that does not depend on them proceeds, and each
unanswered choice (for example the script language and the scripts it
affects) goes to the pending decisions list.

Done when: the user has agreed to the final set, or to all of it except the
choices on the pending decisions list, and until then no file under the
project's skill directory exists or has changed.

### 4. Scaffold

Copy [assets/skill-template.md](assets/skill-template.md) to
`<skills-dir>/<name>/SKILL.md` and rework it line by line. Take `license` from
the project's LICENSE file, or ask; omit the line when the project has none.
`name` equals the directory name: lowercase letters, digits, single hyphens,
at most 64 characters. Create `scripts/`, `references/`, `assets/` only when a
file goes in; a skill with none ships `SKILL.md` alone.
Read [references/spec-portability.md](references/spec-portability.md) when
the user wants the skill to load only when invoked by name, or when a
frontmatter field outside `name`, `description`, `license`, `compatibility`,
`metadata`, `allowed-tools` is about to be written.

### 5. Describe

Write the description: third person; the skill's leading word first; most of
the length on triggers ("Use when …"), one per branch, covering direct and
indirect phrasings; a "Not for …" clause naming the neighbours; nothing the
body also says. Read
[references/description.md](references/description.md) when drafting or
rewriting a description.

Done when: a reviewer reading only the description can tell which requests
load the skill and which adjacent ones do not, and no sentence of it recurs
in the body.

### 6. Write the body

Order: title, one purpose paragraph, rules every branch needs, numbered
steps, gotchas. End a step with `Done when:` only where the boundary is
checkable from observable evidence and changes how the step is executed or
judged; make it exhaustive where thoroughness matters. Disclose material only
some branches reach into `references/` files, each linked at first mention
as `Read references/x.md when <condition>`, never "see references/". Give
one default per decision as a recommendation and reduce the alternative to a
sentence. Read [references/hierarchy.md](references/hierarchy.md) when
deciding what stays in `SKILL.md` and what moves to a reference, when a step
needs a boundary, or when choosing a leading word.

Done when: every `Done when:` can be judged done or not done from evidence,
every reference is linked with a condition, and no decision presents two
equal options.

### 7. Bundle scripts

Bundle a script only when the same logic would be regenerated identically on
every run (a validator, a parser, a formatter), or when a command needs long
argument assembly or output filtering the agent would otherwise rebuild by
trial. A one- or two-line command stays inline in the step; logic that
differs from run to run is an inline instruction. [§2.4] Recommend Python with PEP 723 inline
metadata, standard library first, runnable on plain `python3`, unless the
project's community language is TypeScript or the user chooses otherwise;
confirm the language before writing. Every script obeys the rules in
[references/scripts.md](references/scripts.md); read it when writing or
reviewing any bundled script, or when choosing its language.

Done when: each script answers `--help` with an example, exits 2 with usage
on stderr for bad arguments, exits 0 or 1 otherwise with data on stdout and
diagnostics on stderr, prints identical output on two runs over the same
input, never prompts interactively, pins every dependency to an exact
version, summarises output above about 10,000 characters unless `--full` or
`--output` is given, and `SKILL.md` carries a `compatibility` line naming its
runtime.

### 8. Prune

Three passes over everything written or touched, description included, in
order: deduplicate (each meaning keeps the copy the hierarchy ranks higher;
the other goes); relevance (delete lines that no longer bear on the skill);
no-op hunt (delete, whole, every sentence that would not change behaviour on
the least capable tier the skill carries; never reword it softer). Read
[references/pruning.md](references/pruning.md) when running the passes or
when two readers disagree whether a line is a no-op.

Done when: all three passes have run in order over every touched file, the
description included, and each deleted sentence and each challenged but kept
sentence is listed with its pass and reason.

### 9. Lint

Run the linter shipped with this skill,
[`assets/lint_skill.py`](assets/lint_skill.py), over the pruned skill:
`uv run <this-skill>/assets/lint_skill.py --skill <dir>` when `uv` is
installed, `python3 <this-skill>/assets/lint_skill.py --skill <dir>`
otherwise (same findings; `--json` for machine output). `<this-skill>` is
the directory this `SKILL.md` was loaded from. Fix every error and
re-run until it exits 0. For each warning, apply it or write down why it does
not apply.

Done when: the linter exits 0 and every remaining warning has a stated
reason.

### 10. Test

Run the recorded cases as
[references/testing.md](references/testing.md) prescribes when clean-context
subagents exist: every trigger prompt and near miss at least twice and each
outcome task once, on the least capable tier the skill claims, in an isolated
worktree with the candidate exposed to skill discovery, loading observed
through host telemetry or the neutral `SKILLS_LOADED` line, graded by a
subagent that produced none of the outputs. [§3.4] On a failure, revise the
instruction, never the prompt, then repeat steps 8 to 10 for the affected
cases. A floor-tier solver that cannot complete the task with the skill
loaded is a finding about the claimed tier: strengthen the instruction or ask
the user to raise the tier; never escalate the solver silently.

Done when: every case has a result or a recorded reason it was not run, and
the test report names prompts, tier, scores against the pre-declared rubric,
and every degradation.

### 11. Deliver and report

Act on the linter delivery answer approved at step 3; when that answer now
changes the files, present the changed set and wait again. Delivered: place a
copy of `assets/lint_skill.py` (as is, or rewritten in the agreed language), with
[`assets/lint_skill_test.py`](assets/lint_skill_test.py) or its rewrite beside
it, where the project keeps management scripts, and state in the report that
the layer responsible for the harness self-check owns wiring the linter into
the project's check or CI once its confirmed grade allows the structural tier.
[§5.3] Declined: lint from the plugin's copy in `<this-skill>`, the directory
this `SKILL.md` was loaded from, record the decision, and leave no linter in
the project. Description matching is probabilistic, so when the finished skill
is one the project cannot afford to miss, state in the report that the
entrypoint must name it by scenario and that the layer responsible for
knowledge and routing does so. [§2.3] Close with the test report and the
pending decisions list.

Done when: the report lists files written, lint result, test results or
recorded degradation, the linter decision, the wiring owner for the
delivered linter, any routing handoff, and every pending decision.

### 12. Diagnose an existing skill

Map the symptom to its cause in the skill's text before touching anything.
Read [references/failure-modes.md](references/failure-modes.md) when
improving, reviewing, pruning, or diagnosing any existing skill; it holds the
symptom index and the ordered fixes. Then run step 2 (tests first), step 3
(approval), apply the smallest general fix, and run steps 8 to 11.

Done when: the symptom names one cause in the skill's text, the fix is the
smallest change that addresses that cause, and steps 8 to 11 have run on it.

## Gotchas

- The linter's reachability check follows one hop: a file linked only from a
  reference that `SKILL.md` links counts; one linked from a deeper file does
  not.
