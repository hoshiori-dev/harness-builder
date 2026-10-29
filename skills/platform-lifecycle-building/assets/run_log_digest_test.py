"""Tests for run_log_digest.py with stubbed gh and glab output."""

from __future__ import annotations

import importlib.util
import io
import json
import subprocess
import sys
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "run_log_digest", Path(__file__).with_name("run_log_digest.py")
)
run_log_digest = importlib.util.module_from_spec(SPEC)
sys.modules["run_log_digest"] = run_log_digest
SPEC.loader.exec_module(run_log_digest)


def done(
    stdout: object = "", code: int = 0, stderr: str = ""
) -> subprocess.CompletedProcess:
    text = stdout if isinstance(stdout, str) else json.dumps(stdout)
    return subprocess.CompletedProcess([], code, text, stderr)


def job(
    job_id: int, name: str, conclusion: str, failed_step: str | None = None
) -> dict:
    steps = [{"name": "checkout", "conclusion": "success"}]
    if failed_step:
        steps.append({"name": failed_step, "conclusion": "failure"})
    return {
        "databaseId": job_id,
        "name": name,
        "conclusion": conclusion,
        "steps": steps,
    }


def github_cli(run_view: dict, logs: dict[str, subprocess.CompletedProcess]):
    calls = []

    def fake(cmd):
        calls.append(cmd)
        if "--job" in cmd:
            return logs[cmd[cmd.index("--job") + 1]]
        return done(run_view)

    return fake, calls


def test_red_run_lists_failed_jobs_with_bounded_tails(monkeypatch, capsys):
    run_view = {
        "databaseId": 42,
        "status": "completed",
        "conclusion": "failure",
        "jobs": [
            job(1, "lint", "failure", "ruff"),
            job(2, "test", "failure", "pytest"),
            job(3, "docs", "success"),
        ],
    }
    long_log = "\n".join(f"line {i}" for i in range(100))
    fake, calls = github_cli(
        run_view, {"1": done(long_log), "2": done("\x1b[31mboom\x1b[0m")}
    )
    monkeypatch.setattr(run_log_digest, "run", fake)
    code = run_log_digest.main(["--repo", "octo/app", "--run-id", "42", "--tail", "40"])
    out = json.loads(capsys.readouterr().out)
    assert code == 0
    assert [j["name"] for j in out["failed_jobs"]] == ["lint", "test"]
    assert out["failed_jobs"][0]["failed_steps"] == ["ruff"]
    assert len(out["failed_jobs"][0]["log_tail"]) == 40
    assert out["failed_jobs"][0]["log_tail"][-1] == "line 99"
    assert out["failed_jobs"][1]["log_tail"] == ["boom"]
    assert all("--log-failed" in c for c in calls if "--job" in c)
    assert not any("--log" in c for c in calls if "--job" not in c)


def test_green_run_has_empty_failed_list(monkeypatch, capsys):
    run_view = {
        "databaseId": 7,
        "status": "completed",
        "conclusion": "success",
        "jobs": [job(1, "lint", "success")],
    }
    fake, _ = github_cli(run_view, {})
    monkeypatch.setattr(run_log_digest, "run", fake)
    assert run_log_digest.main(["--repo", "octo/app", "--run-id", "7"]) == 0
    assert json.loads(capsys.readouterr().out)["failed_jobs"] == []


def test_job_without_log_keeps_entry_with_error(monkeypatch, capsys):
    run_view = {
        "databaseId": 9,
        "status": "completed",
        "conclusion": "failure",
        "jobs": [job(5, "deploy", "failure")],
    }
    fake, _ = github_cli(run_view, {"5": done("", 1, "log not found")})
    monkeypatch.setattr(run_log_digest, "run", fake)
    assert run_log_digest.main(["--repo", "octo/app", "--run-id", "9"]) == 0
    entry = json.loads(capsys.readouterr().out)["failed_jobs"][0]
    assert entry["log_tail"] == [] and entry["error"] == "log not found"


def test_timed_out_and_never_started_jobs_count_as_failed(monkeypatch, capsys):
    run_view = {
        "databaseId": 11,
        "status": "completed",
        "conclusion": "failure",
        "jobs": [
            job(1, "slow", "timed_out"),
            {"databaseId": 2, "name": "boot", "conclusion": "startup_failure"},
            job(3, "after", "cancelled"),
            job(4, "lint", "success"),
            job(5, "optional", "skipped"),
        ],
    }
    fake, _ = github_cli(
        run_view,
        {
            "1": done("killed after 360 minutes"),
            "2": done("", 1, "job never started"),
            "3": done("", 1, "log not found"),
        },
    )
    monkeypatch.setattr(run_log_digest, "run", fake)
    assert run_log_digest.main(["--repo", "octo/app", "--run-id", "11"]) == 0
    jobs = json.loads(capsys.readouterr().out)["failed_jobs"]
    assert [j["name"] for j in jobs] == ["slow", "boot", "after"]
    assert jobs[0]["log_tail"] == ["killed after 360 minutes"]
    assert jobs[1]["log_tail"] == [] and jobs[1]["error"] == "job never started"
    assert jobs[1]["failed_steps"] == []


