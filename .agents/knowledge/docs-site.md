# Docs Site

Read when editing anything under `docs/`, `zensical.toml`, the `docs-*`
recipes, or the `docs` workflow, and after upgrading Zensical.

The site is built by [Zensical](https://zensical.org) from `docs/` and
published to GitHub Pages by `.github/workflows/docs.yml` on every push to
`main` that touches the site. It is written in **Chinese only**: the human
audience of this project reads Chinese first, and Zensical has no native
multi-language support (verified 2026-10-29 against version 0.0.73: one
`theme.language` per site, a `extra.alternate` language switcher only, no
i18n plugin in its compatibility list, "Internationalization" on its roadmap
without a date). A bilingual site would mean two builds and two navigation
trees kept in step by hand; that cost is not earned.

## Layout and rules

- `docs/<page>.md`: one page per file, Chinese prose. The root `README.md` is
  not part of the site.
- `docs/.nav.yml`: the navigation, read by the `awesome-nav` plugin; every
  page must be listed (`just harness-check`, rule `doc-reachable`).
- `zensical.toml`: `docs_dir = "docs"`, `site_dir = "site"`,
  `theme.language = "zh"`, no `nav` key (the `.nav.yml` owns it), no
  `extra.alternate`.
- The Zensical version is pinned once, in the `justfile` variable
  `zensical_version`; `.devcontainer/setup.sh` and the workflow read it from
  there. Zensical needs Python 3.11+ and the recipes run it with
  `uvx --python 3.12` because the container's system Python lacks `gettext`.
- `just docs-build` is the check: `--strict` fails the build on any warning
  (broken link, page missing from the nav). `just docs-serve` previews.
- `site/` and `build/` are build output, ignored by git.

## Upgrade

Bump `zensical_version` in the `justfile`, run `just docs-build`, read the
Zensical changelog and its `setup/language` page: when native
multi-language support ships, reopen the decision above in an issue rather
than adding a second site by hand.
