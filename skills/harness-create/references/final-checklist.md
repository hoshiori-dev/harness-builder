# Final Checklist

Read when walking the closing checklist in step 9. Check every item against
the deposited files, not against the plan or memory. Each item ends as
**passed**, **not applicable** with the confirmed grade that omits it, or a
pending decision. A failing item is fixed, re-read, committed, and then
recorded as passed.

## Grading

- [ ] Each of the six layers has its own grade, none chosen for the project
      as a whole, and each grade matches the confirmed variables.

## Entrypoint

- [ ] The always-applies rules come first in `AGENTS.md`.
- [ ] The routing table is organised by when an agent needs to read what,
      not by topic.
- [ ] `AGENTS.md` is within budget (about 100 lines, at most 120); the
      client-specific file (`CLAUDE.md`) only imports it. [§2.1]

## Soft boundaries

- [ ] Content is split by how it loads, not by subject.
- [ ] Every process-critical project skill is routed explicitly from the
      entrypoint.
- [ ] A subdirectory entry file, if any, holds local additions only, never a
      rule that must always apply.

## Scripts and runtime experience

- [ ] Frequent complex commands are wrapped as task-runner recipes or
      scripts.
- [ ] Pagers and interactive prompts are disabled through environment
      variables (`PAGER=cat`, `GIT_PAGER=cat`, `CI=true` or the tool's
      equivalent).
- [ ] A test command for one file or module runs in seconds and is
      documented. [§4.3]

## Hard boundaries and error quality

- [ ] Pre-commit hooks and CI exist at the confirmed grade.
- [ ] Tools run with their native quiet or concise output flags.
- [ ] Every custom check's failure message says how to fix it. [§3.1]

## Security and control plane

- [ ] The isolation need was judged from the three exposure factors, source
      reachability, and whether a human is in the loop.
- [ ] Model resistance was used only as a modifier at the middle grade, and
      confirmed for the models actually in use.
- [ ] The sandbox was audited for host credentials, privileged sockets,
      local network exposure, and where session logs go.
- [ ] Security rules are hard read-only once the project is running;
      engineering configuration has a stated soft read-only invariant.
      [§3.3]

## Authority

- [ ] Irreversible actions are pre-authorised in the plan or spec, never
      allowed by a permission entry.
- [ ] When blocked, agents continue and collect a pending decisions list.
- [ ] Allow and deny lists allow the known safe, deny the known dangerous,
      leave the rest to the default, and hold no ask entry without a
      recorded reason.
- [ ] The authority policy protects itself: changing it is outside agent
      authority. [§4.2]

## Specification and completion

- [ ] A specification is aligned before work starts, at the confirmed grade.
- [ ] Each specification states its completion test, non-goals, and
      deliverables.
- [ ] Its scenarios can be judged by someone who has not read the code.
      [§4.1]

## Checkpoints and commits

- [ ] A checkpoint is a commit; the squash unit is the task.
- [ ] Draft commits never leave the machine.
- [ ] Secret scanning runs on every commit. [§4.3]

## Collaboration and hygiene

- [ ] Handoff files and session logs are treated as secrets: the handoff
      directory, when inside the repository, is in `.gitignore`. When it
      is not, add the rule, commit it as a checkpoint, and record the item
      as passed.
- [ ] Multi-agent rules (worktrees, remote branches, shared-resource
      isolation) exist only when the user said several agents write at
      once. [§4.4]

## Entropy loop

- [ ] Harness drift an agent finds has a place to be reported.
- [ ] Each fact has one source of truth and two-way sync rules.
- [ ] Reference-integrity and structure checks run in CI at the confirmed
      grade.
- [ ] Overly thick constraints are within the cleanup scope. [§5.2] [§6.2]
