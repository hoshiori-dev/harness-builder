#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Resolve, check, and archive the OpenSpec changes a pull or merge request touches.

Run by the person who archives, on the request's branch, from this skill's
directory; the CI jobs call the project's own copy, which has no archive.

Commands:
  related  the related changes with their state and task counts
  status   the related changes with state, documents, and task progress
  check    strict validation, then the archive verdict
  archive  archive every related change through the OpenSpec CLI, or none

A request's *related changes* are the directories under the changes
directory (default openspec/changes) whose files the diff --base...--head
touches; an archive directory counts under its change name without the
YYYY-MM-DD- prefix. check and archive need the OpenSpec CLI.

Exit codes: 0 success; 1 a finding, a refusal, or a failure; 2 bad arguments.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

OUTPUT_LIMIT = 10_000
OPEN_TASK = re.compile(r"^[ \t]*-[ \t]*\[ \][ \t]*(.*)$", re.MULTILINE)
DONE_TASK = re.compile(r"^[ \t]*-[ \t]*\[[xX]\]", re.MULTILINE)
SKIP_SPECS = re.compile(r"^skip_specs[ \t]*:[ \t]*true[ \t]*$", re.MULTILINE)
ARCHIVE_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}-")


class Usage(Exception):
    """Bad arguments (exit 2)."""


class Failure(Exception):
    """A finding or a failure (exit 1)."""


# --- sources -------------------------------------------------------------


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True
    )
    if result.returncode != 0:
        raise Failure(
            f"`git {' '.join(args)}` exited {result.returncode}: {result.stderr.strip()}"
        )
    return result.stdout


class GitSource:
    """Base and head read from a local clone with git plumbing; the working tree is never read."""

    def __init__(self, root: Path, base: str, head: str, changes_dir: str) -> None:
        self.root, self.changes_dir = root, changes_dir
        self.base_sha = self._resolve(base, "--base")
        self.head_sha = self._resolve(head, "--head")

    def _resolve(self, ref: str, flag: str) -> str:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(self.root),
                "rev-parse",
                "--verify",
                "--quiet",
                f"{ref}^{{commit}}",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise Usage(
                f"{flag} {ref!r} is not a commit in {self.root}; fetch it, or pass the right ref."
            )
        return result.stdout.strip()

    def _ls(
        self, sha: str, path: str, recursive: bool = False
    ) -> list[tuple[str, str, str]]:
        out = git(
            self.root,
            "ls-tree",
            "-z",
            *(["-r"] if recursive else []),
            sha,
            "--",
            f"{path}/",
        )
        rows = []
        for record in filter(None, out.split("\0")):
            meta, name = record.split("\t", 1)
            _, kind, obj = meta.split()
            rows.append((kind, obj, name))
        return rows

    def changed_paths(self) -> list[str]:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(self.root),
                "diff",
                "-z",
                "--name-only",
                "--no-renames",
                f"{self.base_sha}...{self.head_sha}",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise Failure(
                f"`git diff base...head` failed: {result.stderr.strip()}. The merge base must be reachable: "
                "fetch with full history (fetch-depth 0)."
            )
        return [p for p in result.stdout.split("\0") if p]

    def dirs(self, side: str) -> list[str]:
        sha = self.base_sha if side == "base" else self.head_sha
        found = [
            name for kind, _, name in self._ls(sha, self.changes_dir) if kind == "tree"
        ]
        archive = f"{self.changes_dir}/archive"
        if archive in found:
            found += [
                name for kind, _, name in self._ls(sha, archive) if kind == "tree"
            ]
        return sorted(found)

    def blobs(self, path: str) -> dict[str, str]:
        return {
            name: obj
            for kind, obj, name in self._ls(self.head_sha, path, recursive=True)
            if kind == "blob"
        }

    def text(self, path: str) -> str | None:
        obj = self.blobs(path.rsplit("/", 1)[0]).get(path)
        if obj is None:
            return None
        raw = subprocess.run(
            ["git", "-C", str(self.root), "cat-file", "blob", obj], capture_output=True
        ).stdout
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise Failure(
                f"{path} is not UTF-8 text ({exc}); nothing is reported from a partial read."
            ) from exc


