# Git Branching Contract

Read before creating a branch, opening a pull request, merging, or tagging.

Model: GitHub Flow. Selected because the plugin ships from one line of
development and every version is a tag of `main`.

## Long-lived branches

| Branch | Meaning | Accepts merges from | Protection |
|---|---|---|---|
| `main` | releasable; every commit passed `checks / gate` | short-lived branches by squash merge | ruleset `main`: PR required, checks required, no force push, no bypass (see `github/platform-settings.md`) |

## Short-lived branches

Name: `<n>-<slug>` as `gh issue develop -c <n>` generates it, where `<n>` is
the issue number. Cut from `main`, merged into `main`, deleted on merge. One
agent, one branch; never push to another agent's branch.

## Commits

Conventional Commits: `<type>(<scope>)?: <subject>` with a lowercase,
imperative subject and no trailing period; types `feat`, `fix`, `docs`,
`refactor`, `test`, `chore`, `ci`, `build`, `perf`, `style`, `revert`; scopes
are catalog or area names (`skills`, `mcp`, `agents`, `harness`, `ci`). No AI
or tool attribution trailers. Checkpoint commits on the branch are allowed;
squash-merge produces the one commit on `main`, whose message is the PR title
and body.

## Tags and versions

`vX.Y.Z` equals `plugin.json#version` (SemVer); `just dist --tag` refuses a
mismatch. Tags are cut from `main` after the version bump merged; pushing the
tag runs the release workflow. Hotfixes follow the same path: branch from
`main`, fix, bump, tag.

## Merge method

Squash for every contribution. Rationale: one commit per change keeps release
notes and `git bisect` aligned with pull requests.
