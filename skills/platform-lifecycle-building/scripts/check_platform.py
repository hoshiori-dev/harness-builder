#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Probe a GitHub or GitLab repository read-only and print one JSON object.

Reads, through the installed and authenticated `gh` or `glab`, the facts a
platform lifecycle build needs before any question: owner type, plan,
visibility, default branch, allowed merge methods, branches, tags,
environments, open milestones, labels, boards (GitHub Projects or GitLab
issue boards), rulesets or protected branches, and the issue and pull or
merge request templates present. It also lists the label definition files
in the local working tree. Nothing is written, locally or remotely: there
is no option that writes a file.

Usage:
  python3 check_platform.py                      # platform and repo from origin
  python3 check_platform.py --repo OWNER/REPO --platform github
  python3 check_platform.py --platform gitlab --repo GROUP/PROJECT \\
      --hostname git.example.com
  python3 check_platform.py --help

A fact the CLI cannot read with the caller's rights (an organisation's plan,
for instance) is null and named in "unknown"; it is never guessed from
another fact. GitHub boards are null and listed in "unknown" when the token
lacks the read:project scope. Output above 10,000 characters lists only the
first 20 entries of each long list unless --full is given.

The platform comes from --platform, else from the remote host's name
(containing "github" or "gitlab"), else from whichever of `glab` and `gh`
is logged in to that host, `glab` asked first.

Exit codes:
  0  probe complete (unknown facts are listed, not fatal)
  1  the CLI is missing, not logged in, or failed
  2  bad arguments, or no repository or platform could be determined
     (re-run with --platform and --hostname, or ask which platform it is)
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path

SUMMARY_LIMIT = 10_000
SUMMARY_ITEMS = 20
LABEL_FILE_RE = re.compile(r"^labels?([._-][\w-]+)?\.(json|ya?ml)$", re.IGNORECASE)
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "build", "target"}
NOT_FOUND = ("HTTP 404", "404 Not Found", "Not Found")
FORBIDDEN = ("HTTP 403", "403 Forbidden", "Upgrade to GitHub Pro")
MISSING_SCOPE = ("INSUFFICIENT_SCOPES", "required scopes", "read:project")
BOARDS_QUERY = (
    "query($owner: String!, $name: String!) { repository(owner: $owner, name: $name)"
    " { projectsV2(first: 100) { nodes { number title closed"
    " items { totalCount } } } } }"
)


class ProbeError(Exception):
    """A CLI failure that ends the probe with exit 1."""


class UsageError(Exception):
    """Missing or contradictory input that ends the probe with exit 2."""


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    """Run one command; the single seam tests replace."""
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def call(cmd: list[str]) -> subprocess.CompletedProcess:
    try:
        return run(cmd)
    except FileNotFoundError as exc:
        tool = cmd[0]
        name = "GitHub CLI" if tool == "gh" else "GitLab CLI"
        raise ProbeError(
            f"`{tool}` is not installed; install the {name}, then run "
            f"`{tool} auth login` and re-run this probe."
        ) from exc


def decode_pages(text: str) -> object:
    """Parse one JSON value, or concatenated JSON arrays from a paginated call."""
    text = text.strip()
    if not text:
        return None
    decoder = json.JSONDecoder()
    values, index = [], 0
    while index < len(text):
        value, index = decoder.raw_decode(text, index)
        values.append(value)
        while index < len(text) and text[index].isspace():
            index += 1
    if len(values) == 1:
        return values[0]
    merged: list = []
    for value in values:
        merged.extend(value if isinstance(value, list) else [value])
    return merged


def api(cmd: list[str], absent: object = "fail") -> object:
    """Run a read-only API call and return its JSON.

    `absent` is returned for a 404, and {"available": False, ...} for a 403;
    with the default "fail", both end the probe like any other failure.
    """
    result = call(cmd)
    if result.returncode == 0:
        try:
            return decode_pages(result.stdout)
        except ValueError as exc:
            raise ProbeError(f"`{' '.join(cmd)}` did not print JSON ({exc}).") from exc
    message = (result.stderr or result.stdout).strip()
    if absent != "fail" and any(token in message for token in NOT_FOUND):
        return absent
    if absent != "fail" and any(token in message for token in FORBIDDEN):
        return {"available": False, "message": message.splitlines()[0]}
    raise ProbeError(f"`{' '.join(cmd)}` exited {result.returncode}: {message}")


def parse_remote(url: str) -> tuple[str, str]:
    """(host, path) from an ssh or https remote URL."""
    url = url.strip()
    match = re.match(r"^[\w.-]+@([^:/]+):(.+)$", url)
    if match:
        host, path = match.group(1), match.group(2)
    else:
        parsed = urllib.parse.urlparse(url)
        if not parsed.hostname:
            raise UsageError(
                f"cannot read a host from remote URL {url!r}; pass --repo."
            )
        host, path = parsed.hostname, parsed.path
    path = path.strip("/")
    if path.endswith(".git"):
        path = path[:-4]
    return host, path


