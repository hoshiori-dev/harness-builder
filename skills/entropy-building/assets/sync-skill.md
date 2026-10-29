---
name: sync-commands  # CONFIGURE: sync-<concern>, the concern this skill owns.
description: >-  # CONFIGURE: the document, its source of truth, and the concrete changes that trigger an update.
  Keeps the commands section of AGENTS.md true to the justfile. Use when a
  change adds, renames, or removes a justfile recipe or changes what one
  does; when a CI job starts or stops calling a recipe; or when asked to
  edit the commands section of AGENTS.md.
---

# Sync Commands

The commands section of `AGENTS.md` names the recipes agents run; the
`justfile` is the source of truth. When the two disagree, the `justfile`
wins and the document is corrected. <!-- # CONFIGURE: the document part, the entrypoint, the source of truth, and the confirmed tie-break. -->

## When the subject changes

<!-- # CONFIGURE: the forward triggers settled with the user, one per concrete change. -->

1. A recipe is added → add one line naming it and when to run it.
2. A recipe is renamed or removed → change or delete every mention in
   `AGENTS.md` and `.agents/knowledge/`. <!-- # CONFIGURE: the entrypoint and knowledge directories. -->
3. A recipe's behaviour changes → rewrite its one-line description.

Apply the update in the same change, never as a follow-up.

## Before editing the document

Check first, and fix or report every mismatch found, not only the one that
prompted the edit:

- `just --summary` lists every recipe the section names. <!-- # CONFIGURE: the runner's recipe-listing command and the reverse checks settled with the user. -->
- Each named recipe runs and does what its line says.
- No line spells out flags the recipe already holds.

## Done when

The section names only existing recipes, each description matches the
recipe's behaviour, and `just harness-check` reports no finding. <!-- # CONFIGURE: the completion criterion and the self-check recipe, or drop the recipe when the user declined the self-check. -->
