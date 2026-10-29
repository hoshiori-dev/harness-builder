#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Report on the Spec-Kit features a pull or merge request touches.

A request's *touched features* are the feature directories under the kit's
specs directory (default ``specs/``, entries named ``<NNN>-<name>`` or
``<YYYYMMDD-HHMMSS>-<name>``) whose files the diff ``--base...--head``
touches. ``spec.md`` and ``plan.md`` are required; ``tasks.md`` lists
tasks as ``- [ ] T001 ...`` checkboxes. The kit ships no validator and no
archive operation, so completion is every task ticked.

Both refs are read with git plumbing; no command checks anything out or
writes to the working tree.

Exit codes: 0 success; 1 a failure or a finding; 2 bad arguments.
Run with --help for every subcommand and option.

Usage example:
    python3 scripts/spec_kit_features.py status --base origin/main --head HEAD
    python3 scripts/spec_kit_features.py check --base origin/main --head HEAD --draft
    python3 scripts/spec_kit_features.py show --base main --head HEAD --feature 003-import
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

OPEN_TASK = re.compile(r"^[ \t]*-[ \t]*\[ \][ \t]*(.*)$", re.MULTILINE)
DONE_TASK = re.compile(r"^[ \t]*-[ \t]*\[[xX]\][ \t]", re.MULTILINE)
FEATURE_DIR = re.compile(r"^\d{3,}-[A-Za-z0-9._-]+$")
DOCS = ("spec.md", "plan.md", "tasks.md")
REQUIRED = ("spec.md", "plan.md")
PROGRESS_LABELS = ("spec:not-started", "spec:in-progress", "spec:done")
OUTPUT_LIMIT = 10_000


class Usage(Exception):
    """Bad arguments (exit 2)."""


class Failure(Exception):
    """A failure or a finding (exit 1)."""


# --- git plumbing ---------------------------------------------------------


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True
    )
    if result.returncode != 0:
        raise Failure(
            f"`git {' '.join(args)}` exited {result.returncode}: "
            f"{result.stderr.strip()}"
        )
    return result.stdout


