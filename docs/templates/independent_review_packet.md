# Independent Review Packet

## Identity

- reviewer_actor:
- reviewer_context_type:
- evidence_pack_path:
- planned_step:
- source_report_path:

## Evidence

- task packet:
- Codex report Markdown:
- Codex report JSON:
- git diff/stat:
- checks:
- risk classifier/eval:
- publish readiness:

## Review Checklist

- Scope matches allowed files.
- Forbidden actions were not performed.
- Tests and gates are declared with evidence.
- No secrets or raw provider payload are present.
- Risk level is not downgraded.
- Publish/merge/deploy/scope decisions remain Alberto-gated.

## Verdict

Choose one:

- PASS
- FIX
- STOP
- ASK_ALBERTO

## Rationale

Record only evidence-backed findings.

## Disagreement

- disagreement_status: NONE | LOW_RISK_CONSERVATIVE_WINS | ASK_ALBERTO_REQUIRED
- compared_with:
- reason:
