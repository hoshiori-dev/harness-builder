# Description: the trigger

Read when drafting or rewriting a description.

The description is the only text the agent reads before activating, and it
is loaded on every turn. It does two jobs: name the capability and list the
triggers. The trigger clause is the payload; the capability is a short
third-person lead-in (action verb or domain concept, then what the skill
makes predictable), never a feature list. Features are identity, and identity
lives in the body. Prune the description harder than the body.

## Shape

```text
<Leading word> <capability clause, third person>. Use when <trigger>;
when <trigger>; when <trigger>. Not for <neighbour> (<who handles it>).
```

- Open on the leading word. Never "This skill helps …", "A tool for …".
- "Use when" holds most of the length. Each trigger is one branch; a synonym
  for a branch already listed is duplication.
- "Not for" names the adjacent tasks that share vocabulary and must not fire
  the skill, and where each belongs. A near miss the tests will exercise
  appears here.
- Nothing the body also says. If a sentence lives in both, keep the copy
  where the hierarchy ranks it (usually the body) and delete the other.
- Budget: warning above 600 characters, strong warning above 900, error
  above 1024. Over 900 is defensible only when every trigger is a distinct
  branch.

## Mining triggers

Walk every signal type asking "should this fire the skill?":

- Direct naming and indirect phrasings: what a user says without naming the
  domain ("the deploy keeps going wrong" for a release skill).
- Intent verbs: create, fix, review, migrate, release.
- The scenario the user is in and the observed agent behaviour the skill
  corrects ("the agent skipped the smoke test again").
- The shape of the material at hand: a pasted or open file of the skill's
  kind.
- Lifecycle events: before a release, after a schema change.
- Questions about the domain.
- Exclusions: the adjacent tasks that must not fire it.

Word triggers with the leading words the project actually uses in its
prompts, docs, and code; the agent links shared language to the skill and
fires it more reliably.

## Invocation mode

Recommend model-invoked: the description stays visible, the agent and other
skills can reach it, and the project pays the context cost of one more
description on every turn. Make a skill user-invoked only when it must never
fire except by the human typing its name; the human then carries the cost of
remembering it, and no other skill can reach it. The switch is host-specific
and outside the Agent Skills specification: read `spec-portability.md` in
this directory before writing it.