def git_source(args: argparse.Namespace, root: Path, changes_dir: str) -> GitSource:
    if not (args.base and args.head):
        raise Usage(f"{args.command} needs --base and --head.")
    return GitSource(root, args.base, args.head, changes_dir)


# --- related changes -----------------------------------------------------


def change_names(paths: list[str], changes_dir: str) -> list[str]:
    names: set[str] = set()
    for path in paths:
        if not path.startswith(f"{changes_dir}/"):
            continue
        parts = path[len(changes_dir) + 1 :].split("/")
        if parts[0] == "archive" and len(parts) >= 3:
            names.add(ARCHIVE_DATE.sub("", parts[1]))
        elif parts[0] != "archive" and len(parts) >= 2:
            names.add(parts[0])
    return sorted(names)


def locate(dirs: list[str], changes_dir: str, name: str) -> tuple[str, str | None]:
    """A change's state in a listing of change directories, and its directory."""
    if f"{changes_dir}/{name}" in dirs:
        return "active", f"{changes_dir}/{name}"
    prefix = f"{changes_dir}/archive/"
    archived = [
        d
        for d in dirs
        if d.startswith(prefix) and ARCHIVE_DATE.sub("", d[len(prefix) :]) == name
    ]
    return ("archived", max(archived)) if archived else ("removed", None)


def task_counts(text: str | None) -> dict:
    if text is None:
        return {"done": 0, "open": 0, "open_tasks": []}
    open_tasks = [m.strip() or "(untitled task)" for m in OPEN_TASK.findall(text)]
    return {
        "done": len(DONE_TASK.findall(text)),
        "open": len(open_tasks),
        "open_tasks": open_tasks,
    }


def related_changes(source, changes_dir: str) -> list[dict]:
    head_dirs, base_dirs = source.dirs("head"), source.dirs("base")
    changes = []
    for name in change_names(source.changed_paths(), changes_dir):
        state, path = locate(head_dirs, changes_dir, name)
        marker = source.text(f"{path}/.openspec.yaml") if path else None
        changes.append(
            {
                "name": name,
                "state": state,
                "at_base": locate(base_dirs, changes_dir, name)[0],
                "path": path,
                "skip_specs": bool(marker and SKIP_SPECS.search(marker)),
                "documents": sorted(source.blobs(path)) if path else [],
                "tasks": task_counts(source.text(f"{path}/tasks.md") if path else None),
            }
        )
    return changes


# --- output --------------------------------------------------------------


def emit(data: dict, args: argparse.Namespace, summary) -> None:
    """JSON on stdout; above OUTPUT_LIMIT characters a summary unless --full or --output is given."""
    text = json.dumps(data, indent=2, sort_keys=True)
    if getattr(args, "output", None):
        Path(args.output).write_text(text + "\n", encoding="utf-8")
        print(
            json.dumps(
                {"output": args.output, **summary(data)}, indent=2, sort_keys=True
            )
        )
    elif getattr(args, "full", False) or len(text) <= OUTPUT_LIMIT:
        print(text)
    else:
        note = f"output is {len(text)} characters; pass --full to print it all or --output FILE to write it"
        print(json.dumps({"summary": note, **summary(data)}, indent=2, sort_keys=True))


def status_summary(data: dict) -> dict:
    brief = [
        {
            "name": c["name"],
            "state": c["state"],
            "done": c["tasks"]["done"],
            "open": c["tasks"]["open"],
        }
        for c in data["changes"]
    ]
    omitted = [p for c in data["changes"] for p in c["documents"]]
    return {
        "base": data["base"],
        "head": data["head"],
        "changes": brief,
        "omitted_documents": omitted,
    }


def plain_summary(data: dict) -> dict:
    return {
        k: (v if not isinstance(v, (list, dict)) else f"{len(v)} item(s) omitted")
        for k, v in data.items()
    }


