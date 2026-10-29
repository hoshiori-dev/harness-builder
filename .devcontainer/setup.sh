#!/usr/bin/env bash
# Runs once after the dev container is created.
set -euo pipefail

pre-commit install --install-hooks
