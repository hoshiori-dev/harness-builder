"""Tests for the deposited spec_changes.py (snapshot, check, status, labels)."""

from __future__ import annotations

import base64
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "spec_changes.py"
_spec = importlib.util.spec_from_file_location("spec_changes_asset", SCRIPT)
sc = importlib.util.module_from_spec(_spec)
sys.modules["spec_changes_asset"] = sc
_spec.loader.exec_module(sc)

CHANGES = "openspec/changes"


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


def commit(repo: Path, message: str) -> str:
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "--allow-empty", "-m", message)
    return git(repo, "rev-parse", "HEAD").strip()


def add_change(repo: Path, name: str, tasks: str = "- [ ] 1.1 Build it\n") -> None:
    base = f"{CHANGES}/{name}"
    write(repo, f"{base}/.openspec.yaml", "schema: spec-driven\n")
    write(repo, f"{base}/proposal.md", f"## Why\n{name}\n")
    write(repo, f"{base}/specs/export/spec.md", "## ADDED Requirements\n")
    write(repo, f"{base}/tasks.md", tasks)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    git(root, "init", "-q", "-b", "main")
    write(root, "README.md", "x\n")
    write(root, f"{CHANGES}/archive/.gitkeep", "")
    commit(root, "base")
    git(root, "branch", "base")
    return root


def run(repo: Path, *args: str) -> tuple[int, dict | None, str]:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(repo), *args],
        capture_output=True,
        text=True,
    )
    try:
        data = json.loads(proc.stdout) if proc.stdout.strip() else None
    except ValueError:
        data = None
    return proc.returncode, data, proc.stderr


def fake_openspec(tmp_path: Path, code: int = 0) -> str:
    exe = tmp_path / "openspec"
    exe.write_text(f"#!/bin/sh\necho validated\nexit {code}\n", encoding="utf-8")
    exe.chmod(0o755)
    return str(exe)


class GitApi(sc.Api):
    """GitHub's REST answers for one pull request, served from a local repository."""

    def __init__(self, repo: Path, labels=(), comments=(), permission="write", **kw):
        super().__init__("o/r", "https://api.invalid", "t", kw.get("max_calls", 200))
        self.root, self.labels, self.comments = repo, list(labels), list(comments)
        self.permission, self.truncate, self.binary = permission, False, None
        self.base = git(repo, "rev-parse", "base").strip()
        self.head = git(repo, "rev-parse", "HEAD").strip()

    def fetch(self, endpoint: str) -> bytes:
        path, _, query = endpoint.partition("?")
        parts = path.split("/")
        if path == "repos/o/r/pulls/1":
            files = self._files()
            body = {
                "base": {"sha": self.base},
                "head": {"sha": self.head},
                "changed_files": len(files),
                "labels": [{"name": n} for n in self.labels],
            }
        elif path == "repos/o/r/pulls/1/files":
            body = [{"filename": f} for f in self._files()] if "page=1" in query else []
        elif parts[3:5] == ["git", "trees"]:
            flags = ["-r", "-t"] if "recursive" in query else []
            rows = git(self.root, "ls-tree", "-l", *flags, parts[5]).splitlines()
            tree = []
            for row in rows:
                meta, name = row.split("\t", 1)
                _, kind, sha, size = meta.split()
                entry = {"path": name, "type": kind, "sha": sha}
                if kind == "blob":
                    entry["size"] = int(size)
                tree.append(entry)
            body = {"tree": tree, "truncated": self.truncate}
        elif parts[3:5] == ["git", "blobs"]:
            raw = subprocess.run(
                ["git", "-C", str(self.root), "cat-file", "blob", parts[5]],
                capture_output=True,
                check=True,
            ).stdout
            if self.binary and self.binary in raw.decode("utf-8", "replace"):
                raw = b"\xff\xfe"
            body = {"content": base64.b64encode(raw).decode(), "encoding": "base64"}
        elif path == "repos/o/r/issues/1/comments":
            body = self.comments if "page=1" in query else []
        elif parts[3] == "collaborators":
            body = {"permission": self.permission}
        else:
            raise AssertionError(f"unexpected GET {endpoint}")
        return json.dumps(body).encode()

    def _files(self) -> list[str]:
        out = git(
            self.root,
            "diff",
            "--name-only",
            "--no-renames",
            f"{self.base}...{self.head}",
        )
        return out.split()


def snapshot(monkeypatch, tmp_path: Path, api: GitApi, *extra: str):
    monkeypatch.setenv("GH_TOKEN", "t")
    monkeypatch.setattr(sc, "Api", lambda *a, **k: api)
    out = tmp_path / "snap.json"
    code = sc.main(
        [
            "--root",
            str(api.root),
            "snapshot",
            "--repo",
            "o/r",
            "--pr",
            "1",
            "--output",
            str(out),
            *extra,
        ]
    )
    return code, out


