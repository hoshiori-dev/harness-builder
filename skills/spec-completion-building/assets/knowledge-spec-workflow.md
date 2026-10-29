Read this before starting a change that alters behaviour, before writing or approving a spec, and before freezing a record.

# Specification Workflow

Level: {{LEVEL}}. <!-- # CONFIGURE: {{LEVEL}}: "spec-anchored: the specs stay the living description of the system, and every change updates them" or "spec-first: a spec builds the change and is archived with it", followed by the fact that decided it, e.g. "maintained for years". -->
Tool: {{TOOL}}. <!-- # CONFIGURE: {{TOOL}}: OpenSpec, Spec-Kit, the framework kept, or "per-change SPEC.md and PLAN.md, or plan mode for one-file changes", with the fact that decided it. -->

## Where specs live

{{SPEC_LOCATIONS}} <!-- # CONFIGURE: {{SPEC_LOCATIONS}}: the verified paths for living specs, one change in progress, and the archive; for per-change documents, where SPEC.md and PLAN.md sit and when plan mode is enough. -->

Behaviour lives in the specs; this file, the entrypoint, issues, and request
bodies link to them and never restate them.

{{NOT_AUTHORITATIVE}} <!-- # CONFIGURE: {{NOT_AUTHORITATIVE}}: delete when no drift decision is deferred; otherwise "Not yet authoritative: <spec path>. It disagrees with <code path>; trust the code until it is fixed." -->

## What every spec answers

1. How done is judged: scenarios or a final check the agent runs itself,
   including "no draft commit left on the branch".
2. What is not done: the non-goals.
3. What is delivered: the pull request, report, or deployment, and the
   pending decisions list.
4. Which irreversible actions are pre-authorised for this change: which
   branch may be pushed, whether comments or a pull request may be opened.

And every spec obeys four rules:

- Each goal has at least one scenario a reader who never saw the code can
  judge; at least one scenario in the spec covers a failure or edge path.
- Non-goals are written down.
- Goals describe behaviour, never the diff.
- Verification runs the scenarios and records the results; reading the diff
  is not verification.

{{HEADINGS}} <!-- # CONFIGURE: {{HEADINGS}}: per-change documents only: "Every SPEC.md or PLAN.md carries these headings: ..." with the five headings from completion-boundary.md's lightweight mapping, each followed by the answers and rules it holds; delete for a framework, and instead say which tool file answers each item. -->

## Approval

Gate mode: {{MODE}}. <!-- # CONFIGURE: {{MODE}}: "conversational: <owner> closes each gate in the conversation" or "recorded: the first gate by the `spec:approved` label, the second by the awaiting-archive check and the freeze". -->

1. The spec, and its design when more than one approach is reasonable or the
   change touches structure, interfaces, or dependencies, is approved by
   {{OWNER}} before any task list is written. The draft request opens when <!-- # CONFIGURE: {{OWNER}}: a role or name, never "the team". -->
   the spec is complete, and the agent stops there until approval.
2. When the last task is verified, the request is marked ready with the
   record still open. After the review closes, {{FREEZER}} freezes the record <!-- # CONFIGURE: {{FREEZER}}: "the implementer, or a maintainer who pulled the fork's branch". -->
   on the request's branch: the change is archived, merged into the living
   specs, or declared frozen at a named commit. A commit after the freeze
   reopens the review. Tasks follow the first approval; the freeze follows
   the review of the ready request.

{{RECORDED}} <!-- # CONFIGURE: {{RECORDED}}: recorded mode only: "A person with write access adds `spec:approved`; it records the version approved and is removed automatically when the spec or design changes afterwards, so it is taken again. The awaiting-archive check stays red on a ready request until the freeze; that is the merge block." Conversational: "Nothing revokes a closing: before pushing or handing over, compare the branch tip with the freeze commit and ask again when they differ." -->

No job approves or freezes a record; a person on the branch does.

## Changes that carry no spec

A change to this project's own harness, tooling, checks, workflows, or
documents carries no spec. {{SPECLESS}} <!-- # CONFIGURE: {{SPECLESS}}: name the tool's marker for such a change when the project records one, and "`<self-check command>` covers it" when the harness self-check exists; otherwise delete. -->
Specs cover behaviour a change touches; nothing is back-filled for code no
change touches.

## Checks while working

- After every edit: `{{FAST_CHECK}}` (seconds, one file or the diff). <!-- # CONFIGURE: {{FAST_CHECK}}: the scoped command run once during the build; delete the line when none exists; the gap goes to the hard-boundary layer by description, or to the pending list only when that layer is omitted or already done (step 2.5). -->
- At the end of every task: `{{FULL_CHECK}}`. <!-- # CONFIGURE: {{FULL_CHECK}}: the project's full check. -->
- Remove every exploratory worktree and branch as soon as its evaluation
  ends; keep only the attempt chosen.
- Use the tool's task list for progress; keep no separate diary.

## Handoff notes

Session handoff and scratch notes go in `{{HANDOFF_DIR}}` and never enter <!-- # CONFIGURE: {{HANDOFF_DIR}}: `.agents/handoff/` (gitignored) or "the system temporary directory". -->
version control: they carry logs, environment values, and credentials more
often than code does.

## Update this file when

- The tool is upgraded, replaced, or its layout moves.
- The level, a gate owner, or the approval mode changes.
- A second copy of any fact here appears; merge it back.
- The fast or full check changes.
