# 61 - ASF Codex Read-Only Diagnostics Hardening

## 1. Scope

This document defines the diagnostics layer for ASF Codex read-only invocation evidence.

The goal is to normalize JSON evidence from read-only invocation, result capture, repeatable trial and CLI probe reports before any broader design discussion.

The diagnostics layer is conservative:

- missing evidence is explicit evidence;
- malformed evidence is explicit evidence;
- stderr is not automatically a target failure;
- a dirty target after a read-only run is a serious safety failure;
- `CODEX_NOT_AVAILABLE` is an environment diagnostic, not a target failure.

## 2. Script

```text
scripts/asf_codex_readonly_diagnostics.py
```

The script reads one or more JSON reports and writes a stable JSON diagnostics report.

Example:

```powershell
python scripts/asf_codex_readonly_diagnostics.py --reports tmp/run/capture.json tmp/run/repeatable_trial.json --output-json tmp/asf_codex_readonly_diagnostics/readonly_diagnostics.json --output-markdown tmp/asf_codex_readonly_diagnostics/readonly_diagnostics.md
```

## 3. Classifications

The diagnostics report can emit:

- `CODEX_NOT_AVAILABLE`
- `CODEX_AVAILABLE`
- `CLI_PROBE_AVAILABLE`
- `EXECUTION_COMPLETED`
- `EXECUTION_FAILED`
- `STDERR_NONEMPTY`
- `STDOUT_EMPTY`
- `OUTPUT_INCOMPLETE`
- `EXIT_CODE_NONZERO`
- `TARGET_CLEAN_AFTER_READONLY`
- `TARGET_DIRTY_AFTER_READONLY`
- `REPORT_MALFORMED`
- `REPORT_MISSING`
- `UNKNOWN_REVIEW_REQUIRED`

## 4. Interpretation

`STDERR_NONEMPTY` means stderr requires review. It is not automatically a failed target run.

`OUTPUT_INCOMPLETE` means the run did not provide enough output evidence for a clean progression.

`TARGET_DIRTY_AFTER_READONLY` means the target changed after a read-only run. This must block progression.

`REPORT_MISSING` and `REPORT_MALFORMED` keep the evidence chain auditable. They should usually lead to a decision gate `HOLD`.

## 5. Output contract

The JSON output contains:

- `schema_version`;
- `report_type`;
- stable `classification_order`;
- overall `classifications`;
- input counts;
- per-report state, classifications, evidence and error.

The optional Markdown summary is for human review only. The decision gate should consume the JSON output.

## 6. Limits

- The diagnostics script does not invoke Codex.
- The diagnostics script does not inspect remote GitHub state.
- The diagnostics script does not modify any target repository.
- The diagnostics script does not authorize workspace-write.

