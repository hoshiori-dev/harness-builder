#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Sync a repository's labels to the committed label file.

Reads a JSON array of {"name", "color", "description"} objects, compares it
with the repository's labels through `gh` (GitHub) or `glab` (GitLab), and
prints the plan as JSON on stdout: create, update, skip, and, with --prune,
delete. Dry-run by default; nothing changes without --apply. Running it
again after an apply prints a plan of skips only.

Usage:
  python3 scripts/sync_labels.py --file .github/labels.json --repo OWNER/REPO
  python3 scripts/sync_labels.py --file .github/labels.json --repo OWNER/REPO --apply
  python3 scripts/sync_labels.py --platform gitlab --hostname gitlab.example.com \\
      --file .gitlab/labels.json --repo GROUP/PROJECT --apply
  python3 scripts/sync_labels.py --help

--prune deletes labels the file does not list. Deleting a label strips it
from every issue and pull or merge request carrying it, so prune only when
the file is the one complete label definition.

Exit codes:
  0  plan printed, or applied cleanly
  1  invalid label file, or the CLI is missing or failed
  2  bad arguments
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.parse

HEX_COLOR = re.compile(r"^[0-9a-f]{6}$")
# A listing at this size may be truncated, which would turn existing labels
# into creates; the script stops instead.
LABEL_LIMIT = 1000


class SyncError(Exception):
    """An invalid file or a CLI failure; ends the script with exit 1."""


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    """Run one command; the single seam tests replace."""
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def cli(cmd: list[str]) -> str:
    try:
        result = run(cmd)
    except FileNotFoundError as exc:
        raise SyncError(
            f"`{cmd[0]}` is not installed; install it and run `{cmd[0]} auth login`."
        ) from exc
    if result.returncode != 0:
        raise SyncError(
            f"`{' '.join(cmd)}` exited {result.returncode}: {result.stderr.strip()}"
        )
    return result.stdout


def load_file(path: str) -> list[dict]:
    """The label file as normalised labels; any defect names the file and index."""
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError) as exc:
        raise SyncError(f"cannot read {path} as JSON: {exc}") from exc
    if not isinstance(data, list) or not data:
        raise SyncError(f"{path} must be a non-empty JSON array of label objects.")
    labels, seen = [], set()
    for index, item in enumerate(data):
        where = f"{path}[{index}]"
        if not isinstance(item, dict) or not str(item.get("name", "")).strip():
            raise SyncError(f"{where}: needs a non-empty string 'name'.")
        name = str(item["name"]).strip()
        color = str(item.get("color", "")).strip().lstrip("#").lower()
        if not HEX_COLOR.match(color):
            raise SyncError(
                f"{where} ({name!r}): color {item.get('color')!r} is not six hex "
                'digits; write it like "d73a4a", without "#".'
            )
        description = item.get("description", "")
        if not isinstance(description, str):
            raise SyncError(f"{where} ({name!r}): description must be a string.")
        if name.lower() in seen:
            raise SyncError(f"{where}: duplicate label name {name!r}; keep one row.")
        seen.add(name.lower())
        labels.append(
            {"name": name, "color": color, "description": description.strip()}
        )
    return labels


def decode_pages(text: str) -> list:
    """One JSON array, or concatenated arrays from a paginated call."""
    decoder = json.JSONDecoder()
    text, index, merged = text.strip(), 0, []
    while index < len(text):
        value, index = decoder.raw_decode(text, index)
        if not isinstance(value, list):
            raise ValueError("expected a JSON array of labels")
        merged.extend(value)
        while index < len(text) and text[index].isspace():
            index += 1
    return merged


class GitHub:
    def __init__(self, repo: str, hostname: str | None):
        self.repo = repo if not hostname else f"{hostname}/{repo}"

    def list(self) -> list[dict]:
        out = cli(
            ["gh", "label", "list", "-R", self.repo, "--json", "name,color,description"]
            + ["--limit", str(LABEL_LIMIT)]
        )
        return decode_pages(out)

    def create(self, label: dict) -> None:
        cli(
            ["gh", "label", "create", label["name"], "-R", self.repo]
            + ["--color", label["color"], "--description", label["description"]]
        )

    def update(self, label: dict) -> None:
        cli(
            ["gh", "label", "edit", label["name"], "-R", self.repo]
            + ["--color", label["color"], "--description", label["description"]]
        )

    def delete(self, name: str) -> None:
        cli(["gh", "label", "delete", name, "-R", self.repo, "--yes"])


