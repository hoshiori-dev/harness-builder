#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Report on the OpenSpec changes a pull or merge request touches.

The project's own management script for its OpenSpec request automation:
the check job and the label job call it at scripts/spec_changes.py. Nothing
here edits the working tree; archiving is a person's command on the branch.

Commands:
  snapshot  read a GitHub pull request's related changes through the REST API
            into one JSON document, without checking out or fetching the head
  check     strict validation, then the archive verdict
  status    the related changes, their state, documents, and task progress
  labels    the spec:* state label and the label and record changes it implies

A request's *related changes* are the directories under the changes
directory (default openspec/changes) whose files the request touches; an
archive directory counts under its change name without the YYYY-MM-DD- prefix.
status and labels read the head from --base/--head (git plumbing) or from
--snapshot; a privileged job uses --snapshot only.

Exit codes: 0 success; 1 a finding or a failure; 2 bad arguments.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path

PENDING, APPROVED, ARCHIVED = "spec:pending", "spec:approved", "spec:archived"
STATE_LABELS = (PENDING, APPROVED, ARCHIVED)
WRITE_PERMISSIONS = ("admin", "maintain", "write")
RECORD_MARKER = "<!-- spec-approval-record -->"
RECORD_AUTHOR = "github-actions[bot]"
SNAPSHOT_SCHEMA = "spec-snapshot/1"
OUTPUT_LIMIT = 10_000

OPEN_TASK = re.compile(r"^[ \t]*-[ \t]*\[ \][ \t]*(.*)$", re.MULTILINE)
DONE_TASK = re.compile(r"^[ \t]*-[ \t]*\[[xX]\]", re.MULTILINE)
SKIP_SPECS = re.compile(r"^skip_specs[ \t]*:[ \t]*true[ \t]*$", re.MULTILINE)
ARCHIVE_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}-")
SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")
SAFE_REPO = re.compile(r"^[A-Za-z0-9._-]{1,100}/[A-Za-z0-9._-]{1,100}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
HASH_RE = re.compile(r"^[0-9a-f]{64}$")
LOGIN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,254}$")
EVENT_RE = re.compile(r"^[A-Za-z0-9._:-]{1,64}$")
# Only these documents are fetched as text; every other blob is hashed by its sha.
TEXT_DOCS = ("tasks.md", ".openspec.yaml")
MAX_FILES, MAX_FILE_BYTES, MAX_TOTAL_BYTES, MAX_CALLS = 3000, 1_000_000, 8_000_000, 200


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

    request = None

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


class SnapshotSource:
    """Base and head replayed from a snapshot document; the head's bytes are parsed, never run."""

    KEYS = {
        ("changed_paths",): list,
        ("base", "sha"): str,
        ("base", "dirs"): list,
        ("head", "sha"): str,
        ("head", "dirs"): list,
        ("head", "blobs"): dict,
        ("head", "files"): dict,
        ("request", "labels"): list,
    }

    def __init__(self, path: Path, changes_dir: str) -> None:
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise Failure(f"cannot read the snapshot {path}: {exc}") from exc
        if not isinstance(doc, dict) or doc.get("schema") != SNAPSHOT_SCHEMA:
            raise Failure(
                f"{path} is not a {SNAPSHOT_SCHEMA} document; rebuild it with the snapshot command."
            )
        if doc.get("changes_dir") != changes_dir:
            raise Failure(
                f"{path} was built for {doc.get('changes_dir')!r}, not {changes_dir!r}; rebuild it."
            )
        for keys, kind in self.KEYS.items():
            value = doc
            for key in keys:
                value = value.get(key) if isinstance(value, dict) else None
            if not isinstance(value, kind):
                raise Failure(
                    f"{path}: `{'.'.join(keys)}` is missing or has the wrong type; rebuild it."
                )
        self.doc = doc
        self.base_sha, self.head_sha = doc["base"]["sha"], doc["head"]["sha"]
        self.request = doc["request"]

    def changed_paths(self) -> list[str]:
        return list(self.doc["changed_paths"])

    def dirs(self, side: str) -> list[str]:
        return sorted(self.doc[side]["dirs"])

    def blobs(self, path: str) -> dict[str, str]:
        return {
            p: s
            for p, s in self.doc["head"]["blobs"].items()
            if p.startswith(f"{path}/")
        }

    def text(self, path: str) -> str | None:
        return self.doc["head"]["files"].get(path)


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


