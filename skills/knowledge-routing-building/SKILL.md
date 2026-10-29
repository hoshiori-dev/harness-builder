---
name: knowledge-routing-building
description: >-
  Agent entrypoint and knowledge routing — builds, splits, trims, or
  reorganises a project's AGENTS.md, its CLAUDE.md import, the knowledge files
  agents read on demand, and the routing table between them. Owns the
  knowledge and routing layer. Use when an AGENTS.md has grown long and agents
  ignore half of it; when setting up a knowledge folder and deciding what
  stays in the root file; when asking whether a procedure belongs in the root
  instructions, a doc, a code comment, or a project skill; when adding a
  CLAUDE.md so Claude Code follows the same rules as other agents; when
  knowledge files exist that nothing points to; or when an approved harness
  plan hands over this layer. Not for writing a project skill's own steps,
  README or other human documentation, or the pre-commit hooks, check
  messages, permissions, and CI that other layers own.
license: Apache-2.0
---

# Knowledge Routing Building

The entrypoint is the one file every agent session reads, so it is the
discovery root: a knowledge file nothing routes to is invisible, and a line
in the entrypoint that only some tasks need is paid for by every task. This
skill decides, with the user, where each piece of project knowledge lives
(entrypoint, knowledge file, code, comment, project skill, script) and
deposits the entrypoint, the knowledge files, and the routes between them.
[§1.2] [§2.1]

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

**The four-question check.** Before proposing any file other than the
entrypoint, answer these for it and show the answers to the user:

1. When, and through what mechanism, does an agent realise it needs this
   file? (A routing row naming a situation, an explicit skill route, or
   nothing.)
2. What does the agent gain by reading it?
3. How much content unrelated to that task does it read along the way?
4. Is the jump (one more tool call) cheaper than inlining the content?

A file that fails any answer is inlined or dropped, never created for
tidiness. Split by when content is needed, not by topic: a split that does
not shrink what some task loads only adds a jump. [§2.1] [§2.2]

**Code describes itself.** Directory topology lives in the file system,
commands in the task runner's recipes, interface contracts in type
signatures. Documents carry only what code cannot state: why, and when to
read what. Never copy a self-described fact into a document; a copy is a
future contradiction. [§1.3] [§5.2]

**Hand off by role, never by name.** A project skill's content goes to the
skill that writes project skills; the entrypoint's sync section to the layer
owning entropy; hooks, checks, and CI to the layer owning the hard boundary;
permissions and the authority policy to the layer owning authority; the
clean-context read-back to the entry skill. README, CONTRIBUTING, and
SECURITY are never written here; mention one only when it contradicts the
harness, as a suggestion.

Deposited files name the project's own commands, paths, and skills, never
this plugin or this skill.

## Workflow

### 1. Inspect the repository

Read, record, write nothing. Collect:

- entrypoints: `AGENTS.md`, `CLAUDE.md`, any subdirectory `AGENTS.md` or
  `CLAUDE.md`, other clients' entry files; the line count of each (`wc -l`);
  for `CLAUDE.md`, every rule absent from `AGENTS.md`;
- knowledge: `.agents/knowledge/` or any other agent docs folder
  (`docs/agents/`, `.github/instructions/`), each file's first line, and
  whether an entrypoint line points to it;
- project skills: `.agents/skills/`, `.claude/skills/` (real directory or
  link, and its target), each skill's name and description;
- the task runner (`justfile`, `Makefile`, `package.json` scripts) and its
  recipe names; the management-script directory and its language;
- client evidence: `.claude/`, `.codex/`, other client settings;
- an architecture document, and human docs (README, CONTRIBUTING);
- the harness plan's grade for this layer and confirmed clients, when an
  entry skill routed here.

For a project that already has a harness, classify each artifact as
current, invisible (no route reaches it), duplicated, contradicting, stale,
or over-thick, with the evidence. [§6.3]

Done when: every item above is recorded as observed, absent, or "ask", and
no file in the target has changed.

### 2. Settle layout and clients

Ask only what step 1 could not observe, each with one recommendation:

- **Clients.** Which agents work in the repository. When the user has not
  answered whether Claude Code is used, plan `AGENTS.md` and add `CLAUDE.md`
  and `.claude/skills` to the pending decisions list with their
  recommendation; create neither.
