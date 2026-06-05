# 63 - ASF Codex Read-Only Decision Gate

## 1. Scope

This document defines the conservative decision gate for ASF Codex read-only invocation evidence.

The decision gate consumes:

- diagnostics JSON files from `scripts/asf_codex_readonly_diagnostics.py`;
- CLI compatibility probe JSON from `scripts/asf_codex_cli_compatibility_probe.py`;
- optional repeatable trial comparison JSON.

It writes a stable JSON decision report and optional Markdown summary.

## 2. Script

```text
scripts/asf_codex_readonly_decision_gate.py
```

Example:

```powershell
python scripts/asf_codex_readonly_decision_gate.py --diagnostics tmp/asf_codex_readonly_diagnostics/readonly_diagnostics.json --cli-probe tmp/asf_codex_cli_compatibility_probe/cli_compatibility_probe.json --trial-comparison tmp/asf_codex_readonly_repeatable_trials/comparison/trial_comparison.json --output-json tmp/asf_codex_readonly_decision_gate/readonly_decision_gate.json --output-markdown tmp/asf_codex_readonly_decision_gate/readonly_decision_gate.md
```

## 3. Allowed decisions

The only allowed decisions are:

- `GO_TO_WORKSPACE_WRITE_DESIGN`
- `GO_TO_MORE_READONLY_TRIALS`
- `WARNING_REVIEW_REQUIRED`
- `HOLD`
- `NO_GO`

`GO_TO_WORKSPACE_WRITE_DESIGN` does not authorize workspace-write. It only means a future design step may be prepared separately.

## 4. Conservative rules

The gate returns `NO_GO` when:

- any evidence shows `TARGET_DIRTY_AFTER_READONLY`;
- any command or sandbox evidence shows forbidden sandbox mode.

The gate returns `HOLD` when:

- core JSON inputs are missing;
- core JSON inputs are malformed;
- diagnostics contain `REPORT_MISSING` or `REPORT_MALFORMED`.

The gate returns `WARNING_REVIEW_REQUIRED` when:

- stderr is non-empty;
- output is incomplete;
- exit code is nonzero;
- target remains clean and no stronger `NO_GO` condition exists.

The gate returns `GO_TO_MORE_READONLY_TRIALS` when:

- Codex is unavailable;
- CLI compatibility is not clear;
- read-only execution evidence is insufficient;
- repeatable clean trial evidence is missing.

The gate returns `GO_TO_WORKSPACE_WRITE_DESIGN` only when:

- diagnostics are complete;
- CLI compatibility is clear for `exec`, `--sandbox` and `read-only`;
- read-only execution completed;
- target remained clean;
- repeated read-only trial evidence is clean;
- no blocking warning exists.

## 5. Safety limits

- The decision gate does not invoke Codex.
- The decision gate does not modify any target repository.
- The decision gate does not execute commit, push, pull request, merge, tag or deploy.
- The decision gate does not authorize broader execution.

