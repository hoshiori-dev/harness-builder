# harness-builder

[中文](README.md)

An Agent Plugins v1.0.0 plugin that **creates, improves, and restructures the
agent harness** of other projects. It turns the Agent Harness construction
methodology into skills that load in Claude Code, Codex, and Antigravity: two
user-invoked entry points (create / improve), a methodology manual, six
builders, one per harness layer, a platform lifecycle builder, a project-skill
writer, and
spec-driven development (SDD) with three carriers (OpenSpec, Spec-Kit, a
lightweight SPEC.md). A read-only verifier agent reads a freshly built
harness back in a clean context (Claude Code only).

Every decision is confirmed with the user: the plugin recommends, with
reasons, and never chooses on the user's behalf.

## Install

- **Claude Code**: `/plugin marketplace add hoshiori-dev/harness-builder`,
  then install `harness-builder`; for local development, `claude --plugin-dir .`.
- **Codex**: `codex plugin marketplace add hoshiori-dev/harness-builder`, then
  `codex plugin add harness-builder@harness-builder`.
- **Antigravity**: `agy plugin install https://github.com/hoshiori-dev/harness-builder`.

Scripts and template assets bundled with the skills are Python (PEP 723,
standard library first): they run with `uv run` where uv exists and with a
plain `python3` where it does not. Target projects never need Deno.

## Skills

| Skill | Invocation | Summary |
|---|---|---|
| [`harness-create`](skills/harness-create/SKILL.md) | User-invoked | Creates a project's first harness: reads the repository, tells greenfield from brownfield, asks the five variables, grades the six layers row by row, builds layer by layer after plan approval, then reads back and reviews in a clean context. |
| [`harness-improve`](skills/harness-improve/SKILL.md) | User-invoked | Audits, repairs, thins, hardens, or migrates an existing harness: audit first, the user decides repair or rebuild, then each layer goes to its builder. |
| [`harness-architecture`](skills/harness-architecture/SKILL.md) | Model-invoked | The methodology manual: five variables, context economics, five loading modes, single source of truth, the entropy law; answers "where should this rule live". |
| [`environment-building`](skills/environment-building/SKILL.md) | Model-invoked | Environment and sandbox layer: keeps an existing isolated environment, otherwise lists options for the user; lethal-trifecta tiering, five-item sandbox audit, control-plane spectrum, non-interactive environment. |
| [`knowledge-routing-building`](skills/knowledge-routing-building/SKILL.md) | Model-invoked | Knowledge and routing layer: AGENTS.md (always-on block, routing table, validation, Keep In Sync), knowledge-file splits, scripts with denoised output. |
| [`project-skill-building`](skills/project-skill-building/SKILL.md) | Model-invoked | Writes, improves, and diagnoses a target project's skills: tests first, description and body hierarchy, pruning, a bundled lint_skill.py, behavioural tests through subagents. |
| [`hard-boundary-building`](skills/hard-boundary-building/SKILL.md) | Model-invoked | Hard-boundary layer: formatting, secret scanning, lint, typecheck, tests, and a CI gate by grade; custom checks whose errors route to the fix; management-script language confirmed with the user. |
| [`authority-building`](skills/authority-building/SKILL.md) | Model-invoked | Authority layer: actions classified by reversibility, approval at both ends with a pending decisions list, a fixed deny list and a user-confirmed allow list with no ask entries, checkpoint-commit rules. |
| [`spec-completion-building`](skills/spec-completion-building/SKILL.md) | Model-invoked | Specification and completion layer: level and carrier, the four completion answers, approval gate modes, the spec contract, and the handoff to the carrier skill. |
| [`entropy-building`](skills/entropy-building/SKILL.md) | Model-invoked | Entropy layer: correction reports that land, a Keep In Sync table or a sync skill, a delivered check_harness.py in CI, periodic reclamation and thinning. |
| [`platform-lifecycle-building`](skills/platform-lifecycle-building/SKILL.md) | Model-invoked | Platform lifecycle layer on GitHub or GitLab: minimal entity set with a deletion test, branching and merge methods, forms, templates, labels, the publish gate, and the project workflow skill. |
| [`spec-driven-development`](skills/spec-driven-development/SKILL.md) | Model-invoked | Spec-driven development methodology: the eight-step loop, specification quality rules, the approval package, how specs meet issues and PRs, adopting existing code without backfilling. |
| [`openspec-workflow`](skills/openspec-workflow/SKILL.md) | Model-invoked | OpenSpec carrier: approval package, in-request archive, the awaiting-archive gate, status labels, and GitHub or GitLab automation. |
| [`spec-kit-workflow`](skills/spec-kit-workflow/SKILL.md) | Model-invoked | Spec-Kit carrier: spec-plus-plan approval package, completion when every task is ticked, the lock declaration, status labels and platform automation. |
| [`lightweight-spec-workflow`](skills/lightweight-spec-workflow/SKILL.md) | Model-invoked | Lightweight carrier: plan mode for small edits, SPEC.md or PLAN.md for mid-size changes, with the completion answers, scenarios, non-goals, and pre-authorised actions. |

Plus the Claude Code agent [`harness-verifier`](com.anthropic.claude-code/agents/harness-verifier.md): read-only, reads a freshly built harness back in a clean context and reports gaps file by file.

## Documentation

The methodology document and the skill guides are published at
<https://hoshiori-dev.github.io/harness-builder/> (Chinese).

## Development

Open the dev container and run `just check`. Workflow, specification, and
authority conventions live in [AGENTS.md](AGENTS.md) (the agent entrypoint)
and [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache-2.0, see [LICENSE](LICENSE).
