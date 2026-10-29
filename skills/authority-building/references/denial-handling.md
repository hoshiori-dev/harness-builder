# Denial Handling

Read when writing the refusal section of a policy, or when a user or an
existing policy proposes another response to a refused action.

## Two responses, one prohibition

A refusal from a permission rule, a hook, a check, or the platform is a
decision to read, not an obstacle to pass. [§4.2]

1. **The plan put the work in the wrong place.** A refused edit to a
   protected file often means the logic belongs elsewhere. Return to the plan
   and choose another approach.
2. **A real policy boundary.** The action is outside what agents may do on
   their own. Record it as a pending decision with the five fields and
   continue with everything that does not depend on it.

Forbidden: retrying the same intent through an equivalent command, a script,
a different tool, a shell redirect, or a loosened rule. Denied
`git push --force`, then `git push --force-with-lease` on the same branch, is
routing around. A refused `Edit` of a protected file, then the same change
through `cat >` or `sed -i`, is routing around. Giving up at the first
refusal and routing around it are the same laziness in two directions.

## A third response is not added

"Fix the entry that blocked you" is not a response: loosening a permission
list, a hook, a check, or the policy file is outside every agent's
authority, including to unblock the current task. When a denied command
turns out to be required by the approved plan, the agent proposes the policy
change with its reason and waits. The policy's self-protection section
carries this rule; keep both the two responses and the prohibition when a
user or an existing policy proposes a third. [§4.2]

## A check that found a defect

A failing test, linter, or secret scan is not a refusal under this section;
it is a finding to fix. The policy says so in one sentence so that agents do
not file defects as pending decisions.
