"""Tests for check_platform.py; every CLI call is stubbed, nothing leaves the machine."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "check_platform", Path(__file__).with_name("check_platform.py")
)
check_platform = importlib.util.module_from_spec(SPEC)
sys.modules["check_platform"] = check_platform
SPEC.loader.exec_module(check_platform)


def done(
    stdout: object = "", code: int = 0, stderr: str = ""
) -> subprocess.CompletedProcess:
    text = stdout if isinstance(stdout, str) else json.dumps(stdout)
    return subprocess.CompletedProcess([], code, text, stderr)


class FakeCli:
    """Answers by the first matching fragment ("=x": last argument equals x); records calls."""

    def __init__(self, answers: list[tuple[str, subprocess.CompletedProcess]]):
        self.answers = answers
        self.calls: list[list[str]] = []

    def __call__(self, cmd: list[str]) -> subprocess.CompletedProcess:
        self.calls.append(cmd)
        joined = " ".join(cmd)
        for fragment, answer in self.answers:
            exact = fragment.startswith("=") and cmd[-1] == fragment[1:]
            if exact or (not fragment.startswith("=") and fragment in joined):
                return answer
        raise AssertionError(f"unexpected command: {joined}")


BOARDS = {
    "data": {
        "repository": {
            "projectsV2": {
                "nodes": [
                    {
                        "number": 3,
                        "title": "Roadmap",
                        "closed": False,
                        "items": {"totalCount": 12},
                    }
                ]
            }
        }
    }
}

GITHUB = [
    ("auth status", done("Logged in")),
    ("graphql", done(BOARDS)),
    (
        "repos/octo/app/rulesets",
        done([{"name": "main", "target": "branch", "enforcement": "active", "id": 1}]),
    ),
    ("protection", done("", 1, "gh: Branch not protected (HTTP 404)")),
    ("environments", done({"environments": [{"name": "production"}]})),
    (
        "contents/.github/ISSUE_TEMPLATE",
        done([{"name": "bug.yml"}, {"name": "task.yml"}]),
    ),
    (
        "contents/.github",
        done([{"name": "pull_request_template.md"}, {"name": "workflows"}]),
    ),
    ("branches?per_page", done('[{"name": "main"}][{"name": "staging"}]')),
    ("tags?per_page", done([{"name": "v1.0.0"}])),
    ("milestones", done([{"title": "1.0"}])),
    (
        "label list",
        done(
            [
                {"name": "type:task", "color": "1D76DB", "description": "Task"},
                {"name": "area:core", "color": "c5def5", "description": ""},
            ]
        ),
    ),
    ("orgs/octo", done({"login": "octo", "plan": {"name": "team"}})),
    (
        "repos/octo/app",
        done(
            {
                "owner": {"login": "octo", "type": "Organization"},
                "visibility": "public",
                "default_branch": "main",
                "allow_squash_merge": True,
                "allow_merge_commit": False,
                "allow_rebase_merge": False,
            }
        ),
    ),
]


def test_github_probe_reports_every_fact(monkeypatch, tmp_path, capsys):
    (tmp_path / ".github").mkdir()
    (tmp_path / ".github" / "labels.json").write_text("[]")
    fake = FakeCli(GITHUB)
    monkeypatch.setattr(check_platform, "run", fake)
    code = check_platform.main(
        ["--repo", "octo/app", "--platform", "github", "--path", str(tmp_path)]
    )
    out = json.loads(capsys.readouterr().out)
    assert code == 0
    assert out["platform"] == "github"
    assert out["owner_type"] == "organization"
    assert out["plan"] == "team"
    assert out["visibility"] == "public"
    assert out["default_branch"] == "main"
    assert out["branches"] == ["main", "staging"]
    assert out["environments"] == ["production"]
    assert out["protection"]["rulesets"][0]["name"] == "main"
    assert out["protection"]["branch_protection"] is None
    assert out["templates"] == {
        "issue": ["bug.yml", "task.yml"],
        "request": ["pull_request_template.md"],
        "codeowners": False,
    }
    assert [label["name"] for label in out["labels"]] == ["area:core", "type:task"]
    assert out["labels"][1]["color"] == "1d76db"
    assert out["label_files"] == [".github/labels.json"]
    assert out["boards"] == [
        {"number": 3, "title": "Roadmap", "closed": False, "items_total": 12}
    ]
    assert out["unknown"] == []
    assert all(call[0] == "gh" for call in fake.calls)


def test_private_free_repository_reports_unavailable_rulesets(
    monkeypatch, capsys, tmp_path
):
    answers = [
        ("auth status", done("ok")),
        ("graphql", done({"data": {"repository": {"projectsV2": {"nodes": []}}}})),
        (
            "rulesets",
            done(
                "",
                1,
                "gh: Upgrade to GitHub Pro or make this repository public (HTTP 403)",
            ),
        ),
        ("protection", done("", 1, "gh: Upgrade to GitHub Pro (HTTP 403)")),
        ("api user", done({"login": "alice", "plan": {"name": "free"}})),
        (
            "=repos/alice/app",
            done(
                {
                    "owner": {"login": "alice", "type": "User"},
                    "visibility": "private",
                    "default_branch": "main",
                    "allow_squash_merge": True,
                    "allow_merge_commit": True,
                    "allow_rebase_merge": True,
                }
            ),
        ),
        ("label list", done([])),
        ("repos/alice/app/", done("", 1, "gh: Not Found (HTTP 404)")),
    ]
    monkeypatch.setattr(check_platform, "run", FakeCli(answers))
    code = check_platform.main(
        ["--repo", "alice/app", "--platform", "github", "--path", str(tmp_path)]
    )
    out = json.loads(capsys.readouterr().out)
    assert code == 0
    assert out["owner_type"] == "user"
    assert out["plan"] == "free"
    assert out["visibility"] == "private"
    assert out["protection"]["rulesets"]["available"] is False
    assert out["protection"]["branch_protection"]["available"] is False


def test_gitlab_detected_from_origin_runs_no_gh(monkeypatch, capsys, tmp_path):
    answers = [
        ("remote get-url", done("git@gitlab.example.com:team/sub/app.git\n")),
        ("auth status", done("ok")),
        ("namespaces/7", done({"id": 7, "plan": "premium"})),
        (
            "/labels",
            done('[{"name": "type:bug", "color": "#D73A4A", "description": "Bug"}]'),
        ),
        (
            "protected_branches",
            done(
                [
                    {
                        "name": "main",
                        "allow_force_push": False,
                        "push_access_levels": [{"access_level": 0}],
                        "merge_access_levels": [{"access_level": 40}],
                    }
                ]
            ),
        ),
        ("repository/branches", done([{"name": "main"}])),
        ("repository/tags", done([])),
        ("environments", done([])),
        ("milestones", done([])),
        ("issue_templates", done([{"name": "Bug.md"}])),
        ("merge_request_templates", done("", 1, "glab: 404 Not Found (HTTP 404)")),
        (
            "/boards",
            done(
                [
                    {
                        "id": 5,
                        "name": "Development",
                        "lists": [{"label": {"name": "doing"}}, {"label": None}],
                    }
                ]
            ),
        ),
        (
            "projects/team%2Fsub%2Fapp",
            done(
                {
                    "namespace": {"id": 7, "kind": "group"},
                    "visibility": "internal",
                    "default_branch": "main",
                    "merge_method": "ff",
                    "squash_option": "always",
                    "only_allow_merge_if_pipeline_succeeds": True,
                }
            ),
        ),
    ]
    fake = FakeCli(answers)
    monkeypatch.setattr(check_platform, "run", fake)
    code = check_platform.main(["--path", str(tmp_path)])
    out = json.loads(capsys.readouterr().out)
    assert code == 0
    assert out["platform"] == "gitlab"
    assert out["host"] == "gitlab.example.com"
    assert out["repo"] == "team/sub/app"
    assert out["owner_type"] == "group"
    assert out["plan"] == "premium"
    assert out["labels"] == [
        {"name": "type:bug", "color": "d73a4a", "description": "Bug"}
    ]
    assert out["protection"]["protected_branches"][0]["push_access_levels"] == [0]
    assert out["templates"] == {"issue": ["Bug.md"], "request": []}
    assert out["boards"] == [{"id": 5, "name": "Development", "list_labels": ["doing"]}]
    assert not any(call[0] == "gh" for call in fake.calls)


def test_unauthenticated_cli_exits_1_without_json(monkeypatch, capsys):
    monkeypatch.setattr(
        check_platform, "run", FakeCli([("auth status", done("", 1, "not logged in"))])
    )
    code = check_platform.main(["--repo", "octo/app", "--platform", "github"])
    captured = capsys.readouterr()
    assert code == 1
    assert captured.out == ""
    assert "gh auth login" in captured.err


def test_missing_cli_names_the_tool(monkeypatch, capsys):
    def absent(cmd):
        raise FileNotFoundError(cmd[0])

    monkeypatch.setattr(check_platform, "run", absent)
    code = check_platform.main(["--repo", "team/app", "--platform", "gitlab"])
    captured = capsys.readouterr()
    assert code == 1
    assert captured.out == ""
    assert "`glab` is not installed" in captured.err


def test_unknown_host_without_a_logged_in_cli_needs_platform(monkeypatch, capsys):
    monkeypatch.setattr(
        check_platform,
        "run",
        FakeCli(
            [
                ("remote get-url", done("https://git.example.com/a/b.git")),
                ("auth status", done("", 1, "not logged in")),
            ]
        ),
    )
    assert check_platform.main([]) == 2
    err = capsys.readouterr().err
    assert "--platform" in err and "--hostname git.example.com" in err


def test_unknown_host_detected_from_logged_in_glab(monkeypatch, capsys, tmp_path):
    answers = [
        ("remote get-url", done("git@git.example.com:team/app.git\n")),
        ("glab auth status", done("ok")),
        ("namespaces/7", done({"id": 7, "plan": "free"})),
        ("/labels", done([])),
        ("protected_branches", done([])),
        ("repository/branches", done([{"name": "main"}])),
        ("repository/tags", done([])),
        ("environments", done([])),
        ("milestones", done([])),
        ("issue_templates", done([])),
        ("merge_request_templates", done([])),
        ("/boards", done([])),
        (
            "projects/team%2Fapp",
            done(
                {
                    "namespace": {"id": 7, "kind": "group"},
                    "visibility": "private",
                    "default_branch": "main",
                    "merge_method": "merge",
                    "squash_option": "default_off",
                }
            ),
        ),
    ]
    fake = FakeCli(answers)
    monkeypatch.setattr(check_platform, "run", fake)
    assert check_platform.main(["--path", str(tmp_path)]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["platform"] == "gitlab" and out["host"] == "git.example.com"
    assert not any(call[0] == "gh" for call in fake.calls)


def test_github_boards_unknown_without_project_scope(monkeypatch, capsys, tmp_path):
    scope = "Your token has not been granted the required scopes: ['read:project']"
    answers = [("graphql", done("", 1, scope)), *GITHUB]
    monkeypatch.setattr(check_platform, "run", FakeCli(answers))
    args = ["--repo", "octo/app", "--platform", "github", "--path", str(tmp_path)]
    assert check_platform.main(args) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["boards"] is None and "boards" in out["unknown"]


def test_no_output_option_writes_nothing(tmp_path):
    with pytest.raises(SystemExit) as exc:
        check_platform.main(["--output", str(tmp_path / "probe.json")])
    assert exc.value.code == 2
    assert list(tmp_path.iterdir()) == []


def test_bad_repo_is_exit_2(capsys):
    assert check_platform.main(["--repo", "nope", "--platform", "github"]) == 2


def test_repeated_runs_are_identical(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(check_platform, "run", FakeCli(GITHUB))
    args = ["--repo", "octo/app", "--platform", "github", "--path", str(tmp_path)]
    check_platform.main(args)
    first = capsys.readouterr().out
    check_platform.main(args)
    assert capsys.readouterr().out == first


def test_long_output_is_summarised_unless_full(monkeypatch, capsys, tmp_path):
    many = [
        {"name": f"label-{i:03}", "color": "ededed", "description": "x" * 80}
        for i in range(200)
    ]
    answers = [("label list", done(many)), *GITHUB]
    monkeypatch.setattr(check_platform, "run", FakeCli(answers))
    args = ["--repo", "octo/app", "--platform", "github", "--path", str(tmp_path)]
    check_platform.main(args)
    summary = json.loads(capsys.readouterr().out)
    assert summary["labels"]["count"] == 200
    assert len(summary["labels"]["first"]) == 20
    check_platform.main([*args, "--full"])
    assert len(json.loads(capsys.readouterr().out)["labels"]) == 200


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("git@github.com:octo/app.git", ("github.com", "octo/app")),
        ("https://gitlab.com/g/s/p.git", ("gitlab.com", "g/s/p")),
        ("ssh://git@gitlab.example.com:2222/g/p.git", ("gitlab.example.com", "g/p")),
    ],
)
def test_parse_remote(url, expected):
    assert check_platform.parse_remote(url) == expected


def test_repo_alone_outside_a_checkout_means_github(monkeypatch, capsys, tmp_path):
    answers = [("remote get-url", done("", 128, "not a git repository")), *GITHUB]
    monkeypatch.setattr(check_platform, "run", FakeCli(answers))
    code = check_platform.main(["--repo", "octo/app", "--path", str(tmp_path)])
    assert code == 0
    assert json.loads(capsys.readouterr().out)["platform"] == "github"
