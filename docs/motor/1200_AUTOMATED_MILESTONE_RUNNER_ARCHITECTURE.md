# 1200 - Automated Milestone Runner Architecture

## Scope

This document defines the future ASF Automated Milestone Runner architecture.
It does not implement an automatic runner. It defines the components,
boundaries and contracts needed to move from manual mega-steps to supervised
milestone-by-milestone execution.

## Design Principle

The model sees little, but it sees the right little.

ASF must not rely on long model memory. ASF must store state, context, gates,
repair attempts and audit evidence in versioned or operational artifacts.

## Components

| Component | Responsibility | V1 status |
|---|---|---|
| Roadmap Compiler | Reads long roadmap and selects the next milestone slice. | Contract only. |
| State Store SQLite | Stores runner state, transitions, evidence pointers and retry counters. | Roadmap. |
| Task Packet Builder | Builds a compact executable packet with scope, deliverables, gates and stop rules. | Schema and example. |
| Context Pack Builder | Selects summaries and relevant files under a size policy. | Schema and example. |
| State Card Generator | Produces the short state summary for the next model turn. | Schema and example. |
| Codex Execution Adapter | Invokes Codex only after approval and within an allowed sandbox. | Roadmap, no real invocation. |
| Gate Runner | Runs deterministic checks and records command evidence. | Roadmap, contract only. |
| AI Reviewer Node | Reviews evidence independently after deterministic gates. | Contract only. |
| Repair Loop Controller | Builds smaller repair packets and stops after bounded attempts. | Contract only. |
| Publish Controller | Coordinates branch, PR and merge through explicit approvals. | Roadmap, no publish here. |
| Bridge Artifact Manager | Writes operational prompt/report artifacts and compact summaries. | Manual Bridge output only. |
| Human Escalation Manager | Stops for Alberto on risk, policy, cost, privacy or ambiguity. | Policy document. |
| Budget / Quota / Timeout Controller | Tracks tokens, provider quota, runtime and retry budgets. | Roadmap. |
| MCP Tool Gateway | Future tool gateway with allow-list and audit. | Roadmap, no MCP execution. |
| Dashboard / Report UI futura | Future status and evidence UI. | Roadmap. |

## Target Loop

```text
Roadmap
-> Roadmap Compiler
-> State Card
-> Context Pack
-> Task Packet
-> human approval when required
-> Codex Execution Adapter
-> deterministic local gates
-> AI Reviewer Node
-> repair loop when safe
-> Publish Controller when approved
-> updated State Card
-> next milestone
```

## V1 Now

This step creates:

- ADR 1200;
- architecture documents;
- state machine specification;
- JSON Schemas under `schemas/asf_automation/`;
- examples under `examples/asf_automation/`;
- `scripts/asf_validate_automation_schemas.py`;
- `tests/unit/test_asf_automation_schemas.py`;
- minimal documentation sync.

## Roadmap Later

Later steps must implement:

- Roadmap Compiler;
- State Card and Context Pack builders;
- Codex adapter lab;
- unified gate evidence store;
- AI reviewer and repair loop;
- publish controller integration;
- dashboard and recovery/replay tooling.

## Explicit Non-Goals For This Step

This step does not:

- call OpenAI or any provider;
- invoke Codex;
- execute MCP tools;
- run unattended loops;
- commit, push, open PRs, merge, tag or deploy;
- create a UI;
- add runtime dependencies.