def package_hash(source, changes: list[dict]) -> str:
    """sha256 over "path blob-sha" of every file of the active changes except tasks.md (written after approval)."""
    lines = []
    for c in changes:
        if c["state"] == "active":
            lines += [
                f"{p} {s}"
                for p, s in source.blobs(c["path"]).items()
                if p != f"{c['path']}/tasks.md"
            ]
    return hashlib.sha256("\n".join(sorted(lines)).encode("utf-8")).hexdigest()


# --- approval record -----------------------------------------------------


def valid_record(data: object) -> dict | None:
    """The record's fields when ``data`` is a well-formed approval record, else None."""
    if not isinstance(data, dict) or data.get("status") not in (
        "approved",
        "withdrawn",
    ):
        return None
    checks = ((COMMIT_RE, "commit"), (LOGIN_RE, "by"), (HASH_RE, "hash"))
    if not all(isinstance(data.get(k), str) and rx.match(data[k]) for rx, k in checks):
        return None
    event = data.get("event")
    if event is not None and not (isinstance(event, str) and EVENT_RE.match(event)):
        return None
    return {k: data.get(k) for k in ("status", "commit", "by", "hash", "event")}


def parse_record(body: str) -> dict | None:
    """The record a record comment carries, or None when the body is not a well-formed record."""
    if not body.startswith(RECORD_MARKER):
        return None
    start, end = body.find("{"), body.rfind("}")
    try:
        return valid_record(json.loads(body[start : end + 1])) if start != -1 else None
    except ValueError:
        return None


def record_body(record: dict) -> str:
    fields = {k: record[k] for k in ("status", "commit", "by", "hash", "event")}
    if record["status"] == "approved":
        note = (
            f"Approved by {record['by']} at {record['commit']}. The label job keeps `{APPROVED}` while the "
            f"package (every file of the unarchived changes but tasks.md) hashes the same."
        )
    else:
        note = f"Withdrawn: {record.get('note', 'the approval no longer holds')}. Re-add `{APPROVED}` to approve again."
    return f"{RECORD_MARKER}\n{note}\n\n```json\n{json.dumps(fields, sort_keys=True)}\n```\n"


def decide_labels(
    source,
    changes_dir: str,
    current: list[str],
    record: dict | None,
    event: dict | None,
) -> dict:
    changes = related_changes(source, changes_dir)
    active = [c for c in changes if c["state"] == "active"]
    result = {
        "changes": [c["name"] for c in changes],
        "package_hash": None,
        "record": None,
    }
    if not changes or (
        not active and not any(c["state"] == "archived" for c in changes)
    ):
        state, reason = None, "no related OpenSpec change"
    elif not active:
        state, reason = ARCHIVED, "every related change is archived"
    else:
        digest = package_hash(source, changes)
        result["package_hash"] = digest
        names = ", ".join(c["name"] for c in active)
        new_event = bool(event) and not (
            record and event.get("id") and record.get("event") == event["id"]
        )
        problem = None
        if APPROVED not in current:
            problem = f"`{APPROVED}` is not on the request"
        elif new_event:
            if event["permission"] not in WRITE_PERMISSIONS:
                problem = (
                    f"{event['by']} has {event['permission']} permission, below write"
                )
            elif event.get("commit") and event["commit"] != source.head_sha:
                problem = f"the head moved past {event['commit']}, the commit the approval named"
        elif not record or record["status"] != "approved":
            problem = "no standing approval record"
        elif record["hash"] != digest:
            problem = f"the package changed since the approval at {record['commit']}"
        if problem is None and new_event:
            state, reason = (
                APPROVED,
                f"{names}: approved by {event['by']} at {source.head_sha}",
            )
            fresh = {
                "status": "approved",
                "commit": source.head_sha,
                "by": event["by"],
                "hash": digest,
            }
            fresh["event"] = event.get("id")
            result["record"] = {
                "id": (record or {}).get("id"),
                "body": record_body(fresh),
                **fresh,
            }
        elif problem is None:
            state, reason = (
                APPROVED,
                f"{names}: the approval at {record['commit']} by {record['by']} stands",
            )
        else:
            state, reason = PENDING, f"{names}: {problem}"
            if record and record["status"] == "approved":
                spent = {**record, "status": "withdrawn", "note": problem}
                result["record"] = {
                    "id": record.get("id"),
                    "body": record_body(spent),
                    **spent,
                }
    result.update(
        state=state,
        reason=reason,
        add=[state] if state and state not in current else [],
        remove=[label for label in STATE_LABELS if label in current and label != state],
    )
    return result


