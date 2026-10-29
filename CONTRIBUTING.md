# Contributing

Thanks for helping improve this plugin. The short version: work from an
issue, propose behaviour changes as an OpenSpec change, keep `just check`
green, and open a draft pull request early.

## Set up

Open the repository in the dev container; `.devcontainer/setup.sh` installs
the git hooks. Without the container you need deno 2.x, uv (for `just` and
`pre-commit`), betterleaks, openspec 1.15, and optionally the client CLIs.

## Make a change

1. Pick or open an issue using the forms (bug, feature, task).
2. Branch with `gh issue develop -c <n>` and open a draft PR right away.
3. For a change to a shipped skill, MCP server, or agent, add an OpenSpec
   change (`openspec/changes/<id>/`) and wait for a maintainer to add
   `spec: approved` before implementing. Harness, tooling, and documentation
   changes are spec-less and need no change directory; the pull request is
   labelled `spec: skipped` automatically.
4. Implement; run `just gen` after touching `plugin.json`, `mcp.json`, or an
   agents directory; run `just check` before every push.
5. Mark the PR ready when the checklist is ticked. A maintainer reviews, the
   change is archived on the branch, and the PR is squash-merged.

## Conventions

- Everything in the repository is written in English.
- Commit messages and PR titles follow Conventional Commits with a lowercase
  subject (`feat(skills): add release-notes skill`).
- Never edit generated files; the hooks and CI fail on drift.
- Never commit secrets; betterleaks runs on every commit locally, and CI
  scans every pushed commit.

## Reporting security issues

See `SECURITY.md`.
