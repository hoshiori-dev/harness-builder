#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Architecture boundary check: fail on imports that cross a forbidden direction.

Reads Python and TypeScript/JavaScript sources under each rule's source
directory and reports every import that resolves into the rule's forbidden
directory. Data goes to stdout as JSON; routing messages go to stderr.

Exit codes: 0 no violation, 1 violation or unreadable input, 2 bad arguments.

Examples:
  python3 scripts/check_boundaries.py                 # the whole tree
  python3 scripts/check_boundaries.py app/a.py app/b.ts   # only these files
  python3 scripts/check_boundaries.py --root path/to/repo --full
  python3 scripts/check_boundaries.py --help
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Rule:
    source: str  # files under this directory are checked
    forbidden: str  # imports resolving under this directory are violations
    instead: str  # what to do instead, shown in the failure
    doc: str  # the knowledge file that states the rule


RULES = [
    Rule(
        source="app/",  # CONFIGURE: the directory whose imports are checked
        forbidden="infra/",  # CONFIGURE: the directory it must not import from
        instead="depend on the interfaces in app/ports/ and let infra/ implement them",  # CONFIGURE: the allowed alternative
        doc=".agents/knowledge/architecture.md",  # CONFIGURE: the knowledge file stating the rule
    ),
]
MODULE_ROOTS = [".", "src"]  # CONFIGURE: directories absolute imports resolve against
ALIASES = {"@/": "src/"}  # CONFIGURE: path aliases from tsconfig or the bundler

