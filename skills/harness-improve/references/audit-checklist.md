# Audit Checklist

Read before inventorying the first artifact of an audit, and again at the
final review for the closing checklist. The audit reads and reports; it
changes nothing.

## Where to look

- Entrypoints: `AGENTS.md`, `CLAUDE.md` (an `@AGENTS.md` import or a copy),
  `GEMINI.md`, `.github/copilot-instructions.md`, and every subdirectory
  entrypoint.
- Knowledge: `.agents/knowledge/`, `docs/` files an entrypoint names,
  `ARCHITECTURE.md`, `CONTRIBUTING.md` only as a source of facts.
- Project skills: `.agents/skills/`, `.claude/skills/` (real directory or
  symlinks), `.codex/skills/`, and any rules directory such as
  `.claude/rules/`.
- Client configuration: `.claude/settings*.json`, `.codex/config.toml`,
  `.codex/rules/`, `.gemini/`, hook scripts these name.
- Gates: `.pre-commit-config.yaml` or other hook managers, CI workflows
  (`.github/workflows/`, `.gitlab-ci.yml`), the task-runner file
  (`justfile`, `Makefile`, `package.json` scripts).
- Specification: `openspec/`, `.specify/` or `specs/`, `SPEC.md` and
  `PLAN.md`.
- Environment: `.devcontainer/`, container files, environment variables set
  for agents.
- Entropy: a harness self-check (`check_harness.py` or a recipe that runs
  one), a Keep In Sync section, a sync or cleanup skill.
- Platform: issue and pull-request templates, label definitions, branch
  model notes.
- History: the last 30 commit titles (commit convention, abandoned
  conventions); use history only to tell current from abandoned.

## Inventory fields

One row per artifact; write `none` where a field is missing.

| Field | Question | `none` usually means |
| --- | --- | --- |
| Discovery path | Which entrypoint line, route, or location makes an agent find it? | invisible |
| Load trigger | Always, on a stated condition, by file location, by event, or by name? | invisible or orphaned |
| Source of truth | Which file or tool must it agree with? | drifted, or duplicates code |
| Update mechanism | Which sync rule, check, or routine keeps it current? | will drift next |

## Classes

- **Stale**: names a path, command, interface, or structure that no longer
  exists. Check each path exists and each command against the task runner
  or manifest; run what is cheap to run.
- **Duplicated**: one fact in two places, still agreeing. Disposition: keep
  the copy at the source, replace the other with a pointer.
- **Contradictory**: one fact in two places, disagreeing, or a spec that
  contradicts the code. The source of truth decides which copy survives; for
  a rule that states intent, ask the user. Always the first plan item.
- **Invisible**: nothing reaches it, or its trigger can no longer fire.
  Disposition: reconnect (add the route) or remove; never leave.
- **Missing**: a layer the five variables call for has nothing. An absent
  harness self-check is always a missing finding for the entropy layer.
- **Excessive**: a constraint, lint rule, skill, routing entry, or gate
  that guards against something no longer present, or is thicker than the
  confirmed grade. Evidence by kind: a guard whose target is gone names the
  vanished cause; an over-thick gate names the confirmed grade it exceeds
  and what exceeds it. Disposition: thin or remove.

Also always check: a project check, hook, or recipe calling a script inside
a skill directory (the binding is the finding; the fix gives the project
its own copy); the entrypoint against the 100-line target and 120-line
limit; a document restating what code already states (directory listings,
command flags).

## Dispositions

Update (needed but wrong), reconnect (correct but unreachable), move (loaded
more often than it applies: behind a narrower pointer), merge (two files
always read together), split (part always needed, the rest conditional;
prefer merge), thin (valid but overweight), remove (obsolete, duplicated,
or its cause is gone), leave (accurate, reachable, proportionate). Ask
before removing anything that looks maintained.

## Finding format

```markdown
- <file>:<line>: <class>, <what is wrong>.
  Evidence: <files and lines>. Source of truth: <file or tool>.
  Disposition: <action> (proposed | user: <their choice and reason>)
```

Group findings by layer; quote the self-check's output above the hand
findings and do not repeat what it already reports.

## Observing a grade

| Layer | Observed light | Observed medium | Observed thick |
| --- | --- | --- | --- |
| Environment and sandbox | runs on the host, scoped tokens | documented environment file | container or VM isolation, network allow list, hard read-only security rules |
| Knowledge and routing | one root entrypoint pointing at existing docs | knowledge files behind routes | layered knowledge, architecture documents, subdirectory entrypoints |
| Hard boundary | formatting and secret scan only | lint, typecheck, tests in pre-commit and CI | plus architecture checks and an aggregate required gate |
| Authority | a few allow and deny entries | a written policy | plus irreversible-actions list and pending decisions format |
| Specification and completion | plan mode in conversation | a spec format in the repository | a spec framework with checkable scenarios, strict validation in CI |
| Entropy | a few sync reminders | a Keep In Sync table or sync skill, reference check | plus structural checks in CI and periodic cleanup |

Nothing at all is omitted. State an observed grade as observed.

## Closing checklist

Walk at the final review; mark each item passed, passed after a fix (name
the fix), or not applicable with a reason.

- [ ] Grades: each of the six layers graded on its own, each grade matching
  error cost, maintenance lifetime, isolation, autonomy, and team size.
- [ ] Entrypoint: always-applicable constraints first; routes organised by
  when an agent needs what; within budget.
- [ ] Loading: files split by loading behaviour, not topic; process-critical
  skills routed explicitly; subdirectory entrypoints carry only local
  additions, no rule that must always hold.
- [ ] Scripts and runtime: frequent complex commands wrapped in scripts;
  pagers and interactive prompts disabled by environment variables; a
  seconds-fast scoped test command exists.
- [ ] Hard boundary: hooks and CI in place; tools use their native quiet
  output; custom check messages say how to fix.
- [ ] Security and control plane: isolation decided on exposure, source
  reachability, and human in the loop; model resistance used only as a
  middle-grade adjuster and confirmed for each model in use; sandbox audited for host credentials, privileged
  sockets, local network exposure, and session-log destination; security
  rules hard read-only and engineering invariants stated soft read-only.
- [ ] Authority: irreversible actions pre-authorised in the spec; blocked
  work continues with a pending decisions list; allow and deny lists allow
  the known safe, deny the known dangerous, leave the rest to the default,
  with no needless ask entries; the policy protects itself.
- [ ] Specification and completion: spec alignment before work; each spec
  states completion, non-goals, and deliverables; scenarios a reader who
  never saw the code can judge.
- [ ] Checkpoints and commits: checkpoints are commits; squash unit is the
  task; drafts never leave the machine; secret scan runs on every commit.
- [ ] Hygiene: handoff files and session logs treated as secret and kept out
  of Git; parallel agents, when used, isolated by worktree, branch, and
  shared resource.
- [ ] Entropy loop: harness deviations an agent finds have a place to land;
  one source of truth per fact with forward and reverse sync rules, each
  pair named in both files; reference integrity and structural checks in
  CI; excessive constraints in the cleanup scope.

[§6.1] [§6.3] [§5.3]
