# Platform Settings Register

Read when configuring a repository created from this template, when a check is
"not running" rather than failing, or before changing a remote setting. These
are account-side settings no checkout can recreate; the template ships them as
conventions until the owner enables them, then records the date here.

| Setting | Intended value | Tier | Readback |
|---|---|---|---|
| Ruleset on `main` | require a PR (0 approvals: solo maintainer; stale reviews dismissed; threads resolved; squash only); required checks `checks / gate`, `secrets / scan`, `checks / pr`, `checks / spec-archived` (required since 2026-10-27, after #7 merged); block deletion and force push; no bypass actors, so the owner also merges through PRs | enabled 2026-10-27 (ruleset id 25938075) | `gh api repos/{owner}/{repo}/rulesets` → `main`, `active` |
| Merge methods | squash only; delete head branch on merge; squash commit = PR title + PR body | enabled 2026-10-27 | `gh repo view --json squashMergeAllowed,mergeCommitAllowed,rebaseMergeAllowed,deleteBranchOnMerge` → `true,false,false,true` |
| Secret scanning + push protection | enabled | enabled (GitHub default for this public repository, read 2026-10-27) | `gh api repos/{owner}/{repo} --jq .security_and_analysis` → both `enabled` |
| Private vulnerability reporting | enabled (`SECURITY.md` sends reporters there) | enabled 2026-10-27 | `gh api repos/{owner}/{repo}/private-vulnerability-reporting` → `{"enabled":true}` |
| Actions default token | read-only; workflows request `contents: write` per job | enabled (GitHub default, read 2026-10-27) | `gh api repos/{owner}/{repo}/actions/permissions/workflow` → `read`, approvals `false` |
| Template repository | enabled on the template itself, off on repositories created from it | enabled 2026-10-27 | `gh repo view --json isTemplate` → `true` |
| Repository metadata | description and homepage equal to `plugin.json`; topics from its `keywords` | enabled 2026-10-27 | `gh repo view --json description,homepageUrl,repositoryTopics` |
| Labels | `.github/labels.json` applied by the `labels` workflow on every push to `main` that changes it; GitHub's default labels left in place | applied 2026-10-27; workflow since #5 | `just labels` reports no drift |

Rows marked "enabled" describe this repository. A repository created from
the template starts at "convention" again: run the same commands there
(`gh repo edit`, `gh api -X POST repos/{owner}/{repo}/rulesets --input`,
`gh api -X PUT .../private-vulnerability-reporting`, `just labels --apply`)
and record the date.

Secrets and variables: none required. The release workflow uses the
workflow's own `GITHUB_TOKEN`.

Update trigger: when a row changes tier (a setting is enabled), record the
date and the readback result in this table.
