---
name: hard-boundary-building
description: >-
  Hard boundaries — sets up, grades, thickens, thins, or repairs the
  deterministic checks a project runs before a commit and in CI. Owns the
  hard-boundary layer: formatter, secret scan, lint, typecheck, tests,
  boundary checks, pre-commit hooks, and GitHub or GitLab check jobs and
  gate. Use when agents will commit to a repository and nothing broken or
  secret may land on main; when check output floods the agent with full logs
  and should be quieter; when a custom hook or boundary check should tell
  whoever hits it what to do instead; when a CI gate went green although a
  job was skipped; when the pre-commit hook is too slow and gets bypassed;
  or when an approved harness plan hands over this layer. Not for fixing one
  failing test or lint error, build, deploy, or release pipelines, agent
  command permissions, or labels, templates, and required-check settings on
  the remote.
license: Apache-2.0
compatibility: Scripts need Python 3.10+; uv optional.
---

# Hard Boundary Building

Defects are kept off the default branch by Git hooks and CI, not by
instructions. This skill settles a grade with the user, chooses tools from
the project's own ecosystem, and deposits a seconds-fast pre-commit hook
with a secret scan, task-runner recipes, the CI checks for GitHub or
GitLab, and a knowledge file that tells future agents how the checks are
run and what they may not weaken. A failing check is context injected into
the agent: it must arrive as errors and a route, not as a log. [§3] [§3.1]

## Rules on every step

<!-- shared:confirm-not-guess -->
Confirm, do not guess. Settle a fact from the repository when it can be
observed there (tools in use, directories, commands, history); ask the user
for everything else, and ask before choosing on any point where two readings
would lead to different work. Only a choice whose answer is plain from the
repository is made without asking.
<!-- /shared:confirm-not-guess -->

<!-- shared:recommendation-not-decision -->
A recommendation is not a decision. Present one recommended option with its
reason and the alternatives in a sentence each, then wait for the user's
choice. Challenge a choice once when the evidence contradicts it; after that
the choice binds every later step.
<!-- /shared:recommendation-not-decision -->

<!-- shared:nothing-lands-before-agreement -->
Nothing lands before agreement. Create or change no file in the target
project until the user has approved the plan that names it; an inspection
step reads and reports, it never writes.
<!-- /shared:nothing-lands-before-agreement -->

<!-- shared:plan-is-not-approval -->
An approved plan authorises the files it names and nothing else. Publishing
anything outside the repository, changing a remote setting, deleting work,
and widening what agents may do on their own are each a separate, explicit
decision by the user, taken when that step is reached.
<!-- /shared:plan-is-not-approval -->

<!-- shared:management-code-ownership -->
A script, hook, check, CI step, or task-runner recipe written into the target
project is the project's own management code: written for its role in the
language the project agreed to, readable first, failing with a message that
names what to fix, with no fallback that hides an unexpected error, and never
calling a script inside a skill directory. Tell the user that later fixes to
this plugin do not reach the delivered copy.
<!-- /shared:management-code-ownership -->

<!-- shared:pending-decisions -->
When a step is blocked on a decision only the user can make, continue with
every step that does not depend on it and add the blocked item to a pending
decisions list. Each item states: what is blocked and why; the options; the
recommended option and its reason; which finished work each option would
change. Present the list once, at the end or when nothing else can proceed,
never one question at a time.
<!-- /shared:pending-decisions -->

- **Quiet, never parsed.** Every check runs with its tool's own quiet or
  compact flags. Never propose or add an output parser, filter, or wrapper.
  When the user asks for one, explain once that it is a fragile second
  system to maintain and offer the quiet flags or a scoped command
  instead; write nothing until they answer. If they still want it, write
  it as project-owned code in the agreed language and record the
  maintenance trade-off in the knowledge file and the report. A tool with
  no quiet mode keeps its native output, recorded in one sentence. [§3.1]
- **Fixing application code is out of scope.** A check that fails on
  existing code is reported as a finding; never weaken the check, and do
  not fix the code unless the user asks.
