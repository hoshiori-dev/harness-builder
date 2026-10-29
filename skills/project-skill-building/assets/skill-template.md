---
name: skill-name
description: >
  <Leading word first, third person: what this skill makes predictable, in
  one clause.> Use when <the direct request>; when <an indirect phrasing that
  never names the domain>; when <the agent behaviour this skill corrects, or
  the lifecycle event that calls for it>. Not for <the adjacent task that
  shares vocabulary, and where it belongs instead>.
license: <the project's licence identifier, or omit the line>
# compatibility: <only when the skill ships scripts, e.g. "Scripts need Python 3.10+; uv optional.">
---

# <Skill Title>

<One paragraph: the unit of work this skill covers and what the agent would
get wrong without it.>

## Rules on every step

- <A rule every branch needs, stated once here and nowhere else.>

## Workflow

1. <First action, imperative, with the input it reads.>
2. <Action with a meaningful boundary.>
   Done when: <observable criterion; exhaustive where thoroughness matters,
   e.g. "every call site listed with file and line">.
   Read `references/<topic>.md` when <the precise condition only some runs
   meet>.
3. <Verification action.>
   Done when: <command> exits 0 and <the evidence a reviewer can see>.

## Gotchas

- <A non-obvious fact the agent would get wrong by reasonable assumption.>
