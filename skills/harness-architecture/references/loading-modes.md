# Loading Modes

Read when a placement recommendation depends on location, action, or
description-matched loading, or when the user wants to put a constraint in
a subdirectory entrypoint. The question to answer first is "when does the
agent need this content?"; the mode follows [§2.2].

## The five modes

| Content is needed | Lands in | Loading decided by |
| --- | --- | --- |
| On every task | Always-applicable block at the top of the root entrypoint | Nobody; resident |
| By task type | Knowledge file named in the routing table, or a flow-critical skill the entrypoint names by scenario | The agent, from the routing table |
| By location | Subdirectory entrypoint file, path-matched rules (framework-dependent) | The framework, when the agent touches that location |
| By action | Event-triggered injection, such as a hook around a class of tool call (framework-dependent) | The framework, when the event fires |
| As a recognisable auxiliary flow | Description-matched skill | The framework, by description similarity |

The first two work in every framework. The last three load without the
agent having to realise it needs the content, so they beat the routing
table on reliability and description matching on determinism, with the
limits below [§2.2].

## Framework caveats

Location and action loading are framework-dependent. Frameworks disagree
on when a subdirectory file loads and on what wins when several apply:
some load it on demand when the agent reads or writes under that directory,
some load only the chain from the working directory to the root at start-up
and never look below, some define "nearest wins" without saying whether the
parent also applies. Whether a project may rely on these modes is decided by
which frameworks the team expects to use: one framework, confirmed to
support it, may rely on them; mixed or undecided frameworks use them only
for local, supplementary information [§2.2].

Behaviour recorded in the methodology as of October 2026, to be checked
against each framework's current documentation before relying on it:

- Claude Code loads `CLAUDE.md` from the working directory and its
  ancestors at start-up, loads a subdirectory's file when the agent reads
  or writes under it, and supports path-matched rules under
  `.claude/rules/`.
- Codex loads `AGENTS.md` from the repository root down to the working
  directory and concatenates them; it does not load files below the working
  directory.
- Gemini CLI loads a directory's `GEMINI.md` and its ancestors when a tool
  touches that directory, concatenated and sent with every prompt.
- Cursor applies a nested `AGENTS.md` when working in that directory or
  below, merged with parents, the more specific winning; glob-matched rule
  files attach automatically.
- GitHub Copilot documents only "nearest `AGENTS.md` wins", with no
  statement about parents; its `applyTo`-matched instruction files apply
  to the cloud agent and code review only.
- The `agents.md` convention itself fixes only "nearest to the edited file
  wins" and defines no loading moment.

When the repository does not show which frameworks the team uses, ask
before recommending location or action loading; the answer changes the
placement.

## The defensive rule for subdirectory files

Framework-independent and never waived: a subdirectory entrypoint carries
no constraint that must take effect, and never contradicts the root. The
first because the file may never load; the second because which file
overrides which differs between frameworks, so a contradiction resolves
unpredictably. Global safety rules and commit discipline live only in the
root entrypoint [§2.2].

## Hooks: soft or hard

A lifecycle hook that blocks a class of operation is a hard boundary; one
that injects "remember to update X" after a class of operation is a soft
boundary [§2.2]. A hook is not the default home of a sync rule: a small
project keeps the rule as a line in the root entrypoint, and a hook or a
sync skill replaces it only when the project is medium or large with many
sync items, a thickness decision that belongs to the entropy layer and its
builder [§5.2] [§6.1].

## Description matching is probabilistic

Good enough for an optional auxiliary skill. For a flow-critical skill (a
pre-commit compliance review, a release procedure) a ten percent miss rate
equals not having the skill, so the entrypoint names it explicitly by
scenario: "when you are about to do X, invoke Y". The test is the first of
the four routing questions: if the honest answer to "how does the agent
know it needs this?" is "we hope the description matches", and a miss
causes harm, route it explicitly [§2.1] [§2.3].

## Placement answers by content

- A rule whose violation is costly whatever the task (secret handling,
  commit discipline, the validation command): always-applicable block of
  the root entrypoint. Not a subdirectory file (may not load), not a
  knowledge file (loads only when routed), not a skill (probabilistic)
  [§2.1] [§2.2].
- Information or architecture needed for a class of task: a knowledge file
  with a routing line stating when to read it [§2.3].
- A recurring, non-obvious procedure that is fragile, ordered, or branching:
  a project skill; flow-critical ones routed explicitly [§2.3].
- A fact code can state (directory layout, command flags, interface): not
  in a document at all; point at the code or the recipe [§1.3].
- Local, historical "why we did this": a comment beside the code [§1.3].
- Something needed only when editing one directory, in a team on one
  framework confirmed to load it: a subdirectory file, supplementary only
  [§2.2].
- A forward sync rule ("when X changes, update Y"): a keep-in-sync line in
  the root entrypoint, naming its trigger; a hook or sync skill only under
  the condition in "Hooks: soft or hard" above [§5.2] [§6.1].
- An entrypoint or a draft of one: apply the lines above to each block,
  then report the resulting line count against the budget stated in
  `SKILL.md`; always-applicable constraints are never squeezed out to meet
  it [§2.1].
