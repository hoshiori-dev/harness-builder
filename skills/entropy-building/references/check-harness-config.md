# Self-Check Configuration

Read when settling, configuring, porting, or wiring the harness self-check.

The check exits 2 on an input it cannot use instead of skipping it, because a skipped check looks like a passed one; a port keeps
that. [§5.3]

## Settings from observation

Set every `# CONFIGURE:` line of [the script](../assets/check_harness.py)
from what the inspection and the inventory found.

| Setting | From |
|---|---|
| `ENTRYPOINT` | the entrypoint file (`AGENTS.md`) |
| `KNOWLEDGE_DIRS` | each knowledge directory (`.agents/knowledge`) |
| `EXTRA_DOCS` | other harness documents (`CLAUDE.md`, `ARCHITECTURE.md`) |
| `TASK_RUNNER`, `RUNNER_FILE` | `"just"` + `justfile`, `"make"` + `Makefile`, `"npm"` + `package.json`; `None` without a runner |
| `MIRROR_PAIRS` | each confirmed pair, source side first (the finding tells the agent to correct the second file), with the heading lines of the sections that must match in each file; `[]` compares the whole files |
| `IGNORE_PATHS` | only mentions the user confirms are deliberately not repository paths (gitignored, generated) |
| `TIER2`, `ENTRYPOINT_BUDGET`, `SKILL_DIRS` | `True` at thick grade or on request; the budget the knowledge and routing layer set; the project skill directories |

Tier 1 checks links and backticked paths in the entrypoint, knowledge
files, and extra documents; backticked task-runner mentions
(`` `just test` ``) against the runner's recipe list; that every knowledge
file is referenced from the entrypoint; and the mirror pairs. Tier 2 checks
project skill frontmatter (name equals directory, description present and
at most 1024 characters) and the entrypoint's line budget; while it is off,
stderr says so.

## Language and placement

Put the script where the project's management scripts live (`scripts/`).
The Python is a reference implementation: ask whether the project keeps it
or has it rewritten in its agreed management language, and recommend the
port when that language is not Python, because the team must read and
maintain its own checks. A port (TypeScript on Deno, for example) keeps the
same settings, rule ids, messages, JSON shape, and exit codes; on Deno it
runs with `--allow-read --allow-run=<runner>`. A port lists recipes from
`just --summary` (not `just --list`, which adds comments and groups), from
`make -pRrq` minus the entries under `# Not a target:`, or from the
`scripts` keys of `package.json`. The Python copy needs only `python3`;
introduce uv as a project dependency only after asking.

## Wiring

1. Add one recipe (`harness-check: python3 scripts/check_harness.py`, or
   the runner's equivalent).
2. Add that recipe to the aggregate `check` recipe (or the runner's
   equivalent), so `just check` runs it with every other check.
3. Fill the `# harness:` slot the hard-boundary layer left in the CI
   workflow with a job that runs the recipe, shaped like the jobs beside
   it, and delete the slot comment.
4. At thick grade, add that job to the gate's dependencies (`needs`, and
   `GATE_JOBS` on GitLab), so the required gate fails when the self-check
   fails.

When the workflow has no slot, add the job beside the other check jobs and
report that the slot was missing. When the project has no CI checks
workflow, add the job to the pending decisions list as a need for the skill
that owns the hard-boundary layer. Run the recipe once and put its output in
the report.
