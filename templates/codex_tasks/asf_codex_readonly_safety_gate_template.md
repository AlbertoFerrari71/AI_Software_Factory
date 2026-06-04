# ASF Codex Read-Only Safety Gate Template

## Summary

- project-name:
- repo-path:
- step:
- result-capture:
- decisione: GO_TO_WORKSPACE_WRITE_DESIGN / WARNING_REVIEW_REQUIRED / HOLD / NO_GO

## Evidenze

- result capture:
- target branch:
- target working tree:
- exit code:
- stdout/stderr:

## Rischi

- forbidden actions:
- file modifications:
- output incomplete:
- ambiguous plan:

## Decision criteria

- GO_TO_WORKSPACE_WRITE_DESIGN: capture PASS, working tree CLEAN, no forbidden action, no bypass, no secret or `.env`.
- WARNING_REVIEW_REQUIRED: incomplete or ambiguous nonblocking evidence.
- HOLD: missing or insufficient capture.
- NO_GO: fail signal, dirty working tree, forbidden action, bypass, secret or `.env`.

## Note

This gate does not authorize broader execution directly. It only supports a future separate design step with explicit human approval.
