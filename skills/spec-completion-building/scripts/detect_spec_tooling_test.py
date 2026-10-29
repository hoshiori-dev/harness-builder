"""Tests for detect_spec_tooling.py (run with pytest)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).with_name("detect_spec_tooling.py")


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def write(path: Path, text: str = "x\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_help_shows_example() -> None:
    result = run("--help")
    assert result.returncode == 0
    assert "example:" in result.stdout
    assert "--root" in result.stdout


def test_openspec_counts_and_owned_paths(tmp_path: Path) -> None:
    write(
        tmp_path / "openspec/specs/auth/spec.md",
        "### Requirement: Login\nThe system SHALL work.\n",
    )
    write(tmp_path / "openspec/specs/export/spec.md")
    write(tmp_path / "openspec/changes/add-export/proposal.md")
    write(tmp_path / "openspec/changes/archive/2026-01-01-old/proposal.md")
    write(tmp_path / "openspec/config.yaml", "schema: spec-driven\n")
    write(tmp_path / "AGENTS.md", "Read openspec/specs before changing behaviour.\n")
    result = run("--root", str(tmp_path))
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    [tool] = report["tools"]
    assert tool["tool"] == "openspec"
    assert tool["specs"] == 2
    assert tool["active_changes"] == 1
    assert tool["archived_changes"] == 1
    assert tool["owned_paths"] == ["openspec"]
    assert report["entrypoint_pointers"][0]["file"] == "AGENTS.md"
    assert report["requirement_restating_candidates"] == []
    assert report["partial"] is False


def test_nothing_found(tmp_path: Path) -> None:
    write(tmp_path / "README.md", "# Tool\n\nA small tool.\n")
    result = run("--root", str(tmp_path))
    assert result.returncode == 0
    report = json.loads(result.stdout)
    assert report["tools"] == []
    assert report["requirement_restating_candidates"] == []
    assert "tools: none" in result.stderr


def test_bad_root(tmp_path: Path) -> None:
    result = run("--root", str(tmp_path / "missing"))
    assert result.returncode == 2
    assert result.stdout == ""
    assert "not a directory" in result.stderr
    assert "--root ." in result.stderr


def test_bad_max_candidates(tmp_path: Path) -> None:
    result = run("--root", str(tmp_path), "--max-candidates", "0")
    assert result.returncode == 2
    assert result.stdout == ""


@pytest.mark.skipif(
    os.name != "posix" or os.geteuid() == 0, reason="needs a non-root POSIX user"
)
def test_unreadable_subdirectory(tmp_path: Path) -> None:
    locked = tmp_path / "docs/locked"
    write(locked / "notes.md")
    locked.chmod(0)
    try:
        result = run("--root", str(tmp_path))
    finally:
        locked.chmod(0o755)
    assert result.returncode == 1
    assert "docs/locked" in result.stderr
    if result.stdout:
        assert json.loads(result.stdout)["partial"] is True


def test_restating_document_found(tmp_path: Path) -> None:
    write(tmp_path / "openspec/specs/a/spec.md")
    write(
        tmp_path / "docs/requirements.md",
        "# Requirements\n\n## Acceptance criteria\n\n- works\n",
    )
    write(
        tmp_path / ".github/ISSUE_TEMPLATE/feature.yml",
        "body:\n  - label: Acceptance\n",
    )
    report = json.loads(run("--root", str(tmp_path)).stdout)
    files = [c["file"] for c in report["requirement_restating_candidates"]]
    assert files == [".github/ISSUE_TEMPLATE/feature.yml", "docs/requirements.md"]


def test_spec_kit_and_kiro(tmp_path: Path) -> None:
    write(tmp_path / ".specify/memory/constitution.md")
    write(tmp_path / "specs/001-login/spec.md")
    write(tmp_path / "specs/002-export/plan.md")
    for name in ("requirements.md", "design.md", "tasks.md"):
        write(tmp_path / ".kiro/specs/search" / name)
    report = json.loads(run("--root", str(tmp_path)).stdout)
    tools = {t["tool"]: t for t in report["tools"]}
    assert tools["spec-kit"]["features"] == 2
    assert tools["spec-kit"]["specs"] == 1
    assert tools["spec-kit"]["constitution"] == ".specify/memory/constitution.md"
    assert tools["kiro"]["specs"] == 1


def test_committed_documents(tmp_path: Path) -> None:
    write(tmp_path / "SPEC.md", "## Acceptance criteria\n")
    report = json.loads(run("--root", str(tmp_path)).stdout)
    assert report["tools"][0]["tool"] == "committed-documents"
    assert report["requirement_restating_candidates"] == []


def test_skill_trees_and_symlink_skipped(tmp_path: Path) -> None:
    write(tmp_path / ".agents/skills/release/SKILL.md", "## Acceptance criteria\n")
    write(
        tmp_path / ".agents/skills/release/references/a.md", "## Acceptance criteria\n"
    )
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude/skills").symlink_to(
        tmp_path / ".agents/skills", target_is_directory=True
    )
    write(tmp_path / "docs/real/req.md", "## Acceptance criteria\n")
    (tmp_path / "docs/link").symlink_to(
        tmp_path / "docs/real", target_is_directory=True
    )
    report = json.loads(run("--root", str(tmp_path)).stdout)
    files = [c["file"] for c in report["requirement_restating_candidates"]]
    assert len(files) == 1
    assert files[0] in {"docs/real/req.md", "docs/link/req.md"}


def test_repeated_run_is_identical_and_writes_nothing(tmp_path: Path) -> None:
    write(tmp_path / "openspec/specs/a/spec.md")
    write(tmp_path / "docs/requirements.md", "## Acceptance criteria\n")
    before = sorted(p.as_posix() for p in tmp_path.rglob("*"))
    first = run("--root", str(tmp_path))
    second = run("--root", str(tmp_path))
    assert first.stdout == second.stdout
    assert sorted(p.as_posix() for p in tmp_path.rglob("*")) == before


def test_large_output_summarised(tmp_path: Path) -> None:
    lines = "".join(
        f"see openspec/specs/area{i}/spec.md for area {i} details\n" for i in range(300)
    )
    write(tmp_path / "AGENTS.md", lines)
    short = json.loads(run("--root", str(tmp_path)).stdout)
    assert short["summarised"] is True
    assert short["entrypoint_pointers_not_shown"] == 280
    full = json.loads(run("--root", str(tmp_path), "--full").stdout)
    assert len(full["entrypoint_pointers"]) == 300
