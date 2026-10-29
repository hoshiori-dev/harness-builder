# Checks

Read this when changing a check, a hook, or a CI file, or when a check
fails.

Grade: {{GRADE}}. <!-- # CONFIGURE: {{GRADE}}: light, medium, or thick, with the reason and, below thick, "raised later by hardening". -->

Pre-commit budget: {{BUDGET}} seconds on a typical commit. <!-- # CONFIGURE: {{BUDGET}}: the agreed number. -->

## Where each check runs

<!-- # CONFIGURE: keep only the rows of the confirmed grade; the CI job column uses the platform's job names (GitLab: `format`, `lint`, ..., `secret-scan`). -->

| Check | Tool | Hook | Recipe | CI job |
|---|---|---|---|---|
| Format | ruff format | yes | `just fmt-check` | `checks / format` |
| Secret scan | betterleaks | yes | `just secrets` | `checks / secrets` |
| Lint | ruff check | yes | `just lint` | `checks / lint` |
| Typecheck | pyright | yes | `just typecheck` | `checks / typecheck` |
| Tests | pytest | no: over budget | `just test`; one file: `just test-fast <path>` | `checks / test` |
| Boundaries | `scripts/check_boundaries.py` | yes | `just boundaries` | `checks / boundaries` |

Before finishing a task run `just check`; for a small change run the
scoped recipe, not the full suite.

`checks / gate` passes only when every job above succeeded; a skipped job
fails it. <!-- # CONFIGURE: thick only; delete at medium and light; on GitLab the job is `gate`. -->

{{INCOMPLETE_HOOK}} <!-- # CONFIGURE: {{INCOMPLETE_HOOK}}: when the user declined every secret scanner, "Incomplete: the pre-commit hook has no secret scan, so the light grade is not met." and the pending decision; delete otherwise. -->

## Changing a rule

Never weaken a lint, type, test, or build rule, and never delete an
assertion, to make a failing check pass. When a check fails, fix the code;
or make an adjustment that keeps the rule's invariant (a narrower
exclusion with its reason beside it); or propose the rule change to the
user and wait. This covers:

{{SOFT_READ_ONLY}} <!-- # CONFIGURE: {{SOFT_READ_ONLY}}: one line per configuration file this layer delivers (pyproject.toml [tool.ruff], pyrightconfig.json, .pre-commit-config.yaml outside the secret-scan hook, the CI files). -->

Hard read-only, never changed by an agent: the secret-scan hook and the
CI secret-scan job. A refusal from either is a policy boundary; report it.

## Output

Every check runs with its tool's quiet flags; read the errors, not a log.

{{NO_QUIET_MODE}} <!-- # CONFIGURE: {{NO_QUIET_MODE}}: one sentence per tool without a quiet mode, or per log filter the user kept with its maintenance cost; delete when none. -->

## Custom checks

{{CUSTOM_CHECKS}} <!-- # CONFIGURE: {{CUSTOM_CHECKS}}: each project-owned check, its language, what it enforces, and the rule's alternative; delete when none. -->

## Before opening a pull request

{{SELF_CHECK}} <!-- # CONFIGURE: {{SELF_CHECK}}: the named self-check step and the verifier, or the no-subagent degradation sentence; delete when none. -->
