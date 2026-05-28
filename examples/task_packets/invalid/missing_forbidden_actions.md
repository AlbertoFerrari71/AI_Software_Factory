# STEP XXX - Missing Action Block

## Project context

Repository: AI Software Factory.

## Completed steps

- 010) Visione e contesto.
- 020) Repository Genesis.

## BRANCH DA USARE

Usare branch dedicato `step-xxx-missing-forbidden-actions`.

## Objective

Aggiornare un documento dimostrativo.

## ALLOWED SCOPE

- `docs/**`
- `tests/**`

## FORBIDDEN SCOPE

- `src/**`
- `policies/**`
- secret e `.env`.

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

## Final Codex report

```text
A) STEP ESEGUITO
B) STATO
C) FILE CREATI
D) FILE MODIFICATI
E) VERIFICHE ESEGUITE
F) VERIFICHE NON ESEGUITE
G) RISCHI / NOTE
H) PROSSIMO STEP CONSIGLIATO
I) RIEPILOGO FINALE OBBLIGATORIO
```

La sezione I deve includere:

- Step eseguito: ...
- Tempo impiegato: ...
- Stato step: ...
- Prossimo step: ...
