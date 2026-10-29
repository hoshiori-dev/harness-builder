#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Digest one failed CI run or pipeline into a single JSON object.

Reads a GitHub Actions run through `gh`, or a GitLab pipeline through
`glab`, and prints its id, status, conclusion, and each failed job with its
failed steps and the last N lines of its log. Full logs never reach stdout:
on GitHub only the failed steps' log is fetched; on GitLab the job trace is
requested with a Range header for its last bytes only, and when the server
ignores the range the trace is streamed with only the last N lines held, so
neither memory nor stdout ever carries the whole log.

Usage:
  python3 scripts/run_log_digest.py --repo OWNER/REPO --run-id 123456 --tail 40
  python3 scripts/run_log_digest.py --platform gitlab --repo GROUP/PROJECT \\
      --run-id 987 --hostname gitlab.example.com
  python3 scripts/run_log_digest.py --help

Output:
  {"run_id": ..., "status": ..., "conclusion": ...,
   "failed_jobs": [{"name": ..., "job_id": ..., "failed_steps": [...],
                    "log_tail": [...], "error": null}]}

A job counts as failed when its conclusion is anything but success,
skipped, or neutral (failure, timed_out, startup_failure, cancelled,
action_required). A failed job whose log the CLI cannot return (one that
never started) keeps an empty log_tail and carries the CLI's message in "error". Log lines longer
than 300 characters are cut unless --full is given.

Exit codes:
  0  digest produced (a green run digests to an empty failed_jobs list)
  1  the CLI is missing or failed on the run
  2  bad arguments
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.parse
from collections import deque

ANSI = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")
GITLAB_SECTION = re.compile(r"section_(?:start|end):\d+:[\w.-]+(?:\[[^\]]*\])?")
GITLAB_DONE = {"success", "failed", "canceled", "skipped", "manual"}
GITHUB_NOT_FAILED = {"success", "skipped", "neutral"}
LINE_LIMIT = 300
RANGE_BYTES_PER_LINE = 1024


class DigestError(Exception):
    """A CLI failure on the run itself; ends the script with exit 1."""


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    """Run one command; the single seam tests replace."""
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def stream(cmd: list[str]) -> subprocess.Popen:
    """Start one command whose stdout is read line by line; the streaming seam."""
    return subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )


def call_tail(cmd: list[str], lines: int) -> subprocess.CompletedProcess:
    """Run a command, holding only the last `lines` lines of its stdout."""
    try:
        proc = stream(cmd)
    except FileNotFoundError as exc:
        raise DigestError(
            f"`{cmd[0]}` is not installed; install it and run `{cmd[0]} auth login`."
        ) from exc
    kept: deque[str] = deque(proc.stdout, maxlen=lines)
    stderr = proc.stderr.read()
    code = proc.wait()
    return subprocess.CompletedProcess(cmd, code, "".join(kept), stderr)


def call(cmd: list[str]) -> subprocess.CompletedProcess:
    try:
        return run(cmd)
    except FileNotFoundError as exc:
        raise DigestError(
            f"`{cmd[0]}` is not installed; install it and run `{cmd[0]} auth login`."
        ) from exc


def read_json(cmd: list[str]) -> object:
    result = call(cmd)
    if result.returncode != 0:
        raise DigestError(
            f"`{' '.join(cmd)}` exited {result.returncode}: {result.stderr.strip()}"
        )
    try:
        return json.loads(result.stdout)
    except ValueError as exc:
        raise DigestError(f"`{' '.join(cmd)}` did not print JSON ({exc}).") from exc


def tail(text: str, lines: int, full: bool) -> list[str]:
    cleaned = GITLAB_SECTION.sub("", ANSI.sub("", text))
    kept = [
        line.rstrip("\r").rsplit("\r", 1)[-1].rstrip()
        for line in cleaned.rstrip("\n").split("\n")
    ]
    kept = kept[-lines:]
    return kept if full else [line[:LINE_LIMIT] for line in kept]


def log_entry(result: subprocess.CompletedProcess, lines: int, full: bool) -> dict:
    if result.returncode == 0 and result.stdout.strip():
        return {"log_tail": tail(result.stdout, lines, full), "error": None}
    message = result.stderr.strip() or "the CLI returned no log for this job"
    return {"log_tail": [], "error": message}


