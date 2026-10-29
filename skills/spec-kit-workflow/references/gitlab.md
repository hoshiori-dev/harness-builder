# Installing the automation on GitLab

Read when installing or changing the Spec-Kit request automation in a
GitLab project.

## What lands where

| Piece | From | To |
|---|---|---|
| Script | [assets/spec_kit_features.py](../assets/spec_kit_features.py) and its `_test.py` | `scripts/spec_kit_features.py` and `scripts/spec_kit_features_test.py` in the project |
| Jobs | [assets/gitlab/ci-spec-jobs.yml](../assets/gitlab/ci-spec-jobs.yml) | included from `.gitlab-ci.yml` or pasted in; stage `spec` added to `stages:` |
| Labels | [assets/gitlab/labels-spec.json](../assets/gitlab/labels-spec.json) | three rows in the project's label file (GitLab colors carry `#`) |

Fill each `# CONFIGURE:` line and remove its marker comment:
`{{PYTHON_IMAGE}}` is an image the project already uses that has `python3`
and `git` (and `curl` and `jq` when the label token is set), pinned by tag
or digest; `{{REQUEST_SHAPE}}` is `combined` or `split`, as the user
confirmed. Done when `grep -rn '{{[A-Z]' .gitlab-ci.yml <fragment>` prints
nothing.

## What GitLab offers, and does not

Tell the user these when installing. The behaviour was verified against
GitLab's documentation on 2026-09-17 by the material this skill derives
from and was not re-checked on 2026-10-29; re-check it before asserting a
detail the user disputes.

- No pipeline starts on a label change or a merge request note, so a label
  a job applies shows after the next pipeline, not at once.
- A merge request pipeline runs the CI configuration of the merge request's
  own branch. No job can run on the base ref the way GitHub's
  `pull_request_target` does, so no job here holds a privileged token by
  default: without `SPEC_LABELS_TOKEN`, `spec:labels` prints the plan and
  changes nothing.
- Pipelines for a merge request from a fork run in the fork, without the
  parent's variables, so the label stays unwritten for a fork. Refuse to
  enable running fork pipelines in the parent project as a workaround:
  GitLab then runs the fork's CI configuration with the parent's variables
  and tokens. [§3.2]
- Enforcement is the project setting **Pipelines must succeed**.

## The label token

`SPEC_LABELS_TOKEN` is a decision for the user, listed under pending
decisions with this deviation spelled out: GitLab cannot run a privileged
job on the base ref, so with the token `spec:labels` holds a write token
while running the merge request branch's own CI configuration and
`scripts/spec_kit_features.py`. That breaks the rule that every privileged
job runs on the base ref and reads the head only as data, and anyone who
can push a branch can read the token.

- Token (recommended when the user accepts that deviation): a project
  access token with `api` scope and the lowest role that may edit merge
  request labels (Reporter in current GitLab; confirm in the project's
  version), stored as a masked variable, because that role gives a branch
  pusher nothing they lack.
- No token: every job stays unprivileged and the rule holds; the plan is
  printed and no label is applied, so the `spec:` labels stay absent on
  GitLab. Name that cost.

Install the fragment either way; it changes nothing until the variable
exists.

## Syncing the labels to the remote

1. Dry run: run the project's label sync tool in its plan mode, or compare
   `glab label list` (or `GET /projects/:id/labels`) with the label file.
   Print the additions and removals.
2. Wait for the user to approve that exact delta.
3. Apply it (`glab label create --name <name> --color <#hex> --description
   <text>` per addition when no tool exists).
4. Read the remote back and report what it now holds.

When the token cannot create labels, put the sync under pending decisions
with the exact delta and do not apply it another way.

## Maintainer actions

- Enable "Pipelines must succeed" once `spec:check` has run (recommended:
  on).
- Create the label token if the user chose one, and record it by name only.

## Verification after installing

- The fragment parses; no placeholder remains.
- `python3 scripts/spec_kit_features.py --help` exits 0; the project's test
  file passes.
- A test merge request: `spec:check` runs on each push and fails on a
  touched feature without a plan; `spec:labels` prints a plan naming one
  `spec:` label.
