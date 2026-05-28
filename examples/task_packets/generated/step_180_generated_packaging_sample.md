# STEP 180 - Prompt Packet Generator Packaging

## Project context

Repository: AlbertoFerrari71/AI_Software_Factory.

Cartella locale: `C:\Users\alberto.ferrari\source\repos\AI_Software_Factory`.

Branch principale: `main`.

Metodo operativo: ChatGPT prepara il task packet, Codex lavora localmente su branch dedicato, Alberto verifica diff, test e stato Git prima di commit, push, PR e merge.

## Completed steps

- 010) Visione e contesto.
- 020) Repository Genesis.
- 030) Safety Model.
- 140) Prompt Packet Validation Lite.
- 150) Prompt Packet Examples and Golden Samples.
- 160) Prompt Packet Validation Strict Mode.

## BRANCH DA USARE

Creare o usare il branch dedicato:

```text
step-180-prompt-packet-generator-packaging
```

Prima di procedere verificare che `main` sia aggiornato e che il working tree sia pulito. Se il branch corrente non corrisponde, fermarsi e segnalarlo.

## Objective

Package the prompt packet generator for local-first usage.

## ALLOWED SCOPE

- `docs/**`
- `tests/**`
- `templates/**`
- `scripts/**`

Se serve uscire dallo scope, fermarsi e segnalarlo.

## FORBIDDEN SCOPE

- `src/**`
- `policies/**`
- `.github/workflows/ci.yml`
- CI fuori scope salvo approval esplicita;
- dipendenze e lockfile salvo approval esplicita;
- secret, `.env` o configurazioni sensibili;
- file fuori repository.

## FORBIDDEN ACTIONS

- Non fare commit.
- Non fare push.
- Non aprire PR.
- Non fare merge.
- Non modificare direttamente GitHub.
- Non applicare configurazioni GitHub reali.
- Non applicare branch protection/rulesets.
- Non installare hook Git.
- Non modificare git config core.hooksPath.
- Non usare bypass ASF_ALLOW_MAIN_BYPASS.
- Non modificare secret, `.env` o configurazioni sensibili.
- Non modificare `src/**`.
- Non modificare `policies/**`.
- Non modificare CI o dipendenze senza approval esplicita.

## File da ispezionare

- `README.md`
- `AGENTS.md`
- `docs/10_ROADMAP.md`
- `docs/05_SECURITY_MODEL.md`
- documenti specifici dello step.

## File modificabili

- Dichiarare qui i file ammessi per lo step.

## Requisiti funzionali

- Mantenere modifiche piccole, leggibili e verificabili.
- Rispettare il branch dedicato e lo scope approvato.
- Non introdurre schema JSON/YAML formale se non richiesto dallo step.

## Required changes

- Descrivere qui le modifiche richieste.
- Aggiungere o aggiornare test automatici se cambia comportamento.
- Aggiornare documentazione solo quando collegata allo step.

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

- valid sample: `examples/task_packets/valid/step_valid_minimal_task_packet.md`;
- valid strict sample: `examples/task_packets/valid/step_valid_strict_task_packet.md`;
- invalid samples: `examples/task_packets/invalid/`.

## Strict-ready note

Questo task packet puo' essere controllato anche con:

```powershell
python scripts/validate_task_packet.py --strict <task-packet.md>
```

## Output finale richiesto

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

- Step eseguito: 180) Prompt Packet Generator Packaging
- Tempo impiegato: ...
- Stato step: ...
- Prossimo step: ...

## Rollback / safe stop

Rollback minimo: ripristinare i file modificati o abbandonare il branch.

Safe stop se:

- compaiono file fuori scope;
- compaiono secret;
- falliscono test critici;
- serve L3/L4 non approvato;
- il rollback non e' chiaro.
