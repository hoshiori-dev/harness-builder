"""Tests for the deposited spec_kit_features.py (snapshot, check, status, labels)."""

from __future__ import annotations

import base64
import importlib.util
import io
import json
import subprocess
import sys
import urllib.parse
from pathlib import Path

import pytest

SCRIPT = Path(__file__).with_name("spec_kit_features.py")
_spec = importlib.util.spec_from_file_location("skw_asset_features", SCRIPT)
features = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(features)

TICKED = "# Tasks\n\n- [x] T001 Parse the file\n- [x] T002 Store rows\n"
MIXED = "# Tasks\n\n- [x] T001 Parse the file\n- [ ] T002 Store rows\n"
UNTICKED = "# Tasks\n\n- [ ] T001 Parse the file\n- [ ] T002 Store rows\n"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    ).stdout


def make_repo(tmp_path: Path, docs: dict[str, str | bytes]) -> tuple[Path, str, str]:
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
        target = feature / name
        if isinstance(text, bytes):
            target.write_bytes(text)
        else:
            target.write_text(text)
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "feature")
    head = git(repo, "rev-parse", "HEAD").strip()
    return repo, base, head


def run(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(repo), *args],
        capture_output=True,
        text=True,
    )


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def serve(repo: Path, base: str, head: str, truncate: bool = False):
    """An urlopen stand-in answering the REST reads from the local repository."""

    def urlopen(request, timeout=30):
        url = urllib.parse.urlsplit(request.full_url)
        path = url.path.split("/repos/o/r/", 1)[1]
        recursive = "recursive=1" in url.query
        if path == "pulls/1":
            changed = git(
                repo, "diff", "--name-only", "--no-renames", f"{base}...{head}"
            )
            body = {
                "base": {"sha": base},
                "head": {"sha": head},
                "changed_files": len(changed.split()),
            }
        elif path == "pulls/1/files":
            page = int(urllib.parse.parse_qs(url.query)["page"][0])
            changed = git(
                repo, "diff", "--name-only", "--no-renames", f"{base}...{head}"
            )
            names = changed.split()[(page - 1) * 100 : page * 100]
            body = [{"filename": n} for n in names]
        elif path.startswith("git/trees/"):
            sha = path.rsplit("/", 1)[1]
            flags = ["-r", "-t"] if recursive else []
            entries = []
            for line in git(repo, "ls-tree", "-l", *flags, sha).splitlines():
                meta, name = line.split("\t", 1)
                _, kind, obj, size = meta.split()
                entry = {"path": name, "type": kind, "sha": obj}
                if kind == "blob":
                    entry["size"] = int(size)
                entries.append(entry)
            body = {"truncated": truncate and recursive, "tree": entries}
        elif path.startswith("git/blobs/"):
            sha = path.rsplit("/", 1)[1]
            raw = subprocess.run(
                ["git", "-C", str(repo), "cat-file", "blob", sha],
                check=True,
                capture_output=True,
            ).stdout
            body = {"encoding": "base64", "content": base64.b64encode(raw).decode()}
        else:
            raise AssertionError(f"unexpected endpoint {path}")
        return FakeResponse(json.dumps(body).encode())

    return urlopen


def snapshot(monkeypatch, repo, base, head, *extra: str) -> int:
    monkeypatch.setenv("GH_TOKEN", "test-token")
    monkeypatch.setattr(features.urllib.request, "urlopen", serve(repo, base, head))
    return features.main(["snapshot", "--repo", "o/r", "--pr", "1", *extra])


def test_help_names_the_four_subcommands():
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"], capture_output=True, text=True
    )
    assert result.returncode == 0
    for command in ("snapshot", "check", "status", "labels"):
        assert command in result.stdout
    assert "Example:" in result.stdout


def test_snapshot_matches_git_refs(tmp_path, monkeypatch):
    repo, base, head = make_repo(
        tmp_path, {"spec.md": "# S\n", "plan.md": "# P\n", "tasks.md": MIXED}
    )
    doc = tmp_path / "snapshot.json"
    assert snapshot(monkeypatch, repo, base, head, "--output", str(doc)) == 0
    for args in (["status", "--json"], ["check"], ["labels", "--json"]):
        from_refs = run(repo, *args, "--base", base, "--head", head)
        from_doc = run(repo, *args, "--snapshot", str(doc))
        assert from_doc.stdout == from_refs.stdout
        assert from_doc.returncode == from_refs.returncode


def test_partial_reads_fail_and_write_nothing(tmp_path, monkeypatch, capsys):
    repo, base, head = make_repo(
        tmp_path, {"spec.md": "# S\n", "plan.md": "# P\n", "tasks.md": b"\xff\xfe"}
    )
    doc = tmp_path / "snapshot.json"
    assert snapshot(monkeypatch, repo, base, head, "--output", str(doc)) == 1
    assert "specs/003-import/tasks.md" in capsys.readouterr().err
    assert (
        snapshot(
            monkeypatch, repo, base, head, "--max-calls", "2", "--output", str(doc)
        )
        == 1
    )
    assert "--max-calls" in capsys.readouterr().err
    monkeypatch.setattr(
        features.urllib.request, "urlopen", serve(repo, base, head, True)
    )
    code = features.main(
        ["snapshot", "--repo", "o/r", "--pr", "1", "--output", str(doc)]
    )
    assert code == 1
    assert "truncated" in capsys.readouterr().err
    assert not doc.exists()


