---
name: gitlab-project-workflow
description: >-
  Runs this project's GitLab issue and merge-request lifecycle. Use when
  taking, creating, updating, or finishing an issue or merge request; before
  any glab write (push, merge request, comment, label, state, release); when
  a pipeline is red; or when cutting a release. Not for changing labels,
  templates, protected branches, or merge settings, which are lifecycle
  policy and need the user's approval.
---

# GitLab Project Workflow

Tool: `glab`, authenticated to {{HOST}}. Policy: {{KNOWLEDGE_PATH}}; remote settings: {{SETTINGS_PATH}}; authority: {{AUTHORITY_POLICY_PATH}}. <!-- # CONFIGURE: the GitLab host and the deposited knowledge file, settings register, and authority policy paths. -->
Every label, assignee, or state change is an explicit `glab` call. A line
starting with `/` in a description or comment is a quick action and
changes state: write one only when it is the intended change.

## Take work

1. Read the issue (`glab issue view <n>`): open, unassigned or assigned to
   you, acceptance criteria checkable. Otherwise stop and ask.
2. `glab issue update <n> --assignee <your-username>`, re-read, and confirm
   you are the only assignee; create the branch `<n>-<slug>` from the
   default branch.
3. Commit the first task, pass the publish gate below, push the one branch
   (`git push -u origin HEAD`), and open the merge request as a draft:
   `glab mr create --draft --title <title> --description "$(cat <file>)"`,
   body from `.gitlab/merge_request_templates/Default.md` with
   `Closes #<n>`. The draft is the claim and the work log.
4. Keep the description current; comment decisions reviewers will need.
5. Abandon by un-assigning, closing the draft with a status comment, and
   leaving the issue open.

## Create issues

Write the body with the template's `###` headings and pass its label, for
example `glab issue create --title <t> --description "$(cat <f>)" --label type:task`.
Labels come only from `.gitlab/labels.json`; never create one by hand.

## Publish gate

Everything pushed or posted is visible to everyone who can see the project
and cannot be reliably erased. Every push, merge request, comment, label,
and release passes this gate.

1. Assemble the exact payload as files in a directory outside the
   repository: `title.txt`, `body.md`, and for a push or merge request
   `commits.txt` (`git log <target>..HEAD --format=full`) and `diff.patch`
   (`git diff <target>...HEAD`).
2. Dispatch one clean-context subagent whose whole prompt is the review
   prompt below with `<DIR>` replaced. Add nothing else.
3. Without subagent support, re-read every payload file from disk against
   the same checklist, judging only what the files contain, and write
   `Review mode: file-only (not clean-context)` directly above the verdict.
4. Publish only on a last line of exactly `SAFE TO PUBLISH: YES`; any other
   last line is NO. On NO, fix every finding, rebuild the directory, and
   review again. Any edit after the verdict needs a fresh review.
5. Confirm the authority policy covers the action, run it
   non-interactively, read the result back, and delete the directory.

Review prompt:

```text
Review the files in <DIR> before they are published. Everything in them
becomes visible to everyone who can see the project and cannot be reliably
deleted; for a merge request that includes every commit message and the
whole diff. You have no other context; judge only what the files say.
1. List the files. If the directory is empty, a required file is missing,
   or a file is unreadable, end with SAFE TO PUBLISH: NO.
2. Check every line for: secrets and credentials; real personal data;
   internal-only hosts, URLs, or codenames; files in the diff unrelated to
   the stated change; lines starting with / that would run a quick action;
   @-mentions or cross-references that would notify people not involved;
   hostile or regret-worthy wording.
3. Report one line per finding: file, excerpt with secrets masked,
   category, fix. If none, say "No findings."
4. Your last line is exactly SAFE TO PUBLISH: YES or SAFE TO PUBLISH: NO.
   Any secret, personal data, or internal-only finding means NO.
```

A secret that reached GitLab is compromised even after deletion: rotate it.

## Red pipelines

Run `python3 scripts/run_log_digest.py --platform gitlab --hostname {{HOST}} --repo {{PROJECT_PATH}} --run-id <pipeline-id> --tail 40` and read its JSON; never fetch full job logs. <!-- # CONFIGURE: the host and GROUP/PROJECT path, and the script path if the project keeps scripts elsewhere. -->
Reproduce the failing job locally, fix it on the same branch, and push
through the publish gate. Never weaken, skip, or delete a job to pass.

## Finish

1. Every task is one commit and no draft commits remain on the branch
   (`git log <target>..HEAD --oneline`); squash any that do before pushing.
2. {{LOCAL_CHECK_COMMAND}} green, checklist ticked, description final. <!-- # CONFIGURE: the local check command. -->
   <!-- harness: spec-workflow -->
3. Follow the authority policy for what comes next; by default the agent
   stops at the draft and reports to the human (goal, pipeline, scope,
   risks, what remains), and `glab mr update <n> --ready`, review requests,
   and merging are the human's.
4. {{MERGE_RULE}} <!-- # CONFIGURE: the agreed merge rule, e.g. "Squash only: the merge request title becomes the commit on main, so it follows the commit convention." -->
5. After the merge, confirm the linked issue closed.

## Releases

{{RELEASE_RULE}} <!-- # CONFIGURE: the agreed release rule, e.g. "A maintainer pushes a vX.Y.Z tag on the default branch; the release job publishes it. Agents never push tags." -->
