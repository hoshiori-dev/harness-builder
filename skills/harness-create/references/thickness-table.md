# Thickness Table

Read when proposing the grade table in step 4, or when the user disputes a
grade. A grade is set per layer, never for the project: real projects are
mixed, and one mode for the whole project is wrong in some part of it.
[§6.1]

## Grades

- **omitted**: nothing is built for this layer.
- **light**: one sentence or one entry.
- **medium**: a dedicated file or configuration, followed by convention.
- **thick**: checks or isolation a machine enforces.

## What light and thick look like per layer

| Layer | Light | Thick |
| --- | --- | --- |
| environment | runs on the host; credentials limited by scoped tokens | container or VM isolation, network allow list, security rules hard read-only |
| knowledge and routing | one root entrypoint under 100 lines pointing at existing docs | root entrypoint plus layered knowledge files, architecture document, directory-level entrypoints |
| hard-boundary | formatting and secret scanning only | type check, lint, tests, and architecture-boundary checks in pre-commit and CI |
| authority | a few allow and deny entries, the rest left to the framework default | written authority policy, list of irreversible actions, pending decisions format |
| specification and completion | plan mode in the conversation, non-goals agreed verbally | a specification framework, every requirement with decidable scenarios, strict validation in CI |
| entropy | a few sync reminders in the root entrypoint | reference-integrity and structure checks of the harness in CI, periodic cleanup, drift labels |

## Presets for two typical combinations

Start from the closer column, then deviate per layer.

| Layer | Exploratory (demo, PoC, research experiment, early prototype) | Engineering (production system, shared main line, refactor, routine fixes) |
| --- | --- | --- |
| solution strategy | encourage divergence; widest exploration radius | force convergence; uniform style, controlled architecture, no regressions |
| who absorbs variety | the human judges the result; little need to control variety | automated guards; any broken invariant becomes long-term debt |
| environment | light to medium: secret isolation and a basic sandbox, no network allow list | thick: container or VM, security rules hard read-only, a decision on where session logs go |
| knowledge and routing | light, expanding: external API and SDK docs, domain background, quick-start scripts; few style rules | medium to thick, routing and constraining: directory topology, layer red lines, procedures, sync rules |
| hard-boundary | light: secret scanning and a "does it run" smoke check; no strict format, coverage, or architecture lint | thick: type check, lint, unit tests, git hooks, and CI gates all on |
| authority | light: wide allow list; humans step in at acceptance; one branch per parallel attempt | medium to thick: written policy, irreversible actions pre-authorised, fixed pending decisions format |
| specification and completion | light: align intent and the final effect; parallel attempts on branches or worktrees | thick: data structures, reused modules, interface contracts, change scope; every requirement with decidable scenarios |
| entropy | omitted to light: the project dies before cleanup matters; one sync reminder in the entrypoint | thick: harness self-check in CI, single source of truth, two-way sync rules, periodic cleanup |

## Deviating per layer

For each layer ask: "do this layer's error cost, maintenance horizon, and
autonomy match the project's overall values?" Where one differs, grade the
layer in the direction that variable pushes.

- A research repository with a data pipeline that must not break: high error
  cost and long horizon there, so hard-boundary and entropy take the
  engineering column; the rest stay exploratory. Name error cost and
  maintenance horizon as the reason.
- An `experiments/` directory inside a production repository: the reverse.
- A production project with one maintainer, always attended: knowledge and
  routing and authority one grade thinner than the engineering column;
  hard-boundary unchanged.
- A prototype discarded within a quarter: entropy omitted or light, with the
  short horizon as the reason; no harness self-check in CI.
