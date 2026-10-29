# Task runner for the harness-builder repository. Every documented
# command is a recipe here; CI jobs run the same recipes.

set shell := ["bash", "-euo", "pipefail", "-c"]
set positional-arguments

export OPENSPEC_NO_UPDATE_CHECK := "1"
export OPENSPEC_TELEMETRY := "0"
export PAGER := "cat"
export GIT_PAGER := "cat"
export GIT_TERMINAL_PROMPT := "0"

# Pinned versions of the Python tools the recipes run through uv. The dev
# container (.devcontainer/setup.sh) and CI read them from here.
ruff_version := "0.15.0"
pytest_version := "9.0.2"
zensical_version := "0.0.73"

# List recipes.
default:
    @just --list

# Generate client-specific files from plugin.json and the agents directories (`--check`: report drift only).
gen *flags:
    deno run --allow-read --allow-write --allow-run=git scripts/gen.ts "$@"

# Format the management scripts.
fmt:
    deno fmt

# Formatting, lint, and type checks for the management code (Deno) and the shipped Python assets (ruff, only once skills/ holds .py files).
lint:
    deno fmt --check
    deno lint
    deno check scripts/*.ts scripts/lib/*.ts
    if compgen -G 'skills/*/*/*.py' >/dev/null; then uvx ruff@{{ ruff_version }} check skills/ && uvx ruff@{{ ruff_version }} format --check skills/; else echo "ruff: no Python under skills/"; fi

# Unit tests of the management scripts (Deno) and of the shipped Python assets (pytest, only once skills/ holds .py files).
test:
    deno test --allow-read --allow-write --allow-run --allow-env
    if compgen -G 'skills/*/*/*_test.py' >/dev/null; then uv run --no-project --python 3.12 --with pytest=={{ pytest_version }} pytest -q skills/; else echo "pytest: no Python tests under skills/"; fi

# Plugin package and client wiring consistency.
validate:
    deno run --allow-read --allow-run=git scripts/check_plugin.ts

# Shipped skills: frontmatter budgets, structure, links, reachability, script hygiene, shared blocks, layer ownership.
skills-check:
    deno run --allow-read --allow-run=git scripts/check_skills.ts

# Harness integrity: links, recipes, budgets, skill frontmatter, symlinks, README mirror, docs nav.
harness-check:
    deno run --allow-read --allow-run=git,just scripts/check_harness.ts

# OpenSpec specs and changes, strict mode.
spec-check:
    openspec validate --all --strict --no-interactive

# Unarchived OpenSpec changes: exit 1 while one exists (the pr workflow then withholds the `checks / spec-archived` check and the ruleset blocks the merge).
spec-archived:
    deno run --allow-read scripts/check_spec_archived.ts

# Print the OpenSpec state label a pull request should carry, without writing (the pr-labels workflow applies it).
pr-labels number:
    deno run --allow-read --allow-env --allow-run=gh scripts/sync_pr_labels.ts "$1"

# Secret scan of the working tree.
secrets:
    betterleaks dir . --no-banner --redact

# Secret scan of the commits in a git range (empty: the whole history); the secrets workflow runs it on the commits a push or pull request adds. The GIT_CONFIG_* variables let the git that betterleaks spawns trust the dev container's root-owned checkout.
secrets-commits range="":
    GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=safe.directory GIT_CONFIG_VALUE_0='*' betterleaks git . --no-banner --redact {{ if range == "" { "" } else { "--log-opts=" + range } }}

# Every pre-commit hook on every file.
pre-commit:
    pre-commit run --all-files

# Build the documentation site (Zensical, strict: any warning fails) into site/.
docs-build:
    uvx --python 3.12 --from zensical=={{ zensical_version }} zensical build --strict --clean

# Serve the documentation site locally with live reload.
docs-serve:
    uvx --python 3.12 --from zensical=={{ zensical_version }} zensical serve

# The documentation check CI runs: a strict build.
docs-check: docs-build

# The checks that need no network beyond uv's cache; the push workflow runs them on every branch but main.
check-fast: (gen "--check") lint validate skills-check harness-check test

# Everything CI runs.
check: check-fast spec-check docs-check secrets

# Validate the package with the installed client CLIs (local only; CI has no clients). Claude runs non-strict: this repository's root CLAUDE.md draws a warning.
clients-validate:
    claude plugin validate .
    ~/.gemini/bin/agy plugin validate .
    ~/.gemini/bin/agy plugin install . >/dev/null
    ~/.gemini/bin/agy plugin list --json | grep -F '"harness-builder"'
    ~/.gemini/bin/agy plugin uninstall harness-builder >/dev/null
    codex plugin marketplace add . >/dev/null
    codex plugin list | grep -F "harness-builder@harness-builder"
    codex plugin marketplace remove harness-builder >/dev/null
    just dist
    name="$(deno eval 'const m = JSON.parse(Deno.readTextFileSync("plugin.json")); console.log(m.name)')"; version="$(deno eval 'const m = JSON.parse(Deno.readTextFileSync("plugin.json")); console.log(m.version)')"; rm -rf /tmp/aps-dist && mkdir -p /tmp/aps-dist && unzip -q "dist/$name-$version.zip" -d /tmp/aps-dist && claude plugin validate "/tmp/aps-dist/$name" && ~/.gemini/bin/agy plugin validate "/tmp/aps-dist/$name"

# Print the versions of the clients and tools the compatibility watch is verified against.
versions:
    deno --version | head -1
    openspec --version
    claude --version
    codex --version
    ~/.gemini/bin/agy changelog 2>/dev/null | awk 'NR == 1 { print "agy " $0 }'
    betterleaks version

# Files that belong to one client (codex | claude-code | antigravity).
client-footprint id:
    deno run --allow-read --allow-run=git scripts/check_plugin.ts --footprint "$1"

# Build the release archive into dist/ (`--tag vX.Y.Z` checks it against plugin.json).
dist *flags:
    deno run --allow-read --allow-write --allow-run=git scripts/dist.ts "$@"

# Compare .github/labels.json with the repository's labels (`--apply` writes).
labels *flags:
    deno run --allow-read --allow-run=gh scripts/sync_labels.ts "$@"

# Refresh the vendored Agent Plugins schemas.
schemas-update:
    for f in plugin mcp; do curl -sfL "https://agent-plugins.org/schemas/1.0.0/$f.schema.json" -o "scripts/schemas/agent-plugins/1.0.0/$f.schema.json"; done

# Remove build output.
clean:
    rm -rf dist
