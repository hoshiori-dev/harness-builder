# Implementation Anchoring

Read when the user asks to code before the specification, when code
already exists for a change nobody approved, or when a requirement names an
implementation.

## Why the specification comes first

Code generated from a wrong understanding stays in the context and pulls
every later step toward itself. Asking the agent to rework a large wrong
implementation is slow and produces worse code than starting from an agreed
specification. Agreement before code is the cheapest point to absorb a
misunderstanding. [§4.1]

## "Just start coding, we'll write the spec after"

Say that the specification comes first, name the risk in one sentence
(code written before agreement anchors the approach, and the specification
written afterwards describes the code instead of the intent), and offer to
write the specification now. A short change gets a short specification;
plan mode is the lightest carrier.

## Code already written without an approved package

Treat it as a spike, not as the implementation:

1. Write the specification from the intent the user states, not from the
   code. Read the code only to answer clarify questions it can settle.
2. Publish the package and take the approval as usual.
3. After approval, keep the spike only where it satisfies the approved
   scenarios; drop the rest. When keeping it would need the specification
   to change, that is a deviation (loop step 5): propose it, do not absorb
   it.

## Implementation inside a requirement

A requirement that names a table, an index, a class, or a library fixes the
approach before review and anchors the work at its source. Rewrite it as the
observable behaviour it serves ("a duplicate email is rejected with a
conflict response"), and move the implementation idea to the design as a
constraint or preference, or drop it. [§4.1]

## Exploring alternatives

When two approaches are both plausible and the difference only shows when
run, try each on its own branch or worktree, compare by running them, keep
one, and remove the others and their worktrees as soon as the comparison
ends. The chosen approach goes into the design; the rejected one goes into
its rejected alternatives. [§4.3]