# --- github rest api (snapshot) ------------------------------------------


class Api:
    """The REST reads the snapshot needs; max_calls bounds what one request can spend of the shared budget."""

    def __init__(self, repo: str, api_url: str, token: str, max_calls: int) -> None:
        self.repo, self.api_url, self.token, self.max_calls, self.calls = (
            repo,
            api_url.rstrip("/"),
            token,
            max_calls,
            0,
        )

    def fetch(self, endpoint: str) -> bytes:
        # Imported here: only snapshot needs HTTP, and some minimal Pythons ship without it.
        import urllib.error
        import urllib.request

        request = urllib.request.Request(
            f"{self.api_url}/{endpoint}",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "spec-changes",
            },
        )
        for attempt in range(1, 4):
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    return response.read()
            except urllib.error.HTTPError as exc:
                if exc.code == 404:
                    raise LookupError(endpoint) from exc
                if exc.code not in (429, 500, 502, 503, 504) or attempt == 3:
                    detail = exc.read().decode("utf-8", "replace")[:200]
                    raise Failure(
                        f"GET {endpoint} answered HTTP {exc.code}: {detail}"
                    ) from exc
            except urllib.error.URLError as exc:
                if attempt == 3:
                    raise Failure(
                        f"cannot reach {self.api_url} for GET {endpoint}: {exc.reason}"
                    ) from exc
            time.sleep(2**attempt)
        raise Failure(f"GET {endpoint} kept failing")

    def get(self, endpoint: str, kind: type):
        if self.calls >= self.max_calls:
            raise Failure(
                f"the --max-calls cap ({self.max_calls}) was reached at GET {endpoint}; no snapshot written."
            )
        self.calls += 1
        try:
            data = json.loads(self.fetch(endpoint))
        except ValueError as exc:
            raise Failure(f"GET {endpoint} did not return JSON: {exc}") from exc
        if not isinstance(data, kind):
            raise Failure(
                f"GET {endpoint} returned {type(data).__name__}, not {kind.__name__}; no snapshot written."
            )
        return data

    def pages(self, endpoint: str, cap: int) -> list:
        items: list = []
        page = 1
        while True:
            batch = self.get(
                f"{endpoint}{'&' if '?' in endpoint else '?'}per_page=100&page={page}",
                list,
            )
            items += batch
            if len(batch) < 100 or len(items) > cap:
                return items
            page += 1

    def tree(self, sha: str, path: str, recursive: bool = False) -> list[dict]:
        quoted = urllib.parse.quote(sha, safe="")
        data = self.get(
            f"repos/{self.repo}/git/trees/{quoted}{'?recursive=1' if recursive else ''}",
            dict,
        )
        if data.get("truncated") is not False or not isinstance(data.get("tree"), list):
            raise Failure(
                f"the tree of {path} came back truncated or malformed; no snapshot written."
            )
        return data["tree"]


def snapshot_dirs(api: Api, commit: str, changes_dir: str) -> dict[str, str]:
    """Tree shas of the change directories (active and archived) at a commit, by path."""
    entries = api.tree(commit, f"commit {commit}")
    walked = []
    for segment in changes_dir.split("/"):
        walked.append(segment)
        match = next(
            (
                e
                for e in entries
                if e.get("path") == segment and e.get("type") == "tree"
            ),
            None,
        )
        if match is None:
            return {}
        entries = api.tree(match["sha"], "/".join(walked))
    found = {
        f"{changes_dir}/{e['path']}": e["sha"]
        for e in entries
        if e.get("type") == "tree"
    }
    archive = f"{changes_dir}/archive"
    if archive in found:
        for e in api.tree(found[archive], archive):
            if e.get("type") == "tree":
                found[f"{archive}/{e['path']}"] = e["sha"]
    return found