- **Handoffs by role, never by skill name.** Which commands an agent may
  run goes to the layer owning authority; the harness self-check and sync
  rules to the layer owning entropy; required-check registration, branch
  protection, labels, and templates to the layer owning the platform
  lifecycle (or a human); sandbox, network, and installing tools into the
  agent environment to the layer owning the environment.
- **Deposited files never name this plugin or this skill** and never
  reference a path inside it.

## Workflow

### 1. Inspect the repository

Read, record, write nothing. Collect:

- the hard-boundary grade and the file list in the approved harness plan,
  if one exists; a harness self-check the plan puts in CI;
- languages and package managers; the task runner and its recipes;
- every tool that runs today and the role it runs in: hooks
  (`.pre-commit-config.yaml`, `.husky/`, `lefthook.yml`, `.git/hooks/`),
  recipes, scripts, CI files; and tool configuration with no runner
  (a `[tool.ruff.lint]` section, `eslint.config.*`, `tsconfig.json`);
- the remote host from `git remote -v` (GitHub, GitLab, other, none);
- runtimes present: `deno` with `deno.json`, `python3`, `uv`, `node`;
- the environment's isolation (dev container, network allowlist) from
  the environment knowledge or `.devcontainer/`;
- whether the client supports subagents;
- a knowledge file that already states the soft read-only invariant;
- how long the test suite takes: ask, or time it only with the user's
  agreement. Never run a hook or formatter here: they rewrite files.

Done when: every item is recorded as observed, absent, or "ask", and no
file in the target has changed.

### 2. Confirm the grade

The grades: **omitted** builds nothing; **light** is the formatter and a
secret scan; **medium** adds lint, typecheck, and tests in pre-commit and
CI; **thick** adds architecture boundary checks and one aggregator gate
meant to become the required check. [§6.1]

- **Plan gives a grade**: restate in one sentence what that grade adds and
  proceed without asking again.
- **Plan marks the layer omitted**: write no hook, recipe, or CI file,
  leave existing checks untouched, and go to the report in step 10; it
  says why the layer is omitted and which variable would raise it.
- **No plan**: recommend from the error cost first (low: light; moderate:
  medium; high: thick), raised one grade for a multi-contributor team or
  long unattended autonomy. Recommend omitted only when agents never
  commit. When the environment is isolated (container plus network
  allowlist), say the isolation argues for one grade looser than the error
  cost alone would, and offer both grades. Name the other grades in a
  sentence each, say which variable would raise the recommendation, and
  wait. [§6.1]
- **User picks thinner than recommended**: challenge once with the
  evidence, then build their grade and record the choice in the
  knowledge file.

Done when: the user confirmed the grade, or the plan supplied it.

### 3. Choose the tools and the platform

For every check the grade calls for, adopt without asking only a tool
whose role is observable: a hook, recipe, script, or CI step runs it in
that role, or its configuration for exactly that role exists. A
`ruff` lint section makes `ruff` the linter, not the formatter. For every
other role, list the ecosystem's candidates with one recommendation and
its reason, and configure only the tool the user names. Read
[references/quiet-output.md](references/quiet-output.md) when listing candidate tools or writing any check
command; it holds the candidates per ecosystem and their quiet flags.

Settle also, each with its recommendation:

- **Task runner**, when none exists: recommend `just` as the single
  command surface for hooks, CI, and agents; `make` and package-manager
  scripts are the alternatives. Every recipe uses the chosen runner.
- **Hook framework**, when none exists: recommend `pre-commit`; `lefthook`
  and `husky` are the alternatives. An existing one is kept.
- **Secret scanner**: recommend betterleaks; gitleaks and TruffleHog are
  the alternatives. When the chosen scanner cannot be installed in the
  target's environment, offer the others with their install path and write
  no hook until the user picks one. When the user declines every scanner,
  the hook ships without one and is marked incomplete in the knowledge
  file and the report, the light grade is not met, and the missing scan is
  the first pending decision, with betterleaks recommended.