- **Entrypoint.** Recommend `AGENTS.md` as the only rule-bearing file and a
  `CLAUDE.md` whose whole content is `@AGENTS.md` when Claude Code is
  confirmed, because one copy cannot drift; never copy rules into both.
  Recommend no subdirectory entry files; read
  [references/entrypoint.md](references/entrypoint.md) when the user insists on one. [§2.1] [§2.2]
- **Layout.** An existing knowledge or skills folder seen in step 1 is
  reused without asking, and new files go there; record the knowledge
  folder's path for the routing rows. A real `.claude/skills` directory
  with mixed clients stays the skills folder unless the user approves
  moving it to `.agents/skills` behind the link; recommend the move, as its
  own item. Otherwise recommend `.agents/knowledge/` and `.agents/skills/`,
  with `.claude/skills` a relative symbolic link to `.agents/skills` when Claude Code shares the
  repository with another client: one real directory serves every client,
  so no skill exists twice. Alternatives, a sentence each: a real
  `.claude/skills` directory when Claude Code is the only client (knowledge
  stays in `.agents/knowledge/`); a single-file harness for a lightweight
  project.

Read [references/knowledge-files.md](references/knowledge-files.md) when presenting the layout,
when the user asks why, or when existing agent docs sit outside the
recommended folder.

A single-file choice is final: build `AGENTS.md` alone under the
about-200-line budget, create no knowledge or skills folder, state once if
that budget will be strained, and never reintroduce the folder later.

Done when: clients, entrypoint form, and layout each have a recorded
answer or a pending-decisions item, and the plan records each choice with
its reason.

### 3. Assign every piece of content a carrier

List every candidate: each line of an existing entrypoint, each rule of an
existing `CLAUDE.md` absent from `AGENTS.md` (propose moving it and reducing
`CLAUDE.md` to the import), each existing knowledge file, each existing
project skill found in step 1, each rule the user names, each procedure the
user lists.
For each, recommend one carrier with its reason and wait for the user's
choice:

- **Always block**: the rule harms when broken regardless of task type
  (secrets, commit and publish limits, language, the check to run before
  handing work back), and any few lines every task needs; no file. "Run the
  formatter before committing" is one.
- **Routing row plus knowledge file**: needed by one kind of task. "Read the
  schema notes before touching the ORM" is a row, not an always rule. Show
  the four answers for the file.
- **Nothing**: the fact is self-described by code (leaf directories, the
  recipe list, signatures); keep at most a macro map of long-lived
  top-level directories in the entrypoint and point at the task runner.
- **Type, signature, or code comment**: read
  [references/inline-vs-document.md](references/inline-vs-document.md) when the user wants to document a
  constraint, an invariant, or a workaround.
- **Project skill**: read [references/project-skill-warrant.md](references/project-skill-warrant.md) when
  a candidate is a procedure, or when the user asks for a skill; state the
  condition it passed or failed.
- **Script**: read [references/scripts.md](references/scripts.md) when an operation takes more than
  two lines, assembles arguments, or filters output.
- **Existing project skill**: recommend process-critical (its omission
  harms: a pre-publish check, a migration gate), which gets the routing row
  `When <situation>, load the <name> skill`, or auxiliary, which gets no
  row; for an auxiliary skill tell the user description matching suffices.

Explain the task-type test to the user each time it classifies a rule. For
an existing knowledge file no route reaches, report it as invisible and
ask whether to route, merge, or delete it; never route all of them
silently. Deleting is a separate decision (rule above).

Done when: every candidate has a recommended carrier with its reason and
the user's choice, and every proposed file has its four answers shown.

### 4. Draft the entrypoint and get the file list approved

Read [references/entrypoint.md](references/entrypoint.md) when drafting or restructuring the
entrypoint, or when its budget is exceeded. Draft from
[assets/agents-md.md](assets/agents-md.md) in this order: Always (ending
with the project map when kept), When To Read What, Validation, then the
Keep In Sync position holding only its marker. When To Read What includes a
row for every process-critical skill: an existing one by name, a new one
with its name left open and its line counted. Validation rows name recipes
read from the task runner, not raw commands, and the user is not asked to
list them.

