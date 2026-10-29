# Installing the automation on GitHub

Read when installing or changing the Spec-Kit request automation in a
GitHub repository.

## What lands where

| Piece | From | To |
|---|---|---|
| Script | [assets/spec_kit_features.py](../assets/spec_kit_features.py) and its `_test.py` | `scripts/spec_kit_features.py` and `scripts/spec_kit_features_test.py` in the project |
| Check job | [assets/github/job-spec-check.yml](../assets/github/job-spec-check.yml) | a job in the existing checks workflow; `spec-check` added to the gate's `needs:` |
| Label workflow | [assets/github/workflow-spec-labels.yml](../assets/github/workflow-spec-labels.yml) | `.github/workflows/spec-labels.yml` |
| Labels | [assets/github/labels-spec.json](../assets/github/labels-spec.json) | three rows appended to the project's label file, keeping its extra fields |

Also set the checks workflow's `on.pull_request.types` to `[opened,
synchronize, reopened, ready_for_review, converted_to_draft]` so the verdict
follows the draft state. The gate is already required, so the check needs no
new required-check setting.

Fill each `# CONFIGURE:` line and remove its marker comment:
`{{PINNED_SHA}}` is the commit SHA of the checkout action release the
project's other workflows pin, followed by the same `# vX.Y.Z` comment;
`{{REQUEST_SHAPE}}` is `combined` or `split`, as the user confirmed. Done
when `grep -rn '{{[A-Z]' .github/` prints
nothing (Actions expressions `${{ … }}` are not placeholders).

## Fork safety [§3.2]

A pull request is an open-write source: anyone can put content there. One
rule carries the safety, and it is structural: **no object authored by the
request reaches a runner holding a writable token.**

- The label workflow runs on `pull_request_target`, so the workflow file and
  the checkout come from the base. It reads the head only through
  `snapshot`, which pulls the file list and the three documents from the
  REST API and parses them as data. Never add a checkout of the head, a
  `git fetch` of it, an install from it, or a `run:` of its files.
- The check job runs on `pull_request` with `contents: read` only, so
  reading the head there is ordinary.
- `permissions: {}` at the top of every workflow, explicit permissions per
  job, every action pinned by commit SHA.
- The label step applies only names of the literal taxonomy written in the
  workflow, so a tampered script cannot apply an arbitrary label.
- The snapshot caps files, bytes per file, total bytes, and API calls, and
  fails on a truncated tree or an undecodable document rather than label
  from partial data.

## Syncing the labels to the remote

1. Dry run: run the project's label sync tool in its plan mode, or, when the
   project has none, compare `gh label list --limit 500 --json
   name,color,description` with the label file. Print the additions and
   removals.
2. Wait for the user to approve that exact delta.
3. Apply it (`gh label create <name> --color <hex> --description <text>`
   per addition when no tool exists).
4. Read the remote back with the same list command and report what it now
   holds and any difference from the file.

When the token cannot create labels (`gh` answers 403 or 404), put the sync
under pending decisions with the exact delta and do not apply it another
way.

## Maintainer actions

These need repository settings; list each under pending decisions when the
agent cannot change it:

- The ruleset or branch protection requires the aggregator gate (recommended
  value: required on the default branch). When the repository has no gate,
  the check job has nothing to join; the install stops at step 6 of the
  skill's workflow.
- Actions may create workflow runs from `pull_request_target` on forks
  (default on; leave it).

## Verification after installing

- Every workflow parses, `permissions: {}` heads each, every `uses:` carries
  a 40-character SHA.
- `grep -n 'fetch\|checkout' .github/workflows/spec-labels.yml` finds only
  the base checkout.
- `python3 scripts/spec_kit_features.py --help` exits 0 and names
  `snapshot`, `check`, `status`, and `labels`; the project's test file
  passes.
- On a real pull request, `snapshot --repo <o/r> --pr <n> --output s.json`
  exits 0 and `status --snapshot s.json` equals `status --base <base sha>
  --head <head sha>` run in a clone.
- The next pull request touching a feature gets exactly one `spec:` label.
