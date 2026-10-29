# Agent Skills specification and host-specific fields

Read when the user wants a skill to load only when invoked by name, or when
any frontmatter field outside the specification is about to be written.

## Structure

`SKILL.md` opens with YAML frontmatter between `---` lines, then a Markdown
body. The directory holds `SKILL.md` and, only when a file goes in,
`scripts/`, `references/`, `assets/`. No `README.md` in the skill root.

## Specification fields

| Field | Rule |
|---|---|
| `name` | Required. Lowercase `a-z`, digits, single hyphens; no leading, trailing, or consecutive hyphens; at most 64 characters; equal to the directory name. |
| `description` | Required, non-empty, at most 1024 characters. Third person: capability first, then triggers. |
| `license` | Optional. A short identifier (`Apache-2.0`) or a path to a bundled license file. |
| `compatibility` | Optional, at most 500 characters. Only real environment requirements (runtime, system packages, network). Absent means "runs anywhere". |
| `metadata` | Optional flat map of string to string; use distinctive keys. |
| `allowed-tools` | Optional space-separated tool names. Experimental; support varies; never rely on it for safety. |

Body rules: no mandatory format; under 500 lines and about 5,000 tokens;
every file link resolves inside the skill directory; a link that resolves
outside it, or an absolute `/` path, breaks when the directory is copied; every
bundled file is linked from `SKILL.md` at first mention.

## Loading stages

| Stage | Content | Loaded |
|---|---|---|
| Metadata | `name` and `description` | every turn |
| Instructions | the `SKILL.md` body | on activation |
| Resources | `scripts/`, `references/`, `assets/` | on demand, when a pointer fires |

Telling the agent to load a reference unconditionally collapses the third
stage into the second.

## Fields outside the specification

A host may read fields the specification does not define. Another host
ignores them silently, and the linter warns on unknown fields. When one is
written, the body names the host it targets, and the user is told:

- `disable-model-invocation: true`: honoured by Claude Code. Hides the
  description from the agent, so the skill is reachable only by the human
  typing its name. Codex and Antigravity do not honour it: there the skill
  still loads by description. A skill that must be user-only everywhere stays
  out of the shared skill directories instead.
- Skill-to-skill invocation (one skill reaching another through its
  description) requires the host to keep every description in the running
  agent's context; not every host does. Flag the dependency when a skill's
  design relies on being reached by another.
- Any other host-specific field: name the host in the body and expect the
  linter's warning.

Say which hosts the project's agents run on before writing any of these;
when the repository does not show it, ask.