def run_validator(root: Path, executable: str) -> bool:
    try:
        result = subprocess.run(
            [executable, "validate", "--all", "--strict", "--no-interactive"],
            cwd=root,
            env={**os.environ, "OPENSPEC_NO_UPDATE_CHECK": "1"},
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
    except FileNotFoundError as exc:
        raise Failure(
            f"the OpenSpec CLI `{executable}` is not on PATH; the project must provide it."
        ) from exc
    sys.stderr.write(result.stdout)
    return result.returncode == 0


def cmd_status(args: argparse.Namespace, root: Path, changes_dir: str) -> int:
    source = git_source(args, root, changes_dir)
    data = {
        "base": source.base_sha,
        "head": source.head_sha,
        "changes": related_changes(source, changes_dir),
    }
    emit(data, args, status_summary)
    return 0


def cmd_check(args: argparse.Namespace, root: Path, changes_dir: str) -> int:
    source = git_source(args, root, changes_dir)
    validated = args.no_validate or run_validator(root, args.openspec)
    changes = related_changes(source, changes_dir)
    unarchived = [c["name"] for c in changes if c["state"] == "active"]
    warnings = [
        f"archived change {c['name']} has {c['tasks']['open']} open task(s)"
        for c in changes
        if c["state"] == "archived" and c["tasks"]["open"]
    ]
    if not validated:
        verdict = "invalid"
    elif unarchived and not args.draft:
        verdict = "awaiting-archive"
    else:
        verdict = "pass"
        warnings += [
            f"unarchived change {name}: archive it once the review closes"
            for name in unarchived
        ]
    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)
    data = {
        "base": source.base_sha,
        "head": source.head_sha,
        "verdict": verdict,
        "draft": args.draft,
    }
    data.update(unarchived=unarchived, warnings=warnings, validated=validated)
    emit(data, args, plain_summary)
    return 0 if verdict == "pass" else 1


def cmd_related(args: argparse.Namespace, root: Path, changes_dir: str) -> int:
    source = git_source(args, root, changes_dir)
    brief = [
        {k: c[k] for k in ("name", "state", "path", "skip_specs")}
        | {"done": c["tasks"]["done"], "open": c["tasks"]["open"]}
        for c in related_changes(source, changes_dir)
    ]
    emit(
        {"base": source.base_sha, "head": source.head_sha, "changes": brief},
        args,
        plain_summary,
    )
    return 0