PY_SUFFIXES = {".py"}
JS_SUFFIXES = {".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".mts", ".cts"}
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__"}
SUMMARY_LIMIT = 50

PY_FROM = re.compile(r"^\s*from\s+(\.*[\w.]*)\s+import\b(.*)")
PY_IMPORT = re.compile(
    r"^\s*import\s+([\w.]+(?:\s+as\s+\w+)?(?:\s*,\s*[\w.]+(?:\s+as\s+\w+)?)*)"
)
JS_SPEC = re.compile(
    r"""(?:\bfrom\s+|\bimport\s*\(?\s*|\brequire\(\s*)['"]([^'"]+)['"]"""
)


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fail on imports that cross a forbidden architecture boundary.",
        epilog="Example: python3 scripts/check_boundaries.py app/service.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="files to check (default: every file under each rule's source)",
    )
    parser.add_argument(
        "--root", default=".", help="repository root (default: current directory)"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help=f"list every violation, not the first {SUMMARY_LIMIT}",
    )
    return parser.parse_args(argv)


def norm(path: str) -> str:
    return os.path.normpath(path).replace(os.sep, "/")


def under(path: str, directory: str) -> bool:
    directory = norm(directory)
    return path == directory or path.startswith(directory + "/")


def python_targets(
    line: str, rel_file: str, roots: list[str]
) -> list[tuple[str, list[str]]]:
    specs: list[str] = []
    match = PY_FROM.match(line)
    if match and match.group(1).strip("."):
        specs.append(match.group(1))
    elif match:
        # `from .. import infra`: the imported names are the modules.
        dots = match.group(1)
        names = match.group(2).split("#")[0].strip().strip("()").split(",")
        specs.extend(
            dots + name.split()[0] for name in names if name.strip() not in ("", "*")
        )
    else:
        match = PY_IMPORT.match(line)
        if match:
            specs.extend(part.split()[0] for part in match.group(1).split(","))
    out = []
    for spec in specs:
        dots = len(spec) - len(spec.lstrip("."))
        module_path = spec.lstrip(".").replace(".", "/")
        if dots:
            base = Path(rel_file).parent
            for _ in range(dots - 1):
                base = base.parent
            candidates = [norm(str(base / module_path))]
        else:
            candidates = [norm(f"{root}/{module_path}") for root in roots]
        out.append((spec, candidates))
    return out


def js_targets(
    line: str, rel_file: str, roots: list[str], aliases: dict[str, str]
) -> list[tuple[str, list[str]]]:
    out = []
    for spec in JS_SPEC.findall(line):
        if spec.startswith("."):
            candidates = [norm(str(Path(rel_file).parent / spec))]
        else:
            resolved = spec
            for prefix, target in aliases.items():
                if spec.startswith(prefix):
                    resolved = target + spec[len(prefix) :]
                    break
            candidates = [norm(f"{root}/{resolved}") for root in roots]
        out.append((spec, candidates))
    return out


def imports_of(text: str, rel_file: str, roots: list[str], aliases: dict[str, str]):
    is_python = Path(rel_file).suffix in PY_SUFFIXES
    for number, line in enumerate(text.splitlines(), start=1):
        stripped = line.lstrip()
        if stripped.startswith("#" if is_python else "//"):
            continue
        if is_python:
            found = python_targets(line, rel_file, roots)
        else:
            found = js_targets(line, rel_file, roots, aliases)
        for spec, candidates in found:
            yield number, spec, candidates


def collect_files(
    root: Path, files: list[str], rules: list[Rule], errors: list[dict]
) -> list[str]:
    suffixes = PY_SUFFIXES | JS_SUFFIXES
    if files:
        out = []
        for name in files:
            path = Path(name) if Path(name).is_absolute() else root / name
            rel = norm(os.path.relpath(path, root))
            if path.suffix in suffixes and any(
                under(rel, rule.source) for rule in rules
            ):
                out.append(rel)
        return out
    out = []
    for rule in rules:
        source = root / rule.source
        if not source.is_dir():
            errors.append(
                {
                    "file": rule.source,
                    "error": "rule source directory does not exist",
                    "fix": "correct the rule's source in RULES or delete the rule",
                }
            )
            continue
        for dirpath, dirnames, filenames in os.walk(source):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
            for filename in sorted(filenames):
                if Path(filename).suffix in suffixes:
                    out.append(norm(os.path.relpath(Path(dirpath) / filename, root)))
    return sorted(set(out))


def check(
    root: Path,
    files: list[str],
    rules: list[Rule],
    roots: list[str],
    aliases: dict[str, str],
) -> dict:
    errors: list[dict] = []
    violations: list[dict] = []
    targets = collect_files(root, files, rules, errors)
    for rel in targets:
        try:
            text = (root / rel).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            reason = (
                exc.strerror if isinstance(exc, OSError) and exc.strerror else str(exc)
            )
            errors.append(
                {
                    "file": rel,
                    "error": f"cannot read: {reason}",
                    "fix": "make the file readable or remove it from the input",
                }
            )
            continue
        applicable = [rule for rule in rules if under(rel, rule.source)]
        for line, spec, candidates in imports_of(text, rel, roots, aliases):
            for rule in applicable:
                if any(under(candidate, rule.forbidden) for candidate in candidates):
                    violations.append(
                        {
                            "file": rel,
                            "line": line,
                            "import": spec,
                            "forbidden": rule.forbidden,
                            "rule": f"{rule.source} must not import from {rule.forbidden}",
                            "instead": rule.instead,
                            "doc": rule.doc,
                        }
                    )
    return {"checked": len(targets), "violations": violations, "errors": errors}


def report(result: dict, full: bool) -> None:
    shown = result["violations"] if full else result["violations"][:SUMMARY_LIMIT]
    for item in result["errors"]:
        print(
            f"ERROR {item['file']}: {item['error']}.\n  Fix: {item['fix']}; the check did not pass.",
            file=sys.stderr,
        )
    for item in shown:
        print(
            f"{item['file']}:{item['line']}: imports {item['import']}, which is inside {item['forbidden']}.\n"
            f"  Rule: {item['rule']} ({item['doc']}).\n"
            f"  Instead: {item['instead']}.",
            file=sys.stderr,
        )
    hidden = len(result["violations"]) - len(shown)
    if hidden:
        print(
            f"... {hidden} more violations; rerun with --full to list them.",
            file=sys.stderr,
        )
    payload = dict(result, violations=shown, truncated=hidden > 0)
    print(json.dumps(payload, indent=2))


def main(
    argv: list[str] | None = None,
    rules: list[Rule] | None = None,
    module_roots: list[str] | None = None,
    aliases: dict[str, str] | None = None,
) -> int:
    args = parse_args(argv)
    root = Path(args.root)
    if not root.is_dir():
        print(f"error: --root {args.root} is not a directory.", file=sys.stderr)
        return 2
    result = check(
        root,
        args.files,
        RULES if rules is None else rules,
        MODULE_ROOTS if module_roots is None else module_roots,
        ALIASES if aliases is None else aliases,
    )
    report(result, args.full)
    return 1 if result["violations"] or result["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
