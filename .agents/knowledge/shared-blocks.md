# Shared Blocks

Read when editing a paragraph wrapped in `<!-- shared:<id> -->` …
`<!-- /shared:<id> -->` in any `skills/*/SKILL.md`, or when adding such a
block. This file is the single source of truth for every shared block; a
skill's copy must equal the canon here byte for byte (trailing whitespace
aside), and `just skills-check` fails on any divergence or on a canon id that
no skill uses. Edit the canon first, then paste it into every skill that uses
the id, in the same change.

Rules stay here because they are repeated across skills on purpose: a plugin
skill may not link outside its own directory, so repetition is the only way
to carry one sentence into several skills, and this file makes that
repetition checkable instead of silent drift.

## recommendation-not-decision

<!-- shared:recommendation-not-decision -->
A recommendation is not a decision. Present one recommended option with its
reason and the alternatives in a sentence each, then wait for the user's
choice. Challenge a choice once when the evidence contradicts it; after that
the choice binds every later step.
<!-- /shared:recommendation-not-decision -->

## confirm-not-guess

<!-- shared:confirm-not-guess -->
Confirm, do not guess. Settle a fact from the repository when it can be
observed there (tools in use, directories, commands, history); ask the user
for everything else, and ask before choosing on any point where two readings
would lead to different work. Only a choice whose answer is plain from the
repository is made without asking.
<!-- /shared:confirm-not-guess -->

## nothing-lands-before-agreement

<!-- shared:nothing-lands-before-agreement -->
Nothing lands before agreement. Create or change no file in the target
project until the user has approved the plan that names it; an inspection
step reads and reports, it never writes.
<!-- /shared:nothing-lands-before-agreement -->

## plan-is-not-approval

<!-- shared:plan-is-not-approval -->
An approved plan authorises the files it names and nothing else. Publishing
anything outside the repository, changing a remote setting, deleting work,
and widening what agents may do on their own are each a separate, explicit
decision by the user, taken when that step is reached.
<!-- /shared:plan-is-not-approval -->

## pending-decisions

<!-- shared:pending-decisions -->
When a step is blocked on a decision only the user can make, continue with
every step that does not depend on it and add the blocked item to a pending
decisions list. Each item states: what is blocked and why; the options; the
recommended option and its reason; which finished work each option would
change. Present the list once, at the end or when nothing else can proceed,
never one question at a time.
<!-- /shared:pending-decisions -->

## management-code-ownership

<!-- shared:management-code-ownership -->
A script, hook, check, CI step, or task-runner recipe written into the target
project is the project's own management code: written for its role in the
language the project agreed to, readable first, failing with a message that
names what to fix, with no fallback that hides an unexpected error, and never
calling a script inside a skill directory. Tell the user that later fixes to
this plugin do not reach the delivered copy.
<!-- /shared:management-code-ownership -->
