# ASF Runner Verification Pack Template

## Progetto target

- Progetto:
- Repo path:
- Profilo runner:

## Step

- Step:
- Titolo:
- Branch previsto:

## Stato Git target letto dal runner

- Project-name:
- Repo-path:
- Branch corrente target:
- Working tree:
- Ultimi commit:

## Pre-Codex checks consigliati

```powershell
git branch --show-current
git status --short
git --no-pager log --oneline --max-count=10
```

- Verificare prerequisito step precedente.
- Leggere handoff.
- Confermare Human gate.

## Post-Codex local checks consigliati

```powershell
git status --short
git --no-pager diff --stat
git --no-pager diff --check
python -m pytest
```

- Eventuale health command del profilo.
- Verifica file temporanei.

## Scope checks

- File creati/modificati.
- Nessun file fuori scope.
- Nessuna modifica a secret/.env.
- Nessuna modifica CI non autorizzata.
- Nessuna operazione vietata.

## Codex report checks

- STEP ESEGUITO.
- STATO.
- BRANCH CORRENTE.
- FILE CREATI.
- FILE MODIFICATI.
- COMANDI ESEGUITI.
- VERIFICHE NON ESEGUITE.
- RISCHI / NOTE.
- CONFERME VINCOLI.
- PROSSIMO STEP.
- RIEPILOGO FINALE.

## ASF checks lato AI_Software_Factory

- task packet Lite validation;
- task packet Strict validation;
- runner report review.

## Human gates

- Review diff.
- Verificare scope.
- Verificare vincoli.
- Approvazione commit.
- Approvazione push.
- Approvazione PR.
- Approvazione merge.
- Usare Quick Reference / Workflow Command Cookbook solo per la fase Git presidiata manuale.

## PR checks handling

```powershell
gh pr checks --watch
```

`no checks reported` e' un'attenzione da registrare, non un fallimento automatico.

## LF/CRLF handling

Warning LF/CRLF non bloccanti se `git diff --check`, test e Verification Gate passano.

## Riferimenti

- Quick Reference: `docs/36_WORKFLOW_QUICK_REFERENCE.md`
- Step Closure Report: `docs/37_STEP_CLOSURE_REPORT.md`
- Workflow Command Cookbook: `docs/38_WORKFLOW_COMMAND_COOKBOOK.md`

## Nota

Il Verification Pack non sostituisce test, review umana, PR checks o Step Closure Report.
