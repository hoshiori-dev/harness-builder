# Necessity: the Minimal Set and the Deletion Test

Read when proposing the entity set, when the user asks for any entity beyond
it, or when the probe finds labels, milestones, or boards the minimal set
does not contain.

## The minimal set

Recommend this and nothing more:

| Entity | Why it earns its place |
|---|---|
| `type:bug`, `type:feature`, `type:task` labels | agents and reviewers filter by kind of work; one per issue |
| `area:<name>` labels, one per real module or ownership boundary | review routing and filtering by where the change lands |
| `spec:` namespace, reserved | the specification workflow appends its state rows to the same label file later |
| bug, feature, and task issue forms (GitHub) or templates (GitLab) | an agent or human files work with the fields acceptance needs |
| one pull or merge request template | the reviewer finds the outcome, the linked issue, and the validation in the same place |

Deliberately not created, and named as such when proposing the set:
Projects, boards, Milestones, iterations, epics, `priority:` and `status:`
labels, Discussions, wiki. A filtered issue list shows current work; a
board over it is a second view to keep in step. [§6.2]

Derive `area:` names from the repository's top-level modules or the
CODEOWNERS boundaries; ask when two readings are possible. A one-module
project gets no `area:` labels.

## The deletion test

Before creating anything outside the minimal set, ask the user one
question and write the answer beside the entity in the knowledge file:

> Without <entity>, what management ability is lost: what could nobody
> find, decide, or coordinate any more?

| Entity | It passes when |
|---|---|
| `priority:` labels | someone schedules from them weekly and an ordered issue list does not serve |
| `status:` labels | an open draft request and the assignee do not already show the state |
| Milestones | releases are dated and people judge progress against the date |
| Projects or boards | several people plan across repositories and a filtered list cannot show it |
| CODEOWNERS | more than one reviewer, and review must follow paths |
| an extra issue form | that kind of work needs fields the three forms do not carry |

An answer of "nice to have", "for later", or "other projects have it" fails
the test: propose not creating it. The user can still insist; then record
their answer as the reason and create it. [§6.2]

## Existing surplus

When the probe finds labels, milestones, or a board outside the set:

1. Count use per object: open issues and requests carrying the label, open
   issues in the milestone, items on the board.
   - GitHub: `gh issue list -R OWNER/REPO --label "<name>" --state open --json number --limit 1`
     and the same with `gh pr list`.
   - GitLab: `glab api "projects/<id>/issues?labels=<name>&state=opened&per_page=1"`
     and `merge_requests?labels=...`.
   - GitHub board (each `number` under the probe's `boards`): open issues
     and requests on it,
     `gh api graphql -f query='query($o:String!,$r:String!,$n:Int!){repository(owner:$o,name:$r){projectV2(number:$n){items(first:100){nodes{content{... on Issue{state} ... on PullRequest{state}}}}}}}' -F o=OWNER -F r=REPO -F n=<number> --jq '[.data.repository.projectV2.items.nodes[] | select(.content.state == "OPEN")] | length'`
     (needs the `read:project` scope; a board over 100 items is counted
     as in use).
   - GitLab board: open issues carrying any label in its `list_labels`,
     with the issues command above per label; a board with no label lists
     shows only the plain issue list and counts as a second view of it.
2. List each object with its use count and the deletion test answered from
   the evidence.
3. Propose removal as its own decision, separate from the build plan. A
   deleted label disappears from every issue and request that carried it;
   a closed milestone keeps its issues, a deleted one unlinks them.
4. Delete only the objects the user said yes to, through the dry-run,
   approval, apply, readback sequence. An object the user keeps is a
   declined proposal.
