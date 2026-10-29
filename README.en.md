# harness-builder

[中文](README.md)

An Agent Plugins v1.0.0 plugin that **creates, improves, and restructures the
agent harness** of other projects. It turns the Agent Harness construction
methodology into skills that load in Claude Code, Codex, and Antigravity: two
user-invoked entry points (create / improve), a methodology manual, six
builders, one per harness layer, a platform lifecycle builder, and
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

## Documentation

The methodology document and the skill guides are published at
<https://hoshiori-dev.github.io/harness-builder/> (Chinese).

## Development

Open the dev container and run `just check`. Workflow, specification, and
authority conventions live in [AGENTS.md](AGENTS.md) (the agent entrypoint)
and [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache-2.0, see [LICENSE](LICENSE).
