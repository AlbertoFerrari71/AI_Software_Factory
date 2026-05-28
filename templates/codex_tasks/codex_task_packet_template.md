# Codex Task Packet Template

## Task ID

ASF-XXX

## Titolo

Titolo breve e preciso.

## Obiettivo

Cosa deve ottenere il task.

## Contesto

Perche' serve questo task.
Stato attuale del progetto.
Decisioni gia' prese.

## Project context

- Repository:
- Branch principale:
- Metodo operativo:

## Completed steps

- 010 ...
- 020 ...

## Current branch and target branch

- Branch corrente atteso:
- Branch di lavoro:
- Se il branch corrente non corrisponde, fermarsi e segnalarlo.

## Branch consigliato

xxx-nome-breve-task

## Livello rischio L0-L4

Livello massimo ammesso: L0 / L1 / L2 / L3 / L4.

Safety level: indicare il livello massimo approvato e il motivo.

Motivazione della classificazione:

- ...

## Modalita' Codex consigliata

A) Ask only
B) Suggest
C) Auto Edit
D) Full Auto sandboxed

Default: B

## File da leggere prima

- `README.md`
- `AGENTS.md`
- `docs/10_ROADMAP.md`
- `docs/05_SECURITY_MODEL.md`
- altri file specifici

## File modificabili

- ...

## Allowed scope

- Aree e file ammessi:
- Tipo di modifica ammesso:
- Se serve uscire dallo scope, fermarsi e segnalarlo.

## File vietati

File da non toccare:

- `.env`
- `.env.*`
- secret o credenziali
- file fuori repository
- ...

## Forbidden scope

- `src/**` salvo richiesta esplicita.
- `.github/workflows/**` salvo approval L3.
- `policies/**` salvo richiesta esplicita e motivata.
- `.githooks/**` salvo task dedicato.
- `scripts/**` salvo task dedicato.
- dipendenze e lockfile salvo approval esplicita.
- secret, `.env`, credenziali o configurazioni sensibili.

## Vincoli obbligatori

- Non fare commit automatico.
- Non fare push automatico.
- Non fare merge.
- Regola sintetica: no commit, no push, no merge.
- Non modificare file fuori lista.
- Non introdurre nuove dipendenze senza motivazione.
- Aggiornare documentazione se cambia comportamento.
- Fermarsi se il task richiede un livello superiore a quello approvato.

## Forbidden actions

- Non fare commit.
- Non fare push.
- Non aprire PR.
- Non fare merge.
- Non modificare direttamente GitHub.
- Non applicare branch protection/rulesets.
- Non installare hook Git.
- Non modificare git config core.hooksPath.
- Non usare bypass ASF_ALLOW_MAIN_BYPASS.
- Non modificare secret, `.env` o configurazioni sensibili.
- Non modificare `src/**` se non esplicitamente richiesto.
- Non introdurre nuove dipendenze se non esplicitamente autorizzato.

## Step richiesti

010. ...
020. ...
030. ...

## Required changes

- ...

## Documentation Sync

Valutare esplicitamente:

- `CHANGELOG.md`;
- `docs/10_ROADMAP.md`;
- `docs/11_DECISIONS.md`;
- documenti specifici dello step.

Non aggiornare documenti per zelo. Se non servono modifiche, dichiararlo nel report finale.

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

## Soft Protection awareness

- `main` e' trattato come protetto.
- GitHub hard protection puo' non essere disponibile sul piano attuale.
- I soft guardrails locali sono opt-in.
- Codex non deve installare hook Git.
- Codex non deve eseguire `git config core.hooksPath`.
- Codex non deve usare `ASF_ALLOW_MAIN_BYPASS`.

## Output atteso

Usare il report finale standard:

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

## Criteri di accettazione

- ...
- ...

## Test / verifica

```powershell
python -m pytest -q
```

## Rischi

- ...

## Rollback / safe stop

Come tornare indietro.

Safe stop se:

- compaiono file fuori scope;
- compaiono secret;
- falliscono test critici;
- serve L3/L4 non approvato;
- il rollback non e' chiaro.

## Cosa fare in caso di errore

Fermarsi, spiegare errore, proporre fix.
Non tentare workaround rischiosi.

## Cosa NON fare

- Non toccare branch principale.
- Non cancellare file.
- Non cambiare architettura fuori scope.
- Non modificare credenziali, secret o configurazioni sensibili.
- Non modificare CI/CD, dipendenze, auth, database o security policy senza approval L3.

## Riferimento hardening

Seguire `docs/25_PROMPT_PACKET_HARDENING.md` per sezioni minime, forbidden actions, allowed scope, forbidden scope, Verification Gate, Documentation Sync, Soft Protection awareness e report finale.
