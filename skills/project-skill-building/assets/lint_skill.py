#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Lint one Agent Skill: spec compliance plus quality heuristics.

Checks frontmatter fields and budgets, directory structure, body size, link
integrity (broken targets and links that escape the skill), reachability of
bundled files, description quality, leftover template placeholders, and
script hygiene.

Usage:
  python3 lint_skill.py --skill PATH [--json] [--full]
  uv run lint_skill.py --skill PATH

PATH is a skill directory or its SKILL.md file. The standard library is
enough: a small built-in parser reads the flat frontmatter a skill uses, and
PyYAML, when installed, is used only for frontmatter that parser cannot read.

Exit codes:
  0  no errors (warnings may be present; stderr counts them)
  1  one or more errors found, or the SKILL.md does not exist
  2  bad arguments
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

KNOWN_FIELDS = frozenset(
    {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
)
REQUIRED_FIELDS = frozenset({"name", "description"})
ALLOWED_ROOT = frozenset({"SKILL.md", "references", "assets", "scripts"})
BUNDLE_DIRS = ("scripts", "references", "assets")
ALLOWED_SCRIPT_EXTS = frozenset({".py", ".ts"})

NAME_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
FENCE_RE = re.compile(r"^(```|~~~)")
LIST_ITEM_RE = re.compile(r"(?:[-*+]|\d+\.)\s")
CONDITION_WORDS = ("when", "if", "before", "after", "unless", "only")
USE_WHEN_RE = re.compile(r"\buse\b(?:\s+\w+){0,2}\s+when\b")
NOT_FOR_RE = re.compile(r"\bnot\s+for\b")
FILLER_OPENERS = ("this ", "a ", "an ", "helps ", "allows ", "provides ")
FIRST_PERSON_RE = re.compile(r"(?:^|\s)(?:i|my|me)\s")
INTERACTIVE_PY_RE = re.compile(r"(?<![\w.\"'])input\s*\(")
INTERACTIVE_TS_RE = re.compile(r"(?<![\w.\"'])(?:prompt|confirm)\s*\(")
PEP723_RE = re.compile(r"^# /// script\s*$", re.MULTILINE)
PLACEHOLDER_RE = re.compile(r"<([A-Za-z][^<>\n]*)>|\{\{[^{}\n]*\}\}")
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
URL_SCHEME_RE = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*:")
HTML_TAG_RE = re.compile(r"/?([A-Za-z][A-Za-z0-9]*)(?:\s+[^<>]*=[^<>]*)?\s*/?")
HTML_TAGS = frozenset(
    "a abbr b br code del details div em hr i img kbd li ol p pre s small span "
    "strong sub summary sup table tbody td th thead tr u ul".split()
)
TEMPLATE_NAME = "skill-name"
CONFIGURE_MARK = "# CONFIGURE:"

DESCRIPTION_MAX = 1024
DESCRIPTION_WARN_MILD = 600
DESCRIPTION_WARN_STRONG = 900
COMPATIBILITY_MAX = 500
NAME_MAX = 64
BODY_WARN_LINES = 500
BODY_WARN_LINES_STRONG = 1000
BODY_WARN_TOKENS = 5000
OUTPUT_SUMMARY_CHARS = 10_000


def issue(location: str, level: str, reason: str, suggestion: str) -> dict:
    return {
        "location": location,
        "level": level,
        "reason": reason,
        "suggestion": suggestion,
    }


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)


# --- frontmatter -----------------------------------------------------------


class FrontmatterError(ValueError):
    """The frontmatter block is missing or cannot be parsed."""


def split_frontmatter(text: str) -> tuple[list[str], str]:
    """Return (frontmatter lines, body) or raise FrontmatterError."""
    if not text.startswith("---"):
        raise FrontmatterError("missing opening '---'")
    lines = text.splitlines(keepends=True)
    end = next(
        (i for i, line in enumerate(lines[1:], 1) if line.strip() == "---"), None
    )
    if end is None:
        raise FrontmatterError("missing closing '---' delimiter")
    return lines[1:end], "".join(lines[end + 1 :])


