# 1100 - Independent Review and Disagreement Protocol

## Purpose

Make the independent reviewer node operational without automatic live model
calls.

## Reviewer independence

For FULL or ESCALATED steps, planner and reviewer must not be the same context.
The reviewer can be:

- a different model;
- a fresh GPT context with only the evidence pack;
- a separate human-assisted review context.

It must not be the same planning chat that produced the step.

## Required review record

Each review records:

- reviewer_actor;
- reviewer_context_type;
- evidence_pack_path;
- verdict;
- rationale;
- disagreement_status.

## Disagreement protocol

- L0-L2 disagreement: the more conservative verdict wins with rationale.
- L3+ disagreement: ASK_ALBERTO is mandatory.
- publish/merge/deploy/scope disagreement: ASK_ALBERTO is mandatory.

## Templates

- `docs/templates/independent_review_packet.md`;
- `docs/templates/disagreement_comparison.md`.

## Pilot example

For a FULL step, the operator builds a reviewer packet from report JSON,
Markdown, tests, diff and readiness. The independent reviewer returns
PASS/FIX/STOP/ASK_ALBERTO. If the reviewer disagrees on publication readiness,
the final state is ASK_ALBERTO.

## Acceptance

- The protocol is documented.
- Templates are present.
- No automatic live calls are introduced.