def test_long_lines_cut_unless_full(monkeypatch, capsys):
    run_view = {
        "databaseId": 3,
        "status": "completed",
        "conclusion": "failure",
        "jobs": [job(1, "x", "failure")],
    }
    fake, _ = github_cli(run_view, {"1": done("y" * 1000)})
    monkeypatch.setattr(run_log_digest, "run", fake)
    run_log_digest.main(["--repo", "octo/app", "--run-id", "3"])
    assert (
        len(json.loads(capsys.readouterr().out)["failed_jobs"][0]["log_tail"][0]) == 300
    )
    run_log_digest.main(["--repo", "octo/app", "--run-id", "3", "--full"])
    assert (
        len(json.loads(capsys.readouterr().out)["failed_jobs"][0]["log_tail"][0])
        == 1000
    )


def test_cli_failure_on_run_exits_1(monkeypatch, capsys):
    monkeypatch.setattr(run_log_digest, "run", lambda cmd: done("", 1, "run not found"))
    assert run_log_digest.main(["--repo", "octo/app", "--run-id", "1"]) == 1
    captured = capsys.readouterr()
    assert captured.out == "" and "run not found" in captured.err


def test_missing_cli_exits_1(monkeypatch, capsys):
    def absent(cmd):
        raise FileNotFoundError(cmd[0])

    monkeypatch.setattr(run_log_digest, "run", absent)
    assert (
        run_log_digest.main(["--platform", "gitlab", "--repo", "g/p", "--run-id", "1"])
        == 1
    )
    assert "`glab` is not installed" in capsys.readouterr().err


@pytest.mark.parametrize(
    "argv", [["--repo", "octo", "--run-id", "1"], ["--repo", "o/r", "--run-id", "0"]]
)
def test_bad_arguments_exit_2(argv):
    with pytest.raises(SystemExit) as exc:
        run_log_digest.main(argv)
    assert exc.value.code == 2


class FakeProcess:
    def __init__(self, stdout: str, code: int = 0, stderr: str = "") -> None:
        self.stdout = io.StringIO(stdout)
        self.stderr = io.StringIO(stderr)
        self.code = code

    def wait(self) -> int:
        return self.code


def gitlab_cli(trace: FakeProcess, streamed: list):
    def fake(cmd):
        endpoint = cmd[-1]
        if "jobs?scope" in endpoint:
            return done(
                [
                    {
                        "id": 11,
                        "name": "test",
                        "stage": "test",
                        "failure_reason": "script_failure",
                    }
                ]
            )
        return done({"id": 99, "status": "failed"})

    def fake_stream(cmd):
        streamed.append(cmd)
        return trace

    return fake, fake_stream


def test_gitlab_pipeline_digest(monkeypatch, capsys):
    streamed: list = []
    fake, fake_stream = gitlab_cli(
        FakeProcess(
            "section_start:1:build\r\nprogress 10%\rprogress 100%\nerror: failed\n"
        ),
        streamed,
    )
    monkeypatch.setattr(run_log_digest, "run", fake)
    monkeypatch.setattr(run_log_digest, "stream", fake_stream)
    assert (
        run_log_digest.main(
            ["--platform", "gitlab", "--repo", "g/s/p", "--run-id", "99"]
        )
        == 0
    )
    out = json.loads(capsys.readouterr().out)
    assert out["run_id"] == 99 and out["conclusion"] == "failed"
    assert out["failed_jobs"][0]["log_tail"] == ["", "progress 100%", "error: failed"]
    assert out["failed_jobs"][0]["failure_reason"] == "script_failure"
    assert streamed[0][-1].endswith("/jobs/11/trace")
    assert "Range: bytes=-51200" in streamed[0]


def test_gitlab_trace_is_held_to_its_tail(monkeypatch, capsys):
    streamed: list = []
    long_trace = "".join(f"line {i}\n" for i in range(10_000))
    fake, fake_stream = gitlab_cli(FakeProcess(long_trace), streamed)
    monkeypatch.setattr(run_log_digest, "run", fake)
    monkeypatch.setattr(run_log_digest, "stream", fake_stream)
    run_log_digest.main(
        ["--platform", "gitlab", "--repo", "g/p", "--run-id", "99", "--tail", "5"]
    )
    tail = json.loads(capsys.readouterr().out)["failed_jobs"][0]["log_tail"]
    assert tail == [f"line {i}" for i in range(9995, 10_000)]


def test_gitlab_job_without_trace_keeps_entry(monkeypatch, capsys):
    streamed: list = []
    fake, fake_stream = gitlab_cli(FakeProcess("", 1, "404 Not Found"), streamed)
    monkeypatch.setattr(run_log_digest, "run", fake)
    monkeypatch.setattr(run_log_digest, "stream", fake_stream)
    run_log_digest.main(["--platform", "gitlab", "--repo", "g/p", "--run-id", "99"])
    entry = json.loads(capsys.readouterr().out)["failed_jobs"][0]
    assert entry["log_tail"] == [] and entry["error"] == "404 Not Found"
