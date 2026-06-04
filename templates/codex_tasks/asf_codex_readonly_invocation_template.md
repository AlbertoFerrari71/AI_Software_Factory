# ASF Codex Read-Only Invocation Template

## Summary

- project-name:
- repo-path:
- step:
- branch:
- handoff-path:
- approval-gate:
- mode: preview / execute-readonly

## Preview command

```powershell
python scripts/asf_codex_readonly_invoke.py --mode preview --project-name <project> --repo-path "<repo>" --step <step> --branch <branch> --handoff-path <handoff> --approval-gate <approval>
```

## Execute-readonly command

```powershell
python scripts/asf_codex_readonly_invoke.py --mode execute-readonly --project-name <project> --repo-path "<repo>" --step <step> --branch <branch> --handoff-path <handoff> --approval-gate <approval> --confirm-readonly-execution YES_I_APPROVE_READONLY_CODEX_EXECUTION
```

## Required gates

- [ ] Human Approval Gate is `GO`.
- [ ] Target working tree is `CLEAN`.
- [ ] Confirmation token is explicit.
- [ ] Sandbox is read-only.
- [ ] Output stays under ignored `tmp/`.

## Stop conditions

- Approval is WARNING, HOLD, NO-GO, missing or ambiguous.
- Target working tree is DIRTY.
- Codex command is not available during execute-readonly.
- Any request for commit, push, PR, merge, GitHub changes, CI changes, dependencies, hooks, secrets or `.env`.

## Notes

Default mode is preview. Codex is not executed in preview.