def origin(path: Path) -> tuple[str, str]:
    try:
        result = run(["git", "-C", str(path), "remote", "get-url", "origin"])
    except FileNotFoundError as exc:
        raise UsageError("`git` is not installed; pass --repo and --platform.") from exc
    if result.returncode != 0:
        raise UsageError(
            "no `origin` remote in this working tree; pass --repo and --platform."
        )
    return parse_remote(result.stdout)


def logged_in(tool: str, host: str) -> bool:
    try:
        result = run([tool, "auth", "status", "--hostname", host])
    except FileNotFoundError:
        return False
    return result.returncode == 0


def detect_platform(host: str) -> str:
    """The platform from the host name, else from the CLI logged in to that host."""
    if "github" in host:
        return "github"
    if "gitlab" in host:
        return "gitlab"
    if logged_in("glab", host):
        return "gitlab"
    if logged_in("gh", host):
        return "github"
    raise UsageError(
        f"cannot tell the platform from host {host!r} and neither `glab` nor `gh` "
        f"is logged in to it; pass --platform github or gitlab with --hostname {host}."
    )


def label_files(path: Path) -> list[str]:
    """Label definition files in the working tree, relative and sorted."""
    found = []
    for candidate in sorted(path.rglob("*")):
        rel = candidate.relative_to(path)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if candidate.is_file() and LABEL_FILE_RE.match(candidate.name):
            found.append(rel.as_posix())
    return found


def names(items: object, key: str = "name") -> list[str]:
    if not isinstance(items, list):
        return []
    return sorted(str(item[key]) for item in items if isinstance(item, dict))


def github_boards(gh_api: list[str], repo: str) -> list | None:
    """Projects (v2) linked to the repository; None when the token cannot read them."""
    owner, name = repo.split("/")
    cmd = [*gh_api, "graphql", "-f", f"query={BOARDS_QUERY}"]
    cmd += ["-F", f"owner={owner}", "-F", f"name={name}"]
    result = call(cmd)
    message = (result.stderr or result.stdout).strip()
    if result.returncode != 0 and any(token in message for token in MISSING_SCOPE):
        return None
    if result.returncode != 0:
        raise ProbeError(
            f"`gh api graphql` (projectsV2) exited {result.returncode}: {message}"
        )
    try:
        data = json.loads(result.stdout)
    except ValueError as exc:
        raise ProbeError(f"`gh api graphql` did not print JSON ({exc}).") from exc
    if data.get("errors"):
        if any(token in json.dumps(data["errors"]) for token in MISSING_SCOPE):
            return None
        raise ProbeError(f"`gh api graphql` (projectsV2) failed: {data['errors']}")
    repository = (data.get("data") or {}).get("repository") or {}
    nodes = (repository.get("projectsV2") or {}).get("nodes") or []
    return [
        {
            "number": node.get("number"),
            "title": node.get("title"),
            "closed": node.get("closed"),
            "items_total": (node.get("items") or {}).get("totalCount"),
        }
        for node in nodes
        if isinstance(node, dict)
    ]


