# Multi-Agent Concurrency

Read when the user describes or asks about more than one agent working at
once. A single agent is the default; for a single agent none of this is
raised [§4.4].

## Workspace: split by read and write

- Read-only concurrency (review, architecture analysis, security scan):
  several agents share one working directory; no worktree needed.
- Writing concurrency (several agents modifying files at once): one
  `git worktree` or one container per agent, so nobody overwrites another's
  files [§4.4].

## Shared resources to check before parallel runs

Anything two agents could hold at the same time: local ports, test database
instances or schemas, fixed-path lock files, build cache directories,
external API rate limits. Allocate dynamically or namespace per instance
[§4.4].

## Remote shared state

A worktree isolates files, not the platform. Two agents commenting on the
same issue produce a thread nobody can read; two agents labelling one pull
request overwrite each other; two agents pushing one remote branch lose
each other's commits on a force push. Three rules:

1. Each agent owns its own remote branch; none is shared.
2. Writes to platform objects (issues, comments, labels, states) go through
   one coordinator, a human or one designated agent; parallel agents only
   produce results.
3. Those writes are external and irreversible, so each is pre-authorised
   in the plan or specification, never decided by an individual agent
   [§4.2] [§4.4].

## Merging back

Name who merges and who adjudicates conflicts before the agents start.
Split the work along file boundaries at planning time; the quality of the
split decides whether concurrency pays [§4.4].

## Before recommending it

Frameworks differ in what their multi-agent support delivers (concurrent
subagents, context sharing, structured returns); a team member on a
framework without the capability runs degraded. Context cost multiplies
with the agent count, worse when prompts share no stable prefix. Confirm
the frameworks in use and the merge owner with the user before the
recommendation; both are facts the repository rarely shows.

## Answer shape for a concurrency design

For N agents each fixing one package: one worktree and one remote branch
per agent; the shared resources above listed and namespaced; one
coordinator for platform writes with those writes pre-authorised; a named
merge owner and conflict adjudicator; each point tagged. No file is built.
