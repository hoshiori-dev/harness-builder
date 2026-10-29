# Installing the automation on GitLab

Read when installing, changing, or repairing the OpenSpec merge request
automation in a GitLab project, after the user approved the plan that names
the files.

## What lands where

| Piece | From | To |
|---|---|---|
| Script and its test | [assets/spec_changes.py](../assets/spec_changes.py), `assets/spec_changes_test.py` | `scripts/spec_changes.py` and `scripts/spec_changes_test.py`, wired into the project's test recipe |
| Jobs | [assets/gitlab/ci-spec-jobs.yml](../assets/gitlab/ci-spec-jobs.yml) | included from `.gitlab-ci.yml` (`include: local:`), with a `spec` stage added |
| Label rows | [assets/gitlab/labels-spec.json](../assets/gitlab/labels-spec.json) | merged into the project's existing label file |
| Artifact rules | the block in `references/config-yaml.md` | `openspec/config.yaml`, after the user confirms |

Replace both `# CONFIGURE:` lines: an image the project already uses that
carries bash, git, python3 3.10+, node, curl, and jq; and the project's own
command that installs its pinned OpenSpec CLI.

## What differs from GitHub

Tell the user these when installing:

- No named required checks. `spec:archive` is the withheld check: while the
  tree holds an unarchived change it is created as a blocking manual job
  (`when: manual`, `allow_failure: false`, stage `.post`), the pipeline shows
  *blocked*, nothing is red, and the project setting **Pipelines must
  succeed** keeps the merge closed. Running it by hand fails it. The rule
  reads the tree, so it sees every unarchived change, not only related ones;
  that matches a default branch that never holds one. Confirm on the first
  live merge request that a blocked pipeline holds the merge, and record the
  observation in the project's checks knowledge.
- No pipeline starts on a label change, and a merge request pipeline runs
  the request's own configuration and head, so it can never hold a writable
  token. `spec:labels` therefore runs only in a pipeline on the default
  branch (a pipeline schedule, or **Run pipeline** on that branch): it labels
  every open merge request into that branch, fork requests included, reading
  each head as git objects (`refs/merge-requests/<iid>/head`) through the
  script's git plumbing, never checking it out or running it. Labels and an
  approval a Maintainer adds therefore take effect on the next pipeline on
  the default branch, normally the schedule's next run.
- Approval is a Maintainer or Owner adding `spec:approved`; the job reads who
  added it from the label events and their access level from the members
  API.
- `SPEC_LABELS_TOKEN` is a project access token with the Reporter role and
  `api` scope, masked and **protected**, so only default-branch pipelines
  see it. Never expose it to merge request pipelines, and **never enable
  running fork pipelines in the parent project**: that runs the fork's
  configuration with the parent's variables.
- No job archives or pushes; archiving is the person's command on the
  branch, as on GitHub.

## Pending decisions this install produces

- Enable **Pipelines must succeed** after `spec:check` has passed once.
- Create `SPEC_LABELS_TOKEN` (Reporter, `api`, masked, protected) and a
  pipeline schedule on the default branch; recommended cadence: every 15
  minutes, the delay before a label follows an edit or an approval.
- Label sync: when the project has a label-sync tool, its dry-run plan,
  applied only after the user approves; otherwise remaining work routed to
  the platform lifecycle layer.

## Verification after installing

- `grep -rn '{{[A-Z_]*}}' .gitlab-ci.yml <fragment> scripts` finds nothing;
  the CI lint (`glab ci lint` or the pipeline editor) accepts the file.
- A test merge request: `spec:check` passes, `spec:archive` waits as a manual
  job while a change is unarchived and is absent after the archive commit,
  and no merge request pipeline contains `spec:labels`.
- A run of the schedule: `spec:labels` prints one plan per open merge
  request, naming only `spec:*` labels.
