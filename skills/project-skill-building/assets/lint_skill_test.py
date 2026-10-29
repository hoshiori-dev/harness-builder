"""Tests for lint_skill.py: run with
`uv run --no-project --python 3.12 --with pytest==9.0.2 pytest -q <this directory>`."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).with_name("lint_skill.py")

GOOD_DESCRIPTION = (
    "Release procedure for this project. Use when the user asks to cut a release, "
    "tag a version, or publish a build; when a release step failed and must be redone. "
    "Not for hotfix branches or changelog prose."
)


def write_skill(
    root: Path,
    name: str = "release-procedure",
    *,
    description: str = GOOD_DESCRIPTION,
    frontmatter_name: str | None = None,
    body: str | None = None,
    files: dict[str, str] | None = None,
) -> Path:
    skill_dir = root / name
    skill_dir.mkdir(parents=True)
    fm_name = frontmatter_name if frontmatter_name is not None else name
    body = body or (
        "# Release Procedure\n\n"
        "One paragraph.\n\n"
        "## Workflow\n\n"
        "1. Read [references/checks.md](references/checks.md) when a check is red.\n"
        "2. Copy [assets/notes.md](assets/notes.md) into the release notes.\n"
    )
    files = (
        files
        if files is not None
        else {
            "references/checks.md": "# Checks\n\nWhat each red check means.\n",
            "assets/notes.md": "# Release notes shape\n",
        }
    )
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {fm_name}\ndescription: >\n  {description}\nlicense: Apache-2.0\n---\n\n{body}",
        encoding="utf-8",
    )
    for rel_path, content in files.items():
        target = skill_dir / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return skill_dir


def run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ, PYTHONPATH="")
    return subprocess.run(
        [sys.executable, "-I", str(SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=cwd,
        env=env,
        check=False,
    )


def findings(skill_dir: Path) -> list[dict]:
    result = run("--skill", str(skill_dir), "--json")
    return json.loads(result.stdout)


def test_passing_skill_exits_zero(tmp_path: Path) -> None:
    skill_dir = write_skill(tmp_path)
    result = run("--skill", str(skill_dir))
    assert result.returncode == 0, result.stderr
    assert "all checks passed" in result.stdout
    assert result.stderr == ""


def test_skill_md_path_is_accepted(tmp_path: Path) -> None:
    skill_dir = write_skill(tmp_path)
    result = run("--skill", str(skill_dir / "SKILL.md"))
    assert result.returncode == 0, result.stderr


def test_broken_link_is_an_error(tmp_path: Path) -> None:
    skill_dir = write_skill(
        tmp_path,
        body="# T\n\n1. Read [references/missing.md](references/missing.md) when lost.\n",
        files={},
    )
    found = findings(skill_dir)
    assert any(
        f["level"] == "error"
        and "does not exist" in f["reason"]
        and "missing.md" in f["location"]
        for f in found
    )


def test_escaping_link_is_an_error(tmp_path: Path) -> None:
    (tmp_path / "outside.md").write_text("outside\n", encoding="utf-8")
    skill_dir = write_skill(
        tmp_path,
        body="# T\n\n1. Read [../outside.md](../outside.md) when in doubt.\n",
        files={},
    )
    found = findings(skill_dir)
    assert any(f["level"] == "error" and "escapes" in f["reason"] for f in found)


def test_unreachable_asset_is_an_error(tmp_path: Path) -> None:
    skill_dir = write_skill(
        tmp_path,
        body="# T\n\n1. Do the thing.\n",
        files={"assets/orphan.md": "unused\n"},
    )
    found = findings(skill_dir)
    assert any(
        f["level"] == "error" and f["location"].endswith("assets/orphan.md")
        for f in found
    )


def test_asset_reached_through_linked_reference_passes(tmp_path: Path) -> None:
    skill_dir = write_skill(
        tmp_path,
        body="# T\n\n1. Read [references/how.md](references/how.md) when copying the shape.\n",
        files={
            "references/how.md": "Copy [../assets/shape.md](../assets/shape.md) line by line.\n",
            "assets/shape.md": "shape\n",
        },
    )
    assert run("--skill", str(skill_dir)).returncode == 0


def test_name_mismatch_and_broken_link_in_json(tmp_path: Path) -> None:
    skill_dir = write_skill(
        tmp_path,
        frontmatter_name="other-name",
        body="# T\n\n1. Read [references/gone.md](references/gone.md) when needed.\n",
        files={},
    )
    result = run("--skill", str(skill_dir), "--json")
    assert result.returncode == 1
    found = json.loads(result.stdout)
    errors = [f for f in found if f["level"] == "error"]
    assert len(errors) == 2
    assert all({"location", "level", "reason", "suggestion"} <= set(f) for f in found)
    assert any("other-name" in f["reason"] for f in errors)
    assert any("gone.md" in f["location"] for f in errors)


@pytest.mark.parametrize(
    ("length", "level", "marker", "exit_code"),
    [
        (700, "warning", ">600", 0),
        (950, "warning", ">900", 0),
        (1100, "error", "maximum", 1),
    ],
)
def test_description_budget_tiers(
    tmp_path: Path, length: int, level: str, marker: str, exit_code: int
) -> None:
    prefix = "Release procedure. Use when releasing. Not for hotfixes. "
    description = prefix + "x" * (
        length - len(prefix) - 1
    )  # the folded scalar adds "\n"
    skill_dir = write_skill(tmp_path, description=description)
    result = run("--skill", str(skill_dir), "--json")
    assert result.returncode == exit_code
    about_length = [f for f in json.loads(result.stdout) if "chars" in f["reason"]]
    assert len(about_length) == 1
    assert about_length[0]["level"] == level
    assert marker in about_length[0]["reason"]


def test_warnings_only_exit_zero_and_are_counted(tmp_path: Path) -> None:
    prefix = "Release procedure. Use when releasing. Not for hotfixes. "
    skill_dir = write_skill(tmp_path, description=prefix + "x" * 900)
    result = run("--skill", str(skill_dir))
    assert result.returncode == 0
    assert "WARNING" in result.stdout
    assert "1 warning(s)." in result.stderr


def test_description_quality_warnings(tmp_path: Path) -> None:
    skill_dir = write_skill(tmp_path, description="This skill helps me release things.")
    reasons = [f["reason"] for f in findings(skill_dir)]
    assert any("Use when" in r for r in reasons)
    assert any("Not for" in r for r in reasons)
    assert any("filler" in r for r in reasons)
    assert any("first person" in r for r in reasons)


def test_missing_skill_file_exits_one(tmp_path: Path) -> None:
    empty = tmp_path / "empty-skill"
    empty.mkdir()
    result = run("--skill", str(empty))
    assert result.returncode == 1
    assert "does not exist" in result.stderr
    assert result.stdout == ""


def test_bad_arguments_exit_two(tmp_path: Path) -> None:
    missing_flag = run()
    assert missing_flag.returncode == 2
    assert "usage" in missing_flag.stderr.lower()

    stray = tmp_path / "notes.txt"
    stray.write_text("x\n", encoding="utf-8")
    wrong_file = run("--skill", str(stray))
    assert wrong_file.returncode == 2
    assert "usage" in wrong_file.stderr.lower()
    assert "SKILL.md" in wrong_file.stderr


def test_help_shows_usage_example() -> None:
    result = run("--help")
    assert result.returncode == 0
    assert "Example" in result.stdout
    assert "--skill" in result.stdout


def test_repeated_run_is_idempotent(tmp_path: Path) -> None:
    skill_dir = write_skill(tmp_path, frontmatter_name="wrong")
    before = sorted((p, p.stat().st_mtime_ns) for p in skill_dir.rglob("*"))
    first = run("--skill", str(skill_dir), "--json")
    second = run("--skill", str(skill_dir), "--json")
    assert (first.returncode, first.stdout, first.stderr) == (
        second.returncode,
        second.stdout,
        second.stderr,
    )
    assert before == sorted((p, p.stat().st_mtime_ns) for p in skill_dir.rglob("*"))


def test_structure_findings(tmp_path: Path) -> None:
    skill_dir = write_skill(tmp_path)
    (skill_dir / "README.md").write_text("readme\n", encoding="utf-8")
    (skill_dir / "scripts").mkdir()
    found = findings(skill_dir)
    assert any(f["level"] == "error" and "README.md" in f["reason"] for f in found)
    assert any("'scripts/' is empty" in f["reason"] for f in found)


def test_script_hygiene_warnings(tmp_path: Path) -> None:
    skill_dir = write_skill(
        tmp_path,
        body="# T\n\n1. Run [scripts/ask.py](scripts/ask.py) when asked.\n",
        files={"scripts/ask.py": "name = input('name? ')\nprint(name)\n"},
    )
    reasons = [f["reason"] for f in findings(skill_dir)]
    assert any("interactive" in r for r in reasons)
    assert any("shebang" in r for r in reasons)
    assert any("PEP 723" in r for r in reasons)
    assert any("--help" in r for r in reasons)


def test_pointer_without_condition_warns(tmp_path: Path) -> None:
    skill_dir = write_skill(
        tmp_path,
        body="# T\n\nSee [references/checks.md](references/checks.md) for details.\n",
        files={"references/checks.md": "checks\n"},
    )
    reasons = [f["reason"] for f in findings(skill_dir)]
    assert any("without a load condition" in r for r in reasons)


def test_unreworked_template_is_an_error(tmp_path: Path) -> None:
    template = SCRIPT.with_name("skill-template.md").read_text(encoding="utf-8")
    skill_dir = tmp_path / "skill-name"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(template, encoding="utf-8")
    result = run("--skill", str(skill_dir), "--json")
    assert result.returncode == 1
    errors = [f for f in json.loads(result.stdout) if f["level"] == "error"]
    reasons = " ".join(f["reason"] for f in errors)
    assert "template value" in reasons
    assert "placeholder left in 'description'" in reasons
    assert "placeholder left in 'license'" in reasons
    assert "<Skill Title>" in reasons


def test_placeholders_allowed_in_code_tags_and_configure_lines(tmp_path: Path) -> None:
    body = (
        "# Release Procedure\n\n"
        "Run `deploy <env>` first, then open <https://example.com>.<br>\n\n"
        "TARGET={{TARGET}}  # CONFIGURE: deployment target\n\n"
        "```text\n<Leading word> <capability>\n```\n"
    )
    skill_dir = write_skill(tmp_path, body=body, files={})
    assert not [f for f in findings(skill_dir) if "placeholder" in f["reason"]]


def test_leftover_braces_placeholder_is_an_error(tmp_path: Path) -> None:
    leftover = "{" * 2 + "TARGET" + "}" * 2
    skill_dir = write_skill(tmp_path, body=f"# T\n\nTarget is {leftover}.\n", files={})
    assert any(leftover in f["reason"] for f in findings(skill_dir))


def test_output_is_summarised_above_budget(tmp_path: Path) -> None:
    links = "".join(
        f"- Read [references/r{i}.md](references/r{i}.md) when case {i}.\n"
        for i in range(120)
    )
    skill_dir = write_skill(tmp_path, body="# T\n\n" + links, files={})
    short = run("--skill", str(skill_dir))
    full = run("--skill", str(skill_dir), "--full")
    assert "more finding(s) omitted" in short.stdout
    assert len(short.stdout) < len(full.stdout)
    assert "omitted" not in full.stdout


def test_flat_frontmatter_parser_matches_yaml_semantics() -> None:
    sys.path.insert(0, str(SCRIPT.parent))
    import lint_skill

    fm, body = lint_skill.parse_frontmatter(
        "---\n"
        "name: demo\n"
        "description: >\n"
        "  First line\n"
        "  second line.\n"
        "license: Apache-2.0  # comment\n"
        "disable-model-invocation: true\n"
        "metadata:\n"
        "  author: org\n"
        "  version: '1.0'\n"
        "---\n"
        "# Body\n"
    )
    assert fm["name"] == "demo"
    assert fm["description"] == "First line second line.\n"
    assert fm["license"] == "Apache-2.0"
    assert fm["disable-model-invocation"] is True
    assert fm["metadata"] == {"author": "org", "version": "1.0"}
    assert body == "# Body\n"
    with pytest.raises(lint_skill.FrontmatterError):
        lint_skill.parse_frontmatter("name: no-delimiters\n")
