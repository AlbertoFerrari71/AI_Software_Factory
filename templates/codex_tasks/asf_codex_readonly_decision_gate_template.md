# ASF Codex Read-Only Decision Gate Template

## Scope

Combine diagnostics JSON, CLI compatibility JSON and optional repeatable trial comparison JSON into one conservative read-only decision.

## Command

```powershell
python scripts/asf_codex_readonly_decision_gate.py --diagnostics tmp/asf_codex_readonly_diagnostics/readonly_diagnostics.json --cli-probe tmp/asf_codex_cli_compatibility_probe/cli_compatibility_probe.json --trial-comparison tmp/asf_codex_readonly_repeatable_trials/comparison/trial_comparison.json --output-json tmp/asf_codex_readonly_decision_gate/readonly_decision_gate.json --output-markdown tmp/asf_codex_readonly_decision_gate/readonly_decision_gate.md
```

## Allowed Decisions

- `GO_TO_WORKSPACE_WRITE_DESIGN`
- `GO_TO_MORE_READONLY_TRIALS`
- `WARNING_REVIEW_REQUIRED`
- `HOLD`
- `NO_GO`

## Required Review

- `TARGET_DIRTY_AFTER_READONLY` must produce `NO_GO`.
- Missing or malformed core reports must produce `HOLD`.
- `CODEX_NOT_AVAILABLE` must produce more read-only trials, not target failure.
- `GO_TO_WORKSPACE_WRITE_DESIGN` must be treated only as permission to prepare a future design step.

## Safety Limits

- Do not invoke Codex.
- Do not modify target repositories.
- Do not authorize workspace-write.
- Do not perform commit, push, pull request, merge, tag or deploy.

