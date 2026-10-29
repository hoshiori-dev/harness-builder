# Hardening

Read when the agreed work includes hardening: a prototype, demo, or
experiment becomes a long-lived product. Hardening moves the harness from
divergent exploration to controlled engineering in three parts; each part
is a plan item the user confirms, not a bundle. [§6.2]

## 1. Record the stable structure

Write the directory structure and commands that have stopped changing into
the entrypoint (or an architecture file it routes to), from the code as it
is, never as it should become. Leave out what the file system already
shows; record what it does not (boundaries, which directories are stable,
which stay experimental). Owned by the knowledge and routing layer.

## 2. Add the gates and lock the control plane

- Type, lint, and test gates go into pre-commit (seconds-fast parts) and CI
  (the rest), using the tools the project already has; propose a tool only
  where none exists, listing the ecosystem's options. These gates are
  **soft read-only invariants**: an agent may change their configuration
  only through a reviewed change, and the entrypoint says so.
- The security control plane is locked **hard read-only**: sandbox and
  container configuration, secret-scan hooks, client permission files, and
  the authority policy. Agents cannot edit them; changes go through the
  user.
- Formatting and secret scanning come first; they are the floor of every
  grade above omitted.

Owned by the hard-boundary layer (gates, soft invariant), the environment
layer (sandbox lock), and the authority layer (permission files). Re-grade
the hard-boundary layer with the user.

## 3. Clear leftovers and install sync

- List exploration leftovers: temporary scripts (`scripts/tmp_*`, scratch
  notebooks), dead experiment directories, context describing abandoned
  approaches. Each is removed or kept by explicit user decision; deleting
  work the user may still want is a separate decision, never implied by the
  plan.
- Install a sync mechanism and a harness self-check wired into the task
  runner and CI. The self-check is the project's own code and calls no path
  inside a skill directory. Owned by the entropy layer.

## Boundary

Changes: gates, entrypoint structure section, control-plane protection,
leftovers, sync. Preserved: the task runner, existing lint configuration,
the branching habit, the commit convention, and all application code.
