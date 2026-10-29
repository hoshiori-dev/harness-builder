# Agent Catalog

## Purpose
Rules shared by every agent this plugin ships. Agents are outside the Agent
Plugins v1.0.0 specification, so each agent exists as one hand-written file per
supported client whose plugin system carries agents, under that client's
namespace directory: today Claude Code only
(`com.anthropic.claude-code/agents/<name>.md`, listed in the generated
`.claude-plugin/plugin.json`). Codex plugins have no agents component, and
Antigravity loads plugin agents only from the plugin root, which this plugin
keeps for portable files; both are recorded limitations
(`.agents/knowledge/compatibility-watch.md`, W9 and W2), not worked around
through workspace configuration, so those clients get no agent files. The
portable product is the skills; the agent is a clean-context verifier the
entry skills dispatch where the client supports it. Each agent has its own spec at `openspec/specs/agent/<name>/spec.md`.

## Requirements

### Requirement: One version per agent-capable client
Every agent SHALL have a file for each supported client whose plugin system
carries agents, named `<name>` plus the client's extension, whose `name` field
equals `<name>` and whose `description` text is identical across clients. A
client whose plugin system carries no agents SHALL have no `agents/` directory
under its namespace.

#### Scenario: Agent missing for one client
- **WHEN** `<name>` exists for some agent-capable clients but not all
- **THEN** `just validate` fails naming the missing file

#### Scenario: Agent file for a client that ships no agents
- **WHEN** `com.openai/agents/` or `com.google.antigravity/agents/` exists
- **THEN** `just validate` fails naming the directory as unsupported

#### Scenario: Descriptions diverge
- **WHEN** two client versions of `<name>` carry different descriptions
- **THEN** `just validate` fails naming the agent

### Requirement: Client fields stay in the client file
Client-specific fields (tool names, model identifiers, permission modes) SHALL
appear only in that client's file; the instructions body SHALL describe the
same behaviour in every version so the agent acts the same wherever it runs.

#### Scenario: Same task in two clients
- **WHEN** the same request is delegated to `<name>` in two clients
- **THEN** both versions follow the same steps and produce the same report format

### Requirement: Read-only by default
An agent SHALL request only read tools unless its spec states why it must
write; where a client's agent format has no tool restriction field, the
instructions SHALL state that the agent reads only.

#### Scenario: Agent spec without a write justification
- **WHEN** an agent's spec names no write operation
- **THEN** every client version that can restrict tools lists read-only tools, and every version's instructions forbid modifying files
