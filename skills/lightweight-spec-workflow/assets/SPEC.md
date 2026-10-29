# {{CHANGE_TITLE}} <!-- # CONFIGURE: {{CHANGE_TITLE}}: the change in a few words. -->

{{PROBLEM}} <!-- # CONFIGURE: {{PROBLEM}}: one paragraph: the problem this change solves and for whom. -->

## Goals

### {{GOAL}} <!-- # CONFIGURE: {{GOAL}}: one heading per goal, stated as observable behaviour. -->

- **Scenario: {{SUCCESS_CASE}}** — given {{STATE}}, when {{ACTION}}, then {{RESULT}}. <!-- # CONFIGURE: {{RESULT}}: an outcome a reader who has not seen the code can judge. -->
- **Scenario: {{FAILURE_CASE}}** — given {{FAILURE_STATE}}, when {{FAILURE_ACTION}}, then {{REJECTION}}. <!-- # CONFIGURE: {{FAILURE_CASE}}: a failing or boundary input; {{REJECTION}}: the stated rejection, error, or limit. -->

## Non-goals

- {{NON_GOAL}} <!-- # CONFIGURE: {{NON_GOAL}}: one line per behaviour this change does not add or alter, or neighbouring work left for later. -->

## Done when

- `{{CHECK_COMMAND}}` exits 0. <!-- # CONFIGURE: {{CHECK_COMMAND}}: the check the agent runs itself. -->
- Every scenario above was exercised against the running result.
- The branch holds only task-level commits: no draft commits remain.

## Deliverable

{{DELIVERABLE}}, carrying the pending decisions list. <!-- # CONFIGURE: {{DELIVERABLE}}: a pull request against the base branch, a report in the conversation, or a deployment. -->

## Pre-authorised irreversible actions

- {{PUSH}} <!-- # CONFIGURE: {{PUSH}}: the push of the change branch to the named remote. -->
- {{PULL_REQUEST}} <!-- # CONFIGURE: {{PULL_REQUEST}}: the draft pull request against the named base branch. -->
- {{COMMENTS}} <!-- # CONFIGURE: {{COMMENTS}}: the comments allowed on that pull request. -->

## Approach

{{APPROACH}} <!-- # CONFIGURE: {{APPROACH}}: the bounds of the approach in a few lines. -->
