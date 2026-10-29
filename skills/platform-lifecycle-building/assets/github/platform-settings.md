Read this when changing or relying on a GitHub setting: merge methods, the default-branch ruleset or branch protection, required checks, label sync, or repository features.

# GitHub Platform Settings

Remote state no checkout can prove. One row per setting. Status is
`enforced` (the platform refuses a violation), `convention` (a named person
enforces it; the trigger says what would make it a setting), `declined`
(the user kept the current value; the trigger reopens it), or
`pending human` (the command a human still has to run).

Repository `{{OWNER_REPO}}`: {{OWNER_TYPE}} owner, {{VISIBILITY}}, {{PLAN}} plan. {{VERIFIED_STATE}} <!-- # CONFIGURE: the probed facts, then "Read back on DATE." or "UNVERIFIED: written from facts the user supplied." -->

| Setting | Current | Target | Status | Owner | Readback | Trigger |
|---|---|---|---|---|---|---|
| Merge methods | {{CURRENT}} | {{TARGET}} | {{STATUS}} | {{OWNER}} | `gh api repos/{{OWNER_REPO}} --jq '{allow_squash_merge,allow_merge_commit,allow_rebase_merge,delete_branch_on_merge}'` | {{TRIGGER}} | <!-- # CONFIGURE: one row; e.g. target "squash only, branch deleted on merge". -->
| Default-branch ruleset | {{CURRENT}} | {{TARGET}} | {{STATUS}} | {{OWNER}} | `gh api repos/{{OWNER_REPO}}/rulesets` | {{TRIGGER}} | <!-- # CONFIGURE: e.g. target "changes only through pull requests, no force push, no deletion, no bypass"; on a private personal free repository: status convention, trigger "plan upgrade or public visibility". -->
| Legacy branch protection | {{CURRENT}} | {{TARGET}} | {{STATUS}} | {{OWNER}} | `gh api repos/{{OWNER_REPO}}/branches/{{DEFAULT_BRANCH}}/protection` | {{TRIGGER}} | <!-- # CONFIGURE: record "none" too; a stale rule silently tightens the ruleset. -->
| Required checks | {{CURRENT}} | {{TARGET}} | {{STATUS}} | {{OWNER}} | `gh api repos/{{OWNER_REPO}}/rulesets/<id>` | {{TRIGGER}} | <!-- # CONFIGURE: only job names that already ran green on the default branch; otherwise "none yet" with the trigger "first green run of JOB". -->
| Labels | `.github/labels.json` | same | {{STATUS}} | {{OWNER}} | `gh label list -R {{OWNER_REPO}} --json name,color,description` | label file changes | <!-- # CONFIGURE: status, and whether the labels workflow or a person runs the sync. -->
| Label pruning | off | off | enforced | {{OWNER}} | the sync's `delete` list is empty | a user-approved delete list | <!-- # CONFIGURE: the owner. -->
