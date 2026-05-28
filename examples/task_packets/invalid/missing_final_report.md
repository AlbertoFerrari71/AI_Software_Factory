# STEP XXX - Missing Final Report

## Project context

Repository: AI Software Factory.

## Completed steps

- 010) Visione e contesto.
- 020) Repository Genesis.

## BRANCH DA USARE

Usare branch dedicato `step-xxx-missing-final-report`.

## Objective

Aggiornare un documento dimostrativo.

## ALLOWED SCOPE

- `docs/**`
- `tests/**`

## FORBIDDEN SCOPE

- `src/**`
- `policies/**`
- secret e `.env`.

## FORBIDDEN ACTIONS

- Non fare commit.
- Non fare push.
- Non aprire PR.
- Non fare merge.
- Non modificare direttamente GitHub.

## Required changes

- Aggiornare il documento indicato.
- Eseguire i test richiesti.

## Verification Gate

```powershell
python -m pytest
git diff --check
git status --short
```

## Documentation Sync

Valutare changelog, roadmap e decision log.

## Soft Protection awareness

`main` e' trattato come protetto e i Soft Protection Guardrails sono opt-in.
