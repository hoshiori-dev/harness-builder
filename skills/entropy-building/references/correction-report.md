# Correction Report

Read when writing the correction-report rule, proposing the drift label, or
the project has no issue tracker.

An agent that finds harness content contradicting the code must leave a
trace the next agent sees; a remark in the conversation vanishes with the
session. The rule names three dispositions and the criterion for each:
[§5.2]

| Disposition | Chosen when | Trace |
|---|---|---|
| Fix in the same change | the deviation is small and the correct state is certain | the commit message says what was corrected |
| Pending decisions list | the intended state is unclear, or the fix exceeds the task's authority | an item in the authority layer's format |
| Tracked issue | the deviation is large and not handled in this task | an issue with the one drift label |

The rule says in so many words that a conversation-only report does not
count. Light grade gets none of this, only the one drift sentence.

## The drift label

1. Read the label namespaces the platform lifecycle layer defined (labels
   on the remote, a labels file, the platform knowledge file).
2. With a `type:` namespace, recommend `type:harness-drift`; with another
   namespace, recommend a name inside it. With none, recommend
   `type:harness-drift` and add the new namespace to the pending decisions
   list for the platform lifecycle layer.
3. Ask the user to confirm or rename. Write the confirmed name into the rule
   and the reclamation routine.
4. Do not create the label: report it as a remote item for the skill that
   owns the platform lifecycle layer or for the user.

While the label is unanswered, land everything else, write the third
disposition as "open an issue" with no label, and add the label to the
pending decisions list with options (`type:harness-drift`, a name in an
existing namespace, the drift file below) and the recommendation. Never
invent a name.

## No issue tracker

When the project has no tracker and the user does not want one, the third
disposition becomes an entry in a tracked file, `.agents/drift.md`
(confirm the path), and the reclamation routine reads and empties it. Tell
the user why: the entry versions with the code, so the next run and every
agent see it, while a list kept outside the repository is seen by no one.
Each entry carries the date, the file and line, the contradiction, the
evidence, and the suggested fix. Create the file with a one-line header so
the entrypoint's pointer resolves.
