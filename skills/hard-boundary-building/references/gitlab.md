# GitLab Checks

Read when writing or changing a GitLab CI pipeline for the project's checks.

## Which asset, where

| Grade | Deliver | Target path |
|---|---|---|
| light | [assets/gitlab/ci-secret.yml](../assets/gitlab/ci-secret.yml), plus a root file holding only `stages: [check]` and the `include:` | `.gitlab/ci/secret.yml`, `.gitlab-ci.yml` |
| medium | [assets/gitlab/ci-checks.yml](../assets/gitlab/ci-checks.yml) without `boundaries`, `gate`, and the `gate` stage, plus the secret file | `.gitlab-ci.yml`, `.gitlab/ci/secret.yml` |
| thick | both files whole | `.gitlab-ci.yml`, `.gitlab/ci/secret.yml` |

An existing `.gitlab-ci.yml` keeps its other jobs and stages; merge the
check jobs into it and present the merged file in the step-5 list.

## Rules every pipeline keeps

- **One pipeline per change**: the `workflow: rules:` block runs merge
  request pipelines and suppresses the duplicate branch pipeline.
- **Pinned images.** Replace each image tag with a digest
  (`image: python:3.12-slim@sha256:<digest>`) once the user confirmed the
  image; record who updates it.
- **No hidden failures.** No `allow_failure: true` on a check, no `|| true`.
- **Recipes, not inline logic**: each job runs the recipe that also runs
  locally.

## The gate (thick only)

In GitLab a job left out by `rules:` simply does not exist in the pipeline,
so "skipped" leaves no trace a later job can read without an API token.
The asset therefore has each check job write a marker artifact only on
success; the gate runs `when: always` with every check in `needs:` as
`optional: true` and fails, naming them, when any listed marker is missing,
covering failed, cancelled, and skipped jobs alike. Keep `GATE_JOBS` and
`needs:` listing the same jobs.

## Remote actions for a human

"Pipelines must succeed" for merges, protected branches, and push rules
are project settings outside this layer. List them in the report for a
human or the layer owning the platform lifecycle; never change them.

## Validating

Run `glab ci lint` when `glab` is available and authenticated; otherwise
parse the YAML and check that every `needs:` entry and every `GATE_JOBS`
word names a job in the pipeline.
