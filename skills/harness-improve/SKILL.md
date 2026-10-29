---
name: harness-improve
description: >-
  Harness improvement entry — audits a project's existing agent harness, then
  repairs, hardens, thins, migrates, or re-layers it with the user behind one
  approved plan. Use when invoked by name to find what is stale, duplicated,
  contradictory, unreachable, missing, or excessive across AGENTS.md,
  CLAUDE.md, knowledge files, project skills, hooks, permissions, and CI; when
  agents keep following an outdated command or rule; when a prototype becomes
  a long-lived product and its harness must harden; when an entrypoint or a
  gate has grown too heavy; when moving between OpenSpec, Spec-Kit, and
  lightweight specs or between GitHub and GitLab; or when rules sit in the
  wrong layer. Not for a repository with no harness yet (harness-create), a
  single layer built on its own, application test or CI fixes, or README,
  CONTRIBUTING, and SECURITY.
license: Apache-2.0
disable-model-invocation: true
---

# Harness Improve

A wrong or stale harness is worse than none: an agent trusts it and builds
on the lie. This entry audits what a project already has, classifies every
defect and every excess with evidence, lets the user choose the repair or
rebuild and the kind of restructuring, re-grades only the layers the work
touches, and executes one approved plan layer by layer through the skills
that own those layers, with a commit per verified layer, a clean-context
read-back, and a closing report. [§5.1] [§6.3]

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

Read [references/pending-decisions.md](references/pending-decisions.md) when the first item is added to the
list, and write every item in its format.

<!-- shared:management-code-ownership -->
A script, hook, check, CI step, or task-runner recipe written into the target
project is the project's own management code: written for its role in the
language the project agreed to, readable first, failing with a message that
names what to fix, with no fallback that hides an unexpected error, and never
calling a script inside a skill directory. Tell the user that later fixes to
this plugin do not reach the delivered copy.
<!-- /shared:management-code-ownership -->

**Drift first.** A specification that contradicts the code, or a harness
that contradicts itself, is fixed or deleted before anything is built,
thinned, hardened, or migrated on top of it. If the user wants other work
first, state this rule once; if they still decline, add the drift to the
pending decisions list and leave every contradicted file and rule out of
the remaining work. [§5.1]

**Keep what works.** The project's task runner, lint configuration, branching
habit, commit convention, and spec carrier stay the source of truth while
they are in use. A tooling migration the audit suggests is a separate
recommended change for the team to decide; no repair item depends on it.
[§6.3]

**A user's disposition binds.** When the user keeps a constraint the report
proposed to thin or remove, record their disposition and reason on the
finding; no later step removes or weakens that constraint.

**Route by role.** Never name a layer builder; route as step 7 states.
Name only the creation entry `harness-create` (step 1) and the plugin's
`harness-verifier` agent (step 8); refer to every other skill by its role.

README, CONTRIBUTING, and SECURITY are never written; a contradiction with
the harness found there is reported as a suggestion.

## Workflow

### 1. Take the request and look for a harness

Record any text after the invocation as the user's goal or complaint: a
complaint ("agents run the old test command") is a lead the audit checks
first, not the audit's whole scope; a restructuring goal ("Spec-Kit to
OpenSpec, GitLab to GitHub") is recorded for confirmation in step 4 and not
acted on before the audit.

Look for any harness artifact: an agent entrypoint (`AGENTS.md`,
`CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`), a knowledge
directory, project skills, client settings or hooks, pre-commit
configuration, CI workflows, a spec directory. If none exists, report that
there is nothing to audit, that `harness-create` is the entry for building
one, and stop. When the only artifacts are generic CI or pre-commit
configuration, or a stray entrypoint with a few rules, report that
`harness-create` fits better because there is little to audit, and ask the
user which entry to run; continue only when the user chooses this one.

Done when: the goal is recorded verbatim; or the no-harness report is
given, or the user chose the creation entry, and nothing was written.

### 2. Audit

Read [references/audit-checklist.md](references/audit-checklist.md) before the first artifact; it holds the
inventory fields, the places to look, the comparisons, and the grade
signs. Then:

1. Inventory every project-visible harness artifact with four fields:
   discovery path (how an agent reaches it), load trigger (what makes it
   load), source of truth (the file or tool it must agree with), update
   mechanism (what keeps it current); write `none` for a missing field.
