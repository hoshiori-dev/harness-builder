#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Check that this repository's agent harness still matches the repository.

Tier 1 (always on): every link in the harness documents, and every backticked
path whose top directory exists, resolves; every backticked task-runner mention (`just test`) names a recipe the
runner has; every knowledge file is referenced from the entrypoint; every
mirror pair agrees on the sections that must match.
Tier 2 (TIER2 below): skill frontmatter and the entrypoint line budget.

Usage:
  python3 scripts/check_harness.py [--root PATH] [--full]
  uv run scripts/check_harness.py

Example:
  python3 scripts/check_harness.py --root .
  python3 scripts/check_harness.py --help

stdout holds JSON: {"count": n, "findings": [{"file", "line", "rule",
"problem", "fix"}, ...]}. stderr holds one "file: rule: problem Fix: fix"
line per finding and every diagnostic. The check is read-only: it never
writes a file.

Exit codes:
  0  no finding
  1  one or more findings
  2  bad arguments or an unusable setting (a configured path is missing, a
     document is not UTF-8, the task runner cannot list its recipes)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

# Settings: facts of this repository. Change them here and nowhere else.
# CONFIGURE: the agent entrypoint, relative to the repository root.
ENTRYPOINT = "AGENTS.md"
# CONFIGURE: directories whose every .md file the entrypoint must reference.
KNOWLEDGE_DIRS: list[str] = [".agents/knowledge"]
# CONFIGURE: further harness documents to check for links, paths, and recipe mentions, e.g. "CLAUDE.md", "ARCHITECTURE.md".
EXTRA_DOCS: list[str] = []
# CONFIGURE: the task runner, "just", "make", or "npm"; None when the project has none.
TASK_RUNNER: str | None = "just"
# CONFIGURE: the file that defines the recipes: "justfile", "Makefile", or "package.json".
RUNNER_FILE = "justfile"
# CONFIGURE: copies that cannot become references, as (source file, corrected file, sections); the first file wins a disagreement; a section is (heading line in the first, heading line in the second); [] compares the whole files.
MIRROR_PAIRS: list[tuple[str, str, list[tuple[str, str]]]] = []
# CONFIGURE: backticked mentions that are deliberately not repository paths (gitignored or generated paths, owner/repo slugs).
IGNORE_PATHS: list[str] = []
# CONFIGURE: True turns on tier 2 (skill frontmatter, entrypoint budget).
TIER2 = False
# CONFIGURE: the entrypoint's line budget, checked by tier 2.
ENTRYPOINT_BUDGET = 120
# CONFIGURE: directories holding project skills as <dir>/<name>/SKILL.md, checked by tier 2.
SKILL_DIRS: list[str] = []

SUMMARY_LIMIT = 10_000
SHOWN_WHEN_SUMMARISED = 25
MENTION_PREFIX = {"just": "just", "make": "make", "npm": "npm run"}
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
CODE_SPAN_RE = re.compile(r"`([^`\n]+)`")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
HEADING_RE = re.compile(r"^(#{1,6})\s")
NOT_A_PATH_RE = re.compile(r"[\s<>{}*?$|()\[\]=,;'\"]|://")
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MAKE_TARGET_RE = re.compile(r"^([A-Za-z0-9][^$#/\t=:%\s]*):(?!=)")


class ConfigError(Exception):
    """A setting or an input the check cannot use; exit 2."""


@dataclass
class Settings:
    entrypoint: str
    knowledge_dirs: list[str]
    extra_docs: list[str]
    task_runner: str | None
    runner_file: str
    mirror_pairs: list[tuple[str, str, list[tuple[str, str]]]]
    ignore_paths: list[str]
    tier2: bool
    entrypoint_budget: int
    skill_dirs: list[str]


def configured() -> Settings:
    """The settings block above, read when the check runs."""
    return Settings(
        ENTRYPOINT,
        KNOWLEDGE_DIRS,
        EXTRA_DOCS,
        TASK_RUNNER,
        RUNNER_FILE,
        MIRROR_PAIRS,
        IGNORE_PATHS,
        TIER2,
        ENTRYPOINT_BUDGET,
        SKILL_DIRS,
    )


@dataclass
class Finding:
    file: str
    line: int | None
    rule: str
    problem: str
    fix: str

    def text(self) -> str:
        where = self.file if self.line is None else f"{self.file}:{self.line}"
        return f"{where}: {self.rule}: {self.problem} Fix: {self.fix}"


