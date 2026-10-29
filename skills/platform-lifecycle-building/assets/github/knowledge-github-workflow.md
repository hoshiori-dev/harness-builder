Read this when taking, creating, or finishing an issue or pull request, before any `gh` write, when a check is red, or before changing labels, issue forms, branch rules, or merge settings.

# GitHub Workflow

Repository `{{OWNER_REPO}}` on {{HOST}}: {{OWNER_TYPE}} owner, {{VISIBILITY}}, {{PLAN}} plan. <!-- # CONFIGURE: the probed facts; write "plan unknown" when the probe could not read it. -->
Remote settings, their owners, and readbacks: {{SETTINGS_PATH}}; {{SETTINGS_STATE}}. <!-- # CONFIGURE: the register's path, then "every row read back on DATE" or "UNVERIFIED: written from facts the user supplied; the remote actions listed there await a human". -->
The procedure for every issue and pull request is the `github-project-workflow` project skill.

## Objects in use

| Object | Use |
|---|---|
| Issues | every unit of work; the bug, feature, and task forms in `.github/ISSUE_TEMPLATE/` set the `type:` label |
| Labels | `type:` one per issue (what), `area:` (where); `spec:` is reserved for the specification workflow, which appends its rows to `.github/labels.json` and keeps no label file of its own |
| Pull requests | the only path into the default branch; opened as drafts; body from `.github/pull_request_template.md` with `Closes #<n>` |
| Not used | Projects, boards, milestones; add one only when the user can name what management ability is lost without it |

`.github/labels.json` is the one label definition. `scripts/sync_labels.py`
plans by default and changes labels only with `--apply`; it deletes labels
only with `--prune`, which runs only when the user approves that exact
delete list.

## Branches and merging

{{BRANCHING_RULE}} <!-- # CONFIGURE: the agreed model and branch names, e.g. "GitHub Flow: short-lived <n>-<slug> branches from main, one per issue, deleted on merge." -->
{{MERGE_RULE}} <!-- # CONFIGURE: e.g. "Squash only: the pull request title becomes the commit on main, so it follows the commit convention." -->
{{PROTECTION_RULE}} <!-- # CONFIGURE: what protects the default branch and whether the platform or a named person enforces it; or "The default branch accepts direct pushes (declined on DATE by OWNER; reopens when CONDITION)." -->

## Releases

{{RELEASE_RULE}} <!-- # CONFIGURE: the agreed release rule, e.g. "A maintainer pushes a vX.Y.Z tag on main; the release workflow publishes it." -->

## Specification workflow

<!-- harness: spec-workflow -->

## Parallel agents

{{PARALLEL_AGENTS}} <!-- # CONFIGURE: delete this section when one agent works at a time. Otherwise: "Remote rules for parallel agents: AUTHORITY_PATH. Coordinator for label, comment, state, ready, and merge writes: COORDINATOR_ROLE. Per-agent branch pattern: agent/<agent>/<n>-<slug>." -->

## Synchronization

| Pair | Trigger |
|---|---|
| `.github/labels.json` ↔ issue-form `labels:` ↔ the label row above | any label added or renamed |
| `.github/pull_request_template.md` checklist ↔ the project skill's Finish step | either is edited |
| the settings register ↔ the remote | any remote setting changes; read it back and record the readback |