def digest_github(args: argparse.Namespace) -> dict:
    repo = args.repo if not args.hostname else f"{args.hostname}/{args.repo}"
    run_data = read_json(
        ["gh", "run", "view", str(args.run_id), "-R", repo]
        + ["--json", "databaseId,status,conclusion,jobs"]
    )
    if not isinstance(run_data, dict) or not isinstance(run_data.get("jobs"), list):
        raise DigestError("`gh run view --json` did not print a run with jobs.")
    failed = [
        job
        for job in run_data["jobs"]
        if job.get("conclusion") and job["conclusion"] not in GITHUB_NOT_FAILED
    ]
    jobs = []
    for job in failed:
        log = call(
            ["gh", "run", "view", "-R", repo, "--job", str(job["databaseId"])]
            + ["--log-failed"]
        )
        steps = [
            step["name"]
            for step in job.get("steps", [])
            if step.get("conclusion") and step["conclusion"] not in GITHUB_NOT_FAILED
        ]
        jobs.append(
            {"name": job["name"], "job_id": job["databaseId"], "failed_steps": steps}
            | log_entry(log, args.tail, args.full)
        )
    return {
        "run_id": run_data.get("databaseId"),
        "status": run_data.get("status"),
        "conclusion": run_data.get("conclusion"),
        "failed_jobs": jobs,
    }


def digest_gitlab(args: argparse.Namespace) -> dict:
    base = ["glab", "api"] + (["--hostname", args.hostname] if args.hostname else [])
    project = f"projects/{urllib.parse.quote(args.repo, safe='')}"
    pipeline = read_json([*base, f"{project}/pipelines/{args.run_id}"])
    failed = read_json(
        [*base, f"{project}/pipelines/{args.run_id}/jobs?scope[]=failed&per_page=100"]
    )
    if not isinstance(pipeline, dict) or not isinstance(failed, list):
        raise DigestError("`glab api` did not print a pipeline and its job list.")
    jobs = []
    for job in failed:
        span = f"Range: bytes=-{args.tail * RANGE_BYTES_PER_LINE}"
        log = call_tail(
            [*base, "--header", span, f"{project}/jobs/{job['id']}/trace"],
            args.tail,
        )
        jobs.append(
            {
                "name": job["name"],
                "job_id": job["id"],
                "stage": job.get("stage"),
                "failure_reason": job.get("failure_reason"),
                "failed_steps": [],
            }
            | log_entry(log, args.tail, args.full)
        )
    status = pipeline.get("status")
    return {
        "run_id": pipeline.get("id"),
        "status": status,
        "conclusion": status if status in GITLAB_DONE else None,
        "failed_jobs": jobs,
    }


def positive(value: str) -> int:
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError(f"{value} is not a positive integer")
    return number


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Digest one failed CI run or pipeline into a single JSON object.",
        epilog="Example: python3 scripts/run_log_digest.py --repo octo/app --run-id 123 --tail 40",
    )
    parser.add_argument("--repo", required=True, help="OWNER/REPO or GROUP/PROJECT")
    parser.add_argument(
        "--run-id", required=True, type=positive, help="run or pipeline id"
    )
    parser.add_argument(
        "--tail",
        type=positive,
        default=50,
        help="log lines kept per failed job (default 50)",
    )
    parser.add_argument("--platform", choices=["github", "gitlab"], default="github")
    parser.add_argument(
        "--hostname", help="GitHub Enterprise or self-managed GitLab host"
    )
    parser.add_argument(
        "--full", action="store_true", help="keep log lines longer than 300 characters"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    parts = args.repo.split("/")
    if (
        len(parts) < 2
        or not all(parts)
        or (args.platform == "github" and len(parts) != 2)
    ):
        parser.error(f"--repo must be OWNER/REPO or GROUP/PROJECT, got {args.repo!r}")
    try:
        digest = (digest_github if args.platform == "github" else digest_gitlab)(args)
    except DigestError as exc:
        print(f"run_log_digest: error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(digest, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