def read(root: Path, rel: str) -> str:
    try:
        return (root / rel).read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ConfigError(
            f"{rel} is not UTF-8 ({error}); convert it or drop it from the settings."
        ) from error


def require(root: Path, setting: str, rel: str, *, directory: bool = False) -> None:
    path = root / rel
    if not (path.is_dir() if directory else path.is_file()):
        kind = "directory" if directory else "file"
        raise ConfigError(
            f"{setting} names {rel}, which is not an existing {kind}; correct the setting."
        )


def validate(root: Path, s: Settings) -> None:
    require(root, "ENTRYPOINT", s.entrypoint)
    for rel in s.knowledge_dirs:
        require(root, "KNOWLEDGE_DIRS", rel, directory=True)
    for rel in s.extra_docs:
        require(root, "EXTRA_DOCS", rel)
    if s.task_runner is not None:
        if s.task_runner not in MENTION_PREFIX:
            raise ConfigError(
                f'TASK_RUNNER is "{s.task_runner}"; use "just", "make", "npm", or None.'
            )
        require(root, "RUNNER_FILE", s.runner_file)
    for pair in s.mirror_pairs:
        for rel in pair[:2]:
            require(root, "MIRROR_PAIRS", rel)
    for rel in s.skill_dirs:
        require(root, "SKILL_DIRS", rel, directory=True)


def outside_fences(text: str) -> list[tuple[int, str]]:
    """(line number, line) for every line outside fenced code blocks."""
    lines, fenced = [], False
    for number, line in enumerate(text.splitlines(), start=1):
        if FENCE_RE.match(line):
            fenced = not fenced
            continue
        if not fenced:
            lines.append((number, line))
    return lines


def claims_path(root: Path, doc: str, token: str) -> bool:
    """A backticked span counts as a path when it has two segments and its
    first segment exists, so `scripts/old.py` is checked and `owner/repo`
    or a bare `SKILL.md` is not."""
    if (
        NOT_A_PATH_RE.search(token)
        or token[0] in "-@~/#"
        or "/" not in token.rstrip("/")
    ):
        return False
    top = token.split("/")[0]
    return (root / top).exists() or (root / doc).parent.joinpath(top).exists()


def exists_from(root: Path, doc: str, target: str) -> bool:
    target = re.sub(r":\d+$", "", target.split("#")[0])
    return (root / doc).parent.joinpath(target).exists() or (root / target).exists()


def list_recipes(root: Path, s: Settings) -> set[str]:
    if s.task_runner == "npm":
        try:
            scripts = json.loads(read(root, s.runner_file)).get("scripts", {})
        except json.JSONDecodeError as error:
            raise ConfigError(
                f"{s.runner_file} is not valid JSON ({error})."
            ) from error
        return set(scripts)
    command = (
        ["just", "--justfile", s.runner_file, "--summary"]
        if s.task_runner == "just"
        else ["make", "-f", s.runner_file, "-pRrq", ":"]
    )
    try:
        result = subprocess.run(
            command, cwd=root, capture_output=True, text=True, check=False
        )
    except FileNotFoundError as error:
        raise ConfigError(
            f"{command[0]} is not installed; install it or set TASK_RUNNER = None."
        ) from error
    if s.task_runner == "just":
        if result.returncode != 0:
            raise ConfigError(
                f"{' '.join(command)} exited {result.returncode}: {result.stderr.strip()}"
            )
        return set(result.stdout.split())
    recipes, not_target = set(), False
    for line in result.stdout.splitlines():
        match = MAKE_TARGET_RE.match(line)
        if match and not not_target:
            recipes.add(match.group(1))
        not_target = line.startswith("# Not a target:")
    if not recipes:
        raise ConfigError(
            f"{' '.join(command)} listed no target: {result.stderr.strip()}"
        )
    return recipes


