# 1200 - Human Escalation Policy

## Purpose

The Human Escalation Manager stops automation when evidence, risk or policy
requires Alberto's decision.

## Mandatory Stop Conditions

Stop for human decision on:

- high risk;
- destructive action;
- secrets or credentials;
- data privacy risk;
- merge, release, public deploy or tag;
- legal, license or privacy concern;
- provider cost anomaly;
- context too large;
- repeated repair failure;
- file outside scope;
- incoherent gates;
- AI reviewer fail without a safe repair;
- unclear ownership of Bridge artifacts;
- target repository dirty after a read-only run.

## Risk Levels

| Risk | Escalation default |
|---|---|
| L0 | May continue with light review if deterministic gates pass. |
| L1 | Human awareness required for workflow changes. |
| L2 | Deterministic gates and independent review required. |
| L3 | Human gate required before execution or publish. |
| L4 | Stop by default; double confirmation and dry-run required. |

## Human Decision States

Recommended decision states:

- `APPROVED_FOR_CONTEXT`;
- `APPROVED_FOR_CODEX`;
- `APPROVED_FOR_REPAIR`;
- `APPROVED_FOR_PUBLISH`;
- `REJECTED`;
- `NEEDS_CLARIFICATION`;
- `ABORTED`.

## What Human Approval Does Not Do

Human approval does not replace:

- deterministic gates;
- repo cleanliness checks;
- scope checks;
- secret checks;
- publish runner flags;
- final verification.

## Evidence Required For Escalation

The escalation packet should include:

- current state;
- blocking reason;
- latest State Card;
- relevant Context Pack summary;
- failing gate evidence;
- proposed next safe choices;
- explicit forbidden actions.
