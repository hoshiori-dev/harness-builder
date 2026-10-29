---
name: github-project-workflow
description: >-
  Runs this repository's GitHub issue and pull-request lifecycle. Use when
  taking, creating, updating, or finishing an issue or pull request; before
  any gh write (push, pull request, comment, label, state, release); when a
  check is red; or when cutting a release. Not for changing labels, forms,
  branch rules, or merge settings, which are lifecycle policy and need the
  user's approval.
---

# GitHub Project Workflow

Tool: authenticated `gh`. Policy: {{KNOWLEDGE_PATH}}; remote settings: {{SETTINGS_PATH}}; authority: {{AUTHORITY_POLICY_PATH}}. <!-- # CONFIGURE: the deposited knowledge file, settings register, and authority policy paths. -->
Every label, assignee, or state change is an explicit `gh` call; nothing
written in a body changes state except the closing keyword.

## Take work

1. Read the issue: open, unassigned or assigned to you, acceptance criteria
   checkable. Otherwise stop and ask.
2. `gh issue edit <n> --add-assignee @me`, re-read, and confirm you are the
   only assignee; then `gh issue develop -c <n>` to create the branch.
3. Commit the first task, pass the publish gate below, push the one branch
   (`git push -u origin HEAD`), and open the pull request as a draft:
   `gh pr create --draft --title <title> --body-file <file>`, body from
   `.github/pull_request_template.md` with `Closes #<n>`. The draft is the
   claim and the work log.
4. Keep the description current; comment decisions reviewers will need.
5. Abandon by un-assigning, closing the draft with a status comment, and
   leaving the issue open.

## Create issues

Non-interactive creation ignores issue forms: write the body with the
form's field labels as `### <label>` headings and pass its labels, for
example `gh issue create --title <t> --body-file <f> --label type:task`.
Labels come only from `.github/labels.json`; never create one with
`gh label create`.

## Publish gate

Everything pushed or posted is public to everyone who can see the
repository and cannot be reliably erased. Every push, pull request, comment,
label, and release passes this gate.

1. Assemble the exact payload as files in a directory outside the
   repository: `title.txt`, `body.md`, and for a push or pull request
   `commits.txt` (`git log <base>..HEAD --format=full`) and `diff.patch`
   (`git diff <base>...HEAD`).
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
becomes visible to everyone who can see the repository and cannot be
reliably deleted; for a pull request that includes every commit message and
the whole diff. You have no other context; judge only what the files say.
1. List the files. If the directory is empty, a required file is missing,
   or a file is unreadable, end with SAFE TO PUBLISH: NO.
2. Check every line for: secrets and credentials; real personal data;
   internal-only hosts, URLs, or codenames; files in the diff unrelated to
   the stated change; @-mentions or cross-references that would notify
   people not involved; hostile or regret-worthy wording.
3. Report one line per finding: file, excerpt with secrets masked,
   category, fix. If none, say "No findings."
4. Your last line is exactly SAFE TO PUBLISH: YES or SAFE TO PUBLISH: NO.
   Any secret, personal data, or internal-only finding means NO.
```

A secret that reached GitHub is compromised even after deletion: rotate it.

## Red checks

Run `python3 scripts/run_log_digest.py --repo {{OWNER_REPO}} --run-id <id> --tail 40` and read its JSON; never fetch full logs. <!-- # CONFIGURE: OWNER/REPO, and the script path if the project keeps scripts elsewhere. -->
Reproduce the failing step locally, fix it on the same branch, and push
through the publish gate. Never weaken, skip, or delete a check to pass.

## Finish

1. Every task is one commit and no draft commits remain on the branch
   (`git log <base>..HEAD --oneline`); squash any that do before pushing.
2. {{LOCAL_CHECK_COMMAND}} green, checklist ticked, description final. <!-- # CONFIGURE: the local check command. -->
   <!-- harness: spec-workflow -->
3. Follow the authority policy for what comes next; by default the agent
   stops at the draft and reports to the human (goal, checks, scope, risks,
   what remains), and `gh pr ready`, review requests, and merging are the
   human's.
4. {{MERGE_RULE}} <!-- # CONFIGURE: the agreed merge rule, e.g. "Squash only: the pull request title becomes the commit on the default branch, so it follows the commit convention." -->
5. After the merge, confirm the linked issue closed.

## Releases

{{RELEASE_RULE}} <!-- # CONFIGURE: the agreed release rule, e.g. "A maintainer pushes a vX.Y.Z tag on the default branch; .github/workflows/release.yml publishes it. Agents never push tags." -->
