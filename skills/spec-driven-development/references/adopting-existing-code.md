# Adopting Existing Code

Read when the project already holds code not written from a specification
(a prototype, a vibe-coded app, a brownfield codebase), before its first
change enters the loop. The loop in SKILL.md still applies; this covers what
comes before it.

## Rule: specify only what the next change touches

Write specifications only for the behaviour the next change touches.
Specifications for code nobody is changing have no change to keep them
true; they rot the day they are written and then mislead every agent that
trusts them. Asked to specify the whole codebase first, decline with that
reason and offer two things instead: the specification for the next change,
and an as-built map that claims no requirement. [§6.3]

## 1. Observe what exists

1. Run the software and observe what it actually does; do not infer
   behaviour from reading the code. The code is a reference implementation,
   not a source of truth.
2. List every document that states requirements or acceptance: README
   sections, design notes, open issues, code comments, exports the user
   offers.
3. List every observed behaviour no document explains, and ask the user to
   rule on each one: a requirement, a non-goal, or a defect. Never promote an
   accident to a requirement on your own.
4. Record what verification the code already has (tests, manual checks,
   none); the first scenarios must run against it.
5. When an existing specification contradicts the running code, apply the
   drift rule in SKILL.md before anything else.

Done when: the user has ruled on every unexplained behaviour that the next
change touches, and on the disposition of every requirement-bearing document
(step 5 lists the options; recommend one per document and wait for the
ruling).

## 2. Build the as-built map

The map describes, for agents, what the code does; it is not a
specification and states no requirement. One file, or one per module for a
large codebase, holding for each module: responsibility, entry points,
conventions, known problems, and integration points. Open each file with
`Mapped at commit <sha> on <date>` so a reader can tell when it went stale.
Keeping the map current by a check is harness work; describe it to the user
as the work of the skill that owns the entropy layer.

Done when: every module the next change touches is mapped, and the map
holds no "SHALL", "MUST", or acceptance criterion.

## 3. Choose the path

Recommend **anchor and evolve**: the code stays, every change from now on
enters the loop, and the specifications grow only where changes land. The
alternative is a rewrite feature by feature from specifications, only when
the user confirms the code cannot be maintained. The carrier follows the
SKILL.md default: the spec tool in use, else the lightweight carrier.

## 4. Run the first change through the loop

Take the next change (ideally small and visible) through all eight steps
before anything else. Record each friction it shows: a scenario that cannot
run reveals missing test infrastructure; a step the carrier does not fit
reveals a convention to record. A failing scenario in behaviour the change
does not touch is filed as a separate defect, never fixed inside the change.

## 5. Reconcile documents that restate requirements

For every document listed in step 1, recommend one disposition and apply
the one the user rules:

- a requirement for behaviour this change touches: move it into the
  specification and leave a pointer;
- a requirement for untouched behaviour: leave it, mark it descriptive, and
  reference it from the map;
- an open issue carrying acceptance criteria for this change: move the
  criteria into the change record; editing the issue to hold the link (or
  any other platform object) happens only when the approved package lists
  it, otherwise add the edit to the pending decisions list;
- duplicated statements: keep one, delete the rest.

Done when: no two files claim to be the source of truth for the same
behaviour of the change.

## 6. Hand the friction over

The frictions are input for the project's spec rules. Describe the skill
that owns the specification and completion layer as the place to record
them; edit no harness file from this skill.
