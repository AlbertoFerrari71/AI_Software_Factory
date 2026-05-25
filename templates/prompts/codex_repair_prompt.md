# Codex Repair Prompt

Usa questo prompt quando un task precedente ha prodotto errore, test falliti o comportamento non conforme.

## Obiettivo

Correggere il problema minimo necessario senza cambiare architettura fuori scope.

## Contesto

La repair e' una modifica controllata: deve partire dalla causa probabile, limitarsi al difetto osservato e rieseguire i test falliti. Non deve trasformarsi in refactor ampio.

## Livello rischio L0-L4

Livello massimo: L2 - Write controlled.

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

## File vietati

- `.env`
- `.env.*`
- secret o credenziali
- file fuori repository
- file non collegati al difetto
- CI/CD, dipendenze e policy senza approval L3

## Vincoli

- Prima spiegare la causa probabile.
- Applicare il fix minimo.
- Non introdurre nuove dipendenze salvo decisione approvata.
- Eseguire i test falliti e quelli di regressione pertinenti.
- Non cancellare codice senza motivazione.
- Non dichiarare completato se i test falliscono.

## Output atteso

1. Causa probabile.
2. Fix applicato.
3. File modificati.
4. Test eseguiti.
5. Esito.
6. Rischi residui.
7. Rollback consigliato.

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

- Non fare refactor non richiesti.
- Non cambiare architettura fuori scope.
- Non fare commit, push o merge.
- Non cancellare file o dati.
- Non aggirare test o policy.
