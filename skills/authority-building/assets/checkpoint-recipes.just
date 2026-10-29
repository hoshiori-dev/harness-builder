# Checkpoints are commits, never stashes. A task's drafts are squashed into
# one commit with squash-task when the task ends; drafts never leave the
# machine; push-one pushes one ref and refuses while a draft remains.
# git reset --hard stays denied: rollback commits the tree before it resets.
# Commits carry no AI or tool attribution: no co-author trailer, tool name,
# or model name.

set shell := ["bash", "-euo", "pipefail", "-c"]
set positional-arguments

export GIT_PAGER := "cat"
export GIT_TERMINAL_PROMPT := "0"

# CONFIGURE: the subject prefix that marks a draft commit; push-one refuses while one is on the branch.
draft_prefix := "checkpoint"
# CONFIGURE: the long-lived branch drafts must never reach.
base_branch := "main"
# CONFIGURE: the remote push-one pushes to; keep it equal to the remote named in the Codex force-push rule.
remote := "origin"
# CONFIGURE: the commit-subject regex of the project's convention. Below: Conventional Commits. Plain 50/72 titles: '^[A-Z]$|^[A-Z].{0,48}[^.]$'.
subject_re := '^(feat|fix|docs|refactor|test|chore|ci|build|perf|style|revert)(\([a-z0-9-]+\))?: [a-z].{0,70}[^.]$'

# Commit everything in the working tree as a draft checkpoint.
checkpoint message:
    @if [ -z "$(git status --porcelain)" ]; then echo "checkpoint: nothing to commit; the tree is clean" >&2; exit 1; fi
    @git add -A
    @git commit --quiet -m "{{ draft_prefix }}: $1"
    @echo "checkpoint $(git rev-parse --short HEAD): {{ draft_prefix }}: $1"

# Squash every commit after <start> into one commit with <message>, non-interactively.
squash-task start message:
    @if ! git merge-base --is-ancestor "$1" HEAD; then echo "squash-task: $1 is not an ancestor of HEAD; pass the commit the task started from" >&2; exit 2; fi
    @if [ "$(git rev-parse "$1")" = "$(git rev-parse HEAD)" ]; then echo "squash-task: nothing after $1 to squash" >&2; exit 1; fi
    @upstream=$(git rev-parse --abbrev-ref '@{upstream}' 2>/dev/null || git rev-parse --verify --quiet --abbrev-ref "{{ remote }}/$(git rev-parse --abbrev-ref HEAD)" || true); if [ -n "$upstream" ]; then pushed=$(comm -12 <(git rev-list "$1..HEAD" | sort) <(git rev-list "$upstream" | sort)); if [ -n "$pushed" ]; then echo "squash-task: commits after $1 are already on $upstream; pushed history is reverted, not rewritten" >&2; exit 1; fi; fi
    @if [ -n "$(git status --porcelain)" ]; then echo "squash-task: the tree is dirty; run 'just checkpoint <message>' first" >&2; exit 1; fi
    @if ! printf '%s\n' "$2" | head -n1 | grep -Eq '{{ subject_re }}'; then echo "squash-task: subject '$2' does not match the commit convention {{ subject_re }}" >&2; exit 2; fi
    @git reset --quiet --soft "$1"
    @git commit --quiet -m "$2"
    @echo "squashed into $(git rev-parse --short HEAD): $2"

# Discard the current approach and return to <ref>, committing a checkpoint first when the tree is dirty.
rollback ref:
    @if ! git rev-parse --verify --quiet "$1^{commit}" >/dev/null; then echo "rollback: $1 does not name a commit" >&2; exit 2; fi
    @if [ -n "$(git status --porcelain)" ]; then git add -A; git commit --quiet -m "{{ draft_prefix }}: before rollback to $1"; echo "rollback: uncommitted work saved as $(git rev-parse --short HEAD) (reachable through git reflog)"; fi
    @git reset --quiet --hard "$1"
    @echo "rolled back to $(git rev-parse --short HEAD)"

# Push the current branch as one explicit ref, after checking that no draft commit remains on it.
push-one:
    @branch=$(git rev-parse --abbrev-ref HEAD); if [ "$branch" = "{{ base_branch }}" ]; then echo "push-one: on {{ base_branch }}; changes reach it through a pull request" >&2; exit 1; fi
    @drafts=$(git log --format='%h %s' "{{ base_branch }}..HEAD" | grep -E '^[0-9a-f]+ {{ draft_prefix }}: ' || true); if [ -n "$drafts" ]; then printf 'push-one: draft commits on the branch; run just squash-task <start> "<message>" first:\n%s\n' "$drafts" >&2; exit 1; fi
    @git push --set-upstream "{{ remote }}" HEAD