def probe_github(repo: str, host: str) -> dict:
    hostflag = [] if host == "github.com" else ["--hostname", host]
    status = call(["gh", "auth", "status", "--hostname", host])
    if status.returncode != 0:
        raise ProbeError(
            f"`gh` is not logged in to {host}; run `gh auth login --hostname {host}`."
        )
    gh_api = ["gh", "api", *hostflag]
    unknown: list[str] = []
    meta = api([*gh_api, f"repos/{repo}"])
    if not isinstance(meta, dict):
        raise ProbeError(f"`gh api repos/{repo}` did not print a repository object.")
    owner = meta.get("owner", {}).get("login", "")
    owner_type = meta.get("owner", {}).get("type")
    plan = None
    if owner_type == "Organization":
        org = api([*gh_api, f"orgs/{owner}"], absent=None)
        if isinstance(org, dict) and isinstance(org.get("plan"), dict):
            plan = org["plan"].get("name")
    else:
        user = api([*gh_api, "user"], absent=None)
        if isinstance(user, dict) and user.get("login") == owner:
            plan = (user.get("plan") or {}).get("name")
    if plan is None:
        unknown.append("plan")
    default = meta.get("default_branch")
    merge = {
        "squash": meta.get("allow_squash_merge"),
        "merge": meta.get("allow_merge_commit"),
        "rebase": meta.get("allow_rebase_merge"),
    }
    if None in merge.values():
        unknown.append("merge_methods")
    slug = repo if host == "github.com" else f"{host}/{repo}"
    labels = api(
        [
            "gh",
            "label",
            "list",
            "-R",
            slug,
            "--json",
            "name,color,description",
            "--limit",
            "1000",
        ]
    )
    rulesets = api([*gh_api, f"repos/{repo}/rulesets"], absent=[])
    protection = api(
        [*gh_api, f"repos/{repo}/branches/{default}/protection"], absent=None
    )
    environments = api([*gh_api, f"repos/{repo}/environments"], absent={})
    github_dir = api([*gh_api, f"repos/{repo}/contents/.github"], absent=[])
    issue_dir = api(
        [*gh_api, f"repos/{repo}/contents/.github/ISSUE_TEMPLATE"], absent=[]
    )
    github_names = names(github_dir)
    boards = github_boards(gh_api, repo)
    if boards is None:
        unknown.append("boards")
    return {
        "platform": "github",
        "host": host,
        "repo": repo,
        "owner_type": {"Organization": "organization", "User": "user"}.get(
            owner_type, owner_type
        ),
        "plan": plan,
        "visibility": meta.get("visibility"),
        "default_branch": default,
        "merge_methods": merge,
        "branches": names(
            api(
                [*gh_api, "--paginate", f"repos/{repo}/branches?per_page=100"],
                absent=[],
            )
        ),
        "tags": names(api([*gh_api, f"repos/{repo}/tags?per_page=100"], absent=[])),
        "environments": names(
            environments.get("environments", [])
            if isinstance(environments, dict)
            else []
        ),
        "milestones": names(
            api(
                [*gh_api, f"repos/{repo}/milestones?state=open&per_page=100"], absent=[]
            ),
            key="title",
        ),
        "labels": sorted(
            (
                {
                    "name": item["name"],
                    "color": str(item.get("color", "")).lower(),
                    "description": item.get("description") or "",
                }
                for item in (labels if isinstance(labels, list) else [])
            ),
            key=lambda item: item["name"].lower(),
        ),
        "protection": {
            "rulesets": rulesets
            if isinstance(rulesets, dict)
            else [
                {
                    "name": item.get("name"),
                    "target": item.get("target"),
                    "enforcement": item.get("enforcement"),
                }
                for item in rulesets
            ],
            "branch_protection": protection,
        },
        "boards": boards,
        "templates": {
            "issue": names(issue_dir),
            "request": [
                n for n in github_names if n.lower().startswith("pull_request_template")
            ],
            "codeowners": "CODEOWNERS" in github_names,
        },
        "unknown": unknown,
    }


def probe_gitlab(repo: str, host: str) -> dict:
    status = call(["glab", "auth", "status", "--hostname", host])
    if status.returncode != 0:
        raise ProbeError(
            f"`glab` is not logged in to {host}; run `glab auth login --hostname {host}`."
        )
    glab_api = ["glab", "api", "--hostname", host]
    project = urllib.parse.quote(repo, safe="")
    base = f"projects/{project}"
    unknown: list[str] = []
    meta = api([*glab_api, base])
    if not isinstance(meta, dict):
        raise ProbeError(f"`glab api {base}` did not print a project object.")
    namespace = meta.get("namespace") or {}
    plan = None
    if namespace.get("id") is not None:
        info = api([*glab_api, f"namespaces/{namespace['id']}"], absent=None)
        if isinstance(info, dict):
            plan = info.get("plan")
    if plan is None:
        unknown.append("plan")
    default = meta.get("default_branch")
    squash = meta.get("squash_option")
    method = meta.get("merge_method")
    if squash is None or method is None:
        unknown.append("merge_methods")
    ref = urllib.parse.quote(str(default or ""), safe="")
    labels = api([*glab_api, "--paginate", f"{base}/labels?per_page=100"])
    protected = api([*glab_api, f"{base}/protected_branches?per_page=100"], absent=[])
    boards = api([*glab_api, f"{base}/boards?per_page=100"], absent=[])
    return {
        "platform": "gitlab",
        "host": host,
        "repo": repo,
        "owner_type": {"group": "group", "user": "user"}.get(
            namespace.get("kind"), namespace.get("kind")
        ),
        "plan": plan,
        "visibility": meta.get("visibility"),
        "default_branch": default,
        "merge_methods": {"merge_method": method, "squash_option": squash},
        "branches": names(
            api(
                [*glab_api, "--paginate", f"{base}/repository/branches?per_page=100"],
                absent=[],
            )
        ),
        "tags": names(
            api([*glab_api, f"{base}/repository/tags?per_page=100"], absent=[])
        ),
        "environments": names(
            api([*glab_api, f"{base}/environments?per_page=100"], absent=[])
        ),
        "milestones": names(
            api([*glab_api, f"{base}/milestones?state=active&per_page=100"], absent=[]),
            key="title",
        ),
        "labels": sorted(
            (
                {
                    "name": item["name"],
                    "color": str(item.get("color", "")).lstrip("#").lower(),
                    "description": item.get("description") or "",
                }
                for item in (labels if isinstance(labels, list) else [])
            ),
            key=lambda item: item["name"].lower(),
        ),
        "protection": {
            "protected_branches": protected
            if isinstance(protected, dict)
            else [
                {
                    "name": item.get("name"),
                    "allow_force_push": item.get("allow_force_push"),
                    "push_access_levels": [
                        level.get("access_level")
                        for level in item.get("push_access_levels", [])
                    ],
                    "merge_access_levels": [
                        level.get("access_level")
                        for level in item.get("merge_access_levels", [])
                    ],
                }
                for item in protected
            ],
            "pipeline_must_succeed": meta.get("only_allow_merge_if_pipeline_succeeds"),
        },
        "boards": boards
        if isinstance(boards, dict)
        else [
            {
                "id": board.get("id"),
                "name": board.get("name"),
                "list_labels": [
                    (item.get("label") or {}).get("name")
                    for item in board.get("lists") or []
                    if item.get("label")
                ],
            }
            for board in boards
        ],
        "templates": {
            "issue": names(
                api(
                    [
                        *glab_api,
                        f"{base}/repository/tree?path=.gitlab/issue_templates&ref={ref}",
                    ],
                    absent=[],
                )
            ),
            "request": names(
                api(
                    [
                        *glab_api,
                        f"{base}/repository/tree?path=.gitlab/merge_request_templates&ref={ref}",
                    ],
                    absent=[],
                )
            ),
        },
        "unknown": unknown,
    }