def resolve(root: Path, ref: str, what: str) -> str:
    result = subprocess.run(
        [
            "git",
            "-C",
            str(root),
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
            f"{what} {ref!r} does not resolve to a commit in {root}; fetch it first, "
            "or pass refs that exist in this clone."
        )
    return result.stdout.strip()


# --- the head --------------------------------------------------------------


class GitSource:
    """Reads the two commits out of a local git object store.

    Use it where the head is already present and trusted: a developer's
    clone, or an unprivileged pull-request check.
    """

    def __init__(self, root: Path, base: str, head: str) -> None:
        self.root = root
        self.base = resolve(root, base, "--base")
        self.head = resolve(root, head, "--head")
        self.base_label = self.base
        self.head_label = self.head

    def ls(self, path: str) -> list[tuple[str, str]]:
        """``(type, path)`` records of ``git ls-tree``; empty for an absent path."""
        out = git(self.root, "ls-tree", "-z", self.head, "--", path)
        records = []
        for record in filter(None, out.split("\0")):
            meta, name = record.split("\t", 1)
            records.append((meta.split()[1], name))
        return records

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
                f"{self.base}...{self.head}",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise Failure(
                f"`git diff {self.base}...{self.head}` failed "
                f"({result.stderr.strip()}); the merge base must be reachable, so "
                "fetch with full history (fetch-depth 0) rather than a shallow clone."
            )
        return [path for path in result.stdout.split("\0") if path]

    def entries(self, path: str) -> list[str]:
        return [child.rsplit("/", 1)[-1] for _, child in self.ls(f"{path}/")]

    def read(self, path: str) -> str | None:
        if self.ls(path) != [("blob", path)]:
            return None
        return git(self.root, "show", f"{self.head}:{path}")


# --- touched features -----------------------------------------------------


def feature_names(paths: list[str], specs_dir: str) -> list[str]:
    prefix = f"{specs_dir}/"
    names: set[str] = set()
    for path in paths:
        if not path.startswith(prefix):
            continue
        parts = path[len(prefix) :].split("/")
        if len(parts) >= 2 and FEATURE_DIR.match(parts[0]):
            names.add(parts[0])
    return sorted(names)


def task_counts(text: str | None) -> dict:
    """Progress from a task list; a missing list or one with no checkbox has not started."""
    if text is None:
        return {"done": 0, "open": 0, "open_tasks": [], "progress": "not-started"}
    done = len(DONE_TASK.findall(text))
    open_tasks = [m.strip() or "(untitled task)" for m in OPEN_TASK.findall(text)]
    if not open_tasks and done > 0:
        progress = "done"
    elif done == 0:
        progress = "not-started"
    else:
        progress = "in-progress"
    return {
        "done": done,
        "open": len(open_tasks),
        "open_tasks": open_tasks,
        "progress": progress,
    }


def describe(source: GitSource, specs_dir: str, name: str) -> dict:
    path = f"{specs_dir}/{name}"
    present = set(source.entries(path))
    return {
        "name": name,
        "path": path,
        "state": "present" if present else "removed",
        "missing": [f for f in DOCS if f not in present] if present else [],
        "tasks": task_counts(source.read(f"{path}/tasks.md") if present else None),
    }


def touched_features(source: GitSource, specs_dir: str) -> list[dict]:
    names = feature_names(source.changed_paths(), specs_dir)
    return [describe(source, specs_dir, n) for n in names]


def select(features: list[dict], wanted: list[str]) -> list[dict]:
    """The named features, or all; a name the request does not touch is a bad argument."""
    by_name = {f["name"]: f for f in features}
    unknown = [name for name in wanted if name not in by_name]
    if unknown:
        raise Usage(
            f"not a feature this request touches: {', '.join(unknown)}. "
            f"Touched features: {', '.join(by_name) or 'none'}."
        )
    return [by_name[name] for name in wanted] if wanted else features


def status_markdown(features: list[dict]) -> str:
    if not features:
        return "No touched Spec-Kit feature: the diff touches nothing under the specs directory.\n"
    lines = ["| Feature | Files | Tasks | Progress |", "|---|---|---|---|"]
    for f in features:
        if f["state"] == "removed":
            files = "removed"
        else:
            files = "missing " + ", ".join(f["missing"]) if f["missing"] else "complete"
        t = f["tasks"]
        lines.append(
            f"| `{f['name']}` | {files} | {t['done']} done, {t['open']} open "
            f"| {t['progress']} |"
        )
    for f in features:
        if f["tasks"]["open_tasks"]:
            lines.append("")
            lines.append(f"Open tasks of `{f['name']}` (first ten):")
            for task in f["tasks"]["open_tasks"][:10]:
                lines.append(f"- {task[:117] + '...' if len(task) > 120 else task}")
    return "\n".join(lines) + "\n"


def readiness(features: list[dict], draft: bool, shape: str) -> tuple[list, list]:
    """Findings that fail the request and warnings that do not.

    Every touched feature carries its specification and plan. A ready
    request carries every task ticked, except the split shape's
    specification request, which implemented nothing: no task ticked.
    """
    findings: list[str] = []
    warnings: list[str] = []
    for f in features:
        if f["state"] == "removed":
            continue
        name = f["name"]
        for m in f["missing"]:
            if m in REQUIRED:
                findings.append(
                    f"feature {name}: missing {m}; the specification and the plan "
                    "form the approval package."
                )
        t = f["tasks"]
        unfinished: list[str] = []
        if "tasks.md" in f["missing"]:
            unfinished.append(
                f"feature {name}: missing tasks.md, so the feature has not started; "
                "every task is ticked before an implementation request is ready."
            )
        elif t["done"] == 0 and t["open"] == 0:
            unfinished.append(
                f"feature {name}: tasks.md carries no checkbox, so the feature has "
                "not started."
            )
        for task in t["open_tasks"]:
            unfinished.append(f"feature {name}: open task {task}")
        if not unfinished:
            continue
        if draft:
            warnings.extend(unfinished)
        elif shape == "split" and t["done"] == 0:
            warnings.append(
                f"feature {name} has not started; allowed for the specification "
                "request of the split shape."
            )
        else:
            findings.extend(unfinished)
    return findings, warnings


def desired_labels(features: list[dict]) -> list[str]:
    live = [f for f in features if f["state"] != "removed"]
    if not live:
        return []
    progress = {f["tasks"]["progress"] for f in live}
    if progress == {"done"}:
        return [PROGRESS_LABELS[2]]
    if progress == {"not-started"}:
        return [PROGRESS_LABELS[0]]
    return [PROGRESS_LABELS[1]]


# --- output ---------------------------------------------------------------


def emit(args: argparse.Namespace, text: str, summary: dict) -> None:
    """Print ``text``, write it to --output, or summarise it when it is long."""
    if args.output:
        try:
            Path(args.output).write_text(text, encoding="utf-8")
        except OSError as exc:
            raise Failure(f"cannot write {args.output}: {exc}") from exc
        print(f"wrote {len(text)} characters to {args.output}", file=sys.stderr)
    elif len(text) > OUTPUT_LIMIT and not args.full:
        summary = {
            **summary,
            "characters": len(text),
            "truncated": True,
            "hint": "pass --full to print it whole, or --output PATH to write it",
        }
        print(json.dumps(summary, indent=2))
    else:
        sys.stdout.write(text)


def fence_for(text: str) -> str:
    longest = max((len(m) for m in re.findall(r"`+", text)), default=0)
    return "`" * max(3, longest + 1)


def show_documents(source: GitSource, features: list[dict], doc: str) -> list[dict]:
    """The documents ``show`` prints, each with its path, size, and text."""
    wanted = DOCS if doc == "all" else (f"{doc}.md",)
    out = []
    for f in features:
        if f["state"] == "removed":
            continue
        for name in wanted:
            path = f"{f['path']}/{name}"
            text = source.read(path)
            if text is not None:
                out.append({"path": path, "characters": len(text), "text": text})
    return out


# --- commands -------------------------------------------------------------


def cmd_related(args: argparse.Namespace, source: GitSource, specs_dir: str) -> int:
    features = touched_features(source, specs_dir)
    if args.json:
        doc = {
            "base": source.base_label,
            "head": source.head_label,
            "features": features,
        }
        text = json.dumps(doc, indent=2) + "\n"
    else:
        text = "".join(
            f"{f['name']}\t{f['state']}\t{f['tasks']['done']} done\t"
            f"{f['tasks']['open']} open\n"
            for f in features
        )
    emit(args, text, {"features": len(features)})
    return 0


def cmd_status(args: argparse.Namespace, source: GitSource, specs_dir: str) -> int:
    features = select(touched_features(source, specs_dir), args.feature)
    if args.json:
        doc = {
            "base": source.base_label,
            "head": source.head_label,
            "features": features,
        }
        text = json.dumps(doc, indent=2) + "\n"
    else:
        text = status_markdown(features)
    emit(args, text, {"features": len(features)})
    return 0


def cmd_show(args: argparse.Namespace, source: GitSource, specs_dir: str) -> int:
    wanted = [args.feature] if args.feature else []
    features = select(touched_features(source, specs_dir), wanted)
    docs = show_documents(source, features, args.doc)
    if not docs:
        text = "No document to show: the request touches no feature with one.\n"
    else:
        blocks = []
        for d in docs:
            fence = fence_for(d["text"])
            blocks.append(
                f"**{d['path']}**\n\n{fence}markdown\n{d['text'].rstrip()}\n{fence}\n"
            )
        text = "\n".join(blocks)
    sizes = [{"path": d["path"], "characters": d["characters"]} for d in docs]
    emit(args, text, {"documents": sizes})
    return 0


def cmd_check(args: argparse.Namespace, source: GitSource, specs_dir: str) -> int:
    features = touched_features(source, specs_dir)
    findings, warnings = readiness(features, args.draft, args.shape)
    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)
    emit(args, "".join(f"{line}\n" for line in findings), {"findings": len(findings)})
    return 1 if findings else 0