2. Run the project's harness self-check when one exists (a
   `check_harness.py` or a task-runner recipe that runs one) and quote its
   findings; add by hand only what it does not cover. When none exists,
   record its absence as a missing finding for the entropy layer. [§5.3]
3. Follow the entrypoint's pointers the way a future agent would: every
   path opened, every documented command checked against the task runner,
   every rule compared with the code and with the other files.
4. Observe each graded layer's current grade where the repository shows it.

Done when: every artifact found has all four fields, the self-check is
quoted or its absence recorded, every entrypoint pointer was followed, and
no file has changed.

### 3. Classify and report

Classify every finding as **stale**, **duplicated**, **contradictory**,
**invisible**, **missing**, or **excessive** (definitions in
audit-checklist.md), each with its evidence (files and lines), its source
of truth, and one proposed disposition. An invisible file is reconnected or
removed, never left unchanged. An excessive finding carries the evidence
audit-checklist.md names for its kind. A contradiction between two rules that state intent goes to the
user as "which is the source of truth?", with the evidence and a
recommendation; the drift-first rule puts it ahead of everything else.
[§6.3]

Present the classified list as one report, grouped by layer, then take the
user's changes to dispositions and record each with its reason.

Done when: every finding carries class, evidence, source of truth, and a
disposition the user accepted or changed.

### 4. Choose repair or rebuild, and the kind of work

Restate the goal recorded in step 1 next to the audit findings and ask the
user to confirm, change, or drop it before classifying the work.

Present repair and rebuild with one recommendation. Recommend repair,
because a rebuild discards conventions the team relies on, unless no
entrypoint survives the findings and most findings are stale or
contradictory; then recommend rebuild. On rebuild, the Keep what works rule
still holds. [§6.3]

Classify the agreed work as one or more kinds and state for each what
changes and what is preserved. Read the matching reference before stating
the boundary:

- **Hardening** (prototype becomes long-lived): read [references/hardening.md](references/hardening.md) when it applies. [§6.2]
- **Thinning** (constraints that no longer catch anything): read [references/thinning.md](references/thinning.md) when it applies. [§6.2]
- **Carrier or platform migration**: read [references/migration.md](references/migration.md) when the
  spec carrier or the code-hosting platform changes.
- **Re-layering** (rules living outside the layer that owns them): name for
  each moved rule its old home, its new home in the owning layer, the
  entrypoint pointer that replaces it, and the copy to delete; drop no rule
  in the move, and re-state the grade of both layers involved.

Read [references/reclamation.md](references/reclamation.md) when the project is long-lived and the audit
found no periodic cleanup, or when the user asks how to keep the harness
from decaying again.

Done when: the step-1 goal was confirmed, changed, or dropped by the user
(or none was recorded), the user chose repair or rebuild, and every kind of
work has a stated boundary.

### 5. Re-grade the touched layers

Grade six layers: environment and sandbox, knowledge and routing, hard
boundary, authority, specification and completion, entropy. Grades are
**omitted** (nothing built), **light** (one sentence or one entry),
**medium** (a dedicated file or configuration kept by convention), and
**thick** (machine-enforced checks or isolation). The platform lifecycle
layer is routed in step 7 but never graded. [§6.1]

For each graded layer the work touches, show current and proposed grade and
the variable that justifies the move: error cost, maintenance lifetime,
environment isolation, autonomy, or team size. State an observed current
grade as observed; ask the user to confirm each changed grade. List every
untouched layer as unchanged without asking. A platform-only migration
shows all six unchanged and says the platform lifecycle layer is rebuilt
without a grade.

Done when: all six layers appear with a grade and every changed grade is
confirmed.

### 6. Write the plan and get approval

Rework [assets/improvement-plan.md](assets/improvement-plan.md) line by line: every file to add, change,
or delete with the finding it resolves, its disposition, its source of
truth, and its verification; the re-graded layers; drift items first, with
every later item marked as depending on them; the checkpoint convention;
and every step that needs its own decision (push, remote setting, branch
deletion, wider agent permissions). Show it in the conversation, or write it
only to the project's handoff directory after `git check-ignore` confirms
the directory is ignored. That plan file is the only write allowed before
approval. When the handoff directory is missing or not ignored, show the
plan in the conversation only; do not create the directory or edit
`.gitignore` before approval. If the user rejects it, revise or end the
work.

Done when: the user approved the plan and no tracked file has been changed
by this work.

