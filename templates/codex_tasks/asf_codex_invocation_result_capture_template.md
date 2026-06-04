# ASF Codex Invocation Result Capture Template

## Summary

- project-name:
- repo-path:
- step:
- invocation-dir:
- classification: PASS / WARNING / FAIL

## Outputs

- stdout.txt:
- stderr.txt:
- exit_code.txt:
- codex_readonly_invocation_result.md:
- preview artifacts:

## stdout summary

```text

```

## stderr summary

```text

```

## Target Git status

- branch:
- working tree:

## Classification criteria

- PASS: exit code 0, required outputs present, working tree CLEAN.
- WARNING: output incomplete or preview-only evidence.
- FAIL: exit code nonzero or working tree DIRTY after read-only.

## Next actions

- Review capture.
- Run read-only safety gate.
- Do not treat capture as approval.