def build_snapshot(
    api: Api, number: int, changes_dir: str, approver: str | None, caps: dict
) -> dict:
    pull = api.get(f"repos/{api.repo}/pulls/{number}", dict)
    try:
        base_sha, head_sha, count = (
            pull["base"]["sha"],
            pull["head"]["sha"],
            int(pull["changed_files"]),
        )
        labels = [label["name"] for label in pull["labels"]]
    except (KeyError, TypeError, ValueError) as exc:
        raise Failure(
            f"pull request {number} lacks {exc}; no snapshot written."
        ) from exc
    changed: list[str] = []
    files = api.pages(f"repos/{api.repo}/pulls/{number}/files", caps["max_files"])
    for item in files:
        changed.append(item["filename"])
        if item.get(
            "previous_filename"
        ):  # a rename: git diff --no-renames reports both paths
            changed.append(item["previous_filename"])
    if len(files) > caps["max_files"] or len(files) < count:
        raise Failure(
            f"the request lists {len(files)} of {count} changed files (cap {caps['max_files']}); "
            "no snapshot written. Split the request."
        )
    base, head = (
        snapshot_dirs(api, base_sha, changes_dir),
        snapshot_dirs(api, head_sha, changes_dir),
    )
    blobs: dict[str, str] = {}
    texts: dict[str, str] = {}
    total = 0
    for name in change_names(changed, changes_dir):
        if not SAFE_NAME.match(name):
            raise Failure(
                f"{changes_dir}/{name!r} is not a plain change name; no snapshot written."
            )
        _, path = locate(list(head), changes_dir, name)
        if path is None:
            continue
        for entry in api.tree(head[path], path, recursive=True):
            if entry.get("type") != "blob":
                continue
            full = f"{path}/{entry['path']}"
            blobs[full] = entry["sha"]
            if entry["path"] not in TEXT_DOCS:
                continue
            size = int(entry.get("size", 0))
            if size > caps["max_file_bytes"] or total + size > caps["max_total_bytes"]:
                raise Failure(
                    f"{full} ({size} bytes) reaches a byte cap; no snapshot written."
                )
            data = api.get(
                f"repos/{api.repo}/git/blobs/{urllib.parse.quote(entry['sha'], safe='')}",
                dict,
            )
            try:
                texts[full] = base64.b64decode(data["content"]).decode("utf-8")
            except (KeyError, binascii.Error, UnicodeDecodeError) as exc:
                raise Failure(
                    f"{full} cannot be decoded as UTF-8 text ({exc}); no snapshot written."
                ) from exc
            total += size
    record = None
    for comment in api.pages(f"repos/{api.repo}/issues/{number}/comments", 1000):
        author = (comment.get("user") or {}).get("login")
        parsed = (
            parse_record(comment.get("body") or "") if author == RECORD_AUTHOR else None
        )
        if parsed and (record is None or comment["id"] > record["id"]):
            record = {"id": comment["id"], **parsed}
    approver_doc = None
    if approver:
        try:
            level = api.get(
                f"repos/{api.repo}/collaborators/{urllib.parse.quote(approver)}/permission",
                dict,
            )
            permission = level.get("permission", "none")
        except LookupError:
            permission = "none"
        approver_doc = {"login": approver, "permission": permission}
    return {
        "schema": SNAPSHOT_SCHEMA,
        "repo": api.repo,
        "pull_request": number,
        "changes_dir": changes_dir,
        "changed_paths": sorted(set(changed)),
        "base": {"sha": base_sha, "dirs": sorted(base)},
        "head": {"sha": head_sha, "dirs": sorted(head), "blobs": blobs, "files": texts},
        "request": {"labels": labels, "record": record, "approver": approver_doc},
    }


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


def snapshot_summary(doc: dict) -> dict:
    return {
        "documents": len(doc["head"]["blobs"]),
        "texts": len(doc["head"]["files"]),
        "head": doc["head"]["sha"],
    }


