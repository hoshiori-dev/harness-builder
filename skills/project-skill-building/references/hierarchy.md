# Information hierarchy

Read when deciding what stays in `SKILL.md` and what moves to a reference,
when a step needs a boundary, or when choosing a leading word.

## The ladder

Rank every piece of content by how immediately the agent needs it:

1. **Steps**: ordered actions in `SKILL.md`, the primary tier.
2. **In-file reference**: rules and facts in `SKILL.md`, consulted on demand.
   A flat set of peers (every rule of a review on one rung) is a fine shape.
3. **Disclosed reference**: a `references/` file behind a pointer, loaded
   only when the pointer fires.

Branching decides the split: inline what every branch needs; disclose what
only some branches reach. In-file reference that should have been disclosed
buries the steps and makes attending to them a coin flip.

Within a rung, co-locate: a concept's definition, rules, and caveats under
one heading, not scattered through the file.

## Completion criteria

A `Done when:` marks the boundary of a step. Add one when the step is prone
to premature completion, when thoroughness matters, or when the result has an
observable success condition; omit it when it would not change how the agent
executes or judges the step.

Two properties make it a lever:

- **Clarity**: the agent can tell done from not done from evidence. "Every
  call site listed with file and line", not "understanding reached".
- **Demand**: how much it requires. "Every modified model accounted for"
  forces a sweep where "produce a change list" does not. Demand also binds
  flat reference: "every rule applied" drives coverage of a rule list.

These buy more the weaker the model: a strong model intuits the done-ness a
vague bound leaves unstated; a weaker one holds the path only when it can
check. A criterion written for the floor tier is never relaxed because the
development model did not need it.

## Pointer wording

The pointer's wording, not its target, decides whether and how reliably the
agent reaches a reference. A must-have reference
behind a weak pointer is a variance bug: sharpen the wording first, inline
the material only if sharpening fails. A reference loaded on every run has no
condition and belongs in `SKILL.md`.

## Leading words

A leading word is a compact concept already in the model's pretraining that
the agent thinks with while running the skill (_checkpoint_, _dry run_,
_exhaustive_). In the body it anchors execution; in the description it
anchors invocation, most strongly when the same word lives in the project's
prompts and docs. Prefer widely attested words: a niche term anchors one
model and recruits nothing on another. Hunt restatements to collapse: "fast,
deterministic, low-overhead" is a _tight_ loop. A word too weak to beat the
default is a no-op (_be thorough_); the fix is a stronger word
(_relentless_), not more sentences.

## Assets versus references

A reference is read to inform the agent's work and takes a load condition.
An asset is copied or emitted, not read; it is linked where it is used and
takes no read condition.
