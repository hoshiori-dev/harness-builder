# Platform Settings Register

Read when configuring this repository's remote, when a check is "not running"
rather than failing, or before changing a remote setting. These are
account-side settings no checkout can recreate; each row is a convention
until the maintainer enables it and records the date here.

| Setting | Intended value | Tier | Readback |
|---|---|---|---|
| Ruleset on `main` | require a PR (0 approvals: solo maintainer; stale reviews dismissed; threads resolved; squash only); required checks `checks / gate`, `secrets / scan`, `checks / pr`, `checks / spec-archived`; block deletion and force push; no bypass actors, so the owner also merges through PRs | convention | `gh api repos/{owner}/{repo}/rulesets` → `main`, `active` |
| Merge methods | squash only; delete head branch on merge; squash commit = PR title + PR body | convention | `gh repo view --json squashMergeAllowed,mergeCommitAllowed,rebaseMergeAllowed,deleteBranchOnMerge` → `true,false,false,true` |
| Secret scanning + push protection | enabled | convention (GitHub default for public repositories; read back after creation) | `gh api repos/{owner}/{repo} --jq .security_and_analysis` → both `enabled` |
| Private vulnerability reporting | enabled (`SECURITY.md` sends reporters there) | convention | `gh api repos/{owner}/{repo}/private-vulnerability-reporting` → `{"enabled":true}` |
| Actions default token | read-only; workflows request `contents: write` per job | convention (GitHub default; read back after creation) | `gh api repos/{owner}/{repo}/actions/permissions/workflow` → `read`, approvals `false` |
| Repository metadata | description and homepage equal to `plugin.json`; topics from its `keywords` | convention | `gh repo view --json description,homepageUrl,repositoryTopics` |
| Labels | `.github/labels.json` applied by the `labels` workflow on every push to `main` that changes it; GitHub's default labels left in place | convention | `just labels` reports no drift |

Rows marked "convention" are not yet enabled on the remote. Enable them with
`gh repo edit`, `gh api -X POST repos/{owner}/{repo}/rulesets --input`,
`gh api -X PUT .../private-vulnerability-reporting`, and `just labels --apply`
from an authenticated `gh`, then record the date and the readback.
GitHub Pages: source "GitHub Actions" (the `docs` workflow deploys).

Secrets and variables: none required. The release workflow uses the
workflow's own `GITHUB_TOKEN`.

Update trigger: when a row changes tier (a setting is enabled), record the
date and the readback result in this table.
