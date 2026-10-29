# Observation and Canaries

Read when the user asks to track agent friction (failing tool calls, retry
loops), to collect session logs, or to run representative agent tasks
after harness changes.

## Session logs are secrets

Framework session logs (JSONL transcripts, hook output, OpenTelemetry
traces) hold prompts, file contents, and sometimes credentials. Treat them
as secrets: [§5.2]

- they stay out of the repository (gitignored) and off shared drives;
- analysis runs on the local machine, or on a redacted copy;
- centralised collection is an exposure-surface decision for the user,
  presented with what would leave the machine and who could read it, and
  never configured silently.

For friction tracking, propose a local analysis: count the tool calls that
fail or retry most often in the local logs, then fix the script or add the
missing sentence they point to. Record the secret-handling rule where the
harness keeps observation guidance (the environment knowledge file, or the
reclamation section when none exists), and ask before any log leaves the
machine.

## Canary tasks are manual

A canary list is a handful of representative past tasks, each with its
source commit, the expected outcome, and how to judge it, re-run by hand
after a major harness refactor to catch a change that made agents worse.

- Offer it only to large projects whose harness is heavy, and only when
  they opt in; never at light grade.
- Never wire it into CI: CI has no credentials to run agent tasks, and
  repeated runs cost too much. When asked for CI wiring, decline with these
  two reasons and offer the manual list the team triggers after major
  harness refactors.
