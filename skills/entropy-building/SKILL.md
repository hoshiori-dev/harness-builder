---
name: entropy-building
description: >-
  Harness entropy — keeps a project's agent harness true to its code. Owns
  the entropy layer: drift correction, sync rules, the harness self-check,
  and periodic reclamation. Use when the entrypoint or knowledge
  files describe commands, paths, or layouts that no longer exist and the
  user wants them kept in sync; when adding a check or CI step that fails
  on stale harness paths, missing recipes, or mirror files out of step; when
  deciding where an agent records docs-versus-code contradictions found
  mid-task; when a long-lived harness needs a routine that finds dead rules
  and over-thick constraints; when session logs or canary tasks are proposed
  for judging harness changes; or when an approved harness plan hands over
  the entropy layer. Not for product lint, tests, or CI; fixing one broken
  link or document; syncing product artifacts such as models and
  migrations; or branch cleanup.
license: Apache-2.0
compatibility: Scripts need Python 3.10+; uv optional.
---

# Entropy Building

A stale harness is worse than none: an agent without one reads the code,
while an agent with a wrong one trusts it, fails, or loops. This skill
builds the mechanisms that keep a target project's harness true to its code:
one source of truth per fact, a rule for what an agent does when it finds
drift, sync rules in both directions, a harness self-check in the project's
own task runner and CI, and a periodic reclamation that thins as well as
updates. [§5.1]

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

Build exactly the grade the user confirmed in conversation; a grade that
appears only in a plan is a recommendation, so state it and ask before
depositing anything. [§6.1]

