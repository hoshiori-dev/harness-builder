# Knowledge Files and Layout

Read when presenting where knowledge and project skills live, when the user
asks why that layout, when writing a knowledge file, or when agent docs
already exist anywhere in the repository.

## Why the layout

A client-neutral folder keeps one real copy of each skill: Codex reads
`.agents/skills/`, Claude Code reads `.claude/skills/`, and the relative
link makes them the same directory.

Keep knowledge in the repository; bridge an external source (wiki,
tracker) only when the maintained truth already lives there, and then the
routing row says it is the source of truth and what agents may read or
write. Never invent an external source or assume access. [§2.1]

## Writing a knowledge file

- **First line**: "Read this when …", naming the situation exactly as its
  routing row does. Nothing (title, front matter) comes before it.
- **One concern** per file. Two situations with disjoint readers are two
  files, or one file with sections the routing rows name.
- **Facts first**: the constraint, value, or decision in the first lines;
  the reason after it; no narrative, history, or greeting.
- **Only what code cannot state**: why, and when to read what. A request to
  list every directory or recipe is declined: keep a macro map of the
  long-lived top-level directories in the entrypoint, point at the task
  runner for recipes, and record only the why and when. [§1.3] [§2.3]
- **Source of truth**: when the file summarises something maintained
  elsewhere, name that source and say it wins on conflict.
- **No placeholder files**: create only what a current need passed the four
  questions for.

Procedures with ordered or branching steps are skill candidates; facts and
architecture are knowledge. [§2.3]

## Existing agent docs (brownfield)

1. **Inventory** every agent-facing doc: path, topic, first line, which
   entrypoint line reaches it.
2. **Report each unreached file as invisible** and ask, per file: route it
   (write the routing row and a "Read this when" first line), merge it into
   another file, or delete it. Never route all of them silently. Deletion
   needs the user's explicit choice for that file.
3. **Deduplicate**: where two files state one fact, recommend keeping the
   current one and deleting the other copy.
4. **Converge in place**: move content into the chosen folder, converting
   it to the rules above as it moves, and update the routing table in the
   same change as each move.
5. **Drop instead of migrating**: content that contradicts the code,
   session-transcript notes with no durable fact, and restatements of what
   code shows. Recommend the drop; the user decides.
6. **Leave public files alone**: README, CONTRIBUTING, and SECURITY are not
   knowledge files; route to one when agents need it, never absorb or
   restyle it. [§6.3]