def _scalar(raw: str) -> object:
    """Parse a flat YAML scalar: quoted string, boolean, null, number, or plain text."""
    value = raw.strip()
    if value == "":
        return ""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        inner = value[1:-1]
        return (
            inner.replace('\\"', '"') if value[0] == '"' else inner.replace("''", "'")
        )
    lowered = value.lower()
    if lowered in {"true", "yes", "on"}:
        return True
    if lowered in {"false", "no", "off"}:
        return False
    if lowered in {"null", "~"}:
        return None
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?\d+\.\d+", value):
        return float(value)
    return value


def _strip_comment(line: str) -> str:
    """Drop a trailing ' # comment' outside quotes."""
    in_quote = ""
    for i, ch in enumerate(line):
        if in_quote:
            if ch == in_quote:
                in_quote = ""
        elif ch in "\"'":
            in_quote = ch
        elif ch == "#" and (i == 0 or line[i - 1].isspace()):
            return line[:i].rstrip()
    return line


def _block_scalar(indicator: str, block: list[str]) -> str:
    """Fold or keep a block scalar per its indicator ('>', '|', '>-', '|-')."""
    stripped = [line.rstrip("\n") for line in block]
    while stripped and stripped[-1].strip() == "":
        stripped.pop()
    indent = min(
        (len(s) - len(s.lstrip(" ")) for s in stripped if s.strip()), default=0
    )
    lines = [s[indent:] for s in stripped]
    if indicator.startswith("|"):
        text = "\n".join(lines)
    else:
        paragraphs: list[str] = []
        current: list[str] = []
        for line in lines:
            if line.strip() == "":
                paragraphs.append(" ".join(current))
                current = []
            else:
                current.append(line.strip())
        paragraphs.append(" ".join(current))
        text = "\n".join(paragraphs)
    return text if indicator.endswith("-") else text + "\n"


