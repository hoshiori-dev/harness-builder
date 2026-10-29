# Verifier Fallback

Read when the user wants a check that no deterministic tool can express:
business-logic consistency, a privacy or personal-data review beyond
pattern matching, a review against a design rule that has no linter.

Both options below are soft boundaries: they make the check a step with a
fixed place, but compliance is not total. Say so to the user, and keep
every check a tool can express in the hook or CI. [§3.4]

## 1. Explicit self-check step (always delivered)

Add a named step to the deposited workflow at a fixed position, usually
"Before opening a pull request" in the knowledge file, and route that
condition from the agent entrypoint. Write it as a short numbered list of
concrete questions about the change, not as advice:

```markdown
### Self-check: personal data (before every pull request)

1. List every new field, log line, and API response that carries personal
   data (name, email, address, identifier, location).
2. For each, name where it is stored and who can read it.
3. Confirm none is written to logs, analytics, or error reports.
4. Put the list and the answers in the pull request description.
```

When a project skill drives the pull-request workflow, the step also
belongs in its finish step; describe that change to the skill that writes
project skills rather than editing the skill here.

## 2. Clean-context verifier (offered as the stronger option)

When the client supports subagents, offer a verifier that runs before the
commit or the pull request with a fresh context, so it neither inherits the
main agent's long-context dilution nor defends its own implementation.
[§3.4]

- Give it read-only tools and only the change (the diff or the file list)
  plus the questions of the self-check step.
- Its output is a list of findings and a pass or fail line; the main agent
  fixes or reports every finding.
- In Claude Code the verifier is a file under `.claude/agents/` with
  `tools: Read, Grep, Glob`; another client follows its own subagent
  format.

## No subagent support

Deliver only the self-check step and record the degradation in the
knowledge file in one sentence: "No clean-context verifier: this client
has no subagents; the self-check step is the only fallback."
