# Tracked Work

Read when a loop step meets a change request: opening the draft, reading
review threads, writing the request body, marking it ready, freezing in the
request, or a recorded approval mode. The project's contract and templates
use the platform's own words (pull request, merge request) and win over
this file.

## Request shapes

| Step | Combined (default when review sits on a request) | Split |
|---|---|---|
| Publish (step 3) | push the pre-authorised branch, open a draft request whose only content is the package (authorised by the user's step 3 confirmation) | open a specification request carrying only the record (same authorisation) |
| First gate | closed by the approver on the draft | the specification request is approved and merged |
| Tasks and code | same branch, after the closing | implementation requests, each linking the merged record |
| Ready (step 7) | mark the same request ready, record still open | per implementation request |
| Freeze (step 8) | on the request's branch, after the second closing | on the last implementation request |

Combined is the default only once the contract or the user puts review on
a request; otherwise the shape is none. Recommend split only where consumers
depend on a stable published contract before implementation starts.

## Approval modes

| | Conversational (default) | Recorded |
|---|---|---|
| What the approver does | discusses, directs record changes, says the review is closed | the same, then leaves the mark the contract names on the version approved |
| What stands as approval | the closing plus the review state at that moment; at the second gate, the freeze commit | a durable, attributable mark bound to one version, such as a platform review approval that a new commit dismisses |
| A record change while waiting | update the record, publish it, keep waiting | the same; the mark is taken again after the last change |

Recommend conversational approval for a solo developer or a pair, and
recorded approval for a multi-person team or unattended agents, or whenever
someone outside the conversation (an auditor, a release manager) must verify
that a named person accepted a named version.

## Reading the review record

Read every comment and every review thread with its resolution state
before reconciling:

- GitHub: `gh api repos/{owner}/{repo}/issues/{n}/comments` for comments,
  and the GraphQL `pullRequest.reviewThreads` connection with `isResolved`
  for threads.
- GitLab: the merge request discussions endpoint; each note carries
  `resolvable` and `resolved`.

Verify the exact command against `gh --help` or the platform's current API
documentation before running it. Record the closing on the request's
approval line: who closed it, when, and which items were confirmed open.
Editing the request body is a platform write: do it only when the approved
package lists it; otherwise record the closing in the change record and add
the edit to the pending decisions list.

## Default request body

Follow the project's template when one exists. Otherwise:

1. An opening paragraph stating what is true once the request merges.
2. Why it is worth merging now.
3. A specification block: `Spec:` linking the change record on the branch;
   `Phase: specification` until the first closing, `implementation` after;
   one link per package file, with the task list labelled after-approval
   material; an `Approval:` line naming the open gate and what closes it.
4. The closing reference to the work item, or why none exists.
5. Changes and Validation, each a reserved line until the request is ready;
   then Changes lists the touched files and Validation names each scenario
   with its result.

Never paste the task list or a diff summary into a draft in the
specification phase.

## Ready, then the freeze

The request is marked ready with its record still unfrozen. A project
check that fails ready requests holding an unfrozen record is the merge
block for the whole second review; it is expected. Never freeze early to
clear it.

The freeze is a commit on the request's branch: every task done and
verified, the carrier's archive or write-back, the validator, the commit.
On a fork the agent cannot push to, the person who holds the branch runs
it.

Before any push, approval claim, or handover, compare the branch tip with
the freeze commit (`git log --oneline <freeze-sha>..HEAD`). Any commit
listed spends the closing: say so, name the commits, and ask whether the
review reopens.

Status labels an automation derives from the record are facts about it;
never set or remove one by hand.
