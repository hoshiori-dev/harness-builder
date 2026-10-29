# Skill Catalog

## Purpose
Rules shared by every skill this plugin ships under `skills/`. Skills are the
portable component of Agent Plugins v1.0.0 and load unchanged in Claude Code,
Codex, Antigravity, and any other conforming client; the Antigravity package
reaches them through its `skills` link. Each shipped skill has its own spec at
`openspec/specs/skill/<name>/spec.md`.

## Requirements

### Requirement: Skill package layout
Each skill SHALL be a directory `skills/<name>/` holding `SKILL.md` with YAML
frontmatter whose `name` equals `<name>` and whose `description` says what the
skill does and when to use it, following the agentskills.io specification.
Supporting material SHALL live in `references/`, `scripts/`, or `assets/`
inside the skill directory and be linked from `SKILL.md` by relative path.

#### Scenario: Valid skill is discovered by every client
- **WHEN** a client scans `skills/` one level deep
- **THEN** every directory containing `SKILL.md` is offered as a skill named by its frontmatter

#### Scenario: Frontmatter name mismatch is rejected before release
- **WHEN** `skills/<name>/SKILL.md` declares a different `name`
- **THEN** `just validate` fails naming the file and the expected name

### Requirement: Plugin skills do not shadow project skills
A skill name under `skills/` SHALL NOT also exist under `.agents/skills/`,
because Codex and Antigravity load both directories in this workspace.

#### Scenario: Duplicate name is reported
- **WHEN** `skills/<name>/` and `.agents/skills/<name>/` both exist
- **THEN** `just validate` fails and names both directories

### Requirement: Client-independent instructions
A skill SHALL describe its procedure in client-neutral terms and SHALL place
client-specific steps in a reference file organised by client, so the same
`SKILL.md` serves every client.

#### Scenario: Skill read in a client it does not name
- **WHEN** an Agent Plugins client other than Claude Code, Codex, or Antigravity loads the skill
- **THEN** the `SKILL.md` body contains no step that only one named client can perform
