Read this when changing or relying on a GitLab setting: merge method, squash, protected branches, pipeline-must-succeed, approvals, or label sync.

# GitLab Platform Settings

Remote state no checkout can prove. One row per setting. Status is
`enforced` (the platform refuses a violation), `convention` (a named person
enforces it; the trigger says what would make it a setting), `declined`
(the user kept the current value; the trigger reopens it), or
`pending human` (the command a human still has to run).

Project `{{PROJECT_PATH}}` on {{HOST}}: {{OWNER_TYPE}} namespace, {{VISIBILITY}}, {{PLAN}} tier. {{VERIFIED_STATE}} <!-- # CONFIGURE: the probed facts, then "Read back on DATE." or "UNVERIFIED: written from facts the user supplied." -->

| Setting | Current | Target | Status | Owner | Readback | Trigger |
|---|---|---|---|---|---|---|
| Merge method and squash | {{CURRENT}} | {{TARGET}} | {{STATUS}} | {{OWNER}} | `glab api projects/{{PROJECT_ID}}` (merge_method, squash_option, remove_source_branch_after_merge) | {{TRIGGER}} | <!-- # CONFIGURE: one row; e.g. target "fast-forward, squash required, source branch removed". -->
| Protected default branch | {{CURRENT}} | {{TARGET}} | {{STATUS}} | {{OWNER}} | `glab api projects/{{PROJECT_ID}}/protected_branches/{{DEFAULT_BRANCH}}` | {{TRIGGER}} | <!-- # CONFIGURE: e.g. target "push: no one, merge: maintainers, force push off". -->
| Pipelines must succeed | {{CURRENT}} | {{TARGET}} | {{STATUS}} | {{OWNER}} | `glab api projects/{{PROJECT_ID}}` (only_allow_merge_if_pipeline_succeeds) | {{TRIGGER}} | <!-- # CONFIGURE: on only after the pipeline ran green on the default branch; otherwise "off" with the trigger "first green pipeline on the default branch". -->
| Approval rules | {{CURRENT}} | {{TARGET}} | {{STATUS}} | {{OWNER}} | `glab api projects/{{PROJECT_ID}}/approval_rules` | {{TRIGGER}} | <!-- # CONFIGURE: required approvals need Premium; on Free: status convention, trigger "tier upgrade". Delete the row when no approvals were agreed. -->
| Labels | `.gitlab/labels.json` | same | {{STATUS}} | {{OWNER}} | `glab api "projects/{{PROJECT_ID}}/labels?per_page=100"` | label file changes | <!-- # CONFIGURE: status, and whether the CI job or a person runs the sync. -->
| Label pruning | off | off | enforced | {{OWNER}} | the sync's `delete` list is empty | a user-approved delete list | <!-- # CONFIGURE: the owner. -->
| Label sync token | {{CURRENT}} | {{TARGET}} | {{STATUS}} | {{OWNER}} | `glab api projects/{{PROJECT_ID}}/access_tokens` | expiry or rotation | <!-- # CONFIGURE: name, scope, role, expiry, and rotation owner; never the value. Delete the row when a person runs the sync. -->
