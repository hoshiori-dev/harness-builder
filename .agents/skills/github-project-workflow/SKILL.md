---
name: github-project-workflow
description: >-
  Runs this repository's GitHub issue and pull-request lifecycle. Use when
  taking, creating, updating, or completing an issue or pull request, before
  any gh write (labels, comments, state), when a CI check is red, or when
  preparing a release. Not for changing the lifecycle policy itself, which
  needs user approval and lives in the knowledge base.
---

# GitHub project workflow

Tool: authenticated `gh`. Policy lives in `.agents/knowledge/github-workflow.md`,
authority in `.agents/knowledge/agent-authority.md`, branch names in
`.agents/knowledge/git-workflow.md`; this skill is the procedure.

## Take work

1. Read the issue; confirm it is open, unassigned (or assigned to you), and
   its acceptance criteria are checkable. Otherwise stop and ask.
2. `gh issue edit <n> --add-assignee @me`, then
   `gh issue develop -c <n>` to create and check out the branch.
3. Push and open a draft PR immediately: title in Conventional Commits form,
   body from `.github/pull_request_template.md`, `Closes #<n>` under
   "Related work" together with the OpenSpec change directory or
   `spec-less: <reason>`. The draft is the claim and the work log.
4. For a spec-carrying change, wait for the `spec: approved` label before
   tasks or code. Keep the PR description current; comment decisions.
5. Abandon by un-assigning, closing the draft with a status comment, and
   leaving the issue open.

## Create issues

Non-interactive creation ignores forms. Mirror the chosen form's `### <label>`
headings (`.github/ISSUE_TEMPLATE/*.yml`) in the body and pass the form's
labels: `gh issue create --title ... --body-file ... --label "type: task" --label "area: harness"`.
Area labels: `area: skills | mcp | agents | harness`.

## Finish

1. `just check` green, generated files regenerated, checklist ticked, PR body
   final.
2. Self-review per `.agents/knowledge/agent-authority.md`: one read of the
   whole diff against the issue and the spec; fix only what changes
   correctness, scope, or reviewability; no style or refactoring pass.
3. `gh pr ready <n>`, then hand off: one PR comment headed `Ready for review`
   (what changed, what the self-review changed, where to start) and the same
   report to the human in the session, with checks and what was verified in
   which client. CODEOWNERS requests every listed owner except the author, so
   with the maintainer's own account the comment is the request
   (`.agents/knowledge/agent-authority.md`, Handoff). Approving and merging
   stay human.
4. After the maintainer's review, archive the OpenSpec change on the branch
   (`openspec-archive-change`); a spec-less change carries `spec: skipped`
   from the `pr-labels` workflow, nothing to do. Report once more. Until the archive is pushed the `pr`
   workflow withholds `checks / spec-archived` and the merge stays blocked;
   `just spec-archived` names what is still open.

## Checks

Red check → read `.agents/knowledge/github/checks.md` for the recipe, run it
locally (`just <recipe>`), fix at the source. `gh run view <id> --log-failed`
shows the failing step. Never edit a workflow to pass.

## Publishing gate

Before any write that leaves the machine (issue, comment, label, PR body,
release), draft the exact text locally, scan it for secrets and private
paths (`betterleaks stdin` or by reading), confirm the action is within the
authority policy, then execute non-interactively and read the result back.
Everything here is public and cannot be reliably undone.

## Releases (maintainer-approved only)

Bump `version` in `plugin.json` through a normal PR (`just gen` updates the
mirrors), merge, then the maintainer tags `v<version>` on `main` and pushes
the tag; `.github/workflows/release.yml` builds and publishes. Verify with
`gh release view v<version>`.
