---
name: plugin-development
description: >-
  Adds, changes, or removes a skill or the agent shipped by this plugin, end
  to end: OpenSpec change with behavioural test scenarios, implementation to
  the skill quality bar, client file generation, checks, behavioural tests
  through subagents, and per-client verification. Use when the user asks to
  add or modify what the plugin ships, when a catalog or skills check fails,
  or when a client stops loading a component. Not for changing which clients
  or catalogs the repository supports (template-adjust) or for GitHub issue
  and PR mechanics (github-project-workflow).
---

# Plugin development

Every shipped entry lives in exactly one catalog and is described by exactly
one spec; `just validate` enforces the pairing. Work spec first, and treat the
spec's scenarios as the entry's behavioural tests.

## Workflow

1. **Define.** Write down the task the skill covers (one coherent unit of
   work), its triggers including indirect phrasings, what the agent lacks
   without it, and its invocation mode (user-invoked only for the two entry
   skills). If a bare agent already does the task well, stop: the skill adds
   nothing. Read `.agents/knowledge/skill-quality.md`.
2. **Spec, tests first.** Read `.agents/knowledge/spec-workflow.md`. Run the
   `openspec-propose` skill with the capability path `<catalog>/<name>`. The
   delta spec carries the behavioural test cases as scenarios: at least three
   prompts that should load the skill and three near misses that should not,
   and at least two outcome tasks with a rubric a reader can judge without
   the skill. State which clients the entry ships to. Stop until the pull
   request carries `spec:approved`.
3. **Implement by catalog** (read `.agents/knowledge/client-matrix.md`):
   - *skill*: `skills/<name>/SKILL.md` per `skill-quality.md`; shared
     paragraphs copied from `.agents/knowledge/shared-blocks.md`; a layer
     builder states `Owns the <layer> layer`; scripts and script assets in
     Python with PEP 723 metadata and a `_test.py` each.
   - *agent*: `com.anthropic.claude-code/agents/<name>.md` only (Codex and
     Antigravity plugins carry no agents; `just validate` rejects an
     `agents/` directory under their namespaces); read-only tools unless the
     spec justifies writes.
4. **Prune.** Three passes over everything written: deduplicate, drop what
   no longer bears on the skill, delete every sentence that would not change
   behaviour on the weakest supported model.
5. **Generate and check.** `just gen` after any change to `plugin.json` or
   an agents directory; `just skills-check`; `just check`. Fix findings at
   their source; never edit a generated file or relax a check.
6. **Behavioural tests.** Run the spec's trigger prompts and outcome tasks
   through clean-context subagents on the least capable model tier
   available; trigger prompts never name the skill. Record pass/fail per
   scenario in the PR's Verification section; record the degradation when no
   subagent is available and the prompts ran in a fresh session instead.
7. **Verify in clients.** `just clients-validate`, then load the entry by
   hand in at least one client (`claude --plugin-dir .`, the Codex
   marketplace, `agy plugin install .` then `agy plugin uninstall
   harness-builder`). Record anything that contradicts the matrix.
8. **Finish.** Update both README skill tables; `openspec-apply-change`
   tracks tasks; archive per `spec-workflow.md`; the PR follows
   `github-project-workflow`.

## Removing an entry

Delete the implementation and the spec in one change (a delta spec with
`## REMOVED Requirements`), remove the README rows, run `just gen`, and
`just check`.

## Gotchas

- `claude plugin validate --strict` fails on any unknown top-level key in
  `.claude-plugin/plugin.json`; that file is generated, so fix `gen.ts`.
- A skill name must not also exist under `.agents/skills/`; Codex and
  Antigravity load both directories here.
- A description over 900 characters is a warning, over 1024 an error; cut
  identity, keep triggers.
- A shared block edited in one skill fails `just skills-check` until the
  canon and every other user change too.
