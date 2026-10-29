#!/usr/bin/env bash
# Runs once after the dev container is created.
set -euo pipefail

pre-commit install --install-hooks

# The documentation site generator, at the version the justfile pins (the
# system Python lacks gettext, so uv manages a 3.12 interpreter for it).
uv tool install "zensical==$(just --evaluate zensical_version)" --python 3.12
