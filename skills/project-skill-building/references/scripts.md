# Bundled scripts

Read when writing or reviewing any script bundled with a project skill, or
when choosing its language.

## Output noise

A script filters noise: it returns the state and the next action, not three
hundred lines of PASSED. [§2.4]

## Rules for every script

- No interactive input; prompts hang in non-interactive shells. Everything
  arrives through flags.
- `--help` with a usage example.
- Data on stdout (JSON preferred), diagnostics on stderr.
- Exit 0 on success, 1 on a finding or error, 2 on bad arguments.
- Idempotent: agents retry; two runs over the same input give the same
  output and change nothing twice.
- Error messages say what is wrong and how to fix it.
- Dependency versions pinned.
- Output above about 10,000 characters summarised by default, full output
  behind `--full` or `--output FILE`; hosts truncate stdout silently.
- A `compatibility` frontmatter line in `SKILL.md` naming the runtime the
  scripts need; a `SKILL.md`-only skill has no such line.
- Linked from `SKILL.md` with a relative markdown link at first mention,
  before any invocation example.

## Choosing the language

Recommend Python with PEP 723 inline metadata, standard library first, so the
script runs on plain `python3` and through `uv run` alike. Name the
alternative in one sentence and confirm with the user before writing:

- Project in a non-TypeScript ecosystem (Go, Rust, Java, Python, …): Python
  is the recommendation; the project's own language is the alternative when
  the team would rather read that.
- Project whose community language is TypeScript: recommend Deno when a Deno
  runtime is already present, for its explicit, scoped permissions;
  otherwise the project's existing TypeScript runtime idiom (Node or Bun as
  found). Name the other as the alternative. Ask before adding any runtime to
  the agent environment.

The user's choice binds; a language the user cannot read is never chosen for
them.

## Python with PEP 723

Declare the runtime and any dependency in the script itself, before imports:

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
```

Use the `python3` shebang when there are no dependencies (the common case:
prefer the standard library). With dependencies, use
`#!/usr/bin/env -S uv run --script` and pin each to an exact
version (`"httpx==0.27.2"`; a range such as `>=0.27,<1` is not a pin); then `uv run script.py` installs them in an isolated
environment and plain `python3` needs them installed by hand, which the
`compatibility` line states.

- `argparse` generates `--help` and exits 2 on bad arguments; put the usage
  example in `epilog`, and use `parser.error(...)` for argument problems the
  parser cannot see.
- Never `input()`.
- No bare `except`, no `except Exception: pass`; an unexpected error is a
  message that names what to fix, then exit 1.
- Ship a sibling `<name>_test.py` (pytest, `tmp_path` fixtures) with every
  script.

Skeleton:

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""One line: what the script does.

Usage:
  python3 scripts/<name>.py --flag VALUE
"""

import argparse
import json
import sys


def main() -> int:
    parser = argparse.ArgumentParser(
        description="One-line description.",
        epilog="Example: python3 scripts/<name>.py --flag VALUE",
    )
    parser.add_argument("--flag", required=True, help="What it means.")
    args = parser.parse_args()
    result = {"flag": args.flag}
    print(json.dumps(result, indent=2))
    print("note for the operator", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

## TypeScript with Deno (Bun differences at the end)

Only when the project's community language is TypeScript and the user chose
it.

- Imports resolve from pinned specifiers, no install step:
  `import { z } from "npm:zod@3.22.0";`, `jsr:` for JSR packages. Unpinned
  imports resolve to latest at runtime.
- Shebang `#!/usr/bin/env -S deno run --allow-read`; Deno is deny-by-default,
  so every access needs a flag (`--allow-read[=path]`, `--allow-write`,
  `--allow-net[=host]`, `--allow-env`, `--allow-run[=cmd]`). Prefer scoped
  flags, never `--allow-all`, and list the required flags in `--help`.
- Arguments from `Deno.args` only; `prompt()` and `confirm()` hang.
- `console.log` is stdout, `console.error` is stderr; `Deno.exit(0|1|2)`.

Bun differences: version-pinned bare specifiers (`"zod@3.22.0"`), auto-install
only when no `node_modules` exists anywhere up the tree, shebang
`#!/usr/bin/env bun`, no permission flags, `process.argv.slice(2)` and
`process.exit(...)`.
