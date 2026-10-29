# Designing the Contract

Read when reworking the contract asset into the target's
`spec-workflow` knowledge file, when changing one recorded value in a
contract already deposited, and when a re-run fills an item the contract
left pending.

## One source of truth per fact

| Fact | Rules | Points to it, never restates |
|---|---|---|
| What the system does | The specs (living specs when spec-anchored) | Entrypoint, knowledge base, issue and request bodies |
| Acceptance of one change | That change's scenarios | The request body, the issue |
| Engineering principles the tool reads (constitution, steering) | The tool's file | The entrypoint |
| How specs are written, approved, and frozen | The contract | Entrypoint, request template, project workflow skill |
| Conventions and mechanics | The knowledge base | Specs never restate them |

A pointing file may summarise in one line and must link. A tool-owned file
(constitution, spec directory, change record) keeps the tool's format; never
rewrite it into harness style.

## Section by section

- **Read condition** (first line): "Read before starting a change that
  alters behaviour, before writing or approving a spec, and before
  freezing a record."
- **Level and carrier**: one sentence each with the fact that decided it,
  in the project's words ("maintained for years", "existing code").
- **Where a spec goes**: the path the tool uses, verified in the tree; for
  the lightweight carrier, where `SPEC.md`/`PLAN.md` live per change and
  when plan mode suffices.
- **What a spec contains**: the four answers and four rules; for the
  lightweight carrier, the five headings that hold them
  (`completion-boundary.md`, Per carrier).
- **Gates**: both gates, who owns each (a role or a name, never "the
  team"), the mode, how the approval is recorded, when tasks are written,
  who freezes, what a commit after the freeze means.
- **Scope**: specs cover behaviour a change touches; a change to the
  project's own harness, tooling, checks, workflows, or documents carries
  no spec. Name the carrier's marker for such a change only when the
  project records one; name the covering harness self-check only when the
  entropy layer deposited it; otherwise state the rule alone. Untouched
  code is described by the codebase map, which is not normative.
- **Not yet authoritative**: each spec whose drift decision was deferred,
  with "trust the code over this spec until it is fixed".
- **Fast feedback**: the scoped command as the check after every edit, the
  full run as the task-end check. [§4.3]
- **Exploration**: an exploratory worktree or branch is removed as soon as
  its evaluation ends; keep the chosen attempt, delete the rest. [§4.3]
- **Handoff notes**: the location and the rule that such files never enter
  version control, because they carry logs, environment values, and
  credentials more often than code does. For the temporary-directory
  choice, the same rule with that location. [§4.3]
- **Progress**: when a framework tracks tasks, use its task list; no
  separate progress diary. [§4.3]
- **Update this file when**: the tool is upgraded or replaced, the level or
  a gate's mode changes, a gate owner changes, a second copy of any fact
  above appears (merge it back), or the fast check changes.

## Vocabulary check

After writing, search the contract for each word this skill coined
(`carrier`, `layer`, `package gate`, `freeze gate`, `selecting fact`), for
the bare noun `request` (write the platform's "pull request" or "merge
request"), and for any spec-tool command line. Replace each hit with the
project's noun or delete it. Tool names and the project's own check commands stay: they are
facts of the project.

## Changing one recorded value

Update every passage that depends on the value, then refresh every marker
block that states it (`approval-gates.md`, marker text). For a gate-mode
change that is the `Gate mode:` line and the whole recorded-or-conversational
paragraph after the gates: recorded names the `spec:approved` label, the
fingerprint that removes it, and the awaiting-archive check; conversational
names the branch-tip comparison with the freeze commit. Leave every line
that does not depend on the value, in the contract and in the marker files,
unchanged.

## Filling a pending item

When an observed fact settles an item the contract left pending (a harness
self-check deposited, a scoped recipe added), write it into its section
(Scope, Fast feedback) as the first deposit would have, refresh any marker
block it affects, and drop it from the pending list. Ask nothing.