| Grade | Deposits |
|---|---|
| omitted | nothing; remove the reserved keep-in-sync heading and marker from the entrypoint, and report it |
| light | one drift sentence in the keep-in-sync section; nothing else |
| medium | correction-report rule, ruling rule, standing reverse rule, and one sync mechanism (table or sync skill, the user's choice); self-check tier 1 with recipe, aggregate `check` hookup, and CI job |
| thick | medium, plus self-check tier 2 and periodic reclamation |

Hand neighbouring work over by role, never by skill name: product lint,
tests, and CI jobs to the skill that owns the hard-boundary layer; writing,
linting, and testing a project skill to the skill that writes project
skills; the pending decisions format to the skill that owns the authority
layer; creating labels or other remote entities to the skill that owns the
platform lifecycle layer; the entrypoint's structure and budget to the skill
that owns the knowledge and routing layer.

Never build a harness that edits its own knowledge from failure history:
repeated agent failures yield a reported pattern and a recommendation, never
an automatic edit.

A deposited file names the project's own commands and paths, never this
plugin, this skill, or the grade ladder.

## Workflow

### 1. Inspect the target

Read, record, write nothing. Collect:

- the entropy grade in the plan, and whether the user confirmed it in
  conversation;
- the entrypoint, its line count and budget, and its keep-in-sync section:
  reserved and empty, populated, or absent;
- existing sync mechanisms: a populated sync table, sync project skills;
- other entropy artifacts: a reclamation section or skill, a harness check
  script;
- the task runner, its recipe file, and how it lists recipes;
- the knowledge directories, other harness documents (`ARCHITECTURE.md`,
  `CLAUDE.md`), and project skill directories;
- where management scripts live and the management language the project
  agreed;
- the CI workflow, the `# harness:` slot the hard-boundary layer left for
  the self-check job, and the gate's dependencies; any CI step that calls
  a script inside a skill
  directory, which is a defect to report with a proposed project-owned copy,
  the duplication accepted as deliberate; [§5.3]
- the issue tracker and its label namespaces (`type:`, `area:`);
- the project's age, release rhythm, and team rituals (release, retro).

Done when: every item is recorded as observed, absent, or "ask", and no file
in the target changed.

### 2. Inventory the copies

Before proposing any mechanism, list every fact the harness states in more
than one place: commands with their flags, directory layouts, versions,
rules repeated across the entrypoint, knowledge files, skills, and public
docs. For each, report the places, the recommended single source (the code
or the task-runner recipe first, then the one document that owns the
topic), and the reference that replaces each copy ("name only the recipe
`just test`; its flags live in the recipe"). List every copy that cannot
become a reference (translations such as `README.md` / `README.en.md`,
files a tool needs in two places) as a mirror pair with the sections that
must match, and ask the user to confirm each pair. For each pair, recommend
a source side (the original language wins and the translation is corrected)
and ask the user to confirm it. End with the recommended ruling rule: the
code or the task runner wins over the document describing it; the document
is the side to correct unless the user records the opposite for that pair;
in a mirror pair the confirmed source side wins. [§5.2]

When step 1 found an existing sync mechanism, report it next to the
inventory with every contradiction between them; the user decides each, add
no second mechanism for a concern it owns, and do not reopen the
table-or-skill choice for it. When step 1 found an existing harness check
script, report what it checks and ask whether to extend it or replace it
with the self-check of step 7. Report any other entropy artifact for the
user to keep, merge, or replace.

Done when: the inventory, the mirror pairs with their source sides, and the
ruling rule are reported, and the user has answered each; nothing is
written.

### 3. Settle the decisions

Ask only what steps 1 and 2 could not settle, each with one recommendation:

- **Grade**, when unconfirmed. When the project is long-lived (maintained
  past a release cycle) but the confirmed grade is medium, recommend thick
  for reclamation and wait for the answer. Light needs no further decision.
- **Sync mechanism** (medium and up), per concern not already owned. Read
  [references/sync-table.md](references/sync-table.md) when presenting the
  choice; read [references/sync-skill.md](references/sync-skill.md) when the
  user picks the skill for any concern.
- **Correction-report dispositions and drift label.** Read
  [references/correction-report.md](references/correction-report.md) when
  proposing the label or the project has no issue tracker.
- **Self-check**: keep the Python reference implementation or port it to
  the agreed management language, where it lives, the recipe name, and the
  CI job. Read
  [references/check-harness-config.md](references/check-harness-config.md) when
  settling any of these. A refusal is recorded as a pending decision
  with its risk ("harness drift reaches the main branch unchecked") and the
  script is not offered again.
- **Reclamation** (thick): section or project skill, the anchor event, and
  the cadence. Read
  [references/reclamation.md](references/reclamation.md) when settling these.
- **Observation and canaries**, only when the user raises them. Read
  [references/observation.md](references/observation.md) when they do.

Done when: every bullet that applies has an answer or a pending decision.

### 4. Plan the artifacts and get approval

List by path: the keep-in-sync section content, the correction-report rule,
the ruling and reverse rules, each sync skill or reclamation skill request,
the script, the recipe, the CI job, and the reclamation section. Say what
each existing file gains or loses. Wait for approval.

Done when: the user approved the list.

### 5. Fill the keep-in-sync section

Write into the section the knowledge and routing layer reserved in the
entrypoint: replace the `<!-- harness: keep-in-sync -->` marker with the
content and keep the heading; never create a second sync section. When the
entrypoint has none, add one at its end within its line budget and report
that the section had not been reserved. At the omitted grade, delete the
reserved heading and marker and deposit nothing else.

- **Light**: this one sentence, with the project's own paths, and nothing
  else: "When harness content here or in the knowledge files contradicts the
  code, fix it in the same change or record it where the next agent will
  find it, never only in the conversation."
- **Medium and thick**: rework
  [assets/keep-in-sync-section.md](assets/keep-in-sync-section.md) line by
  line: the three dispositions, the ruling rule, the standing reverse rule,
  and one table row per concern the table owns. Each row states the change,
  the document to update, and what to run or read before editing that
  document. A mirror pair's row names its source side as the one whose
  change triggers it and the other file as the one corrected. A concern
  owned by a sync skill gets no row. [§5.2]

Done when: the marker no longer appears in the entrypoint; except at the
omitted grade, the entrypoint has exactly one sync section; at medium and
up it names the three dispositions with their criteria, says a
conversation-only report does not count, and every row has all three
cells.

### 6. Hand over the project skills

For each concern the user gave to a sync skill, and for a reclamation the
user wants as a skill, describe the need to the skill that writes project
skills, attaching the raw shape reworked with the settled facts:
[assets/sync-skill.md](assets/sync-skill.md) or
[assets/reclamation-skill.md](assets/reclamation-skill.md). Do not lint,
finish, or test the skill yourself.

Done when: each request names the concern or routine, its triggers, its
checks, and its completion criterion, and no table row covers the same
concern.

### 7. Deposit the self-check (medium and up)

Read [references/check-harness-config.md](references/check-harness-config.md) when
writing it. Copy [assets/check_harness.py](assets/check_harness.py) (or
its agreed port) to where the project's management scripts live and set
every `# CONFIGURE:` line from step 1 and step 2: the entrypoint, the
knowledge directories, the task runner and its file, the mirror pairs;
tier 2 on only at thick grade or on request. Ask only about what the
repository does not show. Add the recipe, add it to the aggregate `check`
recipe, fill the CI slot the hard-boundary layer reserved, then run the
recipe once and report its output verbatim. [§5.3]

When the first run reports findings, show each as printed and ask, per
finding, whether to fix the harness content or adjust the settings; never
edit the check's logic to make it pass.

Done when: the recipe ran and its output is in the report; the CI job fills
the reserved slot, the gate depends on it at thick, and `just check` (or
the runner's aggregate recipe) runs the recipe; and the script calls
nothing inside a skill directory.

### 8. Install reclamation (thick)

Rework [assets/reclamation-section.md](assets/reclamation-section.md) into
the knowledge file or entrypoint section the user chose, or hand the skill
over in step 6. Read
[references/reclamation.md](references/reclamation.md) when filling it. [§6.2]
Then run the routine once as its first sweep: report every finding with its
disposition and evidence, apply nothing the user has not approved, and set
`Last run:` to that day's absolute date.

Done when: the routine carries the hunt list with the thinning signal, the
anchor event, the cadence, and `Last run:` with the date of the first
sweep, the sweep's findings are in the report, and the entrypoint routes to
it.

### 9. Verify and report

Confirm, without fixing silently: the correction-report rule and every
deposited mechanism are reachable from the entrypoint; the recipe runs; the
CI job references it. Report: each file written or changed; the self-check
output; the requests handed to other skills by role; remote items for the
platform lifecycle layer or the user (the drift label); the pending
decisions; at omitted and light grade, what the project adds if it outlives
that grade (at omitted, the drift sentence; at light, the three
dispositions, the table, the self-check); at thick
grade, that canaries are a manual option and session logs stay local.
Say the project owns every deposited copy.

Done when: each verification has a stated result and every item above is
in the report.

## Gotchas

- A mirror pair of translations never matches word for word: the check
  compares what a translation keeps (link targets, code spans, code blocks,
  table row counts) inside the configured sections, so name sections whose
  code and links really are shared.
- The check counts a knowledge file as reachable only when the entrypoint
  names it. A two-hop layout (entrypoint, then an index file) yields a
  finding per file behind the index; report it to the skill that owns the
  knowledge and routing layer instead of weakening the check.
