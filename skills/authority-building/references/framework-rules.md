# Framework Rules

Read when writing a client permission file, when a user asks for an ask entry,
or when a client has no generated format. [§4.2]

## Principle

Explicitly allow what is known safe and what the plan authorised; explicitly
deny what is known dangerous; leave the rest to the framework's default, with
the sandbox making a wrong default survivable. No ask entries unless the user
names a reason no allow or deny entry can serve. On a client whose default is
to ask, the remedy for prompt fatigue is a wider allow list, not ask entries.

The deny list guards against a careless collaborator's mistakes (a hard
reset, a force push, a bulk delete), not an attacker: an agent that runs
code can spell around any text pattern. The sandbox and scoped tokens are the
boundary.

## Fixed deny list

Present for acceptance as one block:

| Intent | Why |
|---|---|
| `git reset --hard` | discards uncommitted work; the rollback recipe commits first |
| `git push --force`, `--force-with-lease`, `-f` | rewrites pushed history |
| `git push --all`, `--mirror`, `--tags` | bulk publication of drafts and local tags |
| `git clean -fd` and variants | deletes untracked work |
| `git branch -D` | deletes unmerged work |
| `rm -rf` at the repository root (`rm -rf .`, `rm -rf ./`, `rm -rf /`, `rm -rf ~`) | unrecoverable; `rm -rf *` cannot be denied on Claude Code, where `*` is the wildcard |
| edits to the authority policy, the permission files, and the security hooks | self-protection: loosening a rule is outside agent authority |

## Allow list

Only from evidence: task-runner recipes, test, lint, build, format, and
read-only inspection commands observed in the repository, each proposed with
its file and line. Task-runner recipes are named one entry per recipe
(`Bash(just test *)`, `["just", "test"]`), never as a runner wildcard
(`Bash(just *)`, `["just"]`): the wildcard also allows every recipe that
pushes, publishes, or releases, `push-one` included. Never: push, publish,
release, tracker comment, label or state change, deletion of others' work,
whether as a raw command or wrapped in a recipe, however often history shows
them; those are governed by pre-authorisation in the plan or spec, or by the
pending decisions list. [§4.2]

## Ask entries and per-command approval

An ask entry the user kept with a reason goes into the client's ask
mechanism (Claude Code: an `ask` array beside `allow` and `deny`; Codex: a
`prompt` rule) and nowhere else. Per-command approval kept as a recorded
deviation is expressed as: Claude Code, no `allow` array (its default asks
for every shell command) with the deny list unchanged; Codex,
`approval_policy = "untrusted"` with the forbidden rules unchanged.

## Claude Code: `.claude/settings.json`

Strict JSON (no comments, no trailing commas), key `permissions` with `allow`
and `deny` arrays; evaluation order is deny, then ask, then allow, and an
allow never carves an exception out of a deny. Bash rules match the whole
command text with `*` as the wildcard; a trailing ` *` also matches the bare
command, and a rule without `*` matches that exact command only; subcommands joined by `&&`, `;`, `|` are each matched, and a deny
matches any subcommand. File rules use `Edit(path)` and `Read(path)`
(`Write(path)` never matches); `path` or `./path` is relative to the working
directory, `//path` is absolute. `settings.json` is the shared file to
commit; `settings.local.json` is per developer. Rework
`assets/claude-settings.jsonc` into strict JSON: the asset is `.jsonc` only so
its `# CONFIGURE:` lines can exist; strip every comment when writing the
target file.

## Codex: `.codex/config.toml` and `.codex/rules/*.rules`

`config.toml` holds `approval_policy`: `on-request` for interactive work
(the recommended default: a command asks only when it needs to leave the
sandbox and no rule decides it), `never` for unattended runs, `untrusted`
only for a recorded per-command deviation. Write only `approval_policy`
there: `sandbox_mode` and the `[sandbox_workspace_write]` table
(`network_access`, `writable_roots`) belong to the environment layer and are
left as they are. Codex reads the file only once the user trusts the
project. Command rules do not live there: they
are `prefix_rule(...)` calls in Starlark files under `.codex/rules/`, loaded
only once the project is trusted. `pattern` is a list of argument prefixes,
each position a literal or a list of alternatives; `decision` is `allow`,
`prompt`, or `forbidden` (most restrictive wins); `match` and `not_match`
are examples Codex validates on load. Chained commands are split and each
part evaluated. Write no `prompt` rule unless the user kept an ask entry
with a reason. Replace `origin` in the remote-first force-push rule with the
project's remote names, kept equal to the recipes' `remote`. Rework `assets/codex-config.toml`
and `assets/codex-authority.rules`. Check a rule with
`codex execpolicy check --rules .codex/rules/authority.rules -- git push --force origin main`.

Prefix matching means `["git", "push", "--force"]` does not match
`git push origin --force`; add the alternative orders the repository's
history shows and accept the rest as fool-proofing.

## Gemini CLI and other clients

Gemini CLI restricts shell commands through its policy engine
(`[[rule]]` entries with `toolName = "run_shell_command"`, `commandPrefix`,
`decision = "allow" | "deny"`, `priority`) in `~/.gemini/policies/*.toml`;
project-level policies are not loaded, and the older
`tools.exclude` / `tools.core` lists with `run_shell_command(<prefix>)` are
deprecated. Antigravity has no shipped permission format. For these and any
other client: write no file, record the policy, and list the client's
permission configuration in the report as a by-hand item with the confirmed
allow and deny entries to transcribe, telling the user to check the client's
current documentation for the file location.

## Existing files that contradict

Ask entries, an allowed push or force push, an allow entry for the whole
MCP server: report each with the methodology's reason, recommend the fix
once, change the file only where the user accepts. Note that Claude Code
saves "don't ask again" answers as allow rules in `settings.local.json`, so a
developer's local file may hold entries the shared file deliberately lacks.
