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

- Branch corrente target:
- Working tree:
- Ultimi commit:

## Pre-Codex checks consigliati

```powershell
git branch --show-current
git status --short
git --no-pager log --oneline --max-count=10
```

## Post-Codex local checks consigliati

```powershell
git status --short
git --no-pager diff --stat
git --no-pager diff --check
python -m pytest
```

## ASF checks lato AI_Software_Factory

- task packet Lite validation;
- task packet Strict validation;
- runner report review.

## Human gates

- Review diff.
- Verificare scope.
- Verificare vincoli.
- Usare Quick Reference / Cookbook solo per la fase Git presidiata manuale.

## Riferimenti

- `docs/36_WORKFLOW_QUICK_REFERENCE.md`
- `docs/37_STEP_CLOSURE_REPORT.md`
- `docs/38_WORKFLOW_COMMAND_COOKBOOK.md`

## Nota

Il Verification Pack non sostituisce test, review umana, PR checks o Step Closure Report.