### 7. Execute layer by layer

Work in plan order, drift items first. For each layer the plan changes,
find the installed skill whose description carries the ownership phrase,
with `<layer>` written exactly as in this table, never a remembered skill
name:

| Plan layer | `<layer>` in `Owns the <layer> layer` |
| --- | --- |
| environment and sandbox | `environment` |
| knowledge and routing | `knowledge and routing` |
| hard boundary | `hard-boundary` |
| authority | `authority` |
| specification and completion | `specification and completion` |
| entropy | `entropy` |
| platform lifecycle | `platform lifecycle` |

Load that skill, pass it the layer's findings and approved dispositions
verbatim with the confirmed grade, let its workflow run the layer, and take
back its report. A file the builder proposes beyond the plan is a plan
amendment the user approves first. When no installed skill claims the
layer, say so, perform the layer's plan items yourself, and record the gap
for the closing report.

An item that needs a separate decision (deleting a branch, changing a
remote setting, widening agent permissions, pushing) stops alone: add it to
the pending decisions list, continue with every item that does not depend
on it, and ask once, with the whole list, when no independent item is left.
Ask at once only when every remaining item depends on that decision.

Checkpoint after each layer: run the project's checks locally; when they
pass, commit that layer's files in the convention the audit found (or the
plan recorded), with no AI attribution trailer, and push nothing unless the
user decided so for that step. Use commits, never stashes or session-only
undo. When a pre-commit hook such as the secret scan rejects the commit,
fix or remove the flagged content and retry; never bypass the hook.
[§4.3]

Done when: every plan item is done, or blocked and in the pending decisions
list; each touched layer has one passing checkpoint commit; nothing was
pushed without a decision.

### 8. Read back in a clean context

Dispatch the plugin's read-only `harness-verifier` agent when the client
offers it, with every changed file and the entrypoint and no plan or
conversation; quote its result lines. When the client has subagents but
not this agent, dispatch a generic read-only subagent with every changed
file and the entrypoint, no plan or conversation, and the same checks
(each file's load condition, pointers resolve, entrypoint budget, undefined
terms, Keep In Sync named in both files); quote its result lines. Only
without any subagent facility, re-read every changed file as a future agent
would, resolve every pointer, and record that read-back ran without a clean
context. Fix every reported gap
(a dangling pointer is fixed or removed before the work is called done) or
add it to the pending decisions list; re-read what you fixed.

Done when: the read-back result is quoted or the degradation recorded, and
no reported gap is left unfixed and unlisted.

### 9. Final review

Review every changed file for:

- **Vocabulary**: a term only this plugin defines, left undefined; define it
  in the file or rewrite the sentence plainly.
- **Self-containment**: any plugin or skill name, a plugin path or phrase, a
  script invoked from a skill directory; replace a skill-directory script
  with the project's own copy and tell the user later plugin fixes do not
  reach it.
- **Mechanics**: every rule reachable from the entrypoint; entrypoint at most
  120 lines; links resolve; documented commands run; each sync concern
  named in both files of the pair.
- **Checklist**: walk the closing checklist in audit-checklist.md item by
  item; mark each passed, passed after a fix (name the fix), or not
  applicable with a reason.

Fix, re-read, and commit what the review changes as a checkpoint. Re-run
the project's harness self-check when one exists.

Done when: every checklist item is marked and the self-check, if present,
passes.

### 10. Close

Report: each change with the finding it resolves; the before-and-after
grade per touched layer; the verification commands run and their results;
any layer no installed skill claimed; manual platform actions left to the
user; and one pending decisions list. When nothing is pending, say so
explicitly and still list the verification commands.

Done when: the report lists every change with its finding, the
before/after grade per touched layer, every verification command with its
result, unclaimed layers, manual platform actions, and exactly one pending
decisions list or the explicit statement that nothing is pending; every
edit traces to a classified finding the user approved.

## Gotchas

- A complaint names one symptom; the same stale fact is usually copied in
  two more places. Search for every copy before proposing the fix.
- A file nothing links to may still load: client settings, hooks, and
  subdirectory entrypoints load by location. Check the load trigger before
  classifying it invisible.
- Thinning evidence is "the thing it caught no longer occurs", not "nobody
  remembers why it exists". Without evidence, the constraint stays and the
  question goes to the user.
- The read-back reader must not see the plan; a reader that knows the intent
  fills the gaps the next agent will fall into.
