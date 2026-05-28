# STEP XXX - Valid Strict Task Packet

## Project context

Repository: AI Software Factory.

Branch principale: `main`.

Metodo operativo: ChatGPT prepara il task packet, Codex lavora localmente su branch dedicato, Alberto verifica diff, test e stato Git prima di commit, push, PR e merge.

## Completed steps

- 010) Visione e contesto.
- 020) Repository Genesis.
- 030) Safety Model.
- 140) Prompt Packet Validation Lite.
- 150) Prompt Packet Examples and Golden Samples.

## BRANCH DA USARE

Creare o usare un branch dedicato:

```text
step-xxx-valid-strict-task
```

Prima di procedere verificare che `main` sia aggiornato e che il working tree sia pulito. Se il branch corrente non corrisponde, fermarsi e segnalarlo.

## Objective

Aggiornare documentazione e test dimostrativi senza introdurre logica applicativa reale.

## ALLOWED SCOPE

- `docs/**`
- `tests/**`
- `examples/task_packets/**`

Se serve uscire dallo scope, fermarsi e segnalarlo.

## FORBIDDEN SCOPE

- `src/**`
- `policies/**`
- `.github/workflows/ci.yml`
- CI fuori scope salvo approval esplicita;
- secret, `.env` o configurazioni sensibili;
- file fuori repository.

## FORBIDDEN ACTIONS

- Non fare commit.
- Non fare push.
- Non aprire PR.
- Non fare merge.
- Non modificare direttamente GitHub.
- Non applicare configurazioni GitHub reali.
- Non installare hook Git.
- Non modificare git config core.hooksPath.
- Non usare bypass ASF_ALLOW_MAIN_BYPASS.
- Non modificare secret, `.env` o configurazioni sensibili.

## Required changes

- Aggiornare solo i documenti esplicitamente richiesti.
- Aggiungere test leggeri se il comportamento del validatore cambia.
- Mantenere Lite mode compatibile.
- Non introdurre schema JSON/YAML in questo step.

## Verification Gate

Eseguire o motivare se non eseguiti:

```powershell
python -m pytest
git diff --check
git status --short
```

Se applicabile:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify.ps1
```

## Documentation Sync

Valutare esplicitamente:

- `CHANGELOG.md`;
- `docs/10_ROADMAP.md`;
- Roadmap;
- `docs/11_DECISIONS.md`;
- Decisions;
- documenti specifici coinvolti.

Non aggiornare documenti per zelo.

## Soft Protection awareness

- `main` e' trattato come protetto.
- I Soft Protection Guardrails sono opt-in.
- Gli hook locali vivono in `.githooks`.
- `core.hooksPath` non deve essere modificato da Codex.
- Codex non deve installare hook Git.
- Codex non deve usare `ASF_ALLOW_MAIN_BYPASS`.

## Golden samples

Usare i golden samples come riferimento:

- valid sample: `examples/task_packets/valid/step_valid_strict_task_packet.md`;
- invalid samples: `examples/task_packets/invalid/`.

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
