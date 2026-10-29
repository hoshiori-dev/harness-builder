# Control Plane

Read when classifying control-plane files, when writing the network
allowlist or mount enforcement, when the user wants the security rules
unreadable by the agent, or when a client has its own sandbox setting.

## Bootstrap and runtime

While the harness is being built (bootstrap), the human is present and
the agent edits configuration like any author. The classification applies
from the runtime phase, once the harness is in daily use. It is the
project's decision per file; present each as a recommendation. [§3.3]

| Class | Typical files | Rule |
|---|---|---|
| Hard read-only | security rules, sandbox and container configuration, secret-scanning hooks, permission files | the agent never changes them; only a person does |
| Soft read-only | linter rules, type-check configuration, test-framework configuration, build scripts | the agent may adjust them while the invariant holds, or propose the change for review |

The soft read-only invariant sentence is written by the hard-boundary
layer; the knowledge file lists the soft files and points to that layer's
knowledge for the wording.

## Enforcing hard read-only at thick grade

- Container: bind-mount each file read-only over the workspace copy
  (`source=${localWorkspaceFolder}/<path>,target=${containerWorkspaceFolder}/<path>,type=bind,readonly`
  in `mounts`). Root inside a container without `CAP_SYS_ADMIN` cannot
  remount it writable.
- VM or host: owned by another account, not writable by the agent's user.
- Below thick, list the file as hard read-only "by convention" and name
  mount-level enforcement as the hardening step.

A read-only file mount makes any git operation that rewrites that file
(checkout, pull, rebase) fail with "Device or resource busy". Changes to
those files then go through a person outside the container, which is the
intent; say so to the user.

## Network allowlist at thick grade

Default-deny outbound traffic, then allow only the hosts the work needs:
the git host, the package registries in use, the model API endpoints of
each client, and documentation hosts the user names. In a dev container
the usual mechanism is a firewall script (iptables with an ipset of
resolved addresses) run as root at `postStartCommand`, with `runArgs`
adding `--cap-add=NET_ADMIN` and `--cap-add=NET_RAW`, and a check at the
end that a blocked host is unreachable and an allowed one is reachable.
List the hosts in the proposal for the user to confirm one by one.

The agent's user must not keep unrestricted `sudo`: root with `NET_ADMIN`
can flush the rules. Allow `sudo` for the firewall script only.

## Opaque security rules

When the user wants the rule logic unreadable by the agent, agree on one
condition: every denial message is readable and says it is a policy
boundary, not a transient fault, and names the alternative path or the
person who decides. Without that, the agent cannot tell a refusal from a
broken environment and retries or looks for a way around. Opacity raises
the cost of bypass; the floor is still the sandbox and the tokens. [§3.3]

## Client sandbox settings

A client's own sandbox (for example Codex `sandbox_mode` and its network
access setting) is a framework aid, not the boundary. Settle its value
here with the user, consistent with the grade and the allowlist, record it
in the knowledge file, and write it only into a file the approved plan
names. Permission lists stay with the authority layer.
