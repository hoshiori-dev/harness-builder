# Value: what a skill adds

Read when deciding whether a requested skill adds anything a bare agent
lacks, or which instruction pattern fits the process it covers.

## Two ways a skill earns its load

- **Context provision**: supplying what the agent does not already have:
  project-specific conventions, non-obvious procedures, exact formats and
  commands. Skip explanations of standard concepts.
- **Output restriction**: reducing variance so the same process runs every
  time, with the patterns below. The goal is the same process on every run,
  not identical output.

A skill may do one or both. One that does neither on the least capable
model the project runs restates what the agent already does.

## Write to the floor

"The agent" is not one model. A project skill runs on whatever tier the
project's agents use, so every model-relative judgement (what the agent
lacks, what counts as standard, whether a sentence is a no-op) is made
against the least capable tier the skill must carry. A stronger model
tolerates a restriction it does not need; a weaker one breaks without it.

Teach the approach, not one worked instance: instructions must survive task
variation. Calibrate specificity to fragility: fragile or ordered operations
get prescriptive steps; where several approaches are valid, say why, not
what. Write for agents: directive, no pleasantries.

## Instruction patterns

Use each where it applies, none by obligation.

- **Gotchas**: non-obvious facts the agent would get wrong by reasonable
  assumption (naming inconsistencies, soft deletes, endpoints that lie). Add
  one only when a correction reveals a reusable failure; "validate inputs"
  adds no signal.
- **Checklists**: for multi-step workflows with dependencies or gates.
- **Validation loops**: do, validate, fix, repeat. A validator whose errors
  say what is wrong and how to fix it lets the agent self-correct without a
  round trip to the user.
- **Plan, validate, execute**: for batch or destructive operations: a
  structured plan, validated against a source of truth, then executed. The
  validation is never skipped.
- **Templates (assets)**: only for material that is intentionally fixed or a
  stable pattern the agent copies or lightly edits. Content needing
  task-specific judgement, broad rewriting, or flexible organisation becomes
  instructions, never an asset. An asset carries inline fill guidance
  (placeholders, embedded comments); the prose about when and how to use it
  lives in `SKILL.md` or a reference.

## Granularity

Each split spends one of two loads: another model-invoked skill adds a
description to every turn (context load); another user-invoked skill adds
something the human must remember to call (cognitive load). Split only when
the cut earns it: by invocation, when a distinct leading word should trigger
the new skill on its own or another skill must reach it; by sequence, when
visible later steps tempt the agent to rush the current one, and only across
a real context boundary (a hand-off or a subagent dispatch).