- **Pre-commit budget** in seconds. Read [references/precommit-budget.md](references/precommit-budget.md) when
  agreeing the budget, placing a check, or when an existing hook runs
  longer than the budget.
- **Platform**: from the remote. No remote: ask which platform will host
  the project and continue with hook and recipes only. Neither GitHub nor
  GitLab: CI files are outside what this skill delivers; the CI checks
  become a pending decision listing the jobs they should run.
- **Deterministic or not**: when the user wants a check no tool can
  express (business-logic consistency, privacy review beyond pattern
  matching), read [references/verifier-fallback.md](references/verifier-fallback.md) when settling that check.

Done when: every check of the grade has a confirmed tool or a pending
decision, and the runner, hook framework, scanner, budget, and platform
each have an answer.

### 4. Agree the management-script language

Only when a custom check, hook, or helper script is needed (thick boundary
checks, a filter the user insisted on). Recommend:

- **Deno runtime present** (`deno.json` and a `deno` binary): Deno, for
  its explicit permissions (`--allow-read=src` shows and limits what the
  check touches).
- **Otherwise the community idiom**: Python, a `python3` stdlib script;
  TypeScript or JavaScript, a Node script run by the package manager; Go,
  a small program under `tools/` run with `go run`; Rust, a `cargo xtask`;
  Ruby, a Rake task. Name Deno as the alternative and the dependency it
  adds to the agent environment.
- **Neither** (only SQL, YAML, or configuration): propose Deno and ask
  whether adding it to the agent environment is acceptable.

Write no script until the user answers. Never use a language the user says
they cannot read; a language the user names binds and is recorded in the
knowledge file.

Done when: the language is confirmed, or no custom code is needed.

### 5. Present the file list and wait

List every file to create or change, each with one line on what its hook,
recipe, or CI content holds: the hook configuration, the recipes, the CI
files, custom checks, the knowledge file, and the entrypoint route line.
State what an existing file gains or loses. The confirmed grade does not
replace this list. An approved plan counts as agreement only for the files
it names; ask for the rest. A struck item is not written and becomes a
pending decision with its recommendation.

Done when: the user agreed to every file to be written.

### 6. Write the hook and the recipes

Rework [assets/pre-commit-config.yaml](assets/pre-commit-config.yaml) line by line for the confirmed tools
(translate it for another hook framework). The hook always holds the
formatter and the secret scan, so every checkpoint commit is scanned.
Light: the hook holds only the formatter and the secret scan. Medium and
thick: it adds lint, typecheck, and other checks only where they fit the
budget. Change an existing hook only as agreed in step 5. [§4.3]

Write recipes for the confirmed runner; with `just`, in this shape:

```just
# Format, scan, lint, typecheck: what the hook runs, over the whole tree.
check-fast: fmt-check secrets lint typecheck
# The task-end gate: everything CI runs (medium: drop `boundaries`).
check: check-fast test boundaries
fmt-check:
    ruff format --check --quiet
secrets:
    betterleaks dir . --no-banner --redact
lint:
    ruff check --output-format concise --quiet
typecheck:
    pyright
test:
    pytest -q --tb=short --no-header
# One file or directory, seconds: `just test-fast tests/test_parser.py`.
test-fast path:
    pytest -q --tb=short --no-header -x {{ path }}
# Thick: the delivered boundary check.
boundaries:
    python3 scripts/check_boundaries.py
```

Light grade: one recipe running the formatter check and the secret scan.
Medium and thick: lint, typecheck, the full test suite, and a scoped fast
test. A recipe calling a Python check uses `python3`, never `uv`, when the
target has no uv. [§4.3]

Done when: every hook entry and every recipe runs a confirmed tool with
its quiet flags, every CI job planned in step 7 has a recipe, and
`check` depends on every one of those recipes.

### 7. Write the CI checks

