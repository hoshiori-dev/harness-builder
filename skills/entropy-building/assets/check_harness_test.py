"""Tests for check_harness.py: run with
`uv run --no-project --python 3.12 --with pytest==9.0.2 pytest -q <this directory>`."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).with_name("check_harness.py")
SPEC = importlib.util.spec_from_file_location("check_harness", SCRIPT)
check_harness = importlib.util.module_from_spec(SPEC)
sys.modules["check_harness"] = check_harness
SPEC.loader.exec_module(check_harness)

ENTRY = """# Agents

Run `just test` before handing back.
Read [the style guide](.agents/knowledge/style.md) when writing code.
Build output lands in `build/out.txt`.
"""


def write(root: Path, files: dict[str, str]) -> None:
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def fake_tool(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str, output: str
) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    tool = bin_dir / name
    tool.write_text(f"#!{sys.executable}\nprint({output!r})\n", encoding="utf-8")
    tool.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}:/usr/bin:/bin")


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "repo"
    write(
        root,
        {
            "AGENTS.md": ENTRY,
            "justfile": "test:\n    echo ok\n",
            ".agents/knowledge/style.md": "# Style\n\nUse `just lint`.\n",
            "build/out.txt": "x\n",
            "README.md": "# 项目\n\n## 安装\n\n`just setup`\n\n| a | b |\n",
            "README.en.md": "# Project\n\n## Install\n\n`just setup`\n\n| a | b |\n",
        },
    )
    fake_tool(tmp_path, monkeypatch, "just", "lint setup test")
    for name, value in {
        "ENTRYPOINT": "AGENTS.md",
        "KNOWLEDGE_DIRS": [".agents/knowledge"],
        "EXTRA_DOCS": [],
        "TASK_RUNNER": "just",
        "RUNNER_FILE": "justfile",
        "MIRROR_PAIRS": [("README.md", "README.en.md", [("## 安装", "## Install")])],
        "IGNORE_PATHS": [],
        "TIER2": False,
        "ENTRYPOINT_BUDGET": 120,
        "SKILL_DIRS": [],
    }.items():
        monkeypatch.setattr(check_harness, name, value)
    return root


def run(
    root: Path, capsys: pytest.CaptureFixture[str], *extra: str
) -> tuple[int, dict, str]:
    code = check_harness.main(["--root", str(root), *extra])
    out, err = capsys.readouterr()
    return code, json.loads(out), err


def rules(report: dict) -> list[str]:
    return sorted(f["rule"] for f in report["findings"])


def snapshot(root: Path) -> dict[str, bytes]:
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in root.rglob("*")
        if p.is_file()
    }


def test_clean_repository_exits_0_twice_and_changes_nothing(repo, capsys):
    before = snapshot(repo)
    for _ in range(2):
        code, report, _ = run(repo, capsys)
        assert code == 0
        assert report == {"count": 0, "findings": []}
    assert snapshot(repo) == before


def test_missing_recipe_and_unreachable_knowledge_file(repo, capsys):
    write(
        repo,
        {
            "AGENTS.md": ENTRY + "Then `just deploy`.\n",
            ".agents/knowledge/orphan.md": "# Orphan\n",
        },
    )
    code, report, err = run(repo, capsys)
    assert code == 1
    assert rules(report) == ["doc-recipe", "knowledge-reachable"]
    by_rule = {f["rule"]: f for f in report["findings"]}
    assert by_rule["doc-recipe"]["file"] == "AGENTS.md"
    assert "deploy" in by_rule["doc-recipe"]["problem"]
    assert by_rule["knowledge-reachable"]["file"] == ".agents/knowledge/orphan.md"
    assert all(f["fix"] for f in report["findings"])
    assert "AGENTS.md:6: doc-recipe:" in err and "Fix:" in err


def test_broken_link_and_backticked_path(repo, capsys):
    text = (
        ENTRY
        + "See [gone](docs/gone.md), `build/missing.txt`, `owner/repo`, `SKILL.md`.\n"
    )
    write(repo, {"AGENTS.md": text})
    code, report, _ = run(repo, capsys)
    assert code == 1
    assert rules(report) == ["doc-link", "doc-path"]
    assert "build/missing.txt" in next(
        f["problem"] for f in report["findings"] if f["rule"] == "doc-path"
    )


def test_ignored_path_and_fenced_block_are_not_checked(repo, capsys, monkeypatch):
    monkeypatch.setattr(check_harness, "IGNORE_PATHS", [".agents/handoff/"])
    text = (
        ENTRY
        + "Handoffs go in `.agents/handoff/`.\n\n```\n`just nothing` [x](nowhere.md)\n```\n"
    )
    write(repo, {"AGENTS.md": text})
    code, report, _ = run(repo, capsys)
    assert (code, report["count"]) == (0, 0)


def test_mirror_pair_out_of_step(repo, capsys):
    write(
        repo,
        {"README.en.md": "# Project\n\n## Install\n\n`just bootstrap`\n\n| a | b |\n"},
    )
    code, report, _ = run(repo, capsys)
    assert code == 1
    (finding,) = [f for f in report["findings"] if f["rule"] == "mirror-pair"]
    for text in ("README.md", "README.en.md", "## 安装", "## Install"):
        assert text in finding["problem"] + finding["fix"] + finding["file"]
    assert finding["file"] == "README.en.md"
    assert finding["fix"].startswith("edit README.en.md to match README.md")


def test_mirror_heading_missing(repo, capsys):
    write(repo, {"README.en.md": "# Project\n\n## Setup\n"})
    code, report, _ = run(repo, capsys)
    assert code == 1
    assert report["findings"][0]["file"] == "README.en.md"


def test_configured_path_missing_exits_2(repo, capsys, monkeypatch):
    monkeypatch.setattr(check_harness, "KNOWLEDGE_DIRS", ["docs/knowledge"])
    code = check_harness.main(["--root", str(repo)])
    out, err = capsys.readouterr()
    assert code == 2
    assert out == ""
    assert "KNOWLEDGE_DIRS" in err and "docs/knowledge" in err


def test_runner_missing_exits_2(repo, capsys, monkeypatch, tmp_path):
    monkeypatch.setenv("PATH", str(tmp_path / "empty"))
    assert check_harness.main(["--root", str(repo)]) == 2
    assert "just is not installed" in capsys.readouterr().err


def test_tier2_off_skips_budget_and_says_so(repo, capsys, monkeypatch):
    monkeypatch.setattr(check_harness, "ENTRYPOINT_BUDGET", 2)
    write(repo, {"AGENTS.md": ENTRY + "`just deploy`\n"})
    code, report, err = run(repo, capsys)
    assert code == 1
    assert rules(report) == ["doc-recipe"]
    assert "tier 2" in err and "off" in err


def test_tier2_budget_and_skill_frontmatter(repo, capsys, monkeypatch):
    monkeypatch.setattr(check_harness, "TIER2", True)
    monkeypatch.setattr(check_harness, "ENTRYPOINT_BUDGET", 3)
    monkeypatch.setattr(check_harness, "SKILL_DIRS", [".agents/skills"])
    write(
        repo,
        {
            ".agents/skills/release/SKILL.md": "---\nname: releases\ndescription: >-\n  Cuts a release.\n---\n# R\n",
            ".agents/skills/ok-skill/SKILL.md": "---\nname: ok-skill\ndescription: Does one thing. Use when asked.\n---\n",
        },
    )
    code, report, _ = run(repo, capsys)
    assert code == 1
    assert rules(report) == ["entrypoint-budget", "skill-name"]
    budget = next(f for f in report["findings"] if f["rule"] == "entrypoint-budget")
    assert budget["file"] == "AGENTS.md"
    assert "5 lines" in budget["problem"] and "3" in budget["problem"]


def test_npm_scripts_are_read_from_package_json(repo, capsys, monkeypatch):
    monkeypatch.setattr(check_harness, "TASK_RUNNER", "npm")
    monkeypatch.setattr(check_harness, "RUNNER_FILE", "package.json")
    monkeypatch.setattr(check_harness, "MIRROR_PAIRS", [])
    write(
        repo,
        {
            "package.json": '{"scripts": {"test": "x"}}',
            "AGENTS.md": "Run `npm run test`, `npm run lint`.\n",
        },
    )
    monkeypatch.setattr(check_harness, "KNOWLEDGE_DIRS", [])
    code, report, _ = run(repo, capsys)
    assert code == 1
    assert [f["rule"] for f in report["findings"]] == ["doc-recipe"]
    assert "lint" in report["findings"][0]["problem"]


def test_make_targets_are_listed(repo, capsys, monkeypatch, tmp_path):
    monkeypatch.setattr(check_harness, "TASK_RUNNER", "make")
    monkeypatch.setattr(check_harness, "RUNNER_FILE", "Makefile")
    monkeypatch.setattr(check_harness, "MIRROR_PAIRS", [])
    monkeypatch.setattr(check_harness, "KNOWLEDGE_DIRS", [])
    fake_tool(
        tmp_path, monkeypatch, "make", "# Not a target:\nMakefile:\ntest: deps\nlint:\n"
    )
    write(
        repo,
        {
            "Makefile": "test:\n\ttrue\n",
            "AGENTS.md": "`make test` `make lint` `make Makefile`\n",
        },
    )
    code, report, _ = run(repo, capsys)
    assert code == 1
    assert [f["problem"] for f in report["findings"]] == [
        "mentions `make Makefile`, but Makefile has no recipe Makefile."
    ]


def test_long_output_is_summarised(repo, capsys, monkeypatch):
    write(
        repo, {"AGENTS.md": ENTRY + "".join(f"`just missing{i}`\n" for i in range(200))}
    )
    code, report, err = run(repo, capsys)
    assert code == 1
    assert report["count"] == 200 and report["truncated"] is True
    assert len(report["findings"]) == check_harness.SHOWN_WHEN_SUMMARISED
    assert "--full" in err
    code, report, _ = run(repo, capsys, "--full")
    assert len(report["findings"]) == 200


def test_cli_help_and_bad_argument_under_plain_python():
    help_run = subprocess.run(
        [sys.executable, "-I", str(SCRIPT), "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert help_run.returncode == 0
    assert "example:" in help_run.stdout
    bad = subprocess.run(
        [sys.executable, "-I", str(SCRIPT), "--bogus"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert bad.returncode == 2
    assert "usage:" in bad.stderr
    assert bad.stdout == ""
