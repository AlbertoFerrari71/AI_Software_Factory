# 1200 - Automated Milestone Runner State Machine

## Purpose

The runner state machine makes milestone progress explicit, recoverable and
auditable. A model turn is never the source of truth. The state store records
the current state, transition evidence and stop reasons.

## States

| State | Meaning |
|---|---|
| PLANNED | Milestone exists in roadmap but no context has been built. |
| READY_FOR_CONTEXT | Preconditions are satisfied and context selection can start. |
| CONTEXT_PACK_BUILT | A compact context pack exists. |
| TASK_PACKET_BUILT | A task packet exists and is ready for approval or execution. |
| WAITING_HUMAN_APPROVAL | A policy requires Alberto approval before execution. |
| READY_FOR_CODEX | The task packet is approved for Codex execution. |
| CODEX_RUNNING | Codex execution is in progress. |
| CODEX_DONE | Codex execution finished and output is available. |
| REPORT_COLLECTED | Codex report was collected and normalized. |
| LOCAL_GATE_RUNNING | Deterministic local gates are running. |
| LOCAL_GATE_PASS | Deterministic local gates passed. |
| LOCAL_GATE_FAIL | Deterministic local gates failed. |
| AI_REVIEW_RUNNING | Independent AI review is running on evidence. |
| AI_REVIEW_PASS | Independent review passed or passed with warnings. |
| AI_REVIEW_FAIL | Independent review failed or blocked. |
| REPAIR_PACKET_BUILT | A smaller scoped repair packet exists. |
| REPAIR_RUNNING | Repair execution is in progress. |
| READY_FOR_PUBLISH | Local gates and review permit a publish request. |
| PUBLISH_RUNNING | Approved publish controller phase is in progress. |
| PUBLISHED | Branch or PR publication finished. |
| CI_RUNNING | Remote CI checks are running. |
| CI_PASS | CI passed. |
| CI_FAIL | CI failed. |
| DONE | Milestone is complete. |
| BLOCKED | Safety, policy or evidence prevents progress. |
| ABORTED | Human explicitly stopped the run. |

## Main Transitions

```text
PLANNED -> READY_FOR_CONTEXT
READY_FOR_CONTEXT -> CONTEXT_PACK_BUILT
CONTEXT_PACK_BUILT -> TASK_PACKET_BUILT
TASK_PACKET_BUILT -> WAITING_HUMAN_APPROVAL
TASK_PACKET_BUILT -> READY_FOR_CODEX
READY_FOR_CODEX -> CODEX_RUNNING
CODEX_RUNNING -> CODEX_DONE
CODEX_DONE -> REPORT_COLLECTED
REPORT_COLLECTED -> LOCAL_GATE_RUNNING
LOCAL_GATE_RUNNING -> LOCAL_GATE_PASS
LOCAL_GATE_RUNNING -> LOCAL_GATE_FAIL
LOCAL_GATE_FAIL -> REPAIR_PACKET_BUILT
AI_REVIEW_FAIL -> REPAIR_PACKET_BUILT
LOCAL_GATE_PASS + AI_REVIEW_PASS -> READY_FOR_PUBLISH
READY_FOR_PUBLISH -> PUBLISH_RUNNING
PUBLISH_RUNNING -> PUBLISHED
PUBLISHED -> CI_RUNNING
CI_RUNNING -> CI_PASS
CI_RUNNING -> CI_FAIL
CI_PASS -> DONE
any state -> BLOCKED on safety or policy violation
any state -> ABORTED on explicit human interruption
```

## Transition Rules

- Every transition requires evidence.
- A failed deterministic gate cannot be overridden by AI review.
- `READY_FOR_PUBLISH` requires both local gate pass and AI review pass.
- `REPAIR_PACKET_BUILT` must point to a parent task packet.
- A repair packet must be smaller than the original task packet.
- Repeated repair failure escalates to `BLOCKED`.
- Publish, merge, deploy and tag remain human-gated.

## Stored Evidence

Each transition should record:

- timestamp;
- actor;
- source state;
- target state;
- event name;
- status;
- evidence file paths;
- warnings;
- blockers.