def plain_summary(data: dict) -> dict:
    return {
        k: (v if not isinstance(v, (list, dict)) else f"{len(v)} item(s) omitted")
        for k, v in data.items()
    }


# --- commands ------------------------------------------------------------


def source_from(args: argparse.Namespace, root: Path, changes_dir: str):
    if args.snapshot and (args.base or args.head):
        raise Usage("--snapshot replaces --base/--head; pass one source.")
    if args.snapshot:
        return SnapshotSource(Path(args.snapshot), changes_dir)
    if not (args.base and args.head):
        raise Usage(f"{args.command} needs --base with --head, or --snapshot.")
    return GitSource(root, args.base, args.head, changes_dir)


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


def cmd_snapshot(args: argparse.Namespace, root: Path, changes_dir: str) -> int:
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise Failure("snapshot needs a token in GH_TOKEN or GITHUB_TOKEN.")
    api = Api(args.repo, args.api_url, token, args.max_calls)
    caps = {
        "max_files": args.max_files,
        "max_file_bytes": args.max_file_bytes,
        "max_total_bytes": args.max_total_bytes,
    }
    emit(
        build_snapshot(api, args.pr, changes_dir, args.approver, caps),
        args,
        snapshot_summary,
    )
    return 0


def cmd_status(args: argparse.Namespace, root: Path, changes_dir: str) -> int:
    source = source_from(args, root, changes_dir)
    data = {
        "base": source.base_sha,
        "head": source.head_sha,
        "changes": related_changes(source, changes_dir),
    }
    emit(data, args, status_summary)
    return 0


def cmd_check(args: argparse.Namespace, root: Path, changes_dir: str) -> int:
    if args.all and (args.base or args.head):
        raise Usage(
            "check --all reads the working tree; do not pass --base/--head with it."
        )
    if not args.all and not (args.base and args.head):
        raise Usage("check needs --base with --head, or --all.")
    source = None if args.all else GitSource(root, args.base, args.head, changes_dir)
    validated = args.no_validate or run_validator(root, args.openspec)
    warnings: list[str] = []
    if source is None:
        live = root / changes_dir
        unarchived = (
            sorted(p.name for p in live.iterdir() if p.is_dir() and p.name != "archive")
            if live.is_dir()
            else []
        )
        data = {"base": None, "head": "working tree"}
    else:
        changes = related_changes(source, changes_dir)
        unarchived = [c["name"] for c in changes if c["state"] == "active"]
        warnings += [
            f"archived change {c['name']} has {c['tasks']['open']} open task(s)"
            for c in changes
            if c["state"] == "archived" and c["tasks"]["open"]
        ]
        data = {"base": source.base_sha, "head": source.head_sha}
    if not validated:
        verdict = "invalid"
    elif unarchived and not args.draft:
        verdict = "awaiting-archive"
    else:
        verdict = "pass"
        warnings += [
            f"unarchived change {name}: archive it in this request once the review closes"
            for name in unarchived
        ]
    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)
    data.update(
        verdict=verdict,
        draft=args.draft,
        unarchived=unarchived,
        warnings=warnings,
        validated=validated,
    )
    emit(data, args, plain_summary)
    return 0 if verdict == "pass" else 1


