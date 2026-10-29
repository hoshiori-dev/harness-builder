# GitHub

Read when the target's platform is GitHub: before proposing settings,
before writing the files, and before any remote write.

## What the plan and visibility allow

Owner type, plan, and visibility are separate facts from the probe; a
missing one is asked, never inferred from another.

| Capability | Available on |
|---|---|
| Rulesets, branch protection, required checks, required reviews, CODEOWNERS enforcement | public repositories on every plan; private repositories only on Pro (personal), Team, or Enterprise |
| Merge-method settings, labels, issue forms, PR template, Actions | every plan and visibility |
| Bypass by team or app | organisation-owned repositories only |

On a private repository of a personal free account, nothing can refuse a
merge: each protection becomes a convention with an owner in the settings
register, and its trigger is "plan upgrade to Pro, or public visibility".
Say this before proposing the protection, not after.

## Files

| File | Path in the target |
|---|---|
| issue forms | `.github/ISSUE_TEMPLATE/bug.yml`, `feature.yml`, `task.yml`, and `config.yml` |
| PR template | `.github/pull_request_template.md` |
| label file | `.github/labels.json` |
| label sync workflow | `.github/workflows/labels.yml` (only when automated sync was chosen) |
| CODEOWNERS | `.github/CODEOWNERS` (only when it passed the deletion test) |
| scripts and tests | `scripts/sync_labels.py`, `scripts/run_log_digest.py`, and their `_test.py` files, or the project's own scripts path |
| knowledge | `github-workflow.md` and `platform-settings.md` in the knowledge directory |
| project skill | `github-project-workflow/SKILL.md` in the project skills directory |

## Remote writes

Each write below is one delta: show the current value (the readback) and
the exact command or JSON, apply only after the user approves that delta,
then run the readback again and record it in the settings register.

**Merge methods**, squash only:

```sh
gh api -X PATCH repos/OWNER/REPO -F allow_squash_merge=true -F allow_merge_commit=false \
  -F allow_rebase_merge=false -F delete_branch_on_merge=true \
  -f squash_merge_commit_title=PR_TITLE -f squash_merge_commit_message=PR_BODY
gh api repos/OWNER/REPO --jq '{allow_squash_merge,allow_merge_commit,allow_rebase_merge,delete_branch_on_merge}'
```

**Default-branch ruleset**, written to a file outside the repository and
shown as the delta:

```json
{
  "name": "default-branch",
  "target": "branch",
  "enforcement": "active",
  "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
  "bypass_actors": [],
  "rules": [
    {"type": "deletion"},
    {"type": "non_fast_forward"},
    {"type": "pull_request", "parameters": {
      "required_approving_review_count": 0,
      "dismiss_stale_reviews_on_push": false,
      "require_code_owner_review": false,
      "require_last_push_approval": false,
      "required_review_thread_resolution": false}}
  ]
}
```

Apply with `gh api -X POST repos/OWNER/REPO/rulesets --input <file>` (an
existing ruleset: `-X PUT repos/OWNER/REPO/rulesets/<id>`), read back with
`gh api repos/OWNER/REPO/rulesets/<id>`. The approval count is the user's
answer; 0 suits a single maintainer. An empty `bypass_actors` binds admins
too; legacy branch protection exempts admins unless `enforce_admins` is on.

**Required check**, added later as its own delta: append
`{"type": "required_status_checks", "parameters": {"strict_required_status_checks_policy": false, "required_status_checks": [{"context": "<job name>"}]}}`
to the ruleset's rules, only after `gh run list -R OWNER/REPO --branch <default> --workflow <file> --status success --limit 1`
shows a green run.

**Labels**: `python3 scripts/sync_labels.py --file .github/labels.json --repo OWNER/REPO`
prints the plan; the same with `--apply` after approval; `gh label list -R OWNER/REPO --json name,color,description`
is the readback.

## Gotchas

- A required check matches the job's displayed name. A path-filtered job
  that is skipped reports success, and a renamed job leaves its required
  check waiting forever; require an aggregating gate job, not a filtered one.
- Rulesets and legacy branch protection both apply, most restrictive wins:
  record both in the register, including "none".
- Labels named in an issue form that do not exist are dropped silently, so
  the label sync runs before the forms are relied on.
- `gh issue create` without `--template` ignores forms; the project skill
  mirrors their headings.
- A draft pull request on a public repository is public the moment it opens.
- Label colours are six hex digits without `#`.
