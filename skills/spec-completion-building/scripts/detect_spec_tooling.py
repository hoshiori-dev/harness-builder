#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Read-only inventory of a checkout's specification tooling.

Reports the spec tool layouts found (OpenSpec, Spec-Kit, Kiro, committed
per-change documents), how many specs and changes each holds and the paths
it owns, every agent-entrypoint line that points at a spec artifact, and
every document that looks like it restates requirements or acceptance
criteria outside the tools' directories and outside installed skill trees.

JSON on stdout, a one-line summary and diagnostics on stderr. Nothing is
written to the checkout, so repeated runs print the same output.

Run with --help for options. Exit codes: 0 inspection complete, 1 inspection failed or partial (some
path unreadable), 2 bad arguments.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

EXAMPLE = """example:
  python3 detect_spec_tooling.py --root .
  uv run detect_spec_tooling.py --root ../app --max-candidates 20 --full
"""

SUMMARY_LIMIT = 10_000
SUMMARY_ITEMS = 20

SKIP_DIRS = {
    ".git",
    "node_modules",
    "vendor",
    ".venv",
    "venv",
    "__pycache__",
    "dist",
    "build",
    "target",
    ".tox",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
}

ENTRYPOINTS = (
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    ".github/copilot-instructions.md",
    ".kiro/steering",
)

SPEC_POINTER = re.compile(
    r"(\.specify|openspec|\.kiro|spec-workflow|\bspecs?/|SPEC\.md|PLAN\.md|"
    r"specification|constitution|steering)",
    re.IGNORECASE,
)

SIGNALS = (
    ("acceptance", re.compile(r"acceptance\s+criteria", re.IGNORECASE)),
    ("shall", re.compile(r"\b(?:SHALL|MUST)\b")),
    (
        "requirement-sentence",
        re.compile(
            r"\b(?:the|this)\s+(?:system|service|api|application|app|cli|"
            r"library|tool)\s+(?:shall|must)\b",
            re.IGNORECASE,
        ),
    ),
    ("user-story", re.compile(r"\buser\s+stor(?:y|ies)\b", re.IGNORECASE)),
    (
        "requirements-heading",
        re.compile(r"^#+\s+.*\brequirements?\b", re.IGNORECASE | re.MULTILINE),
    ),
    ("scenario-heading", re.compile(r"^#+\s+scenario\b", re.IGNORECASE | re.MULTILINE)),
)

TEMPLATE_SUFFIXES = (".md", ".yml", ".yaml")
TEMPLATE_DIRS = (
    ".github/ISSUE_TEMPLATE",
    ".github/PULL_REQUEST_TEMPLATE",
    ".gitlab/issue_templates",
    ".gitlab/merge_request_templates",
)
TEMPLATE_FILES = (
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/pull_request_template.md",
)


