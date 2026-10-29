# Branching Model and Releases

Read when recommending a branching model, when the probe shows branches
other than the default (`develop`, `release/*`, `staging`, `production`),
or when the user asks how releases are cut.

## The recommendation

| Evidence | Recommend |
|---|---|
| One long-lived branch, or no release history | **GitHub Flow**: short-lived branches cut from the default branch, one per issue, merged through a pull or merge request and deleted on merge |
| `staging`, `production`, or similar branches with deployments or environments attached | **GitLab Flow, environment branches**: work merges into the default branch; promotion merges the default branch into each environment branch in order |
| Several released versions maintained at once (`release/1.x` with fixes landing after newer releases) | **GitLab Flow, release branches**: work merges into the default branch; fixes are cherry-picked into each supported release branch |
| `develop` and `release/*` already in use | keep **git-flow**; say once that it is not recommended for new work, because two integration branches double every merge and agents pick the wrong base |

Never propose git-flow for a project that does not already use it. When
recommending GitHub Flow, name the two GitLab Flow variants in one sentence
each as the alternatives, then wait. Record the evidence the recommendation
relied on (branch names, environments, tags) in the report.

## What the knowledge file states

- The model in one line and the branch name pattern (`<n>-<slug>` is what
  `gh issue develop` produces; keep an existing pattern when history shows
  one).
- The base branch for new work and where fixes land.
- With parallel agents only: the per-agent branch pattern, written as
  `remote-state.md` says.
- Branches are deleted on merge (GitHub `delete_branch_on_merge`, GitLab
  `remove_source_branch_after_merge`), applied as a remote setting.

## Releases

Recommend a release triggered by pushing a version tag (`vX.Y.Z`) on the
default branch: a human or a pre-authorised agent pushes the tag, and one
workflow or pipeline job builds and publishes from it. Reason: the tag is
the single, reviewable act that ships, and the history needs no bot
commits. The alternative, in one sentence: a release-management bot opens
and maintains a release pull request from commit messages, at the cost of
bot commits, a token with write access, and a second tool to configure.

Write no release automation until the user has chosen. If the user picks
the bot, challenge the choice once with the reason above; if they keep it,
record it as their decision and plan the bot's configuration as a file of
its own in the plan, which the user approves like any other.

With tags chosen, the plan names one workflow (GitHub: `on: push: tags:
["v*"]`, `permissions: contents: write`, publishing with `gh release create
"$GITHUB_REF_NAME" --generate-notes`) or one GitLab job (`rules: - if:
$CI_COMMIT_TAG`, publishing through the `release:` keyword), pinned by
digest. Who may push tags goes into the knowledge file's release rule.
