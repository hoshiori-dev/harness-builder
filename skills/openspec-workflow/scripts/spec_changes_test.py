"""Tests for the bundled spec_changes.py (related, status, check, archive)."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent / "spec_changes.py"
CHANGES = "openspec/changes"
OPENSPEC = shutil.which("openspec")
needs_cli = pytest.mark.skipif(
    OPENSPEC is None, reason="the OpenSpec CLI is not on PATH"
)

PROPOSAL = """## Why

Spreadsheet users copy every report by hand, which loses rows and wastes hours.

## What Changes

- Reports export as CSV.

## Impact

- The export capability.
"""

SPEC = """## Purpose

Lets people take any report out of the product as a CSV file for spreadsheets.

## ADDED Requirements

### Requirement: CSV export {n}
The system SHALL export report {n} as CSV.

#### Scenario: Export {n}
- **WHEN** the user exports report {n}
- **THEN** a CSV file with every row is produced
"""


def git(repo: Path, *args: str) -> str:
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@example.com",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@example.com",
    }
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    ).stdout


def write(repo: Path, rel: str, text: str) -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def commit(repo: Path, message: str) -> None:
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", message)


def add_change(repo: Path, name: str, tasks: str, n: int = 1) -> None:
    base = f"{CHANGES}/{name}"
    write(repo, f"{base}/.openspec.yaml", "schema: spec-driven\n")
    write(repo, f"{base}/proposal.md", PROPOSAL)
    write(repo, f"{base}/specs/export-{n}/spec.md", SPEC.format(n=n))
    write(repo, f"{base}/tasks.md", tasks)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.name", "t")
    git(root, "config", "user.email", "t@example.com")
    write(root, "openspec/config.yaml", "schema: spec-driven\n")
    write(root, f"{CHANGES}/archive/.gitkeep", "")
    write(root, "openspec/specs/.gitkeep", "")
    commit(root, "base")
    git(root, "branch", "base")
    return root


def run(repo: Path, *args: str) -> tuple[int, dict | None, str]:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(repo), *args],
        capture_output=True,
        text=True,
        env={**os.environ, "OPENSPEC_NO_UPDATE_CHECK": "1", "DO_NOT_TRACK": "1"},
    )
    data = json.loads(proc.stdout) if proc.stdout.strip() else None
    return proc.returncode, data, proc.stderr


REFS = ("--base", "base", "--head", "HEAD")


def test_help_names_the_four_commands():
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"], capture_output=True, text=True
    )
    assert proc.returncode == 0
    for command in ("related", "status", "check", "archive", "examples:"):
        assert command in proc.stdout


def test_unknown_option_exits_2():
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "status", "--bogus"],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 2
    assert "--bogus" in proc.stderr


def test_related_lists_state_and_tasks(repo):
    add_change(repo, "export-csv", "- [x] 1.1 Build\n- [ ] 1.2 Test\n")
    commit(repo, "change")
    code, data, _ = run(repo, "related", *REFS)
    assert code == 0
    assert data["changes"] == [
        {
            "name": "export-csv",
            "state": "active",
            "path": f"{CHANGES}/export-csv",
            "skip_specs": False,
            "done": 1,
            "open": 1,
        }
    ]


@needs_cli
def test_representative_archive_then_repeat(repo):
    add_change(repo, "export-csv", "- [x] 1.1 Build\n")
    commit(repo, "change")
    code, data, err = run(repo, "archive", *REFS, "--message", "archive export-csv")
    assert code == 0, err
    assert data["archived"] == ["export-csv"] and data["validated"]
    assert not (repo / CHANGES / "export-csv").exists()
    assert list((repo / CHANGES / "archive").glob("*-export-csv"))
    assert "CSV export 1" in (repo / "openspec/specs/export-1/spec.md").read_text()
    assert git(repo, "status", "--porcelain") == ""
    code, data, _ = run(repo, "check", *REFS)
    assert (code, data["verdict"]) == (0, "pass")
    head = git(repo, "rev-parse", "HEAD")
    code, data, _ = run(repo, "archive", *REFS)
    assert (code, data["archived"], data["already_archived"]) == (0, [], ["export-csv"])
    assert git(repo, "rev-parse", "HEAD") == head
    assert git(repo, "status", "--porcelain") == ""


def test_one_open_change_refuses_both(repo, tmp_path):
    add_change(repo, "export-csv", "- [x] 1.1 Build\n", 1)
    add_change(repo, "import-csv", "- [x] 1.1 Build\n- [ ] 1.2 Write the docs\n", 2)
    commit(repo, "changes")
    head = git(repo, "rev-parse", "HEAD")
    code, data, err = run(
        repo, "archive", *REFS, "--openspec", str(tmp_path / "never-run")
    )
    assert code == 1
    assert "1.2 Write the docs" in err
    assert data["archived"] == [] and [r["name"] for r in data["refused"]] == [
        "import-csv"
    ]
    assert (repo / CHANGES / "export-csv").is_dir()
    assert git(repo, "rev-parse", "HEAD") == head


def test_uncommitted_tree_is_refused(repo, tmp_path):
    add_change(repo, "export-csv", "- [x] 1.1 Build\n")
    commit(repo, "change")
    write(repo, f"{CHANGES}/export-csv/proposal.md", "edited\n")
    code, _, err = run(
        repo, "archive", *REFS, "--openspec", str(tmp_path / "never-run")
    )
    assert code == 1
    assert f"{CHANGES}/export-csv/proposal.md" in err
    assert (repo / CHANGES / "export-csv/proposal.md").read_text() == "edited\n"


def test_missing_cli_changes_nothing(repo, tmp_path):
    add_change(repo, "export-csv", "- [x] 1.1 Build\n")
    commit(repo, "change")
    code, _, err = run(repo, "archive", *REFS, "--openspec", str(tmp_path / "absent"))
    assert code == 1
    assert "not on PATH" in err
    assert git(repo, "status", "--porcelain") == ""


def test_check_awaits_archive_and_warns_on_draft(repo):
    add_change(repo, "export-csv", "- [ ] 1.1 Build\n")
    commit(repo, "change")
    code, data, _ = run(repo, "check", *REFS, "--no-validate")
    assert (code, data["verdict"], data["unarchived"]) == (
        1,
        "awaiting-archive",
        ["export-csv"],
    )
    code, data, err = run(repo, "check", *REFS, "--no-validate", "--draft")
    assert (code, data["verdict"]) == (0, "pass")
    assert "export-csv" in err


def test_long_status_is_summarised(repo):
    add_change(
        repo, "export-csv", "".join(f"- [ ] {i} task {'x' * 80}\n" for i in range(200))
    )
    commit(repo, "change")
    code, data, _ = run(repo, "status", *REFS)
    assert code == 0
    assert "--full" in data["summary"] and "--output" in data["summary"]
    assert f"{CHANGES}/export-csv/tasks.md" in data["omitted_documents"]
    code, data, _ = run(repo, "status", *REFS, "--full")
    assert len(data["changes"][0]["tasks"]["open_tasks"]) == 200


FAKE_CLI = """#!/bin/sh
# Archives the first change it is given, then fails.
if [ "$1" = archive ] && [ ! -e .fake-archived ]; then
  mkdir -p openspec/changes/archive/2026-01-01-"$2" && mv openspec/changes/"$2"/* openspec/changes/archive/2026-01-01-"$2"/
  rmdir openspec/changes/"$2" && touch openspec/specs/edited.md .fake-archived
  exit 0
fi
echo "fake failure" >&2
exit 1
"""


def test_failure_partway_restores_the_tree(repo, tmp_path):
    add_change(repo, "export-csv", "- [x] 1.1 Build\n", 1)
    add_change(repo, "import-csv", "- [x] 1.1 Build\n", 2)
    commit(repo, "changes")
    head = git(repo, "rev-parse", "HEAD")
    fake = tmp_path / "fake-openspec"
    fake.write_text(FAKE_CLI, encoding="utf-8")
    fake.chmod(0o755)
    code, _, err = run(repo, "archive", *REFS, "--openspec", str(fake))
    assert code == 1
    assert "restored to HEAD" in err
    assert git(repo, "rev-parse", "HEAD") == head
    assert git(repo, "status", "--porcelain", "--", "openspec") == ""
    assert (repo / CHANGES / "export-csv").is_dir()
