# 1110 - ASF Operator Status CLI and Publish Readiness Gate

## Purpose

Provide a local supervised operator that says where ASF is, what happened, what
is missing and what is safe to do next.

## Scripts

- `scripts/asf_step_registry.py`;
- `scripts/asf_latest_report_resolver.py`;
- `scripts/asf_operator_status.py`;
- `scripts/asf_publish_readiness_gate.py`;
- `scripts/asf_reviewer_packet_builder.py`;
- `scripts/asf_codex_next_prompt_builder.py`.

## Commands

```powershell
python scripts/asf_operator_status.py --step latest
python scripts/asf_operator_status.py --expected-step 1050 --json
python scripts/asf_publish_readiness_gate.py --expected-step 1050 --json
python scripts/asf_reviewer_packet_builder.py --expected-step 1050
python scripts/asf_codex_next_prompt_builder.py --step 1140 --title "Prompt Injection Samples" --objective "Add adversarial samples."
```

## Publish readiness

Semaphores:

- GREEN: report PASS, checks declared, no raw payload marker, human gate still
  required;
- YELLOW: degraded or warning state, manual review required before publication;
- RED: missing, ambiguous, incoherent or failing report/evidence.

The gate never publishes. It sets `publish_command_allowed=false` and keeps
publication behind Alberto plus `scripts/asf_publish_step.ps1`.

## Acceptance

- Operator status has text and JSON output.
- Reviewer packet and draft prompt are generable.
- Publish readiness is evaluated without executing publish commands.
