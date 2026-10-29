# Behavioural tests

Read when writing the test cases of a skill, or when the host can dispatch
clean-context subagents and the cases are about to run.

## 1. Cases before the first edit

The trigger prompts mix direct and indirect phrasing. Each rubric item is
judged without seeing the skill. The critical failures and the passing
aggregate are declared before any output exists.

Every solver (trigger and outcome alike) runs on the least capable model
tier the skill claims to carry, with task text, inputs, tools, and limits
equal across solvers. A stronger solver clears the rubric on its own priors
and certifies a skill that breaks below the tier it claims; the floor tier
is also the cheaper run. When the host fixes the solver model or a run
escalates, the result certifies only the tier that ran.

## 2. Observing whether the skill loaded

Prefer the host's own skill-load telemetry or conversation history. When
neither exists, append this line to every solver prompt, without naming the
target skill:

```text
End your answer with SKILLS_LOADED: <comma-separated skill names or none>.
List only skills whose bodies you actually loaded; do not load a skill
merely to report it.
```

A missing or malformed report invalidates the attempt.

## 3. Isolation

Create a disposable worktree detached at the current HEAD immediately before
each run, copy in the complete candidate (staged, unstaged, and intended
untracked files), and keep every output outside version control. Make the
candidate visible to each solver's normal skill discovery. Each writing
solver gets its own worktree and output directory; concurrent writers never
share one.

When no worktree can be created or the candidate cannot be exposed, run in
the best available environment, note which version of the skill (installed or
candidate) the observation reflects, and record the degradation with the
results. A degradation never blocks the run; it is reported with it.

Never tell a trigger-test solver to use the target skill.

## 4. Running and grading

- **Trigger accuracy**: a fresh clean-context subagent per attempt. Run each
  case at least twice, up to three attempts: it passes when two valid
  attempts match the expected decision, fails when two contradict it, and is
  otherwise skipped and reported as inadequate observability.
- **Outcome quality**: one solver per task in its own worktree; keep every
  output, failures included. An output counts only when the observation shows
  the skill loaded; the same three-attempt limit applies.
- **Independent grading**: anonymise the solvers and give outputs, rubric,
  and critical failures to a clean-context subagent that produced none of
  them. The floor rule binds solvers, not graders: grade on a model capable
  of applying the rubric reliably. Require a score and concrete evidence per
  item. Accept only with no critical failure and an aggregate at or above the
  declared threshold.

## 5. Report and clean up

Record prompts, observation method, solver tier, rubric, results, scores,
evidence, every degradation, and every skipped case with its reason. Remove
every test worktree, snapshot, fixture, and output. Confirm the authoring
worktree holds only the intended changes.