def summarise(report: dict) -> dict:
    out = dict(report)
    for key, value in report.items():
        if isinstance(value, list) and len(value) > SUMMARY_ITEMS:
            out[key] = {"count": len(value), "first": value[:SUMMARY_ITEMS]}
    out["summarised"] = True
    return out


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only probe of a GitHub or GitLab repository; prints one JSON object.",
        epilog="Example: python3 check_platform.py --repo octo/hello --platform github",
    )
    parser.add_argument(
        "--repo", help="OWNER/REPO or GROUP/PROJECT (default: from origin)"
    )
    parser.add_argument(
        "--platform", choices=["github", "gitlab"], help="default: from the remote host"
    )
    parser.add_argument(
        "--hostname", help="host for GitHub Enterprise or self-managed GitLab"
    )
    parser.add_argument(
        "--path", default=".", help="working tree to scan for label files (default: .)"
    )
    parser.add_argument(
        "--full", action="store_true", help="never summarise long lists"
    )
    return parser


def resolve(args: argparse.Namespace) -> tuple[str, str, str]:
    """(platform, host, repo) from the flags, reading origin only for what is missing."""
    host, repo, platform = args.hostname, args.repo, args.platform
    if not repo:
        host_seen, repo = origin(Path(args.path))
        host = host or host_seen
    elif not platform and not host:
        # --repo alone means github.com, as for gh -R, unless origin is that repo.
        try:
            host_seen, repo_seen = origin(Path(args.path))
        except UsageError:
            host_seen, repo_seen = "github.com", repo
        host = host_seen if repo_seen == repo else "github.com"
    platform = platform or detect_platform(host)
    host = host or ("github.com" if platform == "github" else "gitlab.com")
    parts = repo.split("/")
    if platform == "github" and (len(parts) != 2 or not all(parts)):
        raise UsageError(f"--repo must be OWNER/REPO, got {repo!r}.")
    if platform == "gitlab" and (len(parts) < 2 or not all(parts)):
        raise UsageError(f"--repo must be GROUP[/SUBGROUP]/PROJECT, got {repo!r}.")
    return platform, host, repo


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        platform, host, repo = resolve(args)
    except UsageError as exc:
        print(f"check_platform: error: {exc}", file=sys.stderr)
        return 2
    try:
        probe = probe_github if platform == "github" else probe_gitlab
        report = probe(repo, host)
    except ProbeError as exc:
        print(f"check_platform: error: {exc}", file=sys.stderr)
        return 1
    report["label_files"] = label_files(Path(args.path))
    for fact in report["unknown"]:
        print(
            f"check_platform: note: {fact} could not be read; ask the user.",
            file=sys.stderr,
        )
    text = json.dumps(report, indent=2, sort_keys=True)
    if not args.full and len(text) > SUMMARY_LIMIT:
        text = json.dumps(summarise(report), indent=2, sort_keys=True)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
