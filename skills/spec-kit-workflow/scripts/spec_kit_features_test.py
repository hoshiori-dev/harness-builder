"""Tests for the bundled spec_kit_features.py (related, status, show, check, labels)."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).with_name("spec_kit_features.py")

TICKED = "# Tasks\n\n- [x] T001 Parse the file\n- [x] T002 Store rows\n"
MIXED = "# Tasks\n\n- [x] T001 Parse the file\n- [ ] T002 Store rows\n"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    ).stdout


def make_repo(tmp_path: Path, docs: dict[str, str]) -> tuple[Path, str, str]:
    """A repository whose `feature` branch adds ``docs`` under specs/003-import."""
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "t")
    (repo / "README.md").write_text("x\n")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "base")
    base = git(repo, "rev-parse", "HEAD").strip()
    git(repo, "checkout", "-qb", "feature")
    feature = repo / "specs" / "003-import"
    feature.mkdir(parents=True)
    for name, text in docs.items():
        (feature / name).write_text(text)
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "feature")
    return repo, base, git(repo, "rev-parse", "HEAD").strip()


def run(repo: Path, *args: str, launcher: list[str] | None = None):
    return subprocess.run(
        [*(launcher or [sys.executable]), str(SCRIPT), "--root", str(repo), *args],
        capture_output=True,
        text=True,
    )


def refs(base: str, head: str) -> list[str]:
    return ["--base", base, "--head", head]


def test_help_names_the_five_subcommands():
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"], capture_output=True, text=True
    )
    assert result.returncode == 0
    for command in ("related", "status", "show", "check", "labels"):
        assert command in result.stdout
    assert "Example:" in result.stdout


def test_finished_feature_passes_and_reads_done(tmp_path):
    repo, base, head = make_repo(
        tmp_path, {"spec.md": "# S\n", "plan.md": "# P\n", "tasks.md": TICKED}
    )
    assert run(repo, "check", *refs(base, head)).returncode == 0
    status = json.loads(run(repo, "status", "--json", *refs(base, head)).stdout)
    assert [f["tasks"]["progress"] for f in status["features"]] == ["done"]


def test_open_task_fails_ready_and_warns_on_draft(tmp_path):
    repo, base, head = make_repo(
        tmp_path, {"spec.md": "# S\n", "plan.md": "# P\n", "tasks.md": MIXED}
    )
    ready = run(repo, "check", *refs(base, head))
    assert ready.returncode == 1
    assert "003-import" in ready.stdout and "T002 Store rows" in ready.stdout
    draft = run(repo, "check", "--draft", *refs(base, head))
    assert draft.returncode == 0
    assert "warning:" in draft.stderr and "T002 Store rows" in draft.stderr


def test_missing_plan_fails(tmp_path):
    repo, base, head = make_repo(tmp_path, {"spec.md": "# S\n", "tasks.md": TICKED})
    result = run(repo, "check", *refs(base, head))
    assert result.returncode == 1
    assert "003-import" in result.stdout and "missing plan.md" in result.stdout


def test_missing_task_list(tmp_path):
    repo, base, head = make_repo(tmp_path, {"spec.md": "# S\n", "plan.md": "# P\n"})
    for extra in (["--draft"], ["--shape", "split"]):
        result = run(repo, "check", *extra, *refs(base, head))
        assert result.returncode == 0
        assert "not started" in result.stderr
    ready = run(repo, "check", *refs(base, head))
    assert ready.returncode == 1
    assert "003-import" in ready.stdout and "missing tasks.md" in ready.stdout


def test_long_show_is_summarised(tmp_path):
    repo, base, head = make_repo(
        tmp_path,
        {"spec.md": "# S\n" + "x" * 12000, "plan.md": "# P\n", "tasks.md": TICKED},
    )
    summary = json.loads(run(repo, "show", *refs(base, head)).stdout)
    assert summary["truncated"] is True and "--full" in summary["hint"]
    sizes = {d["path"]: d["characters"] for d in summary["documents"]}
    assert sizes["specs/003-import/spec.md"] > 12000
    full = run(repo, "show", "--full", *refs(base, head)).stdout
    assert "x" * 12000 in full
    out = tmp_path / "show.md"
    assert run(repo, "show", "--output", str(out), *refs(base, head)).returncode == 0
    assert out.read_text() == full


def test_repeated_runs_are_identical(tmp_path):
    repo, base, head = make_repo(
        tmp_path, {"spec.md": "# S\n", "plan.md": "# P\n", "tasks.md": MIXED}
    )
    before = git(repo, "status", "--porcelain")
    for command in (["check"], ["status", "--json"]):
        first = run(repo, *command, *refs(base, head))
        second = run(repo, *command, *refs(base, head))
        assert (first.returncode, first.stdout, first.stderr) == (
            second.returncode,
            second.stdout,
            second.stderr,
        )
    assert git(repo, "status", "--porcelain") == before


def test_bad_arguments_exit_2(tmp_path):
    repo, base, head = make_repo(tmp_path, {"spec.md": "# S\n", "plan.md": "# P\n"})
    unknown = run(repo, "check", "--bogus", *refs(base, head))
    assert unknown.returncode == 2 and "--bogus" in unknown.stderr
    feature = run(repo, "show", "--feature", "999-nope", *refs(base, head))
    assert feature.returncode == 2
    assert "999-nope" in feature.stderr and "003-import" in feature.stderr


@pytest.mark.skipif(shutil.which("uv") is None, reason="uv is not installed")
def test_plain_interpreter_matches_uv(tmp_path):
    repo, base, head = make_repo(
        tmp_path, {"spec.md": "# S\n", "plan.md": "# P\n", "tasks.md": MIXED}
    )
    plain = run(repo, "status", "--json", *refs(base, head))
    under_uv = run(
        repo,
        "status",
        "--json",
        *refs(base, head),
        launcher=["uv", "run", "--quiet", "--python", sys.executable, "--script"],
    )
    assert (plain.returncode, plain.stdout) == (under_uv.returncode, under_uv.stdout)