GitHub only for a GitHub remote, GitLab only for GitLab; never both. Read
[references/github.md](references/github.md) when writing GitHub workflows, or
[references/gitlab.md](references/gitlab.md) when writing a GitLab pipeline.

- **Light**: only the secret scan in CI.
- **Medium**: one job per check, each running its recipe, plus the secret
  scan job, and no aggregator; tell the user that the gate is what thick
  would add.
- **Thick**: the medium jobs plus one gate job that depends on every check
  job and fails when any of them failed, was cancelled, or was skipped,
  naming that job. The gate is the only name proposed for the required
  check.
- **User declines CI files**: the CI secret scan becomes a pending
  decision with this platform's secret workflow recommended.
- **Harness self-check in the plan**: leave a commented slot for its job
  (and, at thick, in the gate's dependencies) and say that the layer owning
  entropy delivers it.

Registering a required check, branch protection, and "pipelines must
succeed" are remote settings: describe them for the layer owning the
platform lifecycle or a human; never change them.

Done when: every check of the grade has a CI job running its recipe, and
at thick every job is in the gate's dependencies.

### 8. Write custom checks

For each project-specific hook, boundary check, or lint rule: read
[references/error-routing.md](references/error-routing.md) when writing or porting any custom check. Its
failure names the file and line, what is wrong, the allowed alternative,
and the knowledge file that states the rule; an input it cannot read is
an error naming that input, never a pass. Every delivered script runs
non-interactively, offers `--help` with a usage example, puts data on
stdout and diagnostics on stderr, exits 0 on pass, 1 on a finding or
error, and 2 on bad arguments, is idempotent, and in Python runs under
plain `python3` with the standard library unless the user accepted a
dependency. [§3.1]

Done when: each custom check was run once on the clean tree (exit 0,
nothing on stderr) and once on a temporary violating copy (exit 1 with the
routing message), and each result is reported.

### 9. Write the knowledge file

Rework [assets/knowledge-checks.md](assets/knowledge-checks.md) into the knowledge directory the project
uses: grade, budget, each check with its tool, hook, recipe, and CI job,
quiet-output trade-offs, and any self-check step. Below thick it says the
grade can be raised later by hardening. [§6.2] For the soft read-only
invariant, read the existing knowledge files first: [§3.3]

- **No file states it**: keep the asset's sentence, list the configuration
  files this layer delivers under it, and tell the user the layer owning
  the environment should adopt this sentence as its source.
- **An environment knowledge file states it**: delete the sentence from
  the asset, link to that one, and list under the link only the
  configuration files this layer adds. The project keeps one copy.

The secret-scan hook and any security rule are listed as hard read-only, a
separate class: an agent never changes them. Add one route line to the
agent entrypoint with the load condition "before changing a check, a hook,
or a CI file, or when a check fails".

Done when: the knowledge file names every delivered configuration file
under the invariant or the link, and exactly one copy of the sentence
exists in the project.

### 10. Verify and report

Omitted: skip verification; the report states why the layer is omitted
and which variable would raise it, and lists no files.

Otherwise run each recipe in its check-only form. Run the full test suite
(`just test`, `just check`) only with the user's agreement; without it run
`just test-fast` on one test file and say so in the report. Run the hook
on the delivered files only (`pre-commit run --files <files>`) and time it
against the budget. Validate each CI file with the platform's linter when
available.

Report: every file written or changed; the grade and the budget; checks
moved out of the hook and why; a hook without a secret scan, marked
incomplete; whether the full suite ran; findings on existing code; the
pending decisions list; the remote actions a human must take (branch
protection, the required check by name); and that the project owns the
delivered checks.

Done when: every item that applies is in the report (for an omitted
layer, the reason and the raising variable), and no skill is named in it.

## Gotchas

- `pre-commit run --all-files` runs the formatter over the whole tree and
  rewrites files nobody agreed to; verify with `--files`.
- A formatter in the hook rewrites staged files and fails the commit; the
  agent re-stages and commits again. That is the design, not a failure to
  route around with `--no-verify`.