def parse_flat_yaml(lines: list[str]) -> dict:
    """Parse the YAML subset skill frontmatter uses: top-level `key: value`
    pairs, block scalars (`>`, `|`, with optional `-`), and one level of
    nested mapping. Anything else raises FrontmatterError."""
    result: dict = {}
    i = 0
    while i < len(lines):
        raw = lines[i].rstrip("\n")
        if raw.strip() == "" or raw.lstrip().startswith("#"):
            i += 1
            continue
        if raw.startswith((" ", "\t")):
            raise FrontmatterError(
                f"unexpected indentation at line {i + 1}: {raw.strip()!r}"
            )
        if ":" not in raw:
            raise FrontmatterError(f"expected 'key: value' at line {i + 1}: {raw!r}")
        key, _, rest = raw.partition(":")
        key = key.strip()
        rest = _strip_comment(rest.strip())
        if rest in {">", ">-", "|", "|-"}:
            block: list[str] = []
            i += 1
            while i < len(lines) and (
                lines[i].strip() == "" or lines[i].startswith((" ", "\t"))
            ):
                block.append(lines[i])
                i += 1
            result[key] = _block_scalar(rest, block)
            continue
        if rest == "":
            nested: dict = {}
            i += 1
            while i < len(lines) and (
                lines[i].strip() == "" or lines[i].startswith((" ", "\t"))
            ):
                item = lines[i].strip()
                if item and not item.startswith("#"):
                    if item.startswith("-") or ":" not in item:
                        raise FrontmatterError(
                            f"only flat 'key: value' entries are supported under '{key}' (line {i + 1})"
                        )
                    sub_key, _, sub_rest = item.partition(":")
                    nested[sub_key.strip()] = _scalar(_strip_comment(sub_rest))
                i += 1
            result[key] = nested
            continue
        if rest.startswith(("[", "{", "-", "&", "*", "!")):
            raise FrontmatterError(
                f"unsupported YAML syntax for '{key}' at line {i + 1}"
            )
        result[key] = _scalar(rest)
        i += 1
    return result


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Return (frontmatter, body). The built-in parser runs first; PyYAML,
    when importable, handles only what the built-in parser rejects."""
    fm_lines, body = split_frontmatter(text)
    try:
        return parse_flat_yaml(fm_lines), body
    except FrontmatterError as exc:
        builtin_error = exc
    try:
        import yaml
    except ImportError:
        raise builtin_error from None
    try:
        fm = yaml.safe_load("".join(fm_lines))
    except yaml.YAMLError as exc:
        raise FrontmatterError(f"YAML parse error: {exc}") from exc
    if fm is None:
        fm = {}
    if not isinstance(fm, dict):
        raise FrontmatterError("frontmatter must be a YAML mapping")
    return fm, body


# --- text helpers ------------------------------------------------------------


def strip_fenced_code(text: str) -> str:
    """Blank out fenced code blocks so examples inside them are not linted."""
    out: list[str] = []
    in_fence = False
    for line in text.splitlines(keepends=True):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            out.append("\n")
        else:
            out.append(line if not in_fence else "\n")
    return "".join(out)


def split_prose_units(text: str) -> list[str]:
    """Paragraphs and list items as single-line units, so sentence-level
    checks see whole sentences across soft wraps."""
    units: list[str] = []
    current: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            if current:
                units.append(" ".join(current))
                current = []
        elif LIST_ITEM_RE.match(stripped):
            if current:
                units.append(" ".join(current))
            current = [stripped]
        else:
            current.append(stripped)
    if current:
        units.append(" ".join(current))
    return units


# --- checks ------------------------------------------------------------------


def check_frontmatter(base: str, skill_dir: Path, fm: dict) -> list[dict]:
    issues: list[dict] = []
    for key in sorted(fm):
        if key not in KNOWN_FIELDS:
            issues.append(
                issue(
                    f"{base}:frontmatter:{key}",
                    "warning",
                    f"Frontmatter field '{key}' is not in the Agent Skills spec.",
                    f"Spec fields: {', '.join(sorted(KNOWN_FIELDS))}. If '{key}' is a "
                    "host-specific switch, keep it and name the host it targets in the body.",
                )
            )
    for key in sorted(REQUIRED_FIELDS):
        if key not in fm:
            issues.append(
                issue(
                    f"{base}:frontmatter",
                    "error",
                    f"Required field '{key}' is missing.",
                    f"Add '{key}' to the frontmatter block.",
                )
            )

    name = fm.get("name")
    loc = f"{base}:frontmatter:name"
    if name is not None and not isinstance(name, str):
        issues.append(
            issue(
                loc,
                "error",
                f"'name' must be a string, got {type(name).__name__}.",
                "Set 'name' to a lowercase hyphenated string equal to the directory name.",
            )
        )
    elif isinstance(name, str):
        if len(name) > NAME_MAX:
            issues.append(
                issue(
                    loc,
                    "error",
                    f"'name' is {len(name)} chars; maximum is {NAME_MAX}.",
                    f"Shorten the skill name to {NAME_MAX} characters or fewer.",
                )
            )
        if not NAME_RE.fullmatch(name):
            issues.append(
                issue(
                    loc,
                    "error",
                    f"'name' value '{name}' has invalid characters or structure.",
                    "Use only lowercase a-z, digits 0-9, and single hyphens: no leading, "
                    "trailing, or consecutive hyphens ('my-skill', not 'My_Skill' or 'my--skill').",
                )
            )
        if name != skill_dir.name:
            issues.append(
                issue(
                    loc,
                    "error",
                    f"'name' is '{name}' but the directory is '{skill_dir.name}'; they must match.",
                    f"Rename the directory to '{name}' or set name: {skill_dir.name}.",
                )
            )

    issues.extend(check_description(base, fm.get("description")))

    compat = fm.get("compatibility")
    if isinstance(compat, str) and len(compat) > COMPATIBILITY_MAX:
        issues.append(
            issue(
                f"{base}:frontmatter:compatibility",
                "error",
                f"'compatibility' is {len(compat)} chars; maximum is {COMPATIBILITY_MAX}.",
                f"Trim to {COMPATIBILITY_MAX} chars or fewer; state only real environment requirements.",
            )
        )
    meta = fm.get("metadata")
    if meta is not None and not isinstance(meta, dict):
        issues.append(
            issue(
                f"{base}:frontmatter:metadata",
                "error",
                f"'metadata' must be a mapping, got {type(meta).__name__}.",
                "Use a flat mapping:\nmetadata:\n  author: my-org\n  version: '1.0'",
            )
        )
    return issues


def check_description(base: str, desc: object) -> list[dict]:
    issues: list[dict] = []
    loc = f"{base}:frontmatter:description"
    if desc is None:
        return issues
    if not isinstance(desc, str):
        issues.append(
            issue(
                loc,
                "error",
                f"'description' must be a string, got {type(desc).__name__}.",
                "Use a YAML string, optionally with '>' for a folded block scalar.",
            )
        )
        return issues
    if desc.strip() == "":
        issues.append(
            issue(
                loc,
                "error",
                "'description' is empty.",
                "Write the capability in third person, then the triggers ('Use when …').",
            )
        )
        return issues

    length = len(desc)
    if length > DESCRIPTION_MAX:
        issues.append(
            issue(
                loc,
                "error",
                f"'description' is {length} chars; maximum is {DESCRIPTION_MAX}.",
                f"Trim below {DESCRIPTION_MAX}: keep the capability sentence and one trigger per branch.",
            )
        )
    elif length > DESCRIPTION_WARN_STRONG:
        issues.append(
            issue(
                loc,
                "warning",
                f"'description' is {length} chars (>{DESCRIPTION_WARN_STRONG}); it is loaded "
                "into context on every turn.",
                "Cut synonym triggers (keep one per branch) and identity already in the body.",
            )
        )
    elif length > DESCRIPTION_WARN_MILD:
        issues.append(
            issue(
                loc,
                "warning",
                f"'description' is {length} chars (>{DESCRIPTION_WARN_MILD}).",
                "Consider trimming: one trigger per branch, no body identity restated.",
            )
        )

    lowered = desc.lower()
    if not USE_WHEN_RE.search(lowered) and "use this" not in lowered:
        issues.append(
            issue(
                loc,
                "warning",
                "'description' has no 'Use when …' trigger clause.",
                "Add trigger conditions after the capability sentence; the description is "
                "the only text the agent reads before activating.",
            )
        )
    if not NOT_FOR_RE.search(lowered):
        issues.append(
            issue(
                loc,
                "warning",
                "'description' has no 'Not for …' clause.",
                "Name the adjacent tasks that must not fire this skill and who handles them.",
            )
        )
    if lowered.startswith(FILLER_OPENERS):
        issues.append(
            issue(
                loc,
                "warning",
                f"'description' opens with filler ('{desc.split()[0]}').",
                "Front-load the skill's leading word: the action verb or domain concept "
                "that should trigger it.",
            )
        )
    if FIRST_PERSON_RE.search(lowered):
        issues.append(
            issue(
                loc,
                "warning",
                "'description' uses first person.",
                "Write in third person: capability first, then triggers.",
            )
        )
    return issues


def _placeholders(text: str) -> list[str]:
    """Template placeholders left in prose: `<...>` or `{{...}}` outside
    fenced code, inline code, HTML tags, autolinks, and `# CONFIGURE:` lines."""
    kept = "\n".join(line for line in text.splitlines() if CONFIGURE_MARK not in line)
    found: list[str] = []
    for unit in split_prose_units(strip_fenced_code(kept)):
        for match in PLACEHOLDER_RE.finditer(INLINE_CODE_RE.sub("", unit)):
            inner = match.group(1)
            if inner is not None:
                if URL_SCHEME_RE.match(inner):
                    continue
                tag = HTML_TAG_RE.fullmatch(inner)
                if tag and tag.group(1).lower() in HTML_TAGS:
                    continue
            found.append(match.group(0))
    return found


def check_placeholders(base: str, fm: dict, body: str) -> list[dict]:
    issues: list[dict] = []
    if fm.get("name") == TEMPLATE_NAME:
        issues.append(
            issue(
                f"{base}:frontmatter:name",
                "error",
                f"'name' is still the template value '{TEMPLATE_NAME}'.",
                "Set 'name' to the skill's own name and rename the directory to match.",
            )
        )
    for key in sorted(fm):
        value = fm[key]
        if isinstance(value, str):
            for found in _placeholders(value):
                issues.append(
                    issue(
                        f"{base}:frontmatter:{key}",
                        "error",
                        f"Template placeholder left in '{key}': {found[:80]}",
                        "Replace it with the skill's real text, or drop the field.",
                    )
                )
    for found in _placeholders(body):
        issues.append(
            issue(
                f"{base}:body",
                "error",
                f"Template placeholder left in the body: {found[:80]}",
                "Rework the line with the skill's real content; wrap literal angle-bracket "
                "examples in backticks, and keep {{NAME}} only on '# CONFIGURE:' lines.",
            )
        )
    return issues


def check_body_size(base: str, body: str) -> list[dict]:
    lines = len(body.splitlines())
    est_tokens = len(body) // 4
    if lines > BODY_WARN_LINES_STRONG:
        return [
            issue(
                f"{base}:body",
                "warning",
                f"Body is {lines} lines (>{BODY_WARN_LINES_STRONG}); attention thins across the excess.",
                "This is sprawl: disclose branch-specific content into references/ behind "
                "conditional pointers, or split the skill by branch or sequence.",
            )
        ]
    if lines > BODY_WARN_LINES or est_tokens > BODY_WARN_TOKENS:
        return [
            issue(
                f"{base}:body",
                "warning",
                f"Body is {lines} lines / ~{est_tokens} tokens "
                f"(recommended <{BODY_WARN_LINES} lines and <{BODY_WARN_TOKENS} tokens).",
                "Move content needed only on some branches to references/<file>.md with a "
                "conditional load instruction.",
            )
        ]
    return []


def check_structure(skill_dir: Path) -> list[dict]:
    issues: list[dict] = []
    base = rel(skill_dir)
    for entry in sorted(skill_dir.iterdir()):
        if entry.name in ALLOWED_ROOT:
            continue
        loc = f"{base}/{entry.name}"
        if entry.name == "README.md":
            issues.append(
                issue(
                    loc,
                    "error",
                    "README.md found in the skill root.",
                    "SKILL.md is the skill's one entry point; the description covers discovery. "
                    "Move the content into SKILL.md or a reference and delete README.md.",
                )
            )
        elif entry.name.startswith("."):
            issues.append(
                issue(
                    loc,
                    "warning",
                    f"Hidden entry '{entry.name}' in the skill root.",
                    "Skill roots hold only SKILL.md, scripts/, references/, assets/. "
                    "Remove it unless required at runtime.",
                )
            )
        else:
            issues.append(
                issue(
                    loc,
                    "warning",
                    f"Unexpected entry '{entry.name}' in the skill root.",
                    "Move it into scripts/, references/, or assets/, or remove it.",
                )
            )
    for sub in BUNDLE_DIRS:
        sub_dir = skill_dir / sub
        if sub_dir.is_dir() and not any(sub_dir.iterdir()):
            issues.append(
                issue(
                    f"{base}/{sub}/",
                    "warning",
                    f"'{sub}/' is empty.",
                    "An empty directory misleads agents into expecting files. Delete it until a file goes in.",
                )
            )
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.is_dir():
        for entry in sorted(scripts_dir.iterdir()):
            loc = f"{base}/scripts/{entry.name}"
            if entry.is_dir():
                issues.append(
                    issue(
                        f"{loc}/",
                        "warning",
                        f"Subdirectory '{entry.name}' inside scripts/.",
                        "Keep scripts/ flat: inline shared logic into the scripts that use it.",
                    )
                )
                continue
            ext = entry.suffix.lower()
            if ext == ".js":
                issues.append(
                    issue(
                        loc,
                        "warning",
                        f"'{entry.name}' is plain JavaScript.",
                        "Use TypeScript (.ts): Deno and Bun run it natively with type safety.",
                    )
                )
            elif ext in {".sh", ".ps1"}:
                issues.append(
                    issue(
                        loc,
                        "warning",
                        f"'{entry.name}' runs only where its shell exists.",
                        "Rewrite in Python (PEP 723) or TypeScript (Deno/Bun), or name the "
                        "requirement in the 'compatibility' field.",
                    )
                )
            elif ext not in ALLOWED_SCRIPT_EXTS:
                issues.append(
                    issue(
                        loc,
                        "warning",
                        f"Unexpected file type '{ext}' in scripts/.",
                        "Use .py or .ts; remove or convert other files.",
                    )
                )
    return issues


def linked_md_files(skill_dir: Path, skill_body: str) -> list[Path]:
    """Markdown files inside the skill that SKILL.md links directly."""
    out: list[Path] = []
    for match in MD_LINK_RE.finditer(strip_fenced_code(skill_body)):
        target = match.group(1).split("#", 1)[0]
        if not target or target.startswith(
            ("http://", "https://", "mailto:", "/", "../")
        ):
            continue
        resolved = (skill_dir / target).resolve()
        if resolved.suffix == ".md" and resolved.is_file() and resolved not in out:
            out.append(resolved)
    return out


def check_links(skill_dir: Path, skill_body: str) -> list[dict]:
    """Self-containment and broken-target checks over SKILL.md, every
    references/*.md, and every markdown file SKILL.md links."""
    issues: list[dict] = []
    skill_md = skill_dir / "SKILL.md"
    md_files = [skill_md, *sorted(skill_dir.glob("references/*.md"))]
    for extra in linked_md_files(skill_dir, skill_body):
        if extra not in md_files:
            md_files.append(extra)
    skill_root = skill_dir.resolve()
    for md in md_files:
        if not md.exists():
            continue
        text = strip_fenced_code(md.read_text(encoding="utf-8"))
        loc = rel(md)
        for match in MD_LINK_RE.finditer(text):
            target = match.group(1)
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path_part = target.split("#", 1)[0]
            resolved = (md.parent / path_part).resolve()
            if target.startswith("/") or skill_root not in (
                resolved,
                *resolved.parents,
            ):
                issues.append(
                    issue(
                        f"{loc}:link:{target}",
                        "error",
                        f"Link '{target}' escapes the skill directory.",
                        "Skills are installed by copying the directory; outside links break. "
                        "Bundle the material inside the skill or link a URL.",
                    )
                )
                continue
            if not resolved.exists():
                issues.append(
                    issue(
                        f"{loc}:link:{target}",
                        "error",
                        f"Link target '{target}' does not exist.",
                        "A broken pointer has zero reach. Fix the path or create the file.",
                    )
                )
    return issues


def check_reachability(skill_dir: Path, skill_body: str) -> list[dict]:
    """Every bundled file is mentioned by SKILL.md or by a markdown file
    SKILL.md links (one hop), and every reference pointer carries a condition."""
    issues: list[dict] = []
    base = rel(skill_dir)
    body_no_code = strip_fenced_code(skill_body)
    haystack = skill_body + "".join(
        md.read_text(encoding="utf-8") for md in linked_md_files(skill_dir, skill_body)
    )
    for sub in BUNDLE_DIRS:
        sub_dir = skill_dir / sub
        if not sub_dir.is_dir():
            continue
        for entry in sorted(sub_dir.iterdir()):
            if not entry.is_file() or entry.name.endswith("_test.py"):
                continue
            ref = f"{sub}/{entry.name}"
            if ref not in haystack:
                issues.append(
                    issue(
                        f"{base}/{ref}",
                        "error",
                        f"'{ref}' is not reachable from SKILL.md.",
                        "Orphaned files are unreachable sediment. Link it with a relative "
                        "markdown link at first mention (in SKILL.md or a file SKILL.md links), or delete it.",
                    )
                )
    for unit in split_prose_units(body_no_code):
        if "references/" not in unit or not MD_LINK_RE.search(unit):
            continue
        if not any(word in unit.lower() for word in CONDITION_WORDS):
            snippet = unit if len(unit) <= 100 else unit[:97] + "..."
            issues.append(
                issue(
                    f"{rel(skill_dir / 'SKILL.md')}:pointer",
                    "warning",
                    f"Reference pointer without a load condition: {snippet!r}.",
                    "Pointer wording decides reach. State the condition: "
                    "'Read references/<file>.md when <condition>.'",
                )
            )
    return issues


def check_script_hygiene(skill_dir: Path) -> list[dict]:
    issues: list[dict] = []
    for sub in ("scripts", "assets"):
        sub_dir = skill_dir / sub
        if not sub_dir.is_dir():
            continue
        for entry in sorted(sub_dir.iterdir()):
            if not entry.is_file() or entry.suffix not in ALLOWED_SCRIPT_EXTS:
                continue
            if entry.name.endswith("_test.py"):
                continue
            loc = f"{rel(skill_dir)}/{sub}/{entry.name}"
            text = entry.read_text(encoding="utf-8", errors="replace")
            pattern = INTERACTIVE_PY_RE if entry.suffix == ".py" else INTERACTIVE_TS_RE
            if pattern.search(strip_fenced_code(text) if sub == "assets" else text):
                issues.append(
                    issue(
                        loc,
                        "warning",
                        "Script appears to call an interactive prompt builtin.",
                        "Agents run in non-interactive shells where prompts hang forever. "
                        "Accept all input through CLI flags.",
                    )
                )
            if not text.startswith("#!"):
                issues.append(
                    issue(
                        loc,
                        "warning",
                        "Script has no shebang line.",
                        "Start with '#!/usr/bin/env python3' (stdlib only) or "
                        "'#!/usr/bin/env -S uv run --script'.",
                    )
                )
            if entry.suffix == ".py" and not PEP723_RE.search(text):
                issues.append(
                    issue(
                        loc,
                        "warning",
                        "Python script has no PEP 723 '# /// script' block.",
                        "Declare requires-python and pinned dependencies inline so uv and "
                        "plain python3 agree on the runtime.",
                    )
                )
            if "--help" not in text:
                issues.append(
                    issue(
                        loc,
                        "warning",
                        "Script never mentions --help.",
                        "Accept --help with a usage example; agents read it before running the script.",
                    )
                )
    return issues


def lint(skill_md: Path) -> list[dict]:
    skill_dir = skill_md.parent
    base = rel(skill_md)
    text = skill_md.read_text(encoding="utf-8")
    try:
        fm, body = parse_frontmatter(text)
    except FrontmatterError as exc:
        return [
            issue(
                f"{base}:frontmatter",
                "error",
                f"Cannot parse frontmatter: {exc}.",
                "SKILL.md must begin with '---', hold flat 'key: value' lines (block scalars "
                "with '>' or '|' allowed), and close the block with '---' on its own line.",
            )
        ]
    issues: list[dict] = []
    issues += check_frontmatter(base, skill_dir, fm)
    issues += check_placeholders(base, fm, body)
    issues += check_body_size(base, body)
    issues += check_structure(skill_dir)
    issues += check_links(skill_dir, body)
    issues += check_reachability(skill_dir, body)
    issues += check_script_hygiene(skill_dir)
    return issues


# --- CLI ---------------------------------------------------------------------


def format_human(skill_md: Path, issues: list[dict], full: bool) -> str:
    if not issues:
        return f"OK  {rel(skill_md.parent)}: all checks passed.\n"
    blocks = []
    for item in issues:
        label = "ERROR  " if item["level"] == "error" else "WARNING"
        blocks.append(
            f"{label}  [{item['location']}]\n"
            f"           Reason:     {item['reason']}\n"
            f"           Suggestion: {item['suggestion']}\n"
        )
    text = "\n".join(blocks)
    if full or len(text) <= OUTPUT_SUMMARY_CHARS:
        return text
    kept: list[str] = []
    size = 0
    for block in blocks:
        if size + len(block) > OUTPUT_SUMMARY_CHARS:
            break
        kept.append(block)
        size += len(block) + 1
    omitted = len(blocks) - len(kept)
    return (
        "\n".join(kept)
        + f"\n... {omitted} more finding(s) omitted; rerun with --full or --json.\n"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Lint an Agent Skill: spec compliance plus quality heuristics.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Example:\n"
            "  python3 lint_skill.py --skill .agents/skills/release-procedure\n"
            "  uv run lint_skill.py --skill .agents/skills/release-procedure --json\n\n"
            "Exit codes: 0 no errors (stderr counts warnings); 1 errors found or SKILL.md\n"
            "missing; 2 bad arguments. Runs on the standard library; PyYAML is optional."
        ),
    )
    parser.add_argument(
        "--skill",
        required=True,
        metavar="PATH",
        help="A skill directory or its SKILL.md file.",
    )
    parser.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        help="Print findings as a JSON array (location, level, reason, suggestion).",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Print every finding even when the output exceeds ~10,000 characters.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    path = Path(args.skill).resolve()
    if path.is_dir():
        skill_md = path / "SKILL.md"
    elif path.name == "SKILL.md":
        skill_md = path
    else:
        parser.error(
            f"--skill must be a skill directory or a SKILL.md file. Got: {args.skill!r}"
        )
    if not skill_md.exists():
        print(f"Error: '{skill_md}' does not exist.", file=sys.stderr)
        return 1

    issues = lint(skill_md)
    errors = [i for i in issues if i["level"] == "error"]
    if args.json_output:
        print(json.dumps(issues, indent=2))
    else:
        sys.stdout.write(format_human(skill_md, issues, args.full))
    if errors:
        print(f"{len(errors)} error(s) found.", file=sys.stderr)
        return 1
    if issues:
        print(f"{len(issues)} warning(s).", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
