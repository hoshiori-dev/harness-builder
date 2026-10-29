---
name: harness-architecture
description: >-
  Harness methodology manual — explains why an agent harness is shaped as it
  is, where a rule or fact for coding agents should live, what an existing
  harness gets wrong, and how several agents share one repository. Use when
  asked why agents ignore an entrypoint or why a project needs (or does not
  need) CI, hooks, or a sandbox; where a rule, procedure, or fact belongs
  (entrypoint, knowledge file, project skill, hook, subdirectory file);
  whether two copies of a fact may coexist; what an agent would get wrong
  working from an existing AGENTS.md, CLAUDE.md, or .agents folder; how
  parallel agents should split worktrees, branches, and platform writes; or
  which part of the method covers a topic. Not for building, moving,
  splitting, or restructuring harness files (a layer's builder or a
  user-invoked entry owns that), for README or other human documentation, or
  for application code.
license: Apache-2.0
---

# Harness Architecture

The methodology behind every harness layer, written for an agent that
answers questions about a harness without changing it. A harness is the
control and extension layer between the model, the codebase, and the
development environment [§1.1]. This skill explains, places, adjudicates,
audits, and hands off; it writes no file into the project and performs no
build.

## Rules on every step

<!-- shared:recommendation-not-decision -->
A recommendation is not a decision. Present one recommended option with its
reason and the alternatives in a sentence each, then wait for the user's
choice. Challenge a choice once when the evidence contradicts it; after that
the choice binds every later step.
<!-- /shared:recommendation-not-decision -->

<!-- shared:confirm-not-guess -->
Confirm, do not guess. Settle a fact from the repository when it can be
observed there (tools in use, directories, commands, history); ask the user
for everything else, and ask before choosing on any point where two readings
would lead to different work. Only a choice whose answer is plain from the
repository is made without asking.
<!-- /shared:confirm-not-guess -->

- Answer from the methodology. Tag every point with the section it comes
  from (`[§x.y]`), so the reader can check it against the method.
- Trace every trade-off to the five variables (error cost, maintenance
  horizon, environment isolation, autonomy, team size), never to a project
  label such as "prototype" or "production" [§1.1] [§6.1].
- Change no file. An audit reads and reports. When the question becomes a
  build, hand off (workflow step 4).
- A single agent is the default. Raise worktrees, remote-branch ownership,
  and coordinators only when the user describes or asks about more than one
  agent working at once [§4.4].

## Workflow

### 1. Classify the question

Pick the branch that fits: **reasoning** (why a practice holds, whether it
applies), **placement** (where a rule, fact, or procedure lives),
**duplication** (one fact in several places), **audit** (what an existing
harness gets wrong), **concurrency** (more than one agent), **lookup or
build** (which section covers a topic; "set that up for us"). A request to
create, move, split, or restructure files is a build, not a question.

Done when: one branch is named, and any request to create, move, split, or
restructure files has been classified as a build.

### 2. Gather the facts the answer depends on

Read the repository for what it can show: entrypoints, knowledge files,
skills, task-runner recipes, checks, framework configuration, the
self-check if one exists. Ask for what it cannot show before the
recommendation depends on it: which agent frameworks the team uses, team
size, autonomy, error cost, maintenance horizon.

Done when: every fact the recommendation rests on is either observed or
confirmed by the user, and no framework behaviour is assumed.

### 3. Answer within the branch

Every branch rests on this core. A harness tightens the solution space
(soft boundaries shift the distribution of outputs, hard boundaries cut it)
and expands it (private context and tools reach otherwise unreachable
answers); each layer's balance is set by the five variables, never by a
task type [§1.1]. Minimal complete context per task, with the fewest hops:
irrelevant context dilutes attention, missing context causes guessing, and
attention decays with position, so always-applicable constraints come first
[§1.2] [§2.1]. The root entrypoint's budget is about 100 lines, about 200
only when it is the whole harness of a light project [§2.1]. A wrong or
stale harness is worse than none: the agent trusts the lie [§5.1].

- Reasoning (why a practice holds, whether it applies, which rule or budget
  applies): read [references/methodology.md](references/methodology.md) when the
  answer needs more than the core above; name the variables that move the
  answer, cite the sections, state the rule.
- Placement (where a rule, fact, or procedure lives; an entrypoint or a draft
  of one is placement material): when the placement depends on location,
  action, or description-matched loading, or the material is an entrypoint,
  read [references/loading-modes.md](references/loading-modes.md) before answering.
  Classify the content by when it is needed (every task, by task type, by
  location, by action, or by description-matched auxiliary flow), recommend
  one placement with the framework caveat when the mode depends on the
  framework, and, when the material is an entrypoint, end with the resulting
  line count against the 100-line target [§2.1].
- Duplication (a copy exists or is proposed): on this branch read
  [references/source-of-truth.md](references/source-of-truth.md) before answering;
  state the entropy law, name one source, require an adjudication rule.
- Audit (what an existing harness gets wrong): on this branch read
  [references/audit.md](references/audit.md) before judging any file; run the
  harness's self-check first and report each finding as a file, a gap class,
  and a fix.
- Concurrency (the user describes or asks about concurrent agents): on this
  branch read [references/multi-agent.md](references/multi-agent.md) before answering;
  give the worktree, branch, resource, coordinator, and merge rules.
- Lookup (which section, layer, or skill covers a topic): on this branch
  read [references/methodology-map.md](references/methodology-map.md) before answering;
  name the sections, the layer, and the builder that owns the layer, by role.

Done when: every point carries a section tag, every decision has exactly
one recommendation with its alternatives, and every audit finding is a
file, a gap, and a fix.

### 4. Close or hand off

A question that turns into a build ends here: read
[references/methodology-map.md](references/methodology-map.md) when handing off,
and close with its handoff wording, which names the sections, the owning
layer, and the entry skill the user must invoke, and states that an approved
plan precedes any file. Create nothing. Otherwise end with the
recommendation and the open questions.

Done when: no file in the project has changed and the user knows the next
step and who performs it.

## Gotchas

- A label is not a variable. "It is only a prototype" says nothing about
  error cost; a research repository's data pipeline can have the highest
  error cost in the organisation [§6.1].
- An entrypoint that copies the directory tree is wrong the day a directory
  moves; the file system already states it [§1.3].