Budget: about 100 lines and never over 120 with a knowledge folder; about
200 for a single-file harness. No always rule leaves for budget. Over budget
through routable content: propose a knowledge file with its four answers and
routing row, and ask; the draft lands at or under 120 once the user accepts
the file or names which content to drop. Over budget through always rules
alone: keep every rule, tell the user the budget cannot be met without
dropping one, and ask which they consider optional; remove none yourself.

Present one list: every file to create or change, with its path, its
"Read this when" line, the matching routing row, its four answers, and the
entrypoint's projected line count against its budget; for each existing
file, what it loses or gains; links, the `.agents/skills/.gitkeep` keep
file, and scripts included; a move of a real `.claude/skills` directory as
its own item. Wait for approval.

Done when: the user approved the list; until then nothing is written.

### 5. Write the layer

Write only the approved files; resolve every `# CONFIGURE:` line of an
asset and remove its comment:

- `AGENTS.md` from the draft; the last section is `## Keep In Sync` with
  the marker `<!-- harness: keep-in-sync -->` and nothing else. Write no
  sync rule, sync table, or correction-report rule. Leave out a row whose
  skill name is still open; step 6 settles it.
- `CLAUDE.md` from [assets/claude-md.md](assets/claude-md.md): exactly
  `@AGENTS.md`, also when it held its own rules. Each former rule lands in
  `AGENTS.md` only where the user approved its move; each undecided one
  goes, with its full text, to the pending decisions list.
- Each knowledge file from [assets/knowledge-file.md](assets/knowledge-file.md): first line
  "Read this when …" naming the same situation as its routing row, one
  concern, facts first.
- The shared skills folder, when approved, by what step 1 found at
  `.claude/skills`:
  - absent: `mkdir -p .agents/skills .claude`, then the empty tracked
    `.agents/skills/.gitkeep` (git stores no empty directory; skip it when
    the folder already holds a skill), then
    `ln -s ../.agents/skills .claude/skills`;
  - a real directory, move approved:
    `mkdir -p .agents && git mv .claude/skills .agents/skills && ln -s ../.agents/skills .claude/skills`;
    when `.agents/skills` also exists, stop and ask how to merge them;
  - a real directory, move not approved: leave it; the move stays on the
    pending decisions list;
  - already a link to `../.agents/skills`: nothing.
- Approved scripts and recipes, per [references/scripts.md](references/scripts.md) when writing
  any script.

Done when: `wc -l AGENTS.md` is within budget; each knowledge file's first
line matches a routing row; a search for `{{` over the written files
finds nothing; the sync position is empty; where the link was approved,
`test -L .claude/skills && test -d .claude/skills` succeeds and
`readlink .claude/skills` prints `../.agents/skills`.

### 6. Hand off project skills

For each procedure the user confirmed as a skill, write the handoff
definition; read [references/project-skill-warrant.md](references/project-skill-warrant.md) when writing it.
Pass it to the skill that writes project skills, by role. Never write a
skill body. A new process-critical skill's row was approved at step 4 with its name
open: add it, worded as approved, only when the writer reports the name
before step 7; otherwise record it as a follow-up. Add no other row.
[§2.3]

Done when: every confirmed skill has a handoff naming no skill; every row
added here was in the approved list; `wc -l AGENTS.md` is still within
budget; every process-critical row not written is a recorded follow-up.

### 7. Report

Report: every file created or changed, each with its "Read this when"
condition and the routing row that reaches it; what moved where, for a
restructure; the entrypoint's line count
against its budget; every carrier decision with its condition and the
user's choice; the handoffs made, by role; the sync position left for the
layer owning entropy; and the pending decisions list. Tell the user the
project owns any delivered script.

When this skill was loaded directly rather than routed from an entry skill,
end by stating that the layer still awaits a clean-context read-back and
list the files to read. Never re-read them in this context as a substitute.

Done when: every item above is in the report and no file is re-read for
verification.

## Gotchas

- Claude Code reads `CLAUDE.md`, not `AGENTS.md`; without the import line
  it sees none of the entrypoint's rules.
- Git stores `.claude/skills` as a link; a Windows checkout without
  `core.symlinks` gets a text file instead. Ask when the repository shows
  Windows contributors.
- Count lines with `wc -l` on the written file: blank lines, table rows,
  and code fences count toward the budget.
