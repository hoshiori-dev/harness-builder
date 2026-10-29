# Pruning: the three passes

Read when running the passes over a draft, or when two readers disagree
whether a line is a no-op.

## 1. Deduplicate

Every meaning has exactly one home. For each rule or fact stated twice, keep
the copy ranked correctly on the information hierarchy (the description keeps
triggers; the body keeps rules; a reference keeps branch detail) and delete
or pointer-ise the rest. In descriptions, synonym triggers for one branch are
duplication. Distinguish duplication from a leading word: a leading word
repeats a token on purpose; duplication repeats a meaning by accident.

## 2. Relevance

For every line ask: does this still bear on what the skill does? Delete
exposition, material that belongs to a branch already disclosed elsewhere,
and stale layers: instructions for tools that changed, caveats for bugs long
fixed, examples of formats no longer used. When in doubt whether a line is
stale, test the skill without it.

## 3. No-op hunt

Sentence by sentence, not line by line: does this sentence change behaviour
versus what the least capable model the skill carries would do unprompted?

The verdict is model-relative, not reader-relative. Two people disagreeing
whether a line is a no-op disagree about the default; settle it by running
the skill on the floor tier, not by debate. A no-op for a strong model can be
load-bearing for a weaker one, so pruning graded only against the development
model ships a skill that breaks below it.
