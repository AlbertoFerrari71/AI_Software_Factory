# 1200 - Gate and Repair Loop

## Purpose

The Gate and Repair Loop keeps automation bounded. It allows local fixes only
when deterministic evidence shows a narrow, safe repair path.

## Gate Order

1. Deterministic local gates.
2. AI reviewer gate.
3. Human escalation when required.
4. Publish gate only after approval.

AI review cannot override deterministic failures. A local gate failure must be
fixed or escalated.

## Deterministic Gates

Deterministic gates include:

- schema validation;
- unit tests;
- full pytest when required;
- workflow health check;
- verify gate;
- diff check;
- git status;
- secret scanning where configured.

## AI Reviewer Gates

The AI reviewer checks:

- scope coherence;
- diff intent;
- report consistency;
- risk mismatch;
- missing tests;
- unsafe next actions.

The reviewer can return `PASS`, `PASS_WITH_WARNINGS`, `FAIL` or `BLOCKED`.

## Repair Rules

- Maximum repair attempts must be explicit.
- The repair packet must be smaller than the original Task Packet.
- The repair packet must name its parent step or task packet.
- Repair scope must be narrower than original scope.
- Repeated failure escalates to human review.
- Repair cannot authorize commit, push, PR, merge, deploy, tag or live calls
  unless a future human-approved publish step explicitly allows it.

## No False PASS Policy

ASF must never mark a gate as passing when:

- a command was not run;
- a command failed;
- evidence is missing;
- AI review found a blocker;
- deterministic gates failed;
- the working tree is dirty outside scope;
- safety policy is violated.

Skipped gates must be recorded as skipped with reason, not as pass.

## Escalation

Escalate to `BLOCKED` when:

- repair exceeds max attempts;
- the repair would be as large as the original step;
- scope grows instead of shrinking;
- deterministic failures are unclear;
- review fails without safe repair;
- human approval is needed for the next action.