def test_snapshot_for_another_specs_dir_is_refused(tmp_path, monkeypatch):
    repo, base, head = make_repo(
        tmp_path, {"spec.md": "# S\n", "plan.md": "# P\n", "tasks.md": TICKED}
    )
    doc = tmp_path / "snapshot.json"
    assert snapshot(monkeypatch, repo, base, head, "--output", str(doc)) == 0
    for command in ("status", "check", "labels"):
        result = run(repo, "--specs-dir", "docs/specs", command, "--snapshot", str(doc))
        assert result.returncode == 1
        assert "'specs'" in result.stderr and "'docs/specs'" in result.stderr


def test_split_shape_admits_no_ticked_task_only(tmp_path):
    repo, base, head = make_repo(
        tmp_path, {"spec.md": "# S\n", "plan.md": "# P\n", "tasks.md": UNTICKED}
    )
    assert (
        run(
            repo, "check", "--base", base, "--head", head, "--shape", "split"
        ).returncode
        == 0
    )
    (repo / "specs/003-import/tasks.md").write_text(MIXED)
    git(repo, "commit", "-qam", "tick one")
    result = run(repo, "check", "--base", base, "--head", "HEAD", "--shape", "split")
    assert result.returncode == 1
    assert "003-import" in result.stdout and "T002" in result.stdout


def test_missing_task_list_in_snapshot(tmp_path, monkeypatch):
    repo, base, head = make_repo(tmp_path, {"spec.md": "# S\n", "plan.md": "# P\n"})
    doc = tmp_path / "snapshot.json"
    assert snapshot(monkeypatch, repo, base, head, "--output", str(doc)) == 0
    split = run(repo, "check", "--snapshot", str(doc), "--shape", "split")
    assert split.returncode == 0 and "not started" in split.stderr
    assert run(repo, "check", "--snapshot", str(doc), "--draft").returncode == 0
    ready = run(repo, "check", "--snapshot", str(doc))
    assert ready.returncode == 1
    assert "003-import" in ready.stdout and "missing tasks.md" in ready.stdout
    labels = run(repo, "labels", "--snapshot", str(doc), "--json")
    assert json.loads(labels.stdout)["desired"] == ["spec:not-started"]


def test_open_task_fails_ready_and_warns_on_draft(tmp_path):
    repo, base, head = make_repo(
        tmp_path, {"spec.md": "# S\n", "plan.md": "# P\n", "tasks.md": MIXED}
    )
    ready = run(repo, "check", "--base", base, "--head", head)
    assert ready.returncode == 1
    assert "003-import" in ready.stdout and "T002 Store rows" in ready.stdout
    draft = run(repo, "check", "--base", base, "--head", head, "--draft")
    assert draft.returncode == 0
    assert "T002 Store rows" in draft.stderr and draft.stdout == ""


def test_missing_plan_fails(tmp_path):
    repo, base, head = make_repo(tmp_path, {"spec.md": "# S\n", "tasks.md": TICKED})
    for extra in ([], ["--draft"]):
        result = run(repo, "check", "--base", base, "--head", head, *extra)
        assert result.returncode == 1
        assert "003-import" in result.stdout and "plan.md" in result.stdout


def test_labels_replace_a_stale_label(tmp_path):
    repo, base, head = make_repo(
        tmp_path, {"spec.md": "# S\n", "plan.md": "# P\n", "tasks.md": TICKED}
    )
    result = run(
        repo,
        "labels",
        "--base",
        base,
        "--head",
        head,
        "--current",
        "spec:not-started",
        "--json",
    )
    plan = json.loads(result.stdout)
    assert plan["add"] == ["spec:done"] and plan["remove"] == ["spec:not-started"]
    taxonomy = json.loads(run(repo, "labels", "--taxonomy").stdout)
    assert taxonomy["managed"] == ["spec:not-started", "spec:in-progress", "spec:done"]


def test_long_snapshot_is_summarised(tmp_path, monkeypatch, capsys):
    repo, base, head = make_repo(
        tmp_path,
        {"spec.md": "# S\n" + "x" * 12000, "plan.md": "# P\n", "tasks.md": TICKED},
    )
    assert snapshot(monkeypatch, repo, base, head) == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["truncated"] is True and summary["features"] == 1
    assert summary["characters"] > 10000
    assert snapshot(monkeypatch, repo, base, head, "--full") == 0
    assert json.loads(capsys.readouterr().out)["schema"] == "spec-kit-snapshot/1"
    doc = tmp_path / "snapshot.json"
    assert snapshot(monkeypatch, repo, base, head, "--output", str(doc)) == 0
    assert len(json.loads(doc.read_text())["head"]["files"]) == 3


def test_repeated_check_is_identical(tmp_path, monkeypatch):
    repo, base, head = make_repo(
        tmp_path, {"spec.md": "# S\n", "plan.md": "# P\n", "tasks.md": MIXED}
    )
    doc = tmp_path / "snapshot.json"
    assert snapshot(monkeypatch, repo, base, head, "--output", str(doc)) == 0
    before = git(repo, "status", "--porcelain")
    first = run(repo, "check", "--snapshot", str(doc))
    second = run(repo, "check", "--snapshot", str(doc))
    assert (first.returncode, first.stdout, first.stderr) == (
        second.returncode,
        second.stdout,
        second.stderr,
    )
    assert git(repo, "status", "--porcelain") == before


@pytest.mark.parametrize(
    ("args", "needle"),
    [(["check", "--bogus"], "--bogus"), (["status"], "head source")],
)
def test_bad_arguments_exit_2(tmp_path, args, needle):
    repo, _, _ = make_repo(tmp_path, {"spec.md": "# S\n", "plan.md": "# P\n"})
    result = run(repo, *args)
    assert result.returncode == 2
    assert needle in result.stderr
