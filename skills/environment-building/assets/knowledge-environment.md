Read this when a command hangs or prompts, before touching a credential, a mount, a container or sandbox file, a security hook, or a lint, test, type-check, or build configuration, and when asked what this environment can reach.

# Agent Environment

Set by {{OWNER}} on {{DATE}}; grade: {{GRADE}}. <!-- # CONFIGURE: {{OWNER}}, {{DATE}}, {{GRADE}} (light, medium, or thick). -->

## Where the agent runs

{{BASE}} <!-- # CONFIGURE: {{BASE}}: the environment (for example "the dev container in `.devcontainer/`", "the developer's host with a scoped token") and who chose it ("chosen by <user> from: dev container, VM, host"; "existing environment, adopted as is"). -->

## Protection tier

{{TIER}} <!-- # CONFIGURE: {{TIER}}: "regular" or "isolated", the three facts with their evidence (trifecta, source reachability per source, human in the loop), and the condition missing for regular. -->

{{MIDDLE_BAND}} <!-- # CONFIGURE: {{MIDDLE_BAND}}: middle band only: the restriction per model named and who confirmed it, or "pending"; delete otherwise. -->

{{RESTRICTED_INSTANCE}} <!-- # CONFIGURE: {{RESTRICTED_INSTANCE}}: isolated tier only: the restricted instance and the user's answer to it; delete otherwise. -->

## Sandbox audit

| Item | Finding | Decision | Reason |
|---|---|---|---|
| Sensitive assets | {{ASSETS}} | | | <!-- # CONFIGURE: {{ASSETS}} and every audit row: the finding, then accepted, cut, undecided, or declined, then the user's reason. -->
| Host privilege leaks | | | |
| Local and intranet exposure | | | |
| Session-log destination | | | |
| Risk decision | | | |

An undecided item is not accepted. Do not widen an accepted exposure or
undo a cut; propose the change to the user.

## Control plane

Hard read-only: never change these files; if one blocks the work, stop and
report.

{{HARD_READ_ONLY}} <!-- # CONFIGURE: {{HARD_READ_ONLY}}: one line per file with its enforcement ("read-only mount", "by convention; a read-only mount is the thick-grade step", or "enforcement not applicable at light grade"). -->

Soft read-only: the invariant that governs changing these files is in
{{HARD_BOUNDARY_KNOWLEDGE}}. <!-- # CONFIGURE: {{HARD_BOUNDARY_KNOWLEDGE}}: the path of the hard-boundary knowledge file. -->

{{SOFT_READ_ONLY}} <!-- # CONFIGURE: {{SOFT_READ_ONLY}}: one line per soft read-only file. -->

{{NETWORK}} <!-- # CONFIGURE: {{NETWORK}}: thick grade: the allowed hosts and where the firewall script lives; delete below thick. -->

A refusal from a security rule is a policy boundary, not a fault: do not
retry it by another route; report it with the action that was refused.

## Non-interactive commands

{{RUNNER_RULE}} <!-- # CONFIGURE: {{RUNNER_RULE}}: task runner present: "Run project commands through the task runner's recipes; it exports `CI=true`, `PAGER=cat`, `GIT_PAGER=cat`, and `GIT_TERMINAL_PROMPT=0`. When running a tool directly, set the same variables on the command line."; no task runner: "Pending: no task runner chosen; set `CI=true`, `PAGER=cat`, `GIT_PAGER=cat`, and `GIT_TERMINAL_PROMPT=0` on each command." -->

{{FLAGS}} <!-- # CONFIGURE: {{FLAGS}}: per-command flags a recipe still needs (for example the test command's run-once flag) and recipes `CI=true` changes; delete when there are none. -->
