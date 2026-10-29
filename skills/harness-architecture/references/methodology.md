# The Methodology, Operationalised

Read when the question is a reasoning question (why a practice holds,
whether it applies here) or asks for the rule or budget that applies. The
core every branch cites (two duties, five variables, context economics,
entropy law, entrypoint budget) is inline in `SKILL.md`; this file holds
the rest of the method. Loading modes live in `loading-modes.md` and the
single-source rules in `source-of-truth.md`; this file does not restate
them.

## Which variable moves which layer

Every boundary that tightens also suppresses rare, better solutions, so the
balance point is set per layer. Error cost drives hard boundaries and the
environment; maintenance horizon drives entropy management and knowledge;
isolation loosens gates and widens allowlists; autonomy drives authority,
specification, and hard boundaries; team size drives hard boundaries and
knowledge. A task type is one typical combination of those variables, not
an input to the judgement [§1.1] [§6.1].

## Context costs beyond the core

Over-split documents cost a tool call per hop, and missing context causes
expensive rewrite loops; a good structure is cheaper than letting the agent
guess [§1.2]. An entrypoint that agents ignore is usually over budget, not
under-worded [§2.1]. Read `source-of-truth.md` when the question is
whether a fact belongs in a document at all [§1.3].

## The entrypoint

Two parts: always-applicable constraints first (global safety, commit and
release discipline, language, the validation command; the test is that the
cost of violating it does not depend on the task), then a routing table
organised by scenario ("when doing X, read Y") that doubles as the
declaration of where each fact lives. A small project's forward sync rules
are a few keep-in-sync lines in this file, each naming its trigger [§5.2]
[§6.1]. Before any split, four questions: how does the agent know it needs
the file; what does it gain; how much irrelevant content rides along; is
the hop cheaper than inlining. The budget forces that fourth question on
every block; always-applicable constraints are never squeezed out to meet
it [§2.1].

## Knowledge file or project skill

Knowledge files hold information and architecture; skills hold procedures.
A procedure earns a skill when it is recurring, non-obvious, and fragile,
ordered, or branching; otherwise a cheaper carrier (an entrypoint line, a
knowledge file, a recipe) serves [§2.3]. A mechanical operation of one or
two lines is inlined; a long one with argument assembly or output filtering
becomes a script that returns a summary, not the full log [§2.4].

## Entropy

Harness drift is defended like code drift, by checks (reference integrity first,
structural compliance second) whose failure message names the fix [§5.3].
Read `source-of-truth.md` when a fact is copied or a sync rule is in
question.

## Six layers as the only design axes

Thickness is rated per layer, never per project, on four grades: omitted,
light (a sentence or a pointer), medium (a dedicated file or configuration,
enforced by convention), thick (machine-enforced check or isolation). The
layers: environment and sandbox [§3.2] [§3.3]; knowledge and routing
[§2.1] [§2.2] [§2.3]; hard-boundary gates [§3.1]; authority [§4.2];
specification and completion [§4.1]; entropy management [§5.2] [§5.3].
Platform lifecycle (branch model, merge method, issue and pull-request
entities, remote state) is the seventh layer this plugin builds; the method
covers it in checkpoints and publishing [§4.3] and remote shared state
[§4.4]. Over-thick is entropy too: a constraint that no longer blocks
anything only slows the agent [§6.2]. Taking over an existing project:
research first, keep what works as the source of truth, rate each layer
from what exists and add only the gap; specifications for code nobody
changes rot immediately [§6.3].
