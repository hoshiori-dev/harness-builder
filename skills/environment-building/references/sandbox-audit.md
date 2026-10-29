# Sandbox Audit

Read when walking the five audit items, and when the user leaves items
undecided or declines the audit. [§3.3]

Each item ends with one recorded state: **accepted** (with the user's
reason), **cut** (with the change it needs), **undecided**, or
**declined**.

## 1. Sensitive assets

Which credentials, environment variables, and private files the agent and
its scripts can read or write. Observe: credential mounts (`~/.ssh`,
`~/.aws`, `~/.config/gh`, `~/.kube`, `~/.docker/config.json`), token
variables (names only), `.env` files in the workspace, and each token's scopes (`gh auth status`
lists them). On a host base, everything the user's account can read is in
range.

Recommend: cut every host credential mount; give the agent a scoped token
with the least scope the work needs. A token that can push to the default
branch: record the scoped-token recommendation here and hand "push as an
irreversible action needing pre-authorisation" to the authority layer and
"default-branch protection" to the platform lifecycle layer.

## 2. Host privilege leaks

High-privilege host interfaces inside the sandbox: the Docker socket
(`/var/run/docker.sock` mounted or `docker` reaching the host daemon), a
host root or home mount, `--privileged`, added capabilities, host PID or
network namespace. A mounted Docker socket is host root.

Recommend: cut. When the project builds images, offer rootless Docker, or
a remote or VM-hosted builder, in place of the host socket. Docker-in-Docker
is no alternative: it needs `--privileged`, so if the user wants it, record
it under this item as accepted or cut like the socket. If the user keeps
the socket, record it as accepted with their reason.

## 3. Local and intranet exposure

Whether host services (`localhost` databases, admin consoles) or the
company network are reachable through the container's network. Observe:
`--network=host`, `host.docker.internal`, forwarded ports, VPN on the
host. Recommend: cut host networking; at thick grade the allowlist covers
this item.

## 4. Session-log destination

Where each client writes its session logs (for example
`~/.claude/projects/` for Claude Code and `~/.codex/sessions/` for Codex)
and whether the team plans to collect them. Logs carry every file the agent
read and every command output, so they leak credentials and personal data
more easily than handoff files. Central collection is a privacy decision:
name it as one and require an explicit decision (which store, who reads it,
retention, redaction) before recording it.

## 5. Risk decision

The project owner weighs the automation gain against the damage each
remaining exposure allows, and records the decision: the list of accepted
items with reasons, and the cuts to make. Ask for it explicitly; it closes
the audit.

## Undecided and declined

- **Items left undecided** (the conversation ends, the user defers): add
  each to the pending decisions list with the recommended option; the
  knowledge file marks it "undecided", never accepted.
- **The whole audit declined**: record the audit section as "declined by
  the user on <date>", add all five items to the pending decisions list
  with recommendations, and continue with every other step, the
  non-interactive variables included.