def test_help_names_the_four_commands():
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"], capture_output=True, text=True
    )
    assert proc.returncode == 0
    for command in ("snapshot", "check", "status", "labels", "examples:"):
        assert command in proc.stdout


def test_unknown_option_exits_2():
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--bogus"], capture_output=True, text=True
    )
    assert proc.returncode == 2
    assert "--bogus" in proc.stderr


def test_unarchived_change_on_a_ready_request_awaits_the_archive(repo, tmp_path):
    add_change(repo, "export-csv")
    commit(repo, "change")
    code, data, _ = run(
        repo,
        "check",
        "--base",
        "base",
        "--head",
        "HEAD",
        "--openspec",
        fake_openspec(tmp_path),
    )
    assert code == 1
    assert data["verdict"] == "awaiting-archive"
    assert data["unarchived"] == ["export-csv"]


def test_draft_with_unarchived_change_warns(repo, tmp_path):
    add_change(repo, "export-csv")
    commit(repo, "change")
    args = (
        "check",
        "--base",
        "base",
        "--head",
        "HEAD",
        "--draft",
        "--openspec",
        fake_openspec(tmp_path),
    )
    code, data, err = run(repo, *args)
    assert code == 0
    assert data["verdict"] == "pass"
    assert "export-csv" in err


def test_failed_validation_is_invalid_and_missing_cli_is_named(repo, tmp_path):
    add_change(repo, "export-csv")
    commit(repo, "change")
    code, data, _ = run(
        repo,
        "check",
        "--base",
        "base",
        "--head",
        "HEAD",
        "--openspec",
        fake_openspec(tmp_path, 1),
    )
    assert code == 1
    assert data["verdict"] == "invalid"
    code, _, err = run(
        repo,
        "check",
        "--base",
        "base",
        "--head",
        "HEAD",
        "--openspec",
        str(tmp_path / "none"),
    )
    assert code == 1
    assert "not on PATH" in err


def test_archived_change_passes(repo, tmp_path):
    add_change(repo, "export-csv", "- [x] 1.1 Build it\n")
    commit(repo, "change")
    git(repo, "branch", "-f", "base")
    git(repo, "mv", f"{CHANGES}/export-csv", f"{CHANGES}/archive/2026-01-02-export-csv")
    commit(repo, "archive")
    code, data, _ = run(
        repo,
        "check",
        "--base",
        "base",
        "--head",
        "HEAD",
        "--openspec",
        fake_openspec(tmp_path),
    )
    assert (code, data["verdict"], data["unarchived"]) == (0, "pass", [])


def approve(repo: Path, tmp_path: Path) -> dict:
    """The record the label job writes when a person with write permission adds spec:approved."""
    head = git(repo, "rev-parse", "HEAD").strip()
    code, data, _ = run(
        repo,
        "labels",
        "--base",
        "base",
        "--head",
        "HEAD",
        "--current",
        "spec:pending,spec:approved",
        "--approved-by",
        "maint",
        "--approved-at",
        head,
        "--permission",
        "write",
    )
    assert code == 0
    assert data["state"] == "spec:approved"
    assert data["remove"] == ["spec:pending"]
    record = {k: data["record"][k] for k in ("status", "commit", "by", "hash", "event")}
    path = tmp_path / "record.json"
    path.write_text(json.dumps({"id": 7, **record}), encoding="utf-8")
    return {"path": path, "body": data["record"]["body"]}


def test_package_edited_after_approval_returns_to_pending(repo, tmp_path):
    add_change(repo, "export-csv")
    commit(repo, "change")
    record = approve(repo, tmp_path)
    args = (
        "labels",
        "--base",
        "base",
        "--head",
        "HEAD",
        "--current",
        "spec:approved",
        "--record",
        str(record["path"]),
    )
    code, data, _ = run(repo, *args)
    assert (code, data["state"]) == (0, "spec:approved")
    write(repo, f"{CHANGES}/export-csv/tasks.md", "- [x] 1.1 Build it\n")
    commit(repo, "tasks after approval keep the approval")
    assert run(repo, *args)[1]["state"] == "spec:approved"
    write(repo, f"{CHANGES}/export-csv/proposal.md", "## Why\nedited\n")
    commit(repo, "edit the package")
    code, data, _ = run(repo, *args)
    assert code == 0
    assert data["state"] == "spec:pending"
    assert data["remove"] == ["spec:approved"]
    assert data["add"] == ["spec:pending"]
    assert data["record"]["status"] == "withdrawn"
    assert data["record"]["id"] == 7


