# ASF Codex Invocation Dry Run Template

## Summary

- project-name:
- repo-path:
- step:
- branch:
- sandbox:
- approval state:
- status: DRY RUN ONLY / DO NOT RUN

## Comando preview

```powershell
Get-Content -Raw "<codex_handoff.md>" | codex exec --sandbox read-only -
```

Nota: la sintassi e' preview da verificare manualmente nel prossimo step. Non eseguire senza approval di Alberto.

## Approval state

- GO:
- WARNING:
- HOLD:
- NO-GO:

## Stop conditions

- Human Approval Gate HOLD o NO-GO.
- Repo target dirty non ammessa.
- Branch non coerente.
- Task packet non Strict PASS.
- Scope troppo ampio.
- File sensibili, secret o `.env` coinvolti.
- Comando Codex non verificato.

## Manual instructions

- [ ] Review del dry-run Markdown.
- [ ] Review del `.ps1` preview.
- [ ] Conferma esplicita Alberto prima di qualunque esecuzione futura.
- [ ] Nessun commit, push, PR o merge automatico.
- [ ] Nessuna modifica al repository target in questo step.
