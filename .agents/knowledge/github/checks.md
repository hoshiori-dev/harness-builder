# Checks

Read when a check is red or when adding, renaming, or removing a recipe or job.
Every CI job runs a `just` recipe that also runs locally; the recipe is the
source of truth and this table is the map.

| Job name (required-check name) | Workflow and trigger | Recipe | What a healthy run shows |
|---|---|---|---|
| `push / check-fast` | `push`: every push to a branch other than `main` | `just check-fast` | `deno fmt --check`, `deno lint`, `deno check`, the tests, and each check script end clean |
| `checks / lint` | `checks`: pull requests, push to `main` | `just pre-commit` | every hook `Passed`, including `just gen --check` and betterleaks on the whole tree |
| `checks / test` | `checks` | `just test` | Deno tests of the management scripts and pytest of the skills' Python assets pass |
| `checks / plugin` | `checks` | `just gen --check`, `just validate`, `just skills-check`, `just harness-check` | each ends with `...: ok` |
| `checks / spec` | `checks` | `just spec-check` | `openspec validate --all --strict` lists every spec and change as passed |
| `checks / docs` | `checks` | `just docs-check` | the Zensical strict build finishes with `No issues found` |
| `checks / gate` | `checks` | none (aggregator) | success when every `checks /` job above succeeded; required by the ruleset |
| `secrets / scan` | `secrets`: every push and every pull request | `just secrets-commits <range>` | betterleaks reports `no leaks found` for the commits the push or pull request added; required by the ruleset |
| `checks / pr` | `pr`: pull request opened, edited, synchronized, reopened, ready for review | `deno run scripts/check_pr.ts` | `check_pr: ok`; required by the ruleset |
| `checks / archive-verdict` | `pr` | `just spec-archived` | `no unarchived change` (status 0) or the change names (status 1); any other status is a failure |
| `checks / spec-archived` or `checks / awaiting-archive` | `pr`, after `archive-verdict` | none (carrier) | the job succeeds under the first name when no change is unarchived and under the second while one is; only `checks / spec-archived` is required by the ruleset, so the merge stays blocked until the archive lands and nothing turns red |
| `labels / pr` | `pr-labels`: pull request opened, reopened, synchronized, labeled, unlabeled (`pull_request_target`), or dispatch | `just pr-labels <n>` prints the same decision without writing | the decided state label and the label writes; never a required check |
| `labels / sync` | `labels`: push to `main` touching `.github/labels.json`, or dispatch | `just labels --apply` | `applied N change(s)` or `labels: in sync`; holds `issues: write` and never runs on a pull-request event (the other write-token jobs are `labels / pr` and `release / publish`) |
| `release / publish` | `release`: tag `v*` | `just check`, `just dist --tag` | a published release with `dist/<name>-<version>.zip` attached |
| `docs / deploy` | `docs`: push to `main` touching the site | `just docs-build` | the site is deployed to GitHub Pages; never a required check |

## Workflows

- `push` is the fast lane: one job, the Deno-only subset, no openspec,
  pre-commit, or betterleaks install. On a branch with an open pull request
  it runs beside `checks`; the overlap is accepted for the quick signal.
- `checks` is the full suite. A pull request runs it on the merge result of
  its latest commit and a newer push cancels the older run, so only the last
  commit of a pull request is ever fully checked. The push to `main` after a
  squash merge runs it once more on the merged commit.
- `secrets` is separate so that a change to it stands out in review and so
  the ruleset requires it on its own. It scans the commits a push adds
  (`before..HEAD`; the whole history when the branch is new or force-pushed)
  or a pull request adds (`base..HEAD`). Push runs are never cancelled: each
  covers only its own commits. The working tree is still scanned by the
  betterleaks pre-commit hook inside `checks / lint` and by `just secrets`
  inside `just check`.
- `pr` reruns on title and body edits without rerunning the suite, which is
  why it is not folded into `checks`. It also carries the archive gate: a
  required check that is reported only when the tree holds no unarchived
  OpenSpec change. Absent is not failed, so a pull request mid-implementation
  is green yet unmergeable, and `just spec-archived` tells you why.
- `labels` applies the label declaration on `main` only. A pull request that
  edits `.github/labels.json` is reviewed like any other; the labels change
  when it merges.
- `pr-labels` is the one workflow on `pull_request_target`, which runs
  `main`'s copy of the workflow and script with a token that may write to the
  pull request. The rule for that file: never check out, fetch, or run
  anything of the pull request; pull request data reaches the script through
  environment variables and `gh api`, never inside a `run:` line; the job
  alone holds `pull-requests: write`; the token is set on the steps that call
  `gh` and nowhere else; no third-party action beyond the pinned checkout and
  deno setup. A change to it is reviewed against this list.

Not in CI: `just clients-validate` needs the client CLIs (Claude Code, Codex,
Antigravity) and runs in the dev container only; the behavioural tests of the
skills need an agent and run by hand (`spec-workflow.md`, validation).

Every `uses:` is pinned to a commit SHA with the version tag in a trailing
comment, and every checkout sets `persist-credentials: false`; Dependabot
(`.github/dependabot.yml`) bumps SHA and comment together. When adding an
action, resolve the tag with `gh api repos/<owner>/<repo>/git/ref/tags/<tag>`
and pin the same way.

Toolchain versions for CI live in `.github/actions/setup-tools/action.yml`;
the dev container pins its own in `.devcontainer/devcontainer.json`. When one
changes, check the other.
