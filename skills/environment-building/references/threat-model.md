# Threat Model

Read when rating the middle band, when the user disputes the tier, or when
proposing the restricted instance.

## The three facts

- **Trifecta** describes what a successful injection can touch and send.
  Missing any one element, an injection causes no material loss: an agent
  with no credentials that cannot write outside the repository may read
  anything. Almost every networked coding agent has all three (credentials,
  file writes, external reads), so the trifecta only says an exposure
  exists; the next two facts grade it. [§3.2]
- **Source reachability** is the attacker's cost of placing content where
  the agent reads it. Trusted repository: unreachable. Reputation-guarded
  (official documentation, a major package's registry page, a well-known
  project's README): the attacker must compromise that site first.
  Open-write (the project's issues and pull request comments, search
  results, arbitrary pages, an obscure dependency's README): anyone, at no
  cost. Issues and tickets also sit in a task-instruction context, so a
  malicious "next step" reads like a normal request. [§3.2]
- **Human in the loop** means a person issues the task and every
  irreversible outward action (push, comment, release) either was
  pre-authorised in the plan or waits for that person. This single review
  of a few concentrated results is the gate; approving each command is not.
  An unattended agent has no gate. [§3.2]

Record each fact with its evidence: the configuration line, the token
scope, or the user's answer.

## Isolated tier

All three conditions (trifecta, an open-write source, no human) → propose
a separate restricted instance that removes one element of the trifecta:

- its own container or VM, not the developer's environment;
- none of the sensitive credentials; a token scoped to what the task needs
  (for issue triage: read the repository, write comments and labels);
- no write to the main branch and no change to configuration; results land
  as a branch or draft pull request a person reviews.

Present it as the recommendation and record the user's answer. A user who
declines keeps the regular tier as their recorded decision, with their
reason. [§3.2]

## Middle band and model resistance

Middle band: reputation-guarded sources, or open-write sources with a human
in the loop. There, the injection resistance of each model in use decides
how much to restrict sources or clean input for read-only retrieval:

- a model the user confirms as strongly resistant may read search results
  with no extra restriction;
- a weak model, or a lightweight model used as a retrieval sub-agent, gets
  tighter limits at the sandbox network layer or at tool-input cleaning
  (for example only allowlisted documentation hosts, or fetched pages
  reduced to text before the main agent reads them).

Ask the user to confirm resistance per model named (the exact model the
environment runs, and each sub-agent model), never per vendor. When the
model is unknown, add a pending decision with the stricter setting
recommended and continue. [§3.2]

## When the user argues a strong model replaces isolation

Decline to lower the tier and keep the proposal. Resistance lowers the
chance of a hijack; isolation lowers the loss after one. An agent that runs
code can bypass every framework defence once hijacked, so the two are not
substitutes. Challenge once; if the user still declines the restricted
instance, record that as their decision with their reason, and the tier
stays named as isolated in the knowledge file. [§3.2] [§3.3]
