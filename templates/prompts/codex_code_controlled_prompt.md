# Codex Controlled Code Prompt

Usa questo prompt quando Codex deve applicare modifiche controllate su branch dedicato.

## Obiettivo

Eseguire una modifica piccola, testabile e reversibile rispettando il Codex Task Packet approvato.

## Contesto

AI Software Factory consente Auto Edit solo come L2 su branch dedicato, con file consentiti, test e riepilogo. Full Auto non e' ammesso per questo flusso.

Ogni task deve rispettare `docs/25_PROMPT_PACKET_HARDENING.md`: branch dedicato, allowed scope, forbidden scope, forbidden actions, Verification Gate, Documentation Sync, Soft Protection awareness e report finale standard.

## Livello rischio L0-L4

Livello massimo: L2 - Write controlled.

Safety level: L2.

Se il task richiede CI/CD, dipendenze, auth, database schema, security policy, cancellazioni, produzione, force push o merge diretto, fermarsi in safe stop e richiedere approval L3/L4.

## File da leggere

- `README.md`
- `AGENTS.md`
- `docs/10_ROADMAP.md`
- `docs/05_SECURITY_MODEL.md`
- Codex Task Packet allegato
- file specifici indicati nel task

## File modificabili

- Solo i file elencati nel Codex Task Packet.

## Allowed scope

- Solo aree e file dichiarati nel task packet.
- Solo modifiche richieste dallo step.
- Se serve uscire dallo scope, fermarsi e segnalarlo.

## File vietati / file da non toccare

- `.env`
- `.env.*`
- secret o credenziali
- file fuori repository
- file non elencati come modificabili
- `.github/workflows/**` salvo approval L3
- policy di sicurezza salvo approval L3

## Forbidden scope

- File non elencati come modificabili.
- Refactor non richiesti.
- Documentazione non collegata allo step.
- Hook Git, git config, GitHub settings, CI o dipendenze salvo task esplicito.

## Vincoli

- Lavorare sul branch indicato.
- Modificare solo i file consentiti.
- Rispettare i file da non toccare indicati nel task packet.
- Non introdurre dipendenze senza decisione registrata.
- Aggiornare documentazione se cambia comportamento.
- Eseguire i test indicati.
- Se i test falliscono, non dichiarare completato il task.

## Documentation Sync

Valutare `CHANGELOG.md`, `docs/10_ROADMAP.md`, `docs/11_DECISIONS.md` e i documenti specifici coinvolti. Non aggiornare documenti per zelo.

## Verification Gate

Eseguire o motivare se non eseguiti:

```powershell
python -m pytest
git diff --check
git status --short
```

Usare `scripts/verify.ps1` quando applicabile.

## Soft Protection awareness

`main` e' trattato come protetto. Codex non deve installare hook Git, non deve eseguire `git config core.hooksPath` e non deve usare `ASF_ALLOW_MAIN_BYPASS`.

## Output atteso

A) STEP ESEGUITO
B) STATO
C) FILE CREATI
D) FILE MODIFICATI
E) VERIFICHE ESEGUITE
F) VERIFICHE NON ESEGUITE
G) RISCHI / NOTE
H) PROSSIMO STEP CONSIGLIATO
I) RIEPILOGO FINALE OBBLIGATORIO con Step eseguito, Tempo impiegato, Stato step e Prossimo step.

## Criteri di accettazione

- Il diff resta nello scope.
- I file vietati non sono toccati.
- I test richiesti passano o il task termina in safe stop.
- La documentazione necessaria e' aggiornata.
- Il rollback e' chiaro.

## Test / verifica

Eseguire i comandi indicati nel task packet. Default:

```powershell
python -m pytest -q
```

Verificare anche:

```powershell
git status --short
git diff --check
```

## Rollback / safe stop

Rollback L2: ripristinare i file modificati o abbandonare il branch. Safe stop se il diff include file fuori scope, secret, policy/CI non approvate, test critici falliti o livello superiore a L2.

## Cosa NON fare

## Forbidden actions

- Non fare commit.
- Non fare push.
- Non aprire PR.
- Non fare merge.
- Regola sintetica: no commit, no push, no merge.
- Non fare force push.
- Non cancellare file o dati.
- Non aggirare test o policy.