def openspec(root: Path, executable: str, *args: str) -> None:
    """Run one OpenSpec command; its output goes to stderr so stdout stays JSON."""
    try:
        result = subprocess.run(
            [executable, *args],
            cwd=root,
            env={**os.environ, "OPENSPEC_NO_UPDATE_CHECK": "1"},
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
    except FileNotFoundError as exc:
        raise Failure(
            f"the OpenSpec CLI `{executable}` is not on PATH; the project must provide it."
        ) from exc
    sys.stderr.write(result.stdout)
    if result.returncode != 0:
        raise Failure(
            f"`{executable} {' '.join(args)}` exited {result.returncode}; see its output above."
        )


def cmd_archive(args: argparse.Namespace, root: Path, changes_dir: str) -> int:
    """Archive every related change, or none: refuse while any has an open or no ticked task, and restore the tree when a step fails."""
    source = git_source(args, root, changes_dir)
    if git(root, "rev-parse", "HEAD").strip() != source.head_sha:
        raise Usage(
            "archive edits the checked-out tree, so --head must name the checked-out HEAD."
        )
    # The CLI writes the change records and the main specs: everything under the tool's directory.
    owned = changes_dir.rsplit("/", 1)[0] if "/" in changes_dir else changes_dir
    dirty = git(
        root, "status", "--porcelain", "--untracked-files=all", "--", owned
    ).splitlines()
    if dirty:
        paths = ", ".join(line[3:] for line in dirty[:5])
        raise Failure(
            f"uncommitted paths under {owned}: {paths}; commit or stash them first. Nothing was archived."
        )
    changes = related_changes(source, changes_dir)
    todo = [c for c in changes if c["state"] == "active"]
    refused = [
        {
            "name": c["name"],
            "open_tasks": c["tasks"]["open_tasks"] or ["tasks.md has no ticked task"],
        }
        for c in todo
        if c["tasks"]["open"] or not c["tasks"]["done"]
    ]
    plan = {
        "head": source.head_sha,
        "archived": [],
        "already_archived": [c["name"] for c in changes if c["state"] == "archived"],
        "refused": refused,
        "validated": False,
        "commit": None,
    }
    if refused:
        for r in refused:
            print(
                f"refused {r['name']}: open task {r['open_tasks'][0]!r}",
                file=sys.stderr,
            )
        print(
            "nothing archived: every related change must be complete first.",
            file=sys.stderr,
        )
        emit(plan, args, plain_summary)
        return 1
    if not todo:
        emit(plan, args, plain_summary)
        return 0
    try:
        for c in todo:
            # --yes archives even with open tasks, which is why the refusal above runs first.
            openspec(
                root,
                args.openspec,
                "archive",
                c["name"],
                "--yes",
                *(["--skip-specs"] if c["skip_specs"] else []),
            )
            plan["archived"].append(c["name"])
        openspec(
            root, args.openspec, "validate", "--all", "--strict", "--no-interactive"
        )
        plan["validated"] = True
        if not args.no_commit:
            message = (
                args.message or f"archive OpenSpec change {', '.join(plan['archived'])}"
            )
            git(root, "add", "-A", "--", owned)
            git(root, "commit", "-q", "-m", message, "--", owned)
            plan["commit"] = git(root, "rev-parse", "HEAD").strip()
    except Failure as exc:
        raise Failure(f"{exc} {restore(root, owned)}") from exc
    emit(plan, args, plain_summary)
    return 0


def restore(root: Path, owned: str) -> str:
    """Put the tool's directory back to HEAD after a failed archive; it was clean before, so nothing is lost."""
    try:
        git(root, "reset", "-q", "--", owned)
        git(root, "checkout", "-q", "--", owned)
        git(root, "clean", "-fdq", "--", owned)
    except Failure as exc:
        return (
            f"Restoring {owned} also failed ({exc}); run `git reset -q -- {owned} && "
            f"git checkout -- {owned} && git clean -fd -- {owned}` before retrying."
        )
    return f"{owned} was restored to HEAD; nothing was archived. Fix the cause and run the same command again."


# --- arguments -----------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="spec_changes.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Resolve, check, and archive the OpenSpec changes a request touches: "
            "related, status, check, archive. Run <command> --help for its options."
        ),
        epilog=(
            "examples:\n"
            "  python3 <skill>/scripts/spec_changes.py related --base origin/main --head HEAD\n"
            "  python3 <skill>/scripts/spec_changes.py archive --base origin/main --head HEAD "
            "--message 'chore(spec): archive export-csv'"
        ),
    )
    parser.add_argument(
        "--root",
        default=".",
        help="git work tree holding the changes directory (default: .)",
    )
    parser.add_argument(
        "--changes-dir",
        default="openspec/changes",
        help="relative to --root (default: openspec/changes)",
    )
    sub = parser.add_subparsers(dest="command", metavar="<command>")

    def common(p: argparse.ArgumentParser) -> None:
        p.add_argument(
            "--base",
            help="the branch the request merges into, e.g. origin/main",
        )
        p.add_argument("--head", help="the request's head, e.g. HEAD")
        p.add_argument(
            "--full",
            action="store_true",
            help="print output above 10,000 characters instead of a summary",
        )
        p.add_argument(
            "--output",
            metavar="FILE",
            help="write the whole output to FILE; stdout gets a summary",
        )

    p = sub.add_parser(
        "related", help="the related changes with their state and task counts"
    )
    common(p)
    p.set_defaults(func=cmd_related)

    p = sub.add_parser(
        "status", help="the related changes with state, documents, and task progress"
    )
    common(p)
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("check", help="strict validation, then the archive verdict")
    common(p)
    p.add_argument(
        "--draft",
        action="store_true",
        help="an unarchived related change is a warning, not a finding",
    )
    p.add_argument(
        "--no-validate", action="store_true", help="skip the OpenSpec validator"
    )
    p.add_argument(
        "--openspec",
        default="openspec",
        help="OpenSpec CLI executable (default: openspec)",
    )
    p.set_defaults(func=cmd_check)

    p = sub.add_parser(
        "archive",
        help="archive every complete related change, validate strictly, and commit",
    )
    common(p)
    p.add_argument(
        "--message",
        help="commit message in the project's convention (default: a plain sentence)",
    )
    p.add_argument(
        "--no-commit", action="store_true", help="leave the archive uncommitted"
    )
    p.add_argument(
        "--openspec",
        default="openspec",
        help="OpenSpec CLI executable (default: openspec)",
    )
    p.set_defaults(func=cmd_archive)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.error("a command is required: related, status, check, or archive")
    try:
        return args.func(args, Path(args.root).resolve(), args.changes_dir.strip("/"))
    except Usage as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except Failure as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
