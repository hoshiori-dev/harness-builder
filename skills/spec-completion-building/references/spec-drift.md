# Drifted Specs

Read when a spec contradicts the code or another spec, when the user defers
a fix-or-delete decision, or when the user asks for specs covering every
existing module.

A wrong harness is worse than none, and a drifted spec is the sharpest case:
the next agent believes the spec and builds on the lie. Fixing or deleting
it comes before other work in that area. [§5.1]

## Reporting

For each contradiction report three things: the spec (path and
requirement), the other source (code path and line, or the second spec),
and what each says. Then the three options:

- **Fix the spec** to describe what the code does. Recommend this when the
  code's behaviour is intended (a later commit changed it on purpose, or
  the user confirms it) and future changes will touch that behaviour.
- **Delete the spec** (or the requirement). Recommend this when the
  capability is gone or no future change will touch it.

- **Keep the spec, report a defect**: the code is wrong; the spec stays and
  the user files a bug. Recommend this when the spec matches the latest
  stated intent (an issue, a recent spec change) and no commit changed the
  behaviour on purpose.

Which side is right is the user's call: never apply any option, the defect
reading included, without the user's answer. Ask once for all
contradictions together, one recommendation each.

## Applying and deferring

- A decision given: apply it as part of the approved plan, before the layer
  is reported done.
- A decision deferred: add one pending item per contradiction with all
  three options and the recommendation; name the spec in the contract as not yet
  authoritative; continue every step that does not depend on it.

## Back-fill requests

Recommend specs only for behaviour future changes touch; existing code no
change touches is described by the codebase map (an as-built, non-normative
description). A back-filled spec nothing keeps honest is the next drift.
Record the user's final choice, with their reason when they keep the
back-fill.
