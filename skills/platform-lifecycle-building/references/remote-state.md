# Remote State with Parallel Agents

Read when the user states that more than one agent works on the repository
at the same time (parallel worktrees, several sessions, a fleet of agents).

Worktrees isolate files, not platform objects. Two agents commenting on
one issue leave a thread nobody can attribute; two writing labels on one
request overwrite each other; two pushing one branch lose commits. [§4.4]

## Where the rules live

The three remote rules (each agent owns its remote branch; platform writes
go through one coordinator; each such write is pre-authorised) belong to the
authority policy, written by the skill that owns the authority layer. The
platform knowledge file restates none of them. It carries only the
platform mechanics, in its "Parallel agents" section:

- the authority policy's path, as the source of the remote rules;
- the coordinator role (a named human, or the one agent designated as
  coordinator) that makes every label, comment, assignee, state, ready, and
  merge write;
- the per-agent branch pattern, for example `agent/<agent>/<n>-<slug>`.

Write it as one short paragraph and nothing more: no rule sentence about
branch ownership or pre-authorisation, no copy of the policy's wording.
[§4.4]

## Cases

| Situation | Write |
|---|---|
| One agent at a time | delete the "Parallel agents" section; no coordinator or per-agent branch rule anywhere |
| Parallel, authority policy present and holding the rules | the paragraph above, citing the policy by its path |
| Parallel, no authority policy yet | the paragraph above, citing the policy's agreed path (from the harness plan; `.agents/knowledge/agent-authority.md` when the plan names none); list the missing policy in the report as a handoff to the skill that owns the authority layer; write the rules into no file of your own |
| Parallel, the policy lacks the remote rules | the same handoff, naming the missing rules; do not add them to the platform file |
