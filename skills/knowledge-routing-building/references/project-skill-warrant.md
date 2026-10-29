# Project Skill Warrant and Handoff

Read when a candidate is a procedure, when the user asks for a skill, when
deciding whether a skill needs an explicit route, or when writing the
handoff for a confirmed skill.

## The bar

Recommend a project skill only when the procedure is all of:

- **recurring**: it will run again, in future sessions, by agents that did
  not learn it;
- **non-obvious**: an agent without the skill gets it wrong or has to ask;
- at least one of **fragile** (a small mistake costs), **order-sensitive**
  (steps must run in sequence), or **branchy** (the right action depends on
  conditions).

State which condition passed or failed, recommend, and wait for the user's
choice. The final carrier is the one the user confirms. [§2.3]

## Cheaper carriers

| Candidate | Carrier | Failed condition |
|---|---|---|
| "Run the type checker before pushing" | entrypoint line (Always, or a Validation recipe) | non-obvious: one command |
| Stable facts, no procedure (versions, limits, domain rules) | knowledge file | not a procedure |
| A constraint on one function or a local workaround | type or code comment ([inline-vs-document.md](inline-vs-document.md)) | not recurring across the project |
| A problem that happened once ("an agent misconfigured the cache") | knowledge line or code comment now; skill only if it recurs | recurring: one incident is an anecdote |
| A procedure still changing | nothing yet | it changes before it runs again |

Anti-patterns to recommend against: a skill wrapping one command the
Validation table already names; a "general guidelines" skill (no trigger
can fire precisely); one procedure split across two skills.

## Explicit routing

Description matching is probabilistic. A skill whose omission causes harm
(a check before every pull request is published, a migration gate) gets a
routing row: "When publishing a pull request, load the `pr-compliance`
skill." A skill that only helps (formatting changelog entries) gets no row;
tell the user description matching suffices and the row would cost every
session. Test: if the honest answer to question 1 of the four-question check
is "we hope the description matches" and a miss causes harm, route it.
[§2.3]

## Handoff definition

Pass one per confirmed skill to the skill that writes project skills,
described by that role. The handoff names no skill: not the writer, and
not a name for the new skill (the writer chooses it).

```markdown
Handoff to the skill that writes project skills

Procedure: <what the procedure accomplishes, one sentence>
Warrant: recurring because <evidence>; non-obvious because <evidence>;
<fragile | order-sensitive | branchy> because <evidence>
Trigger situations: <direct requests>; <indirect phrasings>; <the event or
agent behaviour that should load it>
Not for: <neighbouring tasks that must not load it>
Source material: <paths, runbooks, incidents>
Owned scripts: <operations longer than two lines, to live under the
skill's scripts/>, or none
Location: <the agreed skills folder>
Process-critical: <yes: report the chosen name so the routing row
"When <situation>, load the <name> skill" can be added | no>
User confirmed: <date or turn>
```

When the skill is not written before this layer reports, list its routing
row in the report as a follow-up waiting for the skill's name.
