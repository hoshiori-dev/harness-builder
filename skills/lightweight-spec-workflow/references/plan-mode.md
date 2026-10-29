# Plan Mode

Read when the chosen carrier is plan mode: a small edit aligned in the
conversation with no `SPEC.md`.

## Presenting the plan

Use the client's own plan mode where it has one: it keeps the session
read-only until the user approves. Where it has none, present the plan as a
message and make no edit until the user approves it. Either way the plan
carries the four completion answers under their own labels, as short as the
edit allows:

```markdown
**Change:** <one sentence: what is wrong and what will be true after.>

**Done when:** `<check command>` exits 0; <the observable result, checked
against the running program>; the branch holds one task-level commit.

**Not doing:** <the neighbouring changes this edit leaves alone.>

**Deliverable:** <a local commit and a report in the conversation, or a pull
request>, with any pending decisions.

**Pre-authorised irreversible actions:** <the push or pull request the user
allows, or "none">.

**Edit:** <file and the change, in a line or two.>
```

A plan missing any of the four answers is not presented: fill the gap or ask
for it first. The done-check command follows the same rule as in a
specification: the task runner's test recipe when one exists, otherwise a
command the agent can run.

## After approval

1. Make the edit and commit it as one task-level commit.
2. Run the done-check command and exercise the stated result against the
   running program; report both.
3. Deliver what the plan named and take only the actions it pre-authorised;
   any remote step it did not authorise goes to the pending decisions list.

## At the freeze

No per-change file exists, so there is nothing to fold or delete. Confirm
with the user that the approved plan in the conversation is the record of
the change; when its rationale should outlive the session, offer to quote
the plan in the commit body or the pull request description.

## When the edit grows

When the edit turns out to need a second task, new behaviour, or a
migration, stop editing, say that plan mode is undersized for it, and
recommend switching to `SPEC.md`; the plan becomes its first draft.