def cmd_labels(args: argparse.Namespace, source: GitSource, specs_dir: str) -> int:
    desired = desired_labels(touched_features(source, specs_dir))
    current = [label.strip() for label in args.current.split(",") if label.strip()]
    result = {
        "desired": desired,
        "add": [label for label in desired if label not in current],
        "remove": [
            label
            for label in current
            if label in PROGRESS_LABELS and label not in desired
        ],
    }
    if args.json:
        text = json.dumps(result, indent=2) + "\n"
    else:
        text = "".join(f"{k}: {' '.join(v) or '(none)'}\n" for k, v in result.items())
    emit(args, text, {})
    return 0


# --- argument parsing -----------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="spec_kit_features.py",
        description=(
            "Report on the Spec-Kit features the diff --base...--head touches: "
            "related, status, show, check, labels. Nothing is written."
        ),
        epilog=(
            "Example: python3 scripts/spec_kit_features.py check "
            "--base origin/main --head HEAD --draft"
        ),
    )
    parser.add_argument("--root", default=".", help="git work tree (default: .)")
    parser.add_argument(
        "--specs-dir",
        default="specs",
        help="the kit's specs directory (default: specs)",
    )
    # Not `required`: argparse would then report a missing command first.
    sub = parser.add_subparsers(dest="command", metavar="<command>")

    def common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--base", required=True, help="base ref, e.g. origin/main")
        p.add_argument("--head", required=True, help="head ref, e.g. HEAD")
        p.add_argument("--full", action="store_true", help="print long output whole")
        p.add_argument("--output", help="write the output to this file instead")

    p = sub.add_parser("related", help="the touched features with their task counts")
    common(p)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_related)

    p = sub.add_parser("status", help="progress of the touched features")
    common(p)
    p.add_argument("--feature", action="append", default=[], help="limit (repeatable)")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("show", help="the documents of the touched features")
    common(p)
    p.add_argument("--feature", help="one touched feature (default: all)")
    p.add_argument("--doc", choices=("spec", "plan", "tasks", "all"), default="all")
    p.set_defaults(func=cmd_show)

    p = sub.add_parser(
        "check", help="files present; unfinished tasks fail a ready request"
    )
    common(p)
    p.add_argument("--draft", action="store_true", help="unfinished tasks only warn")
    p.add_argument(
        "--shape",
        choices=("combined", "split"),
        default="combined",
        help="request shape from the contract; split admits a feature with no ticked task",
    )
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("labels", help="the progress label to add and remove")
    common(p)
    p.add_argument("--current", default="", help="comma-separated current labels")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_labels)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.error("a command is required: related, status, show, check, or labels")
    root = Path(args.root).resolve()
    specs_dir = args.specs_dir.strip("/")
    try:
        source = GitSource(root, args.base, args.head)
        return args.func(args, source, specs_dir)
    except Usage as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except Failure as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
