# 1120 - Real Dogfood Loop Evidence

## Purpose

Demonstrate ASF on ASF with a local non-publishing evidence pack.

## Scenario

1. ChatGPT proposes a small supervised step.
2. Codex executes locally and writes a Markdown report plus JSON sidecar.
3. Latest report resolver reads the Bridge/report fixture.
4. Operator Status summarizes branch, report and next action.
5. GPT Reviewer Packet is generated.
6. Publish Readiness Gate returns a semaphore.
7. Handoff for a new chat is available through the RC runbook.

## Evidence fixtures

- `examples/operator/1120_sample_codex_report.json`;
- `examples/operator/1120_sample_codex_report.md`;
- `examples/operator/1050-1130-Report_Codex.json`;
- `examples/operator/1050-1130-Report_Codex.md`;
- `examples/operator/1120_sample_operator_status.json`;
- `examples/operator/1120_sample_publish_readiness.json`;
- `examples/operator/1120_sample_reviewer_packet.md`;
- `examples/reviewer_packets/1110-GPT_Reviewer_Packet.md`;
- `examples/codex_reports/1080_sample_codex_report.json`;
- `examples/codex_reports/1080_sample_codex_report.md`.

All fixtures are deterministic, local and non-sensitive. They contain no raw
provider payload and require no live call or publication.

## Acceptance

- The evidence pack demonstrates the loop end to end.
- Tests use deterministic fixtures.
- No publish, PR, merge, tag or deploy is required.
