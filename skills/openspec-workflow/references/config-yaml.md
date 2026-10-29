# Artifact rules in openspec/config.yaml

Read when installing the automation, when the project's OpenSpec
configuration has no `rules:` block, or when an existing rule contradicts the
formats this skill uses.

OpenSpec's own skills and `openspec instructions` read `context:` and the
per-artifact `rules:` from `openspec/config.yaml`, so rules recorded there
apply whichever agent or command writes the artifact. Check the keys the
installed version accepts with `openspec instructions --help` and the
comments `openspec init` wrote into the file.

## The block to propose

Show it to the user, adapted to the contract's approval mode, and write it
only after they confirm. Merge into an existing `rules:` key; never add a
second one.

```yaml
rules:
  proposal:
    - Describe the end state, never the approach or steps.
    - 'End with "## Acceptance" holding "**Becomes true:**" and "**Stays true:**" lists; every item is checkable by a command, a scenario, or a walkthrough.'
  specs:
    - Describe observable behaviour, never file contents or implementation steps.
    - Every requirement has a scenario a reader can judge without the code; at least one scenario covers a failure or edge path.
    - A MODIFIED requirement copies every existing scenario; a new capability carries a Purpose of at least 50 characters.
  design:
    - 'Give every Goal and Non-Goal a "Checked by" clause.'
    - Record decisions with their rejected alternatives; state bounds, never steps; no secrets or private data.
  tasks:
    # Recorded mode:
    - Write tasks.md only after the request carries spec:approved; otherwise stop and report that the package is ready for review.
    # Conversational mode, instead of the line above:
    # - Write tasks.md only after the user has approved the package in the conversation.
    - Each task names its own verification.
    - Never add a task that archives the change; the archive follows the review.
```

## When a rule already exists

If an existing rule contradicts one of these (a proposal rule that ends at
Impact, a design rule that asks for steps, a tasks rule that allows writing
them with the proposal): show both rules side by side, recommend one with its
reason, and change nothing until the user chooses. A rule the project wrote
for a reason it can name wins over this skill's default.
