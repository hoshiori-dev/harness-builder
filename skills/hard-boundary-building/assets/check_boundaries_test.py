"""Tests for check_boundaries.py: the behaviours a port to another language must keep."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "check_boundaries", HERE / "check_boundaries.py"
)
assert SPEC is not None and SPEC.loader is not None
cb = importlib.util.module_from_spec(SPEC)
sys.modules["check_boundaries"] = cb
SPEC.loader.exec_module(cb)

RULES = [
    cb.Rule(
        source="app/",
        forbidden="infra/",
        instead="depend on app/ports/",
        doc=".agents/knowledge/architecture.md",
    )
]


def write(root: Path, rel: str, text: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def run(root: Path, *args: str, capsys) -> tuple[int, dict, str]:
    code = cb.main(
        ["--root", str(root), *args],
        rules=RULES,
        module_roots=[".", "src"],
        aliases={"@/": "src/"},
    )
    out, err = capsys.readouterr()
    return code, json.loads(out), err


def test_clean_tree_passes_silently(tmp_path, capsys):
    write(tmp_path, "app/service.py", "from app.ports import repo\nimport os\n")
    write(tmp_path, "infra/db.py", "from app.ports import repo\n")
    code, data, err = run(tmp_path, capsys=capsys)
    assert code == 0
    assert err == ""
    assert data["violations"] == [] and data["errors"] == []
    assert data["checked"] == 1


def test_python_violation_routes(tmp_path, capsys):
    write(tmp_path, "app/service.py", "import os\nfrom infra.db import session\n")
    code, data, err = run(tmp_path, capsys=capsys)
    assert code == 1
    assert data["violations"][0]["file"] == "app/service.py"
    assert data["violations"][0]["line"] == 2
    assert "app/service.py:2: imports infra.db, which is inside infra/." in err
    assert "app/ must not import from infra/" in err
    assert "Instead: depend on app/ports/." in err
    assert ".agents/knowledge/architecture.md" in err


def test_python_plain_and_relative_imports(tmp_path, capsys):
    write(tmp_path, "app/a.py", "import json, infra.cache as c\n")
    write(tmp_path, "app/sub/b.py", "from ...infra import db\n")
    write(tmp_path, "app/sub/c.py", "from ..ports import repo\n# from infra import x\n")
    code, data, _ = run(tmp_path, capsys=capsys)
    assert code == 1
    assert sorted(v["file"] for v in data["violations"]) == ["app/a.py", "app/sub/b.py"]


def test_python_relative_import_of_a_module_name(tmp_path, capsys):
    write(tmp_path, "app/x.py", "from .. import infra\n")
    write(tmp_path, "app/y.py", "from . import ports\n")
    code, data, err = run(tmp_path, capsys=capsys)
    assert code == 1
    assert [v["file"] for v in data["violations"]] == ["app/x.py"]
    assert "app/x.py:1: imports ..infra, which is inside infra/." in err


def test_typescript_relative_alias_and_dynamic(tmp_path, capsys):
    write(
        tmp_path,
        "app/view.ts",
        "import { x } from '../infra/db';\n"
        'import {\n  y,\n} from "@/infra/cache";\n'
        "const z = await import('./local');\n"
        "// import w from '../infra/old';\n",
    )
    code, data, _ = run(tmp_path, capsys=capsys)
    assert code == 1
    assert [(v["line"], v["import"]) for v in data["violations"]] == [
        (1, "../infra/db")
    ]


def test_alias_resolves_into_src(tmp_path, capsys):
    rules = [
        cb.Rule(
            source="src/app/",
            forbidden="src/infra/",
            instead="use ports",
            doc="docs.md",
        )
    ]
    write(tmp_path, "src/app/view.ts", 'import { y } from "@/infra/cache";\n')
    code = cb.main(
        ["--root", str(tmp_path)],
        rules=rules,
        module_roots=["."],
        aliases={"@/": "src/"},
    )
    data = json.loads(capsys.readouterr().out)
    assert code == 1
    assert data["violations"][0]["import"] == "@/infra/cache"


def test_explicit_files_only(tmp_path, capsys):
    write(tmp_path, "app/bad.py", "from infra import db\n")
    write(tmp_path, "app/good.py", "import os\n")
    write(tmp_path, "README.md", "from infra import db\n")
    code, data, _ = run(tmp_path, "app/good.py", "README.md", capsys=capsys)
    assert code == 0
    assert data["checked"] == 1


def test_unreadable_input_is_an_error_not_a_pass(tmp_path, capsys):
    code, data, err = run(tmp_path, "app/missing.py", capsys=capsys)
    assert code == 1
    assert data["errors"][0]["file"] == "app/missing.py"
    assert "ERROR app/missing.py: cannot read" in err
    assert "did not pass" in err


def test_missing_source_directory_is_an_error(tmp_path, capsys):
    code, data, err = run(tmp_path, capsys=capsys)
    assert code == 1
    assert data["errors"][0]["file"] == "app/"
    assert "does not exist" in err


def test_unknown_flag_exits_2_without_writing(tmp_path, capsys):
    write(tmp_path, "app/a.py", "import os\n")
    before = sorted(p.name for p in tmp_path.rglob("*"))
    with pytest.raises(SystemExit) as exc:
        cb.main(["--root", str(tmp_path), "--bogus"], rules=RULES)
    assert exc.value.code == 2
    captured = capsys.readouterr()
    assert "usage:" in captured.err
    assert captured.out == ""
    assert sorted(p.name for p in tmp_path.rglob("*")) == before


def test_bad_root_exits_2(tmp_path, capsys):
    code = cb.main(["--root", str(tmp_path / "nope")], rules=RULES)
    assert code == 2
    assert "not a directory" in capsys.readouterr().err


def test_help_has_usage_example(capsys):
    with pytest.raises(SystemExit) as exc:
        cb.main(["--help"], rules=RULES)
    assert exc.value.code == 0
    assert "Example:" in capsys.readouterr().out


def test_idempotent(tmp_path, capsys):
    write(tmp_path, "app/a.py", "from infra import db\n")
    first = run(tmp_path, capsys=capsys)
    second = run(tmp_path, capsys=capsys)
    assert first == second


def test_summary_truncates_unless_full(tmp_path, capsys):
    write(tmp_path, "app/many.py", "from infra import db\n" * (cb.SUMMARY_LIMIT + 5))
    code, data, err = run(tmp_path, capsys=capsys)
    assert code == 1
    assert len(data["violations"]) == cb.SUMMARY_LIMIT
    assert data["truncated"] is True
    assert "--full" in err
    code, data, _ = run(tmp_path, "--full", capsys=capsys)
    assert len(data["violations"]) == cb.SUMMARY_LIMIT + 5
    assert data["truncated"] is False