class Inventory:
    """Collects findings and unreadable paths for one root."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.errors: list[dict] = []

    def rel(self, path: Path) -> str:
        return path.relative_to(self.root).as_posix()

    def error(self, path: Path | str, err: OSError) -> None:
        try:
            shown = self.rel(Path(path))
        except ValueError:
            shown = str(path)
        self.errors.append({"path": shown, "error": err.strerror or str(err)})
        print(f"warning: cannot read {shown}: {err}", file=sys.stderr)

    def subdirs(self, directory: Path) -> list[Path]:
        try:
            return sorted(p for p in directory.iterdir() if p.is_dir())
        except OSError as err:
            self.error(directory, err)
            return []

    def count(self, directory: Path, name: str) -> int:
        total = 0
        for _dirpath, _dirs, files in os.walk(
            directory, onerror=lambda e: self.error(e.filename, e)
        ):
            total += sum(1 for f in files if Path(f).match(name))
        return total

    def read(self, path: Path) -> str | None:
        try:
            return path.read_text(encoding="utf-8", errors="replace")
        except OSError as err:
            self.error(path, err)
            return None


def detect_openspec(inv: Inventory) -> dict | None:
    base = inv.root / "openspec"
    if not base.is_dir():
        return None
    changes = base / "changes"
    active = (
        [p for p in inv.subdirs(changes) if p.name != "archive"]
        if changes.is_dir()
        else []
    )
    archive = changes / "archive"
    config = next(
        (
            inv.rel(base / n)
            for n in ("config.yaml", "config.yml", "project.md")
            if (base / n).is_file()
        ),
        None,
    )
    return {
        "tool": "openspec",
        "specs": inv.count(base / "specs", "spec.md")
        if (base / "specs").is_dir()
        else 0,
        "active_changes": len(active),
        "active_change_paths": [inv.rel(p) for p in active],
        "archived_changes": len(inv.subdirs(archive)) if archive.is_dir() else 0,
        "config": config,
        "owned_paths": [inv.rel(base)],
    }


def detect_spec_kit(inv: Inventory) -> dict | None:
    hidden = inv.root / ".specify"
    specs = inv.root / "specs"
    features = (
        [p for p in inv.subdirs(specs) if re.match(r"^\d{3,}-", p.name)]
        if specs.is_dir()
        else []
    )
    if not hidden.is_dir() and not features:
        return None
    constitution = hidden / "memory" / "constitution.md"
    owned = [inv.rel(hidden)] if hidden.is_dir() else []
    if features:
        owned.append(inv.rel(specs))
    return {
        "tool": "spec-kit",
        "specs": sum(1 for p in features if (p / "spec.md").is_file()),
        "features": len(features),
        "feature_paths": [inv.rel(p) for p in features],
        "constitution": inv.rel(constitution) if constitution.is_file() else None,
        "owned_paths": owned,
    }


def detect_kiro(inv: Inventory) -> dict | None:
    base = inv.root / ".kiro"
    if not base.is_dir():
        return None
    features = inv.subdirs(base / "specs") if (base / "specs").is_dir() else []
    steering = base / "steering"
    steering_files = (
        sorted(inv.rel(p) for p in steering.glob("*.md")) if steering.is_dir() else []
    )
    if not features and not steering_files:
        return None
    required = ("requirements.md", "design.md", "tasks.md")
    return {
        "tool": "kiro",
        "specs": sum(1 for p in features if all((p / f).is_file() for f in required)),
        "features": len(features),
        "feature_paths": [inv.rel(p) for p in features],
        "steering_files": steering_files,
        "owned_paths": [inv.rel(base)],
    }


def detect_documents(inv: Inventory, owned: set[str]) -> dict | None:
    files = sorted(n for n in ("SPEC.md", "PLAN.md") if (inv.root / n).is_file())
    dirs = []
    for name in (
        "specs",
        "spec",
        "specifications",
        "docs/specs",
        "docs/spec",
        "docs/specifications",
    ):
        directory = inv.root / name
        if directory.is_dir() and inv.rel(directory) not in owned:
            markdown = inv.count(directory, "*.md")
            if markdown:
                dirs.append({"path": inv.rel(directory), "markdown_files": markdown})
    if not files and not dirs:
        return None
    return {
        "tool": "committed-documents",
        "specs": len(files) + sum(d["markdown_files"] for d in dirs),
        "root_files": files,
        "directories": dirs,
        "owned_paths": files + [d["path"] for d in dirs],
    }


def entrypoint_pointers(inv: Inventory) -> list[dict]:
    hits = []
    for candidate in ENTRYPOINTS:
        path = inv.root / candidate
        files = (
            sorted(path.glob("*.md"))
            if path.is_dir()
            else [path]
            if path.is_file()
            else []
        )
        for file in files:
            text = inv.read(file)
            for number, line in enumerate((text or "").splitlines(), start=1):
                if SPEC_POINTER.search(line):
                    hits.append(
                        {
                            "file": inv.rel(file),
                            "line": number,
                            "text": line.strip()[:200],
                        }
                    )
    return hits


def is_skill_tree(current: Path, name: str, inv: Inventory) -> bool:
    """Installed or plugin skill trees hold instructions, not requirements."""
    if name == "skills" and (current.name.startswith(".") or current == inv.root):
        return True
    try:
        return (current / name / "SKILL.md").is_file()
    except OSError:
        return False  # an unreadable directory is reported by the walk itself


def walk_documents(inv: Inventory, owned: set[str]):
    """Yield markdown files once each, following symlinks once."""
    seen: set[str] = set()

    def onerror(err: OSError) -> None:
        inv.error(err.filename, err)

    for dirpath, dirnames, filenames in os.walk(
        inv.root, onerror=onerror, followlinks=True
    ):
        current = Path(dirpath)
        real = os.path.realpath(current)
        if real in seen:
            dirnames[:] = []
            continue
        seen.add(real)
        keep = []
        for d in sorted(dirnames):
            child = current / d
            if (
                d in SKIP_DIRS
                or inv.rel(child) in owned
                or is_skill_tree(current, d, inv)
            ):
                continue
            if os.path.realpath(child) in seen:
                continue
            keep.append(d)
        dirnames[:] = keep
        for filename in sorted(filenames):
            file = current / filename
            if filename.lower().endswith(".md") and inv.rel(file) not in owned:
                real_file = os.path.realpath(file)
                if real_file not in seen:
                    seen.add(real_file)
                    yield file


def identity(path: Path) -> tuple[int, int]:
    info = path.stat()
    return (info.st_dev, info.st_ino)


def requirement_candidates(
    inv: Inventory, owned: set[str], limit: int
) -> tuple[list[dict], int]:
    found: dict[str, dict] = {}
    for file in walk_documents(inv, owned):
        text = inv.read(file)
        if text is None:
            continue
        signals = {name: len(p.findall(text)) for name, p in SIGNALS}
        signals = {k: v for k, v in signals.items() if v}
        if signals:
            found[inv.rel(file)] = {"file": inv.rel(file), "signals": signals}
    templates = [inv.root / f for f in TEMPLATE_FILES]
    for name in TEMPLATE_DIRS:
        directory = inv.root / name
        if directory.is_dir():
            templates.extend(sorted(directory.iterdir()))
    seen = {identity(inv.root / key) for key in found}
    for file in templates:
        if not file.is_file() or file.suffix.lower() not in TEMPLATE_SUFFIXES:
            continue
        if identity(file) in seen and inv.rel(file) not in found:
            continue  # the same file under another spelling (case-insensitive file system)
        seen.add(identity(file))
        text = inv.read(file)
        if text and re.search(r"acceptance", text, re.IGNORECASE):
            entry = found.setdefault(
                inv.rel(file), {"file": inv.rel(file), "signals": {}}
            )
            entry["signals"]["acceptance-field"] = 1
            entry["template"] = True
    ordered = [found[key] for key in sorted(found)]
    return ordered[:limit], max(0, len(ordered) - limit)


def summarise(report: dict) -> dict:
    """Shorten the long lists so stdout stays readable; --full disables this."""
    short = dict(report)
    for key in ("entrypoint_pointers", "requirement_restating_candidates"):
        items = report[key]
        if len(items) > SUMMARY_ITEMS:
            short[key] = items[:SUMMARY_ITEMS]
            short[f"{key}_not_shown"] = len(items) - SUMMARY_ITEMS
    for tool in short["tools"]:
        for key in ("active_change_paths", "feature_paths"):
            if len(tool.get(key, [])) > SUMMARY_ITEMS:
                tool[key] = tool[key][:SUMMARY_ITEMS]
    short["summarised"] = True
    return short


def build_report(root: Path, limit: int) -> tuple[dict, Inventory]:
    inv = Inventory(root)
    tools = [
        t for t in (detect_openspec(inv), detect_spec_kit(inv), detect_kiro(inv)) if t
    ]
    owned = {p for t in tools for p in t["owned_paths"]}
    documents = detect_documents(inv, owned)
    if documents:
        tools.append(documents)
        owned.update(documents["owned_paths"])
    candidates, not_listed = requirement_candidates(inv, owned, limit)
    report = {
        "root": str(root),
        "partial": bool(inv.errors),
        "tools": tools,
        "tool_owned_paths": sorted(owned),
        "entrypoint_pointers": entrypoint_pointers(inv),
        "requirement_restating_candidates": candidates,
        "candidates_not_listed": not_listed,
        "unreadable": inv.errors,
    }
    return report, inv


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(__doc__ or "").split("\n\n")[0],
        epilog=EXAMPLE,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--root", default=".", help="checkout to inspect (default: .)")
    parser.add_argument(
        "--max-candidates",
        type=int,
        default=40,
        help="cap on requirement-restating documents listed; the rest are counted (default: 40)",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help=f"print every list in full even when the JSON exceeds {SUMMARY_LIMIT} characters",
    )
    args = parser.parse_args(argv)

    root = Path(args.root)
    if not root.is_dir():
        print(
            f"error: --root {args.root!r} is not a directory; pass the checkout to inspect, for example --root .",
            file=sys.stderr,
        )
        return 2
    if args.max_candidates < 1:
        print(
            "error: --max-candidates must be 1 or more, for example --max-candidates 40",
            file=sys.stderr,
        )
        return 2

    try:
        report, inv = build_report(root.resolve(), args.max_candidates)
    except OSError as err:
        print(
            f"error: inspection failed: {err}; check that the checkout is readable",
            file=sys.stderr,
        )
        return 1

    text = json.dumps(report, indent=2)
    if len(text) > SUMMARY_LIMIT and not args.full:
        text = json.dumps(summarise(report), indent=2)
        print("note: output summarised; pass --full for every entry", file=sys.stderr)
    sys.stdout.write(text + "\n")

    names = ", ".join(t["tool"] for t in report["tools"]) or "none"
    print(
        f"tools: {names}; entrypoint pointers: {len(report['entrypoint_pointers'])}; "
        f"requirement-restating candidates: {len(report['requirement_restating_candidates'])} "
        f"(+{report['candidates_not_listed']} not listed)",
        file=sys.stderr,
    )
    if inv.errors:
        print(
            f"partial: {len(inv.errors)} path(s) unreadable; fix their permissions and run again",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
