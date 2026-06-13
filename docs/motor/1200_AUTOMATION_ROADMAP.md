# 1200 - Automation Roadmap 1300-2990

## Purpose

This roadmap turns the 1200 architecture into implementable future milestones.
Each milestone must remain local-first, testable, human-gated and fail-closed.

## Roadmap

| Range | Title | Goal |
|---|---|---|
| 1300-1390 | Task Packet Schema and Roadmap Compiler | Implement the first roadmap-to-task-packet compiler and strengthen schema validation. |
| 1400-1490 | Context Pack Builder and State Card Compaction | Build compact context and state artifacts with size policy and auto-split. |
| 1500-1590 | Codex Execution Adapter Lab | Prototype safe Codex invocation in dry-run and lab-only modes. |
| 1600-1690 | Gate Runner Unification and Evidence Store | Unify local gate execution and durable evidence capture. |
| 1700-1790 | AI Reviewer and Repair Loop | Implement independent review contracts and bounded repair packets. |
| 1800-1890 | Publish Controller and GitHub Integration | Connect reviewed output to branch and PR workflow with explicit approvals. |
| 1900-1990 | Human Escalation and Risk Policy | Harden escalation rules, risk policy and blocked-state handling. |
| 2000-2190 | End-to-End Automated Mega-Step Pilot | Run a full supervised milestone pilot without unattended publish. |
| 2200-2390 | FPO Automated Milestone Pilot | Apply the runner to Family Photo Organizer with safety constraints. |
| 2400-2590 | ASF Automation Dashboard | Provide read-only dashboard/report UI over state and evidence. |
| 2600-2790 | Recovery, Replay and Audit | Add replay, recovery, audit trail and failed-run diagnostics. |
| 2800-2990 | Autonomous Milestone Runner RC | Release candidate for bounded supervised autonomous milestone runs. |

## Guardrails For All Future Ranges

- No live provider call without explicit step approval.
- No Codex write invocation without approved sandbox and clean target.
- No commit, push, PR, merge, tag or deploy without explicit human gate.
- No deterministic gate bypass.
- No repair packet larger than the original task.
- No context pack that silently drops stop conditions.
- No Bridge artifact as the only source of truth.

## Next Step

1300-1390) Task Packet Schema and Roadmap Compiler
