# Pending Decisions

Read when a step is blocked on a decision only the user can make, when
writing the pending decisions section of a policy, or when checking an item
someone else wrote.

## Rule

<!-- shared:pending-decisions -->
When a step is blocked on a decision only the user can make, continue with
every step that does not depend on it and add the blocked item to a pending
decisions list. Each item states: what is blocked and why; the options; the
recommended option and its reason; which finished work each option would
change. Present the list once, at the end or when nothing else can proceed,
never one question at a time.
<!-- /shared:pending-decisions -->

A user returning after hours away must be able to decide each item from the
list alone. [§4.2]

## Fields of one item

Every item carries all five, in this order, under these labels:

1. **Blocked**: the step or action that cannot proceed.
2. **Why**: what makes the decision the user's (a policy boundary, a refused
   action, an outward effect nobody pre-authorised, two readings of the
   request).
3. **Options**: each option in one sentence; include "do nothing" when it is
   viable.
4. **Recommended**: one option and its reason.
5. **Impact on finished work**: for each option, which already finished work
   changes, and how; "none" when nothing changes.

An item missing any field is incomplete and is completed before it is
presented.

## Format

```markdown
## Pending decisions

### 1. <short title>
- Blocked: <step or action>
- Why: <reason the user must decide>
- Options:
  - A. <option>
  - B. <option>
- Recommended: <A or B>, because <reason>.
- Impact on finished work:
  - A: <files or results that change, or none>
  - B: <files or results that change, or none>

### 2. <short title>
...
```

## Example

```markdown
### 1. Tracker comment on issue 42
- Blocked: posting the "implementation ready" comment on issue 42
- Why: a comment is outward and irreversible, and the plan did not
  pre-authorise it
- Options:
  - A. Post the comment as drafted in the report.
  - B. Skip the comment; the pull request body carries the same text.
- Recommended: B, because the pull request already links the issue and a
  second copy drifts.
- Impact on finished work:
  - A: none
  - B: none; the drafted comment text is dropped
```
