# ADR 1200 - Automated Milestone Runner Architecture

Date: 2026-06-13

Status: Proposed for human review

## Context

ASF V1 has a supervised operator, Bridge handoff, task packet generation,
report intake, risk classification, independent review packets and controlled
publish tooling. The loop is still driven by large manual mega-steps.

The next architectural problem is context compaction. A model does not need the
entire project memory. It needs a small, correct, versioned slice: State Card,
Context Pack, Task Packet, gates and stop conditions.

## Decision

Define the Automated Milestone Runner as a future local-first, human-gated
orchestrator that advances roadmap milestones through explicit state machine
transitions. The runner stores state outside model memory, builds compact
context artifacts, runs deterministic gates before AI review, creates smaller
repair packets after failures and escalates to Alberto when risk or evidence
requires human judgment.

This step creates only the foundation:

- architecture documents;
- state machine definition;
- JSON Schemas;
- offline examples;
- offline validator;
- unit tests;
- roadmap 1300-2990.

## V1 Scope

V1 for this ADR means the architecture and contracts are versioned and
testable, but not operationally automated.

Included now:

- Roadmap Compiler contract;
- State Card, Context Pack and Task Packet contracts;
- runner state machine;
- deterministic gate and repair policy;
- human escalation policy;
- schema validator and examples.

Excluded now:

- real Codex automation;
- live provider calls;
- MCP execution;
- automatic commit, push, PR, merge, deploy or tag;
- scheduler or unattended loop;
- dashboard UI;
- SQLite implementation.

## Consequences

Positive consequences:

- future automation can be built against small machine-readable contracts;
- model context becomes a managed artifact, not an implicit chat memory;
- deterministic gates remain stronger than AI review;
- repair loops become bounded and auditable;
- human escalation remains explicit.

Residual risks:

- schemas can drift from implementation until a real runner exists;
- examples are offline and cannot prove real execution behavior;
- context compaction may omit important details if the future compiler is too
  aggressive;
- repair logic can only be trusted after real failing-step pilots.

Mitigation: keep the validator simple, keep examples realistic, require local
gates before review, and implement future steps incrementally.

## Next Step

1300-1390) Task Packet Schema and Roadmap Compiler
