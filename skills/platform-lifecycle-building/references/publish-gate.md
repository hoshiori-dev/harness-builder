# Publish Gate

Read when reworking the publish gate in the project skill, or before the
build itself makes a publishable write (an issue, a comment, a pull or
merge request, a push).

Anything published to the platform (bodies, comments, commit messages,
diffs, tags, and their notification copies) cannot be reliably erased, and
on a public repository it is indexed within minutes. Prevention at this
gate is the only control.

## The rules the deposited skill keeps

These survive every rework; adapt wording to the project, never the rule.

1. **Exact payload in files.** Assemble the final payload in a directory
   outside the repository, never from memory: `title.txt`, `body.md`, and
   for a push or request `commits.txt` (`git log <base>..HEAD --format=full`)
   and `diff.patch` (`git diff <base>...HEAD`). A request publishes its
   commits and diff, not only its description.
2. **Clean-context review.** One subagent whose whole prompt is the review
   prompt with the directory path substituted, nothing added: explaining
   intent destroys the independence the review exists for.
3. **File-only fallback.** Where the client cannot dispatch a
   clean-context subagent: re-read every payload file from disk against the
   same checklist, judge only what the files contain, and write
   `Review mode: file-only (not clean-context)` directly above the verdict.
4. **Verbatim verdict.** The review's last line is exactly
   `SAFE TO PUBLISH: YES` or `SAFE TO PUBLISH: NO`. Any other last line,
   including a YES with extra words, is NO.
5. **Fix, rebuild, re-review.** On NO, fix every finding, rebuild the
   directory, and review again. Any edit after a YES needs a fresh review;
   the published bytes equal the reviewed bytes.
6. **Authority, then act.** The authority policy decides whether the agent
   may take the action at all; the gate decides only whether the payload is
   safe. Execute non-interactively and read the result back.
7. **Leaked secret.** A secret that reached the platform is compromised
   after deletion: rotate it.

The review prompt itself is in the project-skill asset; keep its four
numbered checks and its last-line rule unchanged. On GitLab it also checks
for lines starting with `/`, which run quick actions.

## The build's own writes

Label syncs and setting changes follow the dry-run, approval, apply,
readback sequence instead: their payload is the delta the user approves.
Any issue, comment, request, or push the build makes passes this gate
first, and the approval to make it is a separate decision by the user.
