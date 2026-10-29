# Contributing

Thanks for helping improve this plugin. The short version: work from an
issue, propose behaviour changes as an OpenSpec change, keep `just check`
green, and open a draft pull request early. Rules live in `AGENTS.md` and
`.agents/knowledge/`; this page is the overview for people.

## Set up

Open the repository in the dev container; `.devcontainer/setup.sh` installs
the git hooks and the docs-site tool. Without the container you need deno
2.x, uv (for `just`, `pre-commit`, `ruff`, `pytest`, and `zensical`),
betterleaks, openspec 1.15, and optionally the client CLIs.

## Make a change

1. Pick or open an issue using the forms (bug, feature, task).
2. Branch with `gh issue develop -c <n>` and open a draft PR right away.
3. For a change to a shipped skill or the agent, add an OpenSpec change
   (`openspec/changes/<id>/`) whose delta spec carries the skill's
   behavioural test scenarios, and wait for a maintainer to add
   `spec:approved` before implementing. Harness, tooling, documentation, and
   docs-site changes are spec-less; the pull request is labelled
   `spec:skipped` automatically.
4. Implement; run `just gen` after touching `plugin.json` or an agents
   directory; run `just check` before every push. Skill scripts are Python
   with PEP 723 metadata and a `_test.py` each; management scripts in
   `scripts/` are Deno.
5. Run the behavioural tests of a changed skill through clean-context
   subagents and record the results in the PR, then mark it ready. A
   maintainer reviews, the change is archived on the branch, and the PR is
   squash-merged.

## Conventions

- Code, comments, the harness, and the skills are English; `README.md` and
  `docs/` are Chinese, with `README.en.md` as the English mirror.
- Commit messages and PR titles follow Conventional Commits with a lowercase
  subject (`feat(skills): add entropy-building`); no AI attribution.
- Never edit generated files; the hooks and CI fail on drift.
- Never commit secrets; betterleaks runs on every commit locally, and CI
  scans every pushed commit.

## Reporting security issues

See `SECURITY.md`.
