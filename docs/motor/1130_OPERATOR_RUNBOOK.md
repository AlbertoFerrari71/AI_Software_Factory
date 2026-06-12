# 1130 - Operator Runbook

## Preconditions

- Work on a dedicated step branch.
- Keep one writing agent at a time.
- Do not commit, push, open PRs, merge, tag or deploy from Codex.
- Keep Bridge as operational storage; Git and versioned files are authoritative.

## Main commands

```powershell
python scripts/asf_latest_report_resolver.py --bridge "D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\codex_command" --latest --json
python scripts/asf_operator_status.py --json
python scripts/asf_publish_readiness_gate.py --expected-step 1050 --json
python scripts/asf_reviewer_packet_builder.py --expected-step 1050 --output examples/reviewer_packets/1110-GPT_Reviewer_Packet.md
python scripts/asf_codex_next_prompt_builder.py --step 1140 --title "Prompt Injection Samples" --objective "Add adversarial samples." --output tmp/1140-DRAFT-Prompt_Codex.md
python scripts/asf_risk_classifier_eval.py
```

## Reading publish readiness

- GREEN: evidence is locally coherent for Alberto review; publish is still not
  automatic.
- YELLOW: evidence is degraded or incomplete; review manually before any
  publication packet.
- RED: stop publication path and fix evidence or report.

## Handoff to a new chat

Use this compact prompt:

```text
Ripartiamo da ASF motor/1050-1130. Leggi AGENTS.md, docs/motor/1130_OPERATOR_RUNBOOK.md, docs/motor/1130_ASF_V1_SUPERVISED_OPERATOR_RC.md, il report Bridge 1050-1130-Report_Codex.md/json e poi proponi solo il prossimo step sicuro. Non pubblicare nulla senza approval Alberto.
```

If Bridge is unavailable, paste:

- the Markdown report;
- the JSON sidecar;
- `git --no-pager status --short`;
- `git --no-pager diff --stat`;
- final verification outputs.

`Codex fatto` / `cf` means the local Codex execution report is ready for
review. It does not mean publish, PR or merge are authorized.
