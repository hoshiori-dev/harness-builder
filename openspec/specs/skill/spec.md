# Skill Catalog

## Purpose
Rules shared by every skill this plugin ships under `skills/`. Skills are the
portable component of Agent Plugins v1.0.0 and load unchanged in Claude Code,
Codex, Antigravity, and any other conforming client. Two entry skills are
user-invoked; every other skill is model-invoked and reached by its
description. Each shipped skill has its own spec at
`openspec/specs/skill/<name>/spec.md`, whose scenarios are its behavioural
test cases. Non-goals of the catalog: hosting an MCP server, depending on any
other skill library, or shipping scripts that need a runtime other than
Python.

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

### Requirement: Self-containment
A skill SHALL link only to files inside its own directory and SHALL name no
other skill library or install command; a paragraph shared between skills
SHALL be a shared block whose text equals the canon in
`.agents/knowledge/shared-blocks.md`.

#### Scenario: Link leaves the skill directory
- **WHEN** a `SKILL.md` or reference links to a path outside `skills/<name>/`
- **THEN** `just skills-check` fails naming the file and the link

#### Scenario: Shared block drifts from the canon
- **WHEN** a `<!-- shared:<id> -->` block in a skill differs from the canon text
- **THEN** `just skills-check` fails naming the skill and the id

### Requirement: Description budget and invocation
A skill's description SHALL be at most 1024 characters and SHOULD be at most
900; the two entry skills (`harness-create`, `harness-improve`) SHALL carry
`disable-model-invocation: true` and every other skill SHALL NOT.

#### Scenario: Description over budget
- **WHEN** a description exceeds 1024 characters
- **THEN** `just validate` fails naming the skill

#### Scenario: Entry skill without the invocation switch
- **WHEN** `skills/harness-create/SKILL.md` lacks `disable-model-invocation: true`
- **THEN** `just skills-check` fails naming the file

### Requirement: Layer ownership phrase
Every skill whose name ends in `-building`, except `project-skill-building`,
SHALL state exactly one `Owns the <layer> layer` phrase in its description
with a layer name from `scripts/lib/layers.ts`; no other skill SHALL contain
the phrase.

#### Scenario: Builder without a layer
- **WHEN** a `-building` skill's description lacks the phrase or names an unknown layer
- **THEN** `just skills-check` fails naming the skill and the known layers

### Requirement: Delivered scripts are tested Python
Every script under a skill's `scripts/` or `assets/` SHALL be Python with
PEP 723 inline metadata requiring Python 3.10 or later, SHALL run under uv
and under a plain `python3` when it has no third-party dependency, SHALL
offer `--help`, and SHALL have a sibling `<name>_test.py` run by `just test`.

#### Scenario: Script asset without a test
- **WHEN** `skills/<name>/assets/tool.py` exists without `tool_test.py`
- **THEN** `just skills-check` fails naming the missing test

#### Scenario: Placeholder outside a configure line
- **WHEN** an asset contains `{{NAME}}` on a line without `# CONFIGURE:`
- **THEN** `just skills-check` fails naming the file and line

### Requirement: Documented in both READMEs
Every shipped skill SHALL appear in the skill table of `README.md` and of
`README.en.md`.

#### Scenario: Skill missing from one README
- **WHEN** `skills/<name>/` exists but one README's skill table lacks it
- **THEN** `just harness-check` fails naming the README and the skill
