---
name: template-adjust
description: >-
  Template adoption skill. Adapts a repository built from the
  agent-plugins-starter template after it is in use: adding or removing a
  supported client, adding a catalog, thickening or thinning harness layers
  (checks, hooks, CI jobs, authority level), upgrading OpenSpec, or pulling
  in upstream template changes. Use when the user asks to support another
  client, drop one, add a new kind of shipped component, change how strict
  the checks are, or update the template machinery. Not for day-to-day
  entries (plugin-development) or the first-time prune (template-tailor).
---

# Template adjustment

Each branch below is a complete procedure; run only the one the user asked
for, then `just check`. Before any branch, read
`.agents/knowledge/compatibility-watch.md`: a client upgrade may have lifted a
workaround, and that row's disposition is often the real change to make.

## Add or remove a client

Facts live in one place: `scripts/lib/clients.ts`, and the entry there is
the decision: a client is supported because it is registered, never because
some file or directory exists.

1. Add (or delete) the client's entry and its `ClientId`: namespace
   directory, wiring files, generated files, and `agents` (directory and
   extension) only when the client's plugin system carries agents;
   otherwise leave `agents` out and add a watch-list row for the limitation.
   When deleting, run `just client-footprint <id>` first and remove those
   files.
2. Teach `scripts/gen.ts` how to produce the client's files from
   `plugin.json` and `mcp.json`, failing loudly on anything the client
   cannot express; add cases to `scripts/gen_test.ts`.
3. Add the client's wiring checks to `scripts/check_plugin.ts` if it has
   wiring files.
4. Create the namespace directory only if the client has hand-written files
   (one agent file per existing agent when it carries agents); a client
   without such files gets no directory.
5. Update `.agents/knowledge/client-matrix.md` (table, limitations,
   verification log with today's date), `openspec/specs/agent/spec.md`,
   `README.md`, the `justfile` `clients-validate` recipe, and the dev
   container features.
6. `just gen && just check`, then verify in the client and log it.

## Add a catalog

1. Decide the implementation location and how an entry is detected.
2. Add the catalog to the list in `scripts/check_plugin.ts` (`checkCatalogs`)
   and extend its test.
3. Write `openspec/specs/<catalog>/spec.md` with the rules every entry
   follows; add the catalog to `openspec/config.yaml` context and to
   `.agents/knowledge/spec-workflow.md`.
4. Add the `area: <catalog>` label to `.github/labels.json` and the issue
   form dropdowns; update `AGENTS.md`'s project map.

## Thicken or thin a layer

- Checks: add or remove a recipe in the `justfile`, its job in
  `.github/workflows/checks.yml` and the `gate` job's `needs` list, its row
  in `.agents/knowledge/github/checks.md`, and, for a check that needs only
  Deno and just, its place in `check-fast`, in one change. Secret scanning
  keeps its own workflow (`secret.yml`).
- Hooks: `.pre-commit-config.yaml`; keep every hook under a few seconds so
  nobody bypasses it. Secret scanning stays.
- Authority: edit `.agents/knowledge/agent-authority.md` with the user's
  explicit decision and date; never from an agent's own judgement.
- Spec strictness: `openspec/config.yaml` rules and the `--strict` flag in
  `just spec-check`.
- Thinning is as valid as thickening: a check that never fires, a skill
  nobody loads, a knowledge file no task reads is entropy; delete it and
  fix the pointers.

## Upgrade OpenSpec

1. Note the installed version (`openspec --version`) and the one in
   `.agents/knowledge/spec-workflow.md`. Commit or stash everything first so
   the regeneration can be reverted with git.
2. Run `openspec init --tools agents --force` in the repository root; never
   `openspec update` (it would also treat the `.claude/skills` symlinks as a
   Claude install and rewrite the skills).
3. Diff the result; keep only `.agents/skills/openspec-*` and
   `openspec/` changes; delete anything written elsewhere.
4. Update the version in `spec-workflow.md`; `just harness-check`.

## Pull upstream template changes

1. `git remote add template https://github.com/hoshiori-dev/agent-plugins-starter.git`
   (once) and `git fetch template --tags`.
2. Diff the upstream range against the version this repository was created
   from: `git diff <old-tag> <new-tag> -- scripts justfile .github .agents/knowledge .pre-commit-config.yaml`.
3. Apply the pieces that still apply by hand; management code is owned here,
   so expect to adapt rather than merge.
4. `just gen && just check`; record the upstream version in
   `.agents/knowledge/maintenance.md`.