def test_approval_below_write_is_refused(repo, tmp_path):
    add_change(repo, "export-csv")
    commit(repo, "change")
    args = ("labels", "--base", "base", "--head", "HEAD", "--current", "spec:approved")
    code, data, _ = run(
        repo, *args, "--approved-by", "triager", "--permission", "triage"
    )
    assert (code, data["state"], data["remove"]) == (
        0,
        "spec:pending",
        ["spec:approved"],
    )
    assert data["record"] is None


def test_no_related_change_carries_no_label(repo):
    write(repo, "src.txt", "code\n")
    commit(repo, "code only")
    code, data, _ = run(
        repo, "labels", "--base", "base", "--head", "HEAD", "--current", "spec:pending"
    )
    assert (code, data["state"], data["remove"]) == (0, None, ["spec:pending"])


def test_snapshot_and_clone_agree(repo, tmp_path, monkeypatch):
    add_change(repo, "export-csv")
    add_change(repo, "import-csv", "- [x] 1.1 Done\n- [ ] 1.2 Open\n")
    commit(repo, "changes")
    record = approve(repo, tmp_path)
    api = GitApi(
        repo,
        labels=["spec:approved"],
        comments=[
            {"id": 7, "user": {"login": "github-actions[bot]"}, "body": record["body"]}
        ],
    )
    code, snap = snapshot(monkeypatch, tmp_path, api)
    assert code == 0
    for command, clone_extra in (
        ("status", ()),
        ("labels", ("--current", "spec:approved", "--record", str(record["path"]))),
    ):
        from_snapshot = run(repo, command, "--snapshot", str(snap))
        from_clone = run(
            repo, command, "--base", "base", "--head", "HEAD", *clone_extra
        )
        assert from_snapshot[0] == from_clone[0] == 0
        assert from_snapshot[1] == from_clone[1]
    assert run(repo, "labels", "--snapshot", str(snap))[1]["state"] == "spec:approved"


@pytest.mark.parametrize("fault", ["max_calls", "truncated", "binary"])
def test_partial_snapshot_writes_nothing(repo, tmp_path, monkeypatch, capsys, fault):
    add_change(repo, "export-csv")
    commit(repo, "change")
    api = GitApi(repo, max_calls=3 if fault == "max_calls" else 200)
    api.truncate = fault == "truncated"
    api.binary = "Build it" if fault == "binary" else None
    code, out = snapshot(monkeypatch, tmp_path, api)
    assert code == 1
    assert not out.exists()
    err = capsys.readouterr().err
    expected = {
        "max_calls": "--max-calls",
        "truncated": "truncated",
        "binary": f"{CHANGES}/export-csv/tasks.md",
    }
    assert expected[fault] in err


def test_long_snapshot_is_summarised(repo, tmp_path, monkeypatch, capsys):
    add_change(
        repo, "export-csv", "".join(f"- [ ] {i} task {'x' * 80}\n" for i in range(200))
    )
    commit(repo, "big change")
    api = GitApi(repo)
    monkeypatch.setenv("GH_TOKEN", "t")
    monkeypatch.setattr(sc, "Api", lambda *a, **k: api)
    assert sc.main(["--root", str(repo), "snapshot", "--repo", "o/r", "--pr", "1"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert "--output" in printed["summary"]
    assert printed["documents"] == 4
    code, out = snapshot(monkeypatch, tmp_path, api)
    assert code == 0
    assert json.loads(out.read_text())["head"]["files"]


def test_long_status_is_summarised_and_full_prints_all(repo):
    add_change(
        repo, "export-csv", "".join(f"- [ ] {i} task {'x' * 80}\n" for i in range(200))
    )
    commit(repo, "big change")
    code, data, _ = run(repo, "status", "--base", "base", "--head", "HEAD")
    assert code == 0
    assert "--full" in data["summary"] and "--output" in data["summary"]
    assert f"{CHANGES}/export-csv/tasks.md" in data["omitted_documents"]
    code, data, _ = run(repo, "status", "--base", "base", "--head", "HEAD", "--full")
    assert len(data["changes"][0]["tasks"]["open_tasks"]) == 200


def test_repeated_runs_are_identical_and_leave_the_tree(repo, tmp_path):
    add_change(repo, "export-csv")
    commit(repo, "change")
    exe = fake_openspec(tmp_path)
    before = git(repo, "status", "--porcelain")
    first = [
        run(repo, "check", "--base", "base", "--head", "HEAD", "--openspec", exe),
        run(repo, "status", "--base", "base", "--head", "HEAD"),
    ]
    second = [
        run(repo, "check", "--base", "base", "--head", "HEAD", "--openspec", exe),
        run(repo, "status", "--base", "base", "--head", "HEAD"),
    ]
    assert first == second
    assert git(repo, "status", "--porcelain") == before
