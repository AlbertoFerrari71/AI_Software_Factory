# 0940 - Supervised Loop Step Plan Template

Use this template to describe one supervised automatic step before any execution lane is selected.

```yaml
step_id: "NNNN"
title: "<step title>"
objective: "<single concrete objective>"
risk_level: "L0|L1|L2|L3|L4"

allowed_lanes:
  - deterministic
  - reasoning
  - code_editing

forbidden_actions:
  - commit
  - push
  - open_pr
  - merge
  - deploy
  - destructive_reset
  - destructive_clean
  - rebase
  - destructive_checkout
  - mass_line_ending_change
  - os_appunti_write
  - live_api_call

expected_files:
  - "docs/example.md"

expected_commands:
  - command: "python scripts/check_workflow_health.py"
    lane: deterministic
    required: true

verification_commands:
  - "python -m pytest"
  - "python scripts/check_workflow_health.py"
  - "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\\verify.ps1"
  - "git --no-pager diff --check"
  - "git --no-pager status --short"

approval_required:
  publish: false
  merge: false
  deploy: false
  milestone: false

retry_policy:
  name: "GPT-discretionary bounded retry policy"
  max_retry_absolute: 10
  default_retry_budget: 0
  retry_requires_reason: true

bridge_outputs:
  state_json: "supervised_loop/state.json"
  report_markdown: "codex_command/NNNN-Report_Codex.md"
  stdout_log: "supervised_loop/NNNN-stdout.txt"
  stderr_log: "supervised_loop/NNNN-stderr.txt"

success_criteria:
  - "expected files created or updated"
  - "mandatory verification commands pass"
  - "no out-of-scope diff"
  - "report written"

stop_conditions:
  - "risk L3 or higher without Alberto approval"
  - "destructive command proposed"
  - "credential or human input required"
  - "same failure repeats without new diagnosis"
  - "diff outside expected_files"
  - "publish, merge or deploy required"
```

## Report section

The final report should include:

- Step eseguito
- Stato
- File creati
- File modificati
- Verifiche eseguite
- Warning / criticita' residue
- Cose non fatte
- Prossimo step consigliato
- Riepilogo finale

