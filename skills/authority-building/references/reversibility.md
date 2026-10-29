# Reversibility

Read when classifying an action, when the user disputes a classification, or
when the user asks why a local commit and a push are not the same class.

## The one question

Can the agent undo this alone, and does anything outside the working copy
see it? Two classes, no third. [§4.2]

| Class | Examples | What the agent does |
|---|---|---|
| Reversible and internal | edit files, create a branch or worktree, run tests and checks, commit locally, squash unpushed commits | do it, no question |
| Irreversible or outward | push, open or update a pull request, post a comment, add or remove a label, change an issue or PR state, release, publish a package, change a remote setting, delete anything the user wrote, send a message | take it only when the plan or the task's spec pre-authorised it; otherwise add it to the pending decisions list and continue with the rest |

Classify by effect, not by tool: a task-runner recipe that pushes is
outward; an MCP tool that only reads is internal.

## Why commit and push differ

A local commit can be rewritten, reset, or dropped; nobody else saw it. Once
pushed, the remote keeps the objects: a force push moves the branch pointer,
the old commits stay reachable by SHA, the pull request's event log still
links to them, and erasing them means contacting platform support. A push is
therefore outward and irreversible even when it is "only to my branch".

## Framework and MCP tools

The same key sorts tool permissions: read-only tools are allowed; tools with
an outward effect are classified one by one; a whole server or tool family
is never put under ask. [§4.2]

## The deposited policy states the classes

The policy carries the table above with the project's own commands and
platform operations substituted for the generic examples, and states the
rule for each class, so a reader with that file alone can sort a new action.
At thick grade it also carries the explicit list of this project's
irreversible actions.