def check_documents(
    root: Path, s: Settings, docs: list[str], findings: list[Finding]
) -> None:
    recipes = list_recipes(root, s) if s.task_runner else set()
    mention = None
    if s.task_runner:
        mention = re.compile(
            rf"^{re.escape(MENTION_PREFIX[s.task_runner])} ([A-Za-z0-9_][\w:.-]*)"
        )
    for doc in docs:
        for number, line in outside_fences(read(root, doc)):
            for target in LINK_RE.findall(line):
                if re.match(r"^(https?:|mailto:|#)", target) or exists_from(
                    root, doc, target
                ):
                    continue
                findings.append(
                    Finding(
                        doc,
                        number,
                        "doc-link",
                        f"link target {target} does not exist.",
                        "correct the path or remove the link.",
                    )
                )
            for span in CODE_SPAN_RE.findall(line):
                found = mention.match(span) if mention else None
                if found and found.group(1) not in recipes:
                    findings.append(
                        Finding(
                            doc,
                            number,
                            "doc-recipe",
                            f"mentions `{span}`, but {s.runner_file} has no recipe {found.group(1)}.",
                            f"add the recipe to {s.runner_file} or correct the document.",
                        )
                    )
                elif (
                    not found
                    and claims_path(root, doc, span)
                    and span not in s.ignore_paths
                    and not exists_from(root, doc, span)
                ):
                    findings.append(
                        Finding(
                            doc,
                            number,
                            "doc-path",
                            f"mentions {span}, which does not exist.",
                            "correct or remove the mention; list it in IGNORE_PATHS only when it is deliberately not a repository path.",
                        )
                    )


def knowledge_files(root: Path, s: Settings) -> list[str]:
    files = set()
    for rel in s.knowledge_dirs:
        files.update(p.relative_to(root).as_posix() for p in (root / rel).rglob("*.md"))
    return sorted(files)


def check_reachable(
    root: Path, s: Settings, files: list[str], findings: list[Finding]
) -> None:
    text = read(root, s.entrypoint)
    base = (root / s.entrypoint).parent
    targets = {(base / t.split("#")[0]).resolve() for t in LINK_RE.findall(text)}
    for rel in files:
        relative_to_entry = Path(os.path.relpath(root / rel, base)).as_posix()
        if (
            rel in text
            or relative_to_entry in text
            or (root / rel).resolve() in targets
        ):
            continue
        findings.append(
            Finding(
                rel,
                None,
                "knowledge-reachable",
                f"is not referenced from {s.entrypoint}.",
                f"add a when-to-read pointer to it in {s.entrypoint}, or delete the file.",
            )
        )


def section(text: str, heading: str) -> str | None:
    lines = text.splitlines()
    for start, line in enumerate(lines):
        if line.rstrip() == heading.rstrip():
            level = (
                len(HEADING_RE.match(line).group(1)) if HEADING_RE.match(line) else 7
            )
            end = start + 1
            while end < len(lines):
                other = HEADING_RE.match(lines[end])
                if other and len(other.group(1)) <= level:
                    break
                end += 1
            return "\n".join(lines[start + 1 : end])
    return None


def neutral(text: str, own_names: set[str]) -> dict[str, set[str] | int]:
    """What a translation keeps unchanged: link targets, code, and table rows."""
    links, code, fenced_lines, rows, fenced = set(), set(), set(), 0, False
    for line in text.splitlines():
        if FENCE_RE.match(line):
            fenced = not fenced
            continue
        if fenced:
            if line.strip():
                fenced_lines.add(line.strip())
            continue
        links.update(
            t
            for t in LINK_RE.findall(line)
            if Path(t.split("#")[0]).name not in own_names
        )
        code.update(CODE_SPAN_RE.findall(line))
        rows += line.lstrip().startswith("|")
    return {
        "link targets": links,
        "code spans": code,
        "code block lines": fenced_lines,
        "table rows": rows,
    }


def check_mirrors(root: Path, s: Settings, findings: list[Finding]) -> None:
    for first, second, sections in s.mirror_pairs:
        texts = (read(root, first), read(root, second))
        names = {Path(first).name, Path(second).name}
        for heading_a, heading_b in sections or [("", "")]:
            parts = (
                [texts[0], texts[1]]
                if not heading_a
                else [section(texts[0], heading_a), section(texts[1], heading_b)]
            )
            label = (
                "the whole file"
                if not heading_a
                else f'section "{heading_a}" / "{heading_b}"'
            )
            missing = [f for f, part in zip((first, second), parts) if part is None]
            if missing:
                findings.append(
                    Finding(
                        missing[0],
                        None,
                        "mirror-pair",
                        f"has no heading for {label} of the mirror pair {first} / {second}.",
                        "restore the heading, or correct the pair in MIRROR_PAIRS if the section was renamed in both.",
                    )
                )
                continue
            a, b = neutral(parts[0], names), neutral(parts[1], names)
            for key in a:
                if a[key] == b[key]:
                    continue
                if isinstance(a[key], int):
                    detail = f"{a[key]} vs {b[key]}"
                else:
                    detail = f"only in {first}: {sorted(a[key] - b[key])[:5]}; only in {second}: {sorted(b[key] - a[key])[:5]}"
                findings.append(
                    Finding(
                        second,
                        None,
                        "mirror-pair",
                        f"{label} differs from {first} in {key} ({detail}).",
                        f"edit {second} to match {first}; {first} is the source side of the mirror pair.",
                    )
                )


