# Inline Commands and Scripts

Read when an operation takes more than two lines, assembles arguments, or
filters output; when placing a script; or when writing any script into the
target project.

## Inline or script

- At most two short lines, no argument assembly, no output filtering:
  inline in the document or skill (`just test`). No script.
- Anything longer, or with argument assembly or output filtering: a script,
  so no agent rebuilds the command by trial and the document does not carry
  a long block. [§2.4]

## Placement

| Owner | Location | Reached through |
|---|---|---|
| One project skill's procedure only | that skill's `scripts/` | the skill's steps; put it in the handoff definition |
| The project in general (checks, digests) | the management-script directory (existing, else `scripts/`) | a task-runner recipe named in the entrypoint |

The rule against calling a script inside a skill directory covers this
plugin's skills, not the target project's own: a project skill's
`scripts/` is the right place for a script only that skill's steps use.

The recipe needs an agreed task runner; without one, the recipe joins the
pending decisions list and the entrypoint names the script path meanwhile.

## Language

Write in the management-script language the project agreed. When none is
agreed, add the script to the pending decisions list with the recommended
language and its reason, and continue with the rest of the layer.
Recommendation: Deno when the project already uses it (explicit
permissions); otherwise the scripting style common in the project's own
language community; when neither applies, Deno, asking whether a Deno
dependency may be added to the agent environment. Never a language the user
cannot read.

## Delivered-script contract

Every script written into the target project:

- runs without interactive prompts; input comes from flags;
- answers `--help` with a usage example;
- prints its result on stdout (JSON when another tool consumes it) and
  diagnostics on stderr;
- exits 0 on success, 1 on a finding or error, 2 on bad arguments (an
  unknown flag included);
- is idempotent: a second run on an unchanged project gives the same output
  and exit code (no timestamps, random ordering, or state files in the
  output);
- summarises output above about 10,000 characters by default, with a
  `--full` or `--output FILE` option for the rest;
- states only the result and the next action. [§2.4]

Noise reduction, by example: a script wrapping a 300-case test run prints
"all passed" and exits 0, or prints each failing file with its assertion and
exits 1. Three hundred PASSED lines are context spent for nothing.

Run each delivered script once with `--help`, once on the project, a second
time to confirm identical output, and once with an unknown flag (exit 2);
report the outputs.
