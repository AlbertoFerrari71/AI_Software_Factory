# STEP XXX - Valid Minimal Task Packet

## Project context

Repository: AI Software Factory.

Metodo operativo: ChatGPT prepara il task packet, Codex lavora localmente su branch dedicato, Alberto verifica diff, test e stato Git prima di commit, push, PR e merge.

## Completed steps

- 010) Visione e contesto.
- 020) Repository Genesis.
- 030) Safety Model.

## BRANCH DA USARE

Usare un branch dedicato:

```text
step-xxx-valid-minimal-task
```

Se il branch corrente non corrisponde, fermarsi e segnalarlo.

## Objective

Aggiornare un documento dimostrativo senza introdurre logica applicativa reale.

## ALLOWED SCOPE

- `docs/**`
- `tests/**`

Se serve uscire dallo scope, fermarsi e segnalarlo.

## FORBIDDEN SCOPE

- `src/**`
- `policies/**`
- `.github/workflows/**`
- `.githooks/**`
- secret, `.env` o configurazioni sensibili.

## FORBIDDEN ACTIONS

- Non fare commit.
- Non fare push.
- Non aprire PR.
- Non fare merge.
- Non modificare direttamente GitHub.
- Non installare hook Git.
- Non modificare git config core.hooksPath.
- Non usare bypass ASF_ALLOW_MAIN_BYPASS.

## Required changes

- Aggiornare solo i documenti esplicitamente richiesti.
- Aggiungere test documentali leggeri se il formato cambia.
- Non fare refactor non richiesti.

## Verification Gate

Eseguire o motivare se non eseguiti:

```powershell
python -m pytest
git diff --check
git status --short
```

## Documentation Sync

Valutare:

- `CHANGELOG.md`;
- `docs/10_ROADMAP.md`;
- `docs/11_DECISIONS.md`;
- documenti specifici coinvolti.

Non aggiornare documenti per zelo.

## Soft Protection awareness

- `main` e' trattato come protetto.
- I Soft Protection Guardrails sono opt-in.
- Codex non deve installare hook Git.
- Codex non deve usare `ASF_ALLOW_MAIN_BYPASS`.

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