class GitLab:
    def __init__(self, repo: str, hostname: str | None):
        self.base = ["glab", "api"] + (["--hostname", hostname] if hostname else [])
        self.project = f"projects/{urllib.parse.quote(repo, safe='')}/labels"

    def label(self, name: str) -> str:
        return f"{self.project}/{urllib.parse.quote(name, safe='')}"

    def list(self) -> list[dict]:
        out = cli([*self.base, "--paginate", f"{self.project}?per_page=100"])
        return decode_pages(out)

    def create(self, label: dict) -> None:
        cli(
            [*self.base, "-X", "POST", self.project, "-f", f"name={label['name']}"]
            + [
                "-f",
                f"color=#{label['color']}",
                "-f",
                f"description={label['description']}",
            ]
        )

    def update(self, label: dict) -> None:
        cli(
            [*self.base, "-X", "PUT", self.label(label["name"])]
            + [
                "-f",
                f"color=#{label['color']}",
                "-f",
                f"description={label['description']}",
            ]
        )

    def delete(self, name: str) -> None:
        cli([*self.base, "-X", "DELETE", self.label(name)])


def current_labels(client: GitHub | GitLab) -> dict[str, dict]:
    try:
        entries = client.list()
    except ValueError as exc:
        raise SyncError(f"the label listing was not a JSON array ({exc}).") from exc
    if len(entries) >= LABEL_LIMIT:
        raise SyncError(
            f"the listing returned {len(entries)} labels, at the {LABEL_LIMIT} limit; "
            "raise LABEL_LIMIT so no existing label is planned as a create."
        )
    return {
        str(entry["name"]).lower(): {
            "name": entry["name"],
            "color": str(entry.get("color", "")).lstrip("#").lower(),
            "description": (entry.get("description") or "").strip(),
        }
        for entry in entries
    }


def build_plan(desired: list[dict], current: dict[str, dict], prune: bool) -> dict:
    create, update, skip = [], [], []
    for label in desired:
        existing = current.get(label["name"].lower())
        if existing is None:
            create.append(label)
        elif (existing["color"], existing["description"]) != (
            label["color"],
            label["description"],
        ):
            update.append(label)
        else:
            skip.append(label["name"])
    wanted = {label["name"].lower() for label in desired}
    extra = sorted(entry["name"] for key, entry in current.items() if key not in wanted)
    return {
        "create": create,
        "update": update,
        "skip": skip,
        "delete": extra if prune else [],
        "not_in_file": [] if prune else extra,
    }


def apply_plan(client: GitHub | GitLab, plan: dict) -> None:
    for label in plan["create"]:
        print(f"create: {label['name']}", file=sys.stderr)
        client.create(label)
    for label in plan["update"]:
        print(f"update: {label['name']}", file=sys.stderr)
        client.update(label)
    for name in plan["delete"]:
        print(f"delete: {name}", file=sys.stderr)
        client.delete(name)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Plan (default) or apply the label file against the repository.",
        epilog="Example: python3 scripts/sync_labels.py --file .github/labels.json "
        "--repo octo/app --apply",
    )
    parser.add_argument("--file", required=True, help="the committed JSON label file")
    parser.add_argument("--repo", required=True, help="OWNER/REPO or GROUP/PROJECT")
    parser.add_argument("--platform", choices=["github", "gitlab"], default="github")
    parser.add_argument(
        "--hostname", help="GitHub Enterprise or self-managed GitLab host"
    )
    parser.add_argument("--apply", action="store_true", help="execute the plan")
    parser.add_argument(
        "--prune",
        action="store_true",
        help="also plan deleting labels absent from the file",
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
    client = (GitHub if args.platform == "github" else GitLab)(args.repo, args.hostname)
    try:
        desired = load_file(args.file)
        plan = build_plan(desired, current_labels(client), args.prune)
        if args.apply:
            apply_plan(client, plan)
    except SyncError as exc:
        print(f"sync_labels: error: {exc}", file=sys.stderr)
        return 1
    report = {
        "repo": args.repo,
        "platform": args.platform,
        "applied": args.apply,
        **plan,
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
