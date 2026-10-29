# Methodology Map

Read when the user asks which part of the method covers a topic, which
layer owns it, or which skill to invoke, and when handing off a build. Two
user-invoked entries exist and are the only skills this map names:
`harness-create` builds a harness for a project, `harness-improve` audits
and reworks an existing one. Every other skill is named by role: a layer
builder is the skill whose description claims that layer, with the layer
name as written in the Layer column, and the entries route to it by that
claim. A build request ends with the handoff wording below; an approved
plan precedes any file.

| Section | Topic | Layer | Who answers or builds |
| --- | --- | --- | --- |
| §1.1 | Two duties, five variables | all | this manual; `harness-create` asks the five variables |
| §1.2 | Context economics | knowledge and routing | this manual; the knowledge and routing builder |
| §1.3 | Code describes itself; what documents hold | knowledge and routing | this manual (`references/source-of-truth.md`); the knowledge and routing builder |
| §2.1 | Entrypoint: always-applicable block, routing table, four questions, budget | knowledge and routing | the knowledge and routing builder |
| §2.2 | Five loading modes, framework caveats, subdirectory rule, hooks | knowledge and routing | this manual (`references/loading-modes.md`); the knowledge and routing builder |
| §2.3 | Knowledge file versus skill, explicit routing, path addressing | knowledge and routing | the knowledge and routing builder decides the warrant; the skill that writes project skills writes it |
| §2.4 | Heuristic and tool scripts, output quieting | knowledge and routing | the knowledge and routing builder |
| §3.1 | Error engineering: native quiet output, error as routing | hard-boundary | the hard-boundary builder |
| §3.2 | Threat model: lethal trifecta, source reachability, human in the loop | environment | the environment builder |
| §3.3 | Sandbox audit, control-plane spectrum (hard and soft read-only) | environment; hard-boundary for the soft read-only invariant | the environment builder; the hard-boundary builder |
| §3.4 | Fallback verification, verifier subagent | hard-boundary | the hard-boundary builder; the read-back verifier agent |
| §4.1 | Spec-driven development, completion boundary, four quality rules | specification and completion | the specification and completion builder; the development-loop skill; the carrier skills for OpenSpec, Spec-Kit, and the lightweight format |
| §4.2 | Authority: approval at both ends, reversibility, denial handling, framework rules, pairing, self-protection | authority | the authority builder |
| §4.3 | Non-interactive execution, fast feedback, checkpoints as commits, publishing, handoff hygiene | authority (checkpoints), environment (variables), platform lifecycle (branches, push) | the authority builder; the environment builder; the platform lifecycle builder |
| §4.4 | Multi-agent concurrency, shared resources, remote state | authority; platform lifecycle | this manual (`references/multi-agent.md`); the authority builder (remote rules); the platform lifecycle builder |
| §5.1 | Entropy law | entropy | this manual; the entropy builder |
| §5.2 | Correction reports, single source of truth, forward and reverse triggers, observation, canaries | entropy | the entropy builder; this manual (`references/source-of-truth.md`) |
| §5.3 | Deterministic harness checks (reference integrity, structural compliance) | entropy | the entropy builder (delivers the self-check) |
| §6.1 | Six layers, four grades, five variables | all | `harness-create` (five variables, thickness table) |
| §6.2 | Hardening and thinning | all | `harness-improve` |
| §6.3 | Taking over an existing project | all | `harness-create` (brownfield) and `harness-improve` (audit); this manual (`references/audit.md`) |
| Appendix | Quick self-check checklist | all | `harness-create` (final checklist) |

The platform lifecycle layer (branch model, merge method, issue and
pull-request entities, labels, remote settings) has no chapter of its own;
the method reaches it through §4.3 and §4.4, and the platform lifecycle
builder owns it.

## Handoff wording

For a build after a question, and for the closing of an audit: "Sections
§x.y cover this; the <layer> layer owns it; invoke `harness-create` (new
harness) or `harness-improve` (existing harness), which plans with you,
gets the plan approved, and routes the layer to its builder. Nothing is
written before that approval."
