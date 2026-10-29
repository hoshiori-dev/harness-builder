# Tasks

Gate 1 closed in the conversation on 2026-10-29 (bootstrap exception). Every
skill task: write to `.agents/knowledge/skill-quality.md`, copy shared blocks
from `.agents/knowledge/shared-blocks.md`, prune three times, pass
`just skills-check`, verify against its delta spec, one commit.

## 1. Foundation skills

- [x] 1.1 `harness-architecture`: SKILL.md and references (audit, loading-modes, source-of-truth, multi-agent, methodology-map); verify every `[§x.y]` tag names a real section and `just skills-check` passes.
- [x] 1.2 `project-skill-building`: SKILL.md, references (value, description, hierarchy, pruning, scripts, testing, failure-modes, spec-portability), assets `skill-template.md`, `lint_skill.py` + `lint_skill_test.py`; verify `uv run assets/lint_skill.py --help`, the test passes under `just test`, and the linter accepts every skill in this repository.
- [x] 1.3 `authority-building`: SKILL.md, references (reversibility, pending-decisions canon, framework-rules, checkpoints, denial-handling), assets (knowledge-authority, claude-settings.json, codex-config.toml, checkpoint-recipes.just); verify the deny list in the assets matches the spec and `just skills-check` passes.

## 2. Layer builders

- [x] 2.1 `environment-building`: SKILL.md, references (threat-model, sandbox-audit, control-plane, devcontainer), assets (knowledge-environment, justfile-env-snippet.just); verify the five-item audit and the three-conditions rule appear as steps and `just skills-check` passes.
- [x] 2.2 `knowledge-routing-building`: SKILL.md, references (entrypoint, knowledge-files, project-skill-warrant, scripts, inline-vs-document), assets (agents-md, knowledge-file, claude-md); verify the asset AGENTS.md skeleton stays under 120 lines when filled and `just skills-check` passes.
- [x] 2.3 `hard-boundary-building`: SKILL.md, references (quiet-output, error-routing, precommit-budget, verifier-fallback, github, gitlab), assets (pre-commit-config.yaml, github/workflow-checks.yml, github/workflow-secret.yml, gitlab/ci-checks.yml, gitlab/ci-secret.yml, check-message-style.md); verify the language-choice step asks the user and `just skills-check` passes.
- [x] 2.4 `spec-completion-building`: SKILL.md, references (carrier-choice, completion-boundary, approval-gates, contract-design, spec-drift), assets (knowledge-spec-workflow, gitignore-handoff.txt), scripts `detect_spec_tooling.py` + test; verify the script's JSON on this repository lists OpenSpec and exits 0, and `--help` works under plain python3.
- [x] 2.5 `entropy-building`: SKILL.md, references (correction-report, sync-table, sync-skill, check-harness-config, reclamation, observation), assets (check_harness.py + test, keep-in-sync-section, sync-skill, reclamation-section, reclamation-skill); verify `check_harness.py` run against this repository's AGENTS.md passes and its test exercises a broken path, a dead recipe, and a mirror drift.
- [x] 2.6 `platform-lifecycle-building`: SKILL.md, references (necessity, branching, merge-method, publish-gate, remote-state, github, gitlab), assets github/ and gitlab/ sets with three `<!-- harness: spec-workflow -->` markers each, `sync_labels.py` + test, `run_log_digest.py` + test, scripts `check_platform.py` + test; verify `just skills-check` `insertion-markers` passes and every script answers `--help`.

## 3. Spec-driven development

- [x] 3.1 `spec-driven-development`: SKILL.md and references (adoption-decision, tracked-work, adopting-existing-code, anchoring); verify the eight-step loop carries the four completion answers and `just skills-check` passes.
- [x] 3.2 `openspec-workflow`: SKILL.md, references (github, gitlab, artifact-roles, config-yaml), assets github/ and gitlab/ automation, `spec_changes.py` + test, scripts `spec_changes.py` + test; verify `scripts/spec_changes.py check` on this repository reports the unarchived bootstrap change and exits 1.
- [x] 3.3 `spec-kit-workflow`: SKILL.md, references (github, gitlab, layout), assets, `spec_kit_features.py` + test, scripts `spec_kit_features.py` + test; verify `--help` and the test pass.
- [x] 3.4 `lightweight-spec-workflow`: SKILL.md, references (plan-mode), assets (SPEC.md, PLAN.md); verify the templates carry the four completion answers and `just skills-check` passes.

## 4. Entry skills and agent

- [x] 4.1 `harness-create`: SKILL.md with `disable-model-invocation: true`, references (greenfield, brownfield, five-variables, thickness-table, final-checklist, pending-decisions = canon), assets (harness-plan.md); verify it names no builder and `just skills-check` `layer-ownership`, `entry-invocation`, `pending-decisions-identical` pass.
- [x] 4.2 `harness-improve`: SKILL.md with `disable-model-invocation: true`, references (audit-checklist, hardening, thinning, migration, reclamation, pending-decisions = canon), assets (improvement-plan.md); same verification.
- [x] 4.3 `harness-verifier` agent at `com.anthropic.claude-code/agents/harness-verifier.md` (read-only tools, model inherit); `just gen` adds the `agents` pointer; verify `just validate` passes.

## 5. Integration

- [x] 5.1 Both README skill tables list all fifteen skills; `just harness-check` passes.
- [ ] 5.2 `just gen`, `just skills-check`, `just check` green; `just clients-validate` passes in the dev container.
- [ ] 5.3 Behavioural tests: run every spec's Triggering and Outcomes scenarios through clean-context subagents on the least capable model tier available; record pass/fail per scenario in a Verification report kept out of the repository until the pull request exists.
- [ ] 5.4 Canary: run `/harness-create` against a scratch repository in the dev container; the result has an entrypoint within budget, reachable knowledge files, and a passing `check_harness.py`.

## Workflow follow-up

- The maintainer reviews the implementation together with the specs; the
  change is archived only on the maintainer's instruction, before the first
  push to `main`.
