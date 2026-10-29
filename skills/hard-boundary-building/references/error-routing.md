# Error Routing for Custom Checks

Read when writing or porting a project-specific hook, architecture boundary
check, or lint rule, or a filter the user insisted on.

A custom check's failure is the most precise context an agent will get at
that moment. "Forbidden: X" makes the agent guess; "X is forbidden, do Y,
the rule is in Z" turns the block into guidance. [§3.1]

## The message

Every failure follows [assets/check-message-style.md](../assets/check-message-style.md) when writing the
message lines: the location, what is wrong, the rule and where it is
written, and what to do instead. A rule the project cannot state an
alternative for is not ready to be a check; ask the user for the
alternative before writing it.

## The reference implementation

[assets/check_boundaries.py](../assets/check_boundaries.py) is a working import-direction check
(Python and TypeScript or JavaScript sources), stdlib only, with its
tests beside it. Use it when writing a boundary check:

- **Agreed language is Python**: copy it into the project's scripts
  directory, set the `# CONFIGURE:` lines (rules, module roots, aliases),
  and run it with `python3`.
- **Another language**: port it, keeping the command-line contract, the
  JSON on stdout, the message shape, and the exit codes; the test file
  lists the behaviours the port must keep. A Deno port declares only
  `--allow-read` for the source directories.

Path aliases (`@/infra`, `~infra`) resolve only through the aliases the
configuration lists; add every alias the project's `tsconfig.json` or
bundler defines.

## Errors are not passes

- An input the check cannot open is an error that names the file and the
  reason, exit 1, never a skip.
- A configuration that names a directory that does not exist is an error,
  not "nothing to check".
- No `except Exception: pass`, no `|| true`, no default value standing in
  for data the check could not read.
- Bad arguments exit 2 with usage on stderr and touch nothing.

## Naming

Name the check for its role (`check_boundaries.py`), never for a plugin.