def frontmatter(text: str) -> dict[str, str] | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    fields: dict[str, str] = {}
    key = None
    for line in lines[1:]:
        if line.strip() == "---":
            return {k: v.strip().strip("\"'") for k, v in fields.items()}
        match = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", line)
        if match:
            key, value = match.group(1), match.group(2)
            fields[key] = "" if value in (">", ">-", "|", "|-") else value
        elif key and line.startswith((" ", "\t")):
            fields[key] = f"{fields[key]} {line.strip()}".strip()
    return None


def check_tier2(root: Path, s: Settings, findings: list[Finding]) -> None:
    count = len(read(root, s.entrypoint).splitlines())
    if count > s.entrypoint_budget:
        findings.append(
            Finding(
                s.entrypoint,
                None,
                "entrypoint-budget",
                f"has {count} lines; the budget is {s.entrypoint_budget}.",
                "move detail into a knowledge file and leave a when-to-read pointer.",
            )
        )
    for rel in s.skill_dirs:
        for skill in sorted((root / rel).glob("*/SKILL.md")):
            file = skill.relative_to(root).as_posix()
            name = skill.parent.name
            attrs = frontmatter(read(root, file))
            if attrs is None:
                findings.append(
                    Finding(
                        file,
                        1,
                        "skill-frontmatter",
                        "has no frontmatter.",
                        "start the file with --- name / description ---.",
                    )
                )
                continue
            if attrs.get("name") != name:
                findings.append(
                    Finding(
                        file,
                        None,
                        "skill-name",
                        f'name is "{attrs.get("name", "")}", not the directory name.',
                        f"set name: {name}.",
                    )
                )
            elif not SKILL_NAME_RE.match(name) or len(name) > 64:
                findings.append(
                    Finding(
                        file,
                        None,
                        "skill-name",
                        f'"{name}" is not a valid skill name.',
                        "use 1-64 lowercase letters, digits, and single hyphens.",
                    )
                )
            description = attrs.get("description", "")
            if not description or len(description) > 1024:
                findings.append(
                    Finding(
                        file,
                        None,
                        "skill-description",
                        f"description is empty or over 1024 characters ({len(description)}).",
                        "write a 1-1024 character description that names the capability and its triggers.",
                    )
                )


def run(root: Path, s: Settings) -> list[Finding]:
    validate(root, s)
    findings: list[Finding] = []
    files = knowledge_files(root, s)
    docs = list(dict.fromkeys([s.entrypoint, *files, *s.extra_docs]))
    check_documents(root, s, docs, findings)
    check_reachable(root, s, files, findings)
    check_mirrors(root, s, findings)
    if s.tier2:
        check_tier2(root, s, findings)
    else:
        print(
            "check_harness: tier 2 (skill frontmatter, entrypoint budget) is off; set TIER2 = True to run it.",
            file=sys.stderr,
        )
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check the agent harness against the repository it describes.",
        epilog="example: python3 scripts/check_harness.py --root .",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root (default: current directory)",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="print every finding even past 10,000 characters",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if not root.is_dir():
        parser.print_usage(sys.stderr)
        print(f"check_harness: --root {args.root} is not a directory.", file=sys.stderr)
        return 2
    try:
        findings = run(root, configured())
    except ConfigError as error:
        print(f"check_harness: {error}", file=sys.stderr)
        return 2
    report = {"count": len(findings), "findings": [asdict(f) for f in findings]}
    full = json.dumps(report, indent=2, ensure_ascii=False)
    shown = findings
    if not args.full and len(full) > SUMMARY_LIMIT:
        shown = findings[:SHOWN_WHEN_SUMMARISED]
        report = {
            "count": len(findings),
            "findings": [asdict(f) for f in shown],
            "truncated": True,
        }
        print(
            f"check_harness: showing {len(shown)} of {len(findings)} findings; rerun with --full.",
            file=sys.stderr,
        )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    for finding in shown:
        print(finding.text(), file=sys.stderr)
    print(f"check_harness: {len(findings)} finding(s).", file=sys.stderr)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
