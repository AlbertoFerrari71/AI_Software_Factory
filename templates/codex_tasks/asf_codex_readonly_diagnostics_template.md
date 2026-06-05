# ASF Codex Read-Only Diagnostics Template

## Scope

Normalize JSON evidence from read-only invocation, result capture, CLI probe or repeatable trial reports.

## Inputs

- diagnostics source JSON files:
  - `<path-to-json-report>`

## Command

```powershell
python scripts/asf_codex_readonly_diagnostics.py --reports <path-to-json-report> --output-json tmp/asf_codex_readonly_diagnostics/readonly_diagnostics.json --output-markdown tmp/asf_codex_readonly_diagnostics/readonly_diagnostics.md
```

## Required Review

- Confirm missing reports are classified as `REPORT_MISSING`.
- Confirm malformed reports are classified as `REPORT_MALFORMED`.
- Confirm stderr evidence is classified as `STDERR_NONEMPTY`, not automatically as target failure.
- Confirm dirty target evidence is classified as `TARGET_DIRTY_AFTER_READONLY`.

## Safety Limits

- Do not invoke Codex.
- Do not modify target repositories.
- Do not authorize workspace-write.

