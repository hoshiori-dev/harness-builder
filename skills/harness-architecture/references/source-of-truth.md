# Single Source of Truth

Read when a fact is recorded in more than one place, when the user asks
whether a copy is safe, or when a harness deliberately keeps two copies.

## Which place is the source

Code before documents. The file system is the source for topology, the task
runner's recipe for a command and its flags, the type signature for an
interface contract, the code comment for local counter-intuitive logic. A
document is the source only for what code cannot state: why something is
done, and when to read what [§1.3]. A fact copied from code into a document
is a copy that will expire; a large share of harness entropy comes from
such copies [§1.3] [§5.1].

## One fact, one place

Every fact lands in one place; every other place refers to it and does not
restate it. Of the two diseases of a stale harness, drifting from the code
is a missed update, but internal contradiction is almost always one fact
written in two places and updated in one. Contradiction is the more
dangerous: an agent facing two versions has no basis to adjudicate and
believes one at random. Fewer copies means fewer sync obligations [§5.2].

`CLAUDE.md` importing `AGENTS.md` (`@AGENTS.md`) instead of copying it is
an instance of this principle, not a framework trick: the agent that reads
either file reads the same text, and there is nothing to adjudicate [§2.1]
[§5.2].

## The adjudication rule

Wherever two places still state one fact, the harness writes down which
one wins when they disagree. Code (the recipe, the file system, the type)
wins over any document; among documents, the place the routing table
declares as the home of that fact wins [§5.2] [§2.1]. The rule is written
per fact, next to the fact or in the routing table, never derived from
file type: an entrypoint is no closer to code than a knowledge file. Until
the duplicates are removed, say explicitly which copy is authoritative so
the next agent does not choose at random [§5.2].

Example: the entrypoint, a knowledge file, and a README each list the test
command with different flags. The source is the task-runner recipe; every
document names only the recipe (`just test`), the flags exist in one place,
and the recipe is authoritative in the meantime. Collecting commands behind
one runner is also what makes the entropy layer's command check possible
[§5.3].

## Forward and reverse triggers

A sync rule names a trigger, or it is not a rule. Forward: when this part
of the code changes, update these harness files. Reverse: after editing a
harness file, verify the implementation facts it now claims (a command
described in the entrypoint runs as described; a step in a skill still
matches the script interface it calls; a directory described in an
architecture file exists as written, not as hoped). Reverse triggers are
the ones people forget, because editing a document does not feel like a
change that needs verification; by the entropy law it needs it no less than
a code edit [§5.2].

## Deviations must land

A harness requires that a deviation an agent finds (a document, script, or
skill that disagrees with the code) lands somewhere durable: fixed in place
when small and within the task's authority, added to the pending decisions
when intent is unclear, or tracked as an issue when large; a mention in
conversation disappears with the conversation [§5.2]. This skill reports
such a deviation as a finding and changes nothing.

## Copies that cannot be references

Some copies are forced (a README in two languages). Those are compensated
by a mirror check in the harness self-check: the check fails when the pair
diverges and names both files [§5.2] [§5.3].

## When the user wants to keep two copies

Do not rewrite the files. Record the contradiction as a finding: the two
files, the section violated (one fact in one place [§5.2]), and the mirror
check that would compensate for the deliberate copy, so the decision is
visible to the next agent and to the improvement entry. Challenge once with
the evidence, then answer within the user's choice.
