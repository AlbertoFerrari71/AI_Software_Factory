# Codex Repair Prompt

Usa questo prompt quando un task precedente ha prodotto errore, test falliti o comportamento non conforme.

## Obiettivo

Correggere il problema minimo necessario senza cambiare architettura fuori scope.

## Contesto

La repair e' una modifica controllata: deve partire dalla causa probabile, limitarsi al difetto osservato e rieseguire i test falliti. Non deve trasformarsi in refactor ampio.

La repair deve rispettare `docs/25_PROMPT_PACKET_HARDENING.md`: allowed scope, forbidden scope, forbidden actions, Verification Gate, Documentation Sync, Soft Protection awareness e report finale standard.

## Livello rischio L0-L4

Livello massimo: L2 - Write controlled.

Safety level: L2.

Se la riparazione richiede CI/CD, dipendenze, auth, database schema, security policy, cancellazioni, produzione, force push o merge diretto, fermarsi in safe stop e richiedere approval L3/L4.

## File da leggere

- output del test fallito;
- diff del task precedente;
- Codex Task Packet originario;
- file coinvolti dall'errore;
- `AGENTS.md`;
- `docs/05_SECURITY_MODEL.md`.

## File modificabili

- Solo i file necessari alla correzione e ammessi dal task packet o dalla richiesta di repair.

## Allowed scope

- Solo file collegati al difetto osservato.
- Solo correzione minima.
- Se serve uscire dallo scope, fermarsi e segnalarlo.

## File vietati / file da non toccare

- `.env`
- `.env.*`
- secret o credenziali
- file fuori repository
- file non collegati al difetto
- CI/CD, dipendenze e policy senza approval L3

## Forbidden scope

- Refactor non richiesti.
- Riscritture ampie.
- File non collegati al test fallito o al difetto osservato.
- Hook Git, git config, GitHub settings, CI o dipendenze salvo task esplicito.

## Vincoli

- Prima spiegare la causa probabile.
- Applicare il fix minimo.
- Non introdurre nuove dipendenze salvo decisione approvata.
- Eseguire i test falliti e quelli di regressione pertinenti.
- Rispettare i file da non toccare indicati nel task packet o nella repair request.
- Non cancellare codice senza motivazione.
- Non dichiarare completato se i test falliscono.

## Documentation Sync

Aggiornare documentazione solo se la repair cambia comportamento, workflow o decisioni. Dichiarare nel report finale se non era necessario.

## Verification Gate

Rieseguire il test fallito e i controlli pertinenti. Default:

```powershell
python -m pytest
git diff --check
git status --short
```

## Soft Protection awareness

Codex non deve installare hook Git, non deve eseguire `git config core.hooksPath` e non deve usare `ASF_ALLOW_MAIN_BYPASS`.

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

- Il fix e' minimo e nel perimetro.
- I test falliti sono rieseguiti.
- Non sono introdotte dipendenze non approvate.
- Non sono toccati file vietati.
- Il comportamento atteso e' verificato o il task termina in safe stop.

## Test / verifica

Eseguire almeno il test fallito. Se non e' chiaro, usare:

```powershell
python -m pytest -q
```

Verificare anche il diff:

```powershell
git diff --check
```

## Rollback / safe stop

Rollback L2: ripristinare i file modificati o abbandonare il branch. Safe stop se la causa non e' chiara, il fix richiede livello superiore a L2, compaiono secret o i test restano falliti senza diagnosi.

## Cosa NON fare

## Forbidden actions

- Non fare refactor non richiesti.
- Non cambiare architettura fuori scope.
- Non fare commit, push o merge.
- Regola sintetica: no commit, no push, no merge.
- Non cancellare file o dati.
- Non aggirare test o policy.
- Non installare hook Git.
- Non modificare git config core.hooksPath.
- Non usare ASF_ALLOW_MAIN_BYPASS.
