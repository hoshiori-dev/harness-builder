"""Tests for checkpoint-recipes.just: run with
`uv run --no-project --python 3.12 --with pytest==9.0.2 pytest -q <this directory>`.

Each test builds a throwaway repository with a bare remote under tmp_path and
runs the recipes against it through `just --justfile ... --working-directory`.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

JUSTFILE = Path(__file__).with_name("checkpoint-recipes.just")
PLAIN_5072 = "^[A-Z]$|^[A-Z].{0,48}[^.]$"

pytestmark = pytest.mark.skipif(
    shutil.which("just") is None, reason="just is not on PATH"
)

ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "Test",
    "GIT_AUTHOR_EMAIL": "test@example.invalid",
    "GIT_COMMITTER_NAME": "Test",
    "GIT_COMMITTER_EMAIL": "test@example.invalid",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
}


def git(repo: Path, *args: str) -> str:
    done = subprocess.run(
        ["git", *args], cwd=repo, env=ENV, capture_output=True, text=True, check=True
    )
    return done.stdout.strip()


def just(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["just", "--justfile", str(JUSTFILE), "--working-directory", str(repo), *args],
        env=ENV,
        capture_output=True,
        text=True,
        check=False,
    )


def commit_file(repo: Path, name: str, subject: str) -> str:
    (repo / name).write_text(subject + "\n")
    git(repo, "add", name)
    git(repo, "commit", "--quiet", "-m", subject)
    return git(repo, "rev-parse", "HEAD")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    remote = tmp_path / "remote.git"
    work = tmp_path / "work"
    subprocess.run(
        ["git", "init", "--quiet", "--bare", "-b", "main", str(remote)],
        env=ENV,
        check=True,
    )
    subprocess.run(
        ["git", "init", "--quiet", "-b", "main", str(work)], env=ENV, check=True
    )
    commit_file(work, "base.txt", "chore: initial commit")
    git(work, "remote", "add", "origin", str(remote))
    git(work, "push", "--quiet", "origin", "main")
    git(work, "switch", "--quiet", "-c", "task")
    return work


def subjects(repo: Path, rev_range: str) -> list[str]:
    out = git(repo, "log", "--format=%s", rev_range)
    return out.splitlines() if out else []


def test_checkpoint_refuses_clean_tree(repo: Path) -> None:
    result = just(repo, "checkpoint", "nothing")
    assert result.returncode == 1
    assert "tree is clean" in result.stderr


def test_checkpoint_commits_everything_as_draft(repo: Path) -> None:
    (repo / "a.txt").write_text("a\n")
    result = just(repo, "checkpoint", "first step")
    assert result.returncode == 0, result.stderr
    assert subjects(repo, "main..HEAD") == ["checkpoint: first step"]
    assert git(repo, "status", "--porcelain") == ""


def test_squash_task_refuses_non_ancestor(repo: Path) -> None:
    start = git(repo, "rev-parse", "HEAD")
    git(repo, "switch", "--quiet", "--orphan", "other")
    commit_file(repo, "o.txt", "chore: unrelated root")
    result = just(repo, "squash-task", start, "feat: anything")
    assert result.returncode == 2
    assert "not an ancestor" in result.stderr


def test_squash_task_refuses_when_nothing_to_squash(repo: Path) -> None:
    head = git(repo, "rev-parse", "HEAD")
    result = just(repo, "squash-task", head, "feat: anything")
    assert result.returncode == 1
    assert "nothing after" in result.stderr


def test_squash_task_refuses_pushed_commits(repo: Path) -> None:
    start = git(repo, "rev-parse", "HEAD")
    commit_file(repo, "p.txt", "checkpoint: pushed draft")
    git(repo, "push", "--quiet", "--set-upstream", "origin", "task")
    result = just(repo, "squash-task", start, "feat: rewrite pushed history")
    assert result.returncode == 1
    assert "already on" in result.stderr


def test_squash_task_refuses_dirty_tree(repo: Path) -> None:
    start = git(repo, "rev-parse", "HEAD")
    commit_file(repo, "b.txt", "checkpoint: draft")
    (repo / "dirty.txt").write_text("x\n")
    result = just(repo, "squash-task", start, "feat: add b")
    assert result.returncode == 1
    assert "dirty" in result.stderr


def test_squash_task_refuses_bad_subject(repo: Path) -> None:
    start = git(repo, "rev-parse", "HEAD")
    commit_file(repo, "b.txt", "checkpoint: draft")
    result = just(repo, "squash-task", start, "Added b.")
    assert result.returncode == 2
    assert "does not match" in result.stderr


def test_squash_task_folds_drafts_into_one_commit(repo: Path) -> None:
    start = git(repo, "rev-parse", "HEAD")
    for name in ("b.txt", "c.txt", "d.txt"):
        commit_file(repo, name, f"checkpoint: {name}")
    result = just(repo, "squash-task", start, "feat: add b, c and d")
    assert result.returncode == 0, result.stderr
    assert subjects(repo, f"{start}..HEAD") == ["feat: add b, c and d"]
    assert sorted(git(repo, "ls-files").splitlines()) == [
        "b.txt",
        "base.txt",
        "c.txt",
        "d.txt",
    ]


@pytest.mark.parametrize(
    ("subject", "code"),
    [
        ("A", 0),
        ("A" + "b" * 49, 0),
        ("A" + "b" * 50, 2),
        ("Add a file.", 2),
        ("add a file", 2),
    ],
)
def test_plain_5072_subject_regex(repo: Path, subject: str, code: int) -> None:
    start = git(repo, "rev-parse", "HEAD")
    commit_file(repo, "b.txt", "checkpoint: draft")
    result = just(
        repo, "--set", "subject_re", PLAIN_5072, "squash-task", start, subject
    )
    assert result.returncode == code, result.stderr


def test_rollback_refuses_unknown_ref(repo: Path) -> None:
    result = just(repo, "rollback", "no-such-ref")
    assert result.returncode == 2
    assert "does not name a commit" in result.stderr


def test_rollback_saves_dirty_work_before_reset(repo: Path) -> None:
    start = git(repo, "rev-parse", "HEAD")
    commit_file(repo, "b.txt", "checkpoint: draft")
    (repo / "unsaved.txt").write_text("keep me\n")
    result = just(repo, "rollback", start)
    assert result.returncode == 0, result.stderr
    assert git(repo, "rev-parse", "HEAD") == start
    assert not (repo / "unsaved.txt").exists()
    saved = git(repo, "rev-parse", "HEAD@{1}")
    assert git(repo, "show", f"{saved}:unsaved.txt") == "keep me"


def test_push_one_refuses_on_base_branch(repo: Path) -> None:
    git(repo, "switch", "--quiet", "main")
    result = just(repo, "push-one")
    assert result.returncode == 1
    assert "pull request" in result.stderr


def test_push_one_refuses_with_draft_on_branch(repo: Path) -> None:
    commit_file(repo, "b.txt", "checkpoint: draft")
    result = just(repo, "push-one")
    assert result.returncode == 1
    assert "draft commits" in result.stderr
    assert git(repo, "ls-remote", "origin", "task") == ""


def test_push_one_pushes_one_ref(repo: Path) -> None:
    commit_file(repo, "b.txt", "feat: add b")
    git(repo, "tag", "local-only")
    result = just(repo, "push-one")
    assert result.returncode == 0, result.stderr
    assert git(repo, "ls-remote", "origin", "task") != ""
    assert git(repo, "ls-remote", "--tags", "origin") == ""
