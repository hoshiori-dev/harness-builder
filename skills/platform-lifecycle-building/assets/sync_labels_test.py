"""Tests for sync_labels.py against an in-memory repository; no CLI runs."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "sync_labels", Path(__file__).with_name("sync_labels.py")
)
sync_labels = importlib.util.module_from_spec(SPEC)
sys.modules["sync_labels"] = sync_labels
SPEC.loader.exec_module(sync_labels)


class FakeGh:
    """A repository's labels behind the `gh label` commands the script uses."""

    def __init__(self, labels: list[dict]):
        self.labels = {label["name"]: dict(label) for label in labels}
        self.writes: list[list[str]] = []

    def __call__(self, cmd: list[str]) -> subprocess.CompletedProcess:
        verb = cmd[2]
        if verb == "list":
            return subprocess.CompletedProcess(
                cmd, 0, json.dumps(list(self.labels.values())), ""
            )
        self.writes.append(cmd)
        name = cmd[3]
        if verb == "delete":
            self.labels.pop(name)
        else:
            color = cmd[cmd.index("--color") + 1]
            description = cmd[cmd.index("--description") + 1]
            self.labels[name] = {
                "name": name,
                "color": color,
                "description": description,
            }
        return subprocess.CompletedProcess(cmd, 0, "", "")


def write(tmp_path: Path, rows: list[dict]) -> str:
    path = tmp_path / "labels.json"
    path.write_text(json.dumps(rows), encoding="utf-8")
    return str(path)


ROWS = [
    {"name": "type:bug", "color": "d73a4a", "description": "Defect"},
    {"name": "type:task", "color": "1d76db", "description": "Planned work"},
]


def test_dry_run_prints_plan_and_writes_nothing(monkeypatch, tmp_path, capsys):
    fake = FakeGh(
        [
            {"name": "type:bug", "color": "D73A4A", "description": "Old"},
            {"name": "wontfix", "color": "ffffff", "description": ""},
        ]
    )
    monkeypatch.setattr(sync_labels, "run", fake)
    code = sync_labels.main(["--file", write(tmp_path, ROWS), "--repo", "octo/app"])
    plan = json.loads(capsys.readouterr().out)
    assert code == 0
    assert plan["applied"] is False
    assert [label["name"] for label in plan["create"]] == ["type:task"]
    assert [label["name"] for label in plan["update"]] == ["type:bug"]
    assert plan["delete"] == []
    assert plan["not_in_file"] == ["wontfix"]
    assert fake.writes == []


def test_apply_then_rerun_is_all_skips(monkeypatch, tmp_path, capsys):
    fake = FakeGh([{"name": "wontfix", "color": "ffffff", "description": ""}])
    monkeypatch.setattr(sync_labels, "run", fake)
    args = ["--file", write(tmp_path, ROWS), "--repo", "octo/app", "--apply"]
    assert sync_labels.main(args) == 0
    capsys.readouterr()
    assert sync_labels.main(args) == 0
    second = json.loads(capsys.readouterr().out)
    assert second["create"] == [] and second["update"] == [] and second["delete"] == []
    assert second["skip"] == ["type:bug", "type:task"]
    assert "wontfix" in fake.labels, "no label is deleted without --prune"


def test_prune_plans_delete_and_applies_only_with_apply(monkeypatch, tmp_path, capsys):
    fake = FakeGh([{"name": "wontfix", "color": "ffffff", "description": ""}])
    monkeypatch.setattr(sync_labels, "run", fake)
    path = write(tmp_path, ROWS)
    sync_labels.main(["--file", path, "--repo", "octo/app", "--prune"])
    assert json.loads(capsys.readouterr().out)["delete"] == ["wontfix"]
    assert "wontfix" in fake.labels
    sync_labels.main(["--file", path, "--repo", "octo/app", "--prune", "--apply"])
    assert "wontfix" not in fake.labels


def test_invalid_colour_names_file_index_and_fix(monkeypatch, tmp_path, capsys):
    called = []
    monkeypatch.setattr(sync_labels, "run", lambda cmd: called.append(cmd))
    path = write(
        tmp_path, [ROWS[0], {"name": "type:task", "color": "#12345", "description": ""}]
    )
    code = sync_labels.main(["--file", path, "--repo", "octo/app"])
    captured = capsys.readouterr()
    assert code == 1
    assert captured.out == ""
    assert f"{path}[1]" in captured.err and "six hex digits" in captured.err
    assert called == [], "validation runs before any CLI call"


@pytest.mark.parametrize(
    "rows",
    [
        [],
        [{"color": "ededed"}],
        [ROWS[0], ROWS[0]],
        [{"name": "x", "color": "ededed", "description": 3}],
    ],
)
def test_other_file_defects_exit_1(tmp_path, rows):
    assert (
        sync_labels.main(["--file", write(tmp_path, rows), "--repo", "octo/app"]) == 1
    )


def test_missing_cli_exits_1(monkeypatch, tmp_path, capsys):
    def absent(cmd):
        raise FileNotFoundError(cmd[0])

    monkeypatch.setattr(sync_labels, "run", absent)
    assert (
        sync_labels.main(["--file", write(tmp_path, ROWS), "--repo", "octo/app"]) == 1
    )
    assert "`gh` is not installed" in capsys.readouterr().err


def test_bad_repo_is_exit_2(tmp_path):
    with pytest.raises(SystemExit) as exc:
        sync_labels.main(["--file", write(tmp_path, ROWS), "--repo", "octo"])
    assert exc.value.code == 2


def test_gitlab_uses_glab_api_with_hash_colours(monkeypatch, tmp_path, capsys):
    calls = []

    def fake(cmd):
        calls.append(cmd)
        if "--paginate" in cmd:
            listing = (
                '[{"name": "type:bug", "color": "#D73A4A", "description": "Defect"}]'
            )
            return subprocess.CompletedProcess(cmd, 0, listing + "[]", "")
        return subprocess.CompletedProcess(cmd, 0, "{}", "")

    monkeypatch.setattr(sync_labels, "run", fake)
    args = [
        "--platform",
        "gitlab",
        "--hostname",
        "gitlab.example.com",
        "--file",
        write(tmp_path, ROWS),
    ]
    assert sync_labels.main([*args, "--repo", "team/sub/app", "--apply"]) == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["skip"] == ["type:bug"]
    post = [cmd for cmd in calls if "POST" in cmd][0]
    assert post[:4] == ["glab", "api", "--hostname", "gitlab.example.com"]
    assert "projects/team%2Fsub%2Fapp/labels" in post
    assert "color=#1d76db" in post
    assert all(cmd[0] == "glab" for cmd in calls)