def cmd_labels(args: argparse.Namespace, root: Path, changes_dir: str) -> int:
    source = source_from(args, root, changes_dir)
    if source.request is not None:
        if args.current is not None or args.record or args.permission:
            raise Usage(
                "a snapshot carries the labels, the record, and the permission; drop --current/--record/--permission."
            )
        current, record = source.request["labels"], source.request.get("record")
        approver = source.request.get("approver") or {}
        permission = (
            approver.get("permission", "none")
            if approver.get("login") == args.approved_by
            else "none"
        )
    else:
        current = [
            label.strip() for label in (args.current or "").split(",") if label.strip()
        ]
        record = None
        if args.record:
            try:
                raw = json.loads(Path(args.record).read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:
                raise Failure(f"cannot read the record {args.record}: {exc}") from exc
            if raw is not None:
                fields = valid_record(raw)
                if fields is None:
                    raise Failure(
                        f"{args.record} is not a well-formed approval record (or null)."
                    )
                record = {"id": raw.get("id"), **fields}
        permission = args.permission or "none"
    event = None
    if args.approved_by:
        event = {
            "by": args.approved_by,
            "commit": args.approved_at,
            "id": args.approval_id,
            "permission": permission,
        }
    emit(
        decide_labels(source, changes_dir, current, record, event), args, plain_summary
    )
    return 0


# --- arguments -----------------------------------------------------------


def checked(pattern: re.Pattern, what: str):
    def parse(value: str) -> str:
        if not pattern.match(value):
            raise argparse.ArgumentTypeError(f"{value!r} is not {what}")
        return value

    return parse


def positive(value: str) -> int:
    if not value.isdigit() or int(value) <= 0:
        raise argparse.ArgumentTypeError(f"{value!r} is not a positive number")
    return int(value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="spec_changes.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Report on the OpenSpec changes a request touches: snapshot, check, status, labels. Run <command> --help for its options.",
        epilog=(
            "examples:\n"
            "  python3 scripts/spec_changes.py check --base origin/main --head HEAD\n"
            "  python3 scripts/spec_changes.py snapshot --repo owner/name --pr 12 --output snapshot.json\n"
            "  python3 scripts/spec_changes.py labels --snapshot snapshot.json"
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

    def output(p: argparse.ArgumentParser) -> None:
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

    def source(p: argparse.ArgumentParser) -> None:
        p.add_argument("--base", help="base ref, read with git plumbing (with --head)")
        p.add_argument("--head", help="head ref, read with git plumbing (with --base)")
        p.add_argument(
            "--snapshot",
            metavar="FILE",
            help="snapshot document; the only source for a privileged job",
        )

    p = sub.add_parser(
        "snapshot",
        help="read a pull request's related changes through the GitHub REST API",
    )
    p.add_argument(
        "--repo", required=True, type=checked(SAFE_REPO, "an OWNER/NAME pair")
    )
    p.add_argument("--pr", required=True, type=positive, help="pull request number")
    p.add_argument(
        "--approver",
        type=checked(LOGIN_RE, "an account name"),
        help="also read this account's permission",
    )
    p.add_argument(
        "--api-url", default=os.environ.get("GITHUB_API_URL", "https://api.github.com")
    )
    p.add_argument("--max-files", type=positive, default=MAX_FILES)
    p.add_argument("--max-file-bytes", type=positive, default=MAX_FILE_BYTES)
    p.add_argument("--max-total-bytes", type=positive, default=MAX_TOTAL_BYTES)
    p.add_argument("--max-calls", type=positive, default=MAX_CALLS)
    output(p)
    p.set_defaults(func=cmd_snapshot)

    p = sub.add_parser("check", help="strict validation, then the archive verdict")
    p.add_argument("--base", help="base ref (with --head)")
    p.add_argument("--head", help="head ref (with --base)")
    p.add_argument(
        "--all",
        action="store_true",
        help="on the default branch: any unarchived change is a finding",
    )
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
    output(p)
    p.set_defaults(func=cmd_check)

    p = sub.add_parser(
        "status", help="the related changes with state, documents, and task progress"
    )
    source(p)
    output(p)
    p.set_defaults(func=cmd_status)

    p = sub.add_parser(
        "labels",
        help="the spec:* state label and the label and record changes it implies",
    )
    source(p)
    p.add_argument(
        "--current", help="comma-separated labels on the request (git source only)"
    )
    p.add_argument(
        "--record", metavar="FILE", help="the approval record as JSON (git source only)"
    )
    p.add_argument(
        "--permission",
        help="--approved-by's permission: admin, maintain, write, ... (git source only)",
    )
    p.add_argument(
        "--approved-by",
        type=checked(LOGIN_RE, "an account name"),
        help="a person who added spec:approved",
    )
    p.add_argument(
        "--approved-at",
        type=checked(COMMIT_RE, "a full commit sha"),
        help="the head that person saw",
    )
    p.add_argument(
        "--approval-id",
        type=checked(EVENT_RE, "an event id"),
        help="the platform's id for that adding",
    )
    output(p)
    p.set_defaults(func=cmd_labels)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.error("a command is required: snapshot, check, status, or labels")
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
