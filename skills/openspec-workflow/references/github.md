# Installing the automation on GitHub

Read when installing, changing, or repairing the OpenSpec request automation
in a GitHub repository, after the user approved the plan that names the files.

## What lands where

| Piece | From | To |
|---|---|---|
| Script and its test | [assets/spec_changes.py](../assets/spec_changes.py), `assets/spec_changes_test.py` | `scripts/spec_changes.py` and `scripts/spec_changes_test.py` in the project, wired into its test recipe |
| Check jobs | [assets/github/job-spec-check.yml](../assets/github/job-spec-check.yml) | two jobs pasted under `jobs:` of the project's existing checks workflow |
| Label workflow | [assets/github/workflow-spec-labels.yml](../assets/github/workflow-spec-labels.yml) | `.github/workflows/spec-labels.yml` |
| Label rows | [assets/github/labels-spec.json](../assets/github/labels-spec.json) | merged into the project's existing label file; never a second file |
| Artifact rules | the block in `references/config-yaml.md` | `openspec/config.yaml`, after the user confirms |

When the project already has a label workflow or a pull-request label script
(say one that already keeps `spec:*` labels), compare it with the asset and
propose one owner of the labels; two writers of the same label fight.

## Fitting the check jobs

- Add `spec` to the gate job's `needs:`. Leave `spec-archived` out of it: it
  succeeds either way, and its *name* is the signal.
- Rename `checks / …` to the workflow's own job-name prefix; the required
  check is then `<prefix> / spec-archived`. Keep the names unique across
  workflows, since rulesets match by name.
- The workflow must trigger on `pull_request` and on `push` to the default
  branch; a `push` run reports the required name, so the platform has seen
  it before any ruleset asks for it.
- Replace the `# CONFIGURE:` line with the command the project already uses
  to install its pinned OpenSpec CLI (a setup action, a lockfile install),
  so the version pin stays in one place. If the project pins none, that is a
  pending decision, not a version you pick.
- `--draft` comes from `github.event.pull_request.draft`; the job only warns
  on a draft, and the required name is withheld on a draft as on a ready
  request, because a success on a draft's head would still count after it is
  marked ready without a new commit.

## Pinning

Every `uses:` names a commit SHA with the tag as a comment
(`actions/checkout@<sha> # v7.0.1`). Take the SHA the project's other
workflows already use for the same action; the asset carries the one this
skill was verified with. Before committing, replace any tag reference in an
asset or in a workflow you touched with its commit SHA plus the tag comment;
read the SHA from the action's release, never guess it.

## Fork safety

- `checks / spec` runs on `pull_request`: a fork's run gets a read-only token
  and no secrets, so checking out the head there is safe.
- `spec / labels` runs on `pull_request_target`, with a token that can label
  and comment. It checks out the default branch, reads the head only through
  `snapshot` (REST API, parsed as data), and never fetches, checks out,
  installs, or runs anything of the request. Request-controlled values reach
  the shell only through `env`. Never add a head checkout, a `git fetch` of
  the head, or a `run:` of its files to it.
- Every job sets explicit least `permissions:` under a top-level
  `permissions: {}`; no job holds `contents: write`.
- No job archives, pushes, or answers comments; no comment-triggered
  workflow is installed.

## How the approval record works

A person with write permission adds `spec:approved`. The `labeled` run reads
that person's permission and the head through the snapshot, and `labels`
returns a record (commit, account, package hash) that the workflow writes as
one comment by `github-actions[bot]` before it touches a label. The package
is every file of the unarchived related changes except `tasks.md`, so tasks
written after approval keep it. Any later run keeps `spec:approved` only
while the record stands and the hash matches; otherwise it puts
`spec:pending` back and marks the record withdrawn. A failed run removes
`spec:approved`.

## Pending decisions this install produces

- Ruleset (never applied by the agent): require `<prefix> / spec-archived`
  (with the existing gate) on the default branch, after it has reported once
  on a `push` run. A required check the platform has never observed blocks
  every request.
- Label sync: when the project has a label-sync tool, its dry-run plan,
  applied only after the user approves; otherwise remaining work routed to
  the platform lifecycle layer.

## Verification after installing

- `grep -rn '{{[A-Z_]*}}' .github scripts` finds nothing.
- Every `uses:` is a 40-character SHA; every job declares `permissions`.
- `grep -n 'ref:\|fetch\|checkout' .github/workflows/spec-labels.yml` shows
  only the default-branch checkout.
- `python3 scripts/spec_changes.py --help` exits 0; the project's test recipe
  runs `scripts/spec_changes_test.py` and passes.
- On a test pull request: `checks / awaiting-archive` while a change is
  unarchived, `checks / spec-archived` after the archive commit; the label
  workflow's log shows the plan it applied.
