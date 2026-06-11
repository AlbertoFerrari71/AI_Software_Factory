# 0940 - ASF Supervised Loop Architecture

## Scopo

Questo documento descrive il ciclo supervisionato ASF V1. Non implementa un nuovo runner automatico: definisce responsabilita', lane operative, stato, review e gate.

## Ciclo end-to-end

1. Alberto definisce obiettivo o milestone.
2. ASF Supervisor legge piano e stato.
3. GPT planner genera o aggiorna lo step plan.
4. Se l'attivita' e' deterministica, ASF usa PowerShell Fast Lane.
5. Se serve modifica a codice o documenti, ASF usa Codex CLI / `codex exec`.
6. Codex produce report Bridge.
7. ASF Supervisor rileva semaforo o report.
8. GPT reviewer valuta esito, log e diff.
9. ASF runner esegue gate locali.
10. Il loop decide `PASS`, `FIX`, `STOP` o `ASK_ALBERTO`.
11. Publish e merge avvengono solo con approvazione esplicita.
12. `main` finale deve restare pulito, verificato e allineato.

## Ruoli

| Ruolo | Responsabilita' | Puo' fare | Non puo' fare | Output atteso | Condizioni di stop |
|---|---|---|---|---|---|
| Alberto | Definisce milestone, approva publish/merge/deploy, decide scope strategico | Approvare publish, merge, deploy, milestone e cambio scope | Non deve diagnosticare ogni errore meccanico se il loop ha evidence sufficiente | Decisione umana, approval o richiesta di revisione | Evidence insufficiente, rischio L3/L4, decisione strategica non chiara |
| GPT planner/reviewer | Pianifica, rivede report/diff/log, classifica errori, propone retry o stop | Generare step plan, diagnosticare errori, proporre lane, retry o prompt Codex | Non esegue PowerShell direttamente e non modifica file locali | Piano, review, diagnosi, decisione `PASS/FIX/STOP/ASK_ALBERTO` | Non puo' motivare un retry sicuro, serve credenziale, scope ambiguo |
| Codex executor | Modifica localmente codice, test e documentazione dentro scope | Editare file autorizzati, eseguire test locali autorizzati, produrre report Bridge | Non committa, non pusha, non apre PR, non mergea, non fa deploy | Diff locale, test output, report Codex | Diff fuori scope, working tree inatteso, gate fallito non correggibile |
| PowerShell Fast Lane | Esegue comandi noti e verificabili con output strutturato | Eseguire status, diff check, test, verify, health check, raccolta log | Non interpreta scope ambiguo e non esegue comandi rischiosi o interattivi | stdout, stderr, exit code, classificazione, report JSON/log | Comando non autorizzato, timeout, stderr inatteso, richiesta input umano |
| PowerShell Recovery Loop | Gestisce timeout, processo bloccato, stderr, retry e diagnostica | Kill controllato, pacchetto diagnostico, semaforo failure, retry a basso rischio | Non forza retry se rischio o scope non sono chiari | Failure class, log, fix command/script/prompt, next action | Rischio L3+, comando distruttivo, stessi sintomi ripetuti, approval richiesta |
| ASF runner | Esegue Phase A/B/C con gate espliciti | Eseguire gate locali, publish runner controllato e verifica finale autorizzata | Non pubblica senza `-ApprovePublish`, non mergea senza `-ApproveMerge` | Risultati gate, report deterministici, stato publish/merge | Gate fallito, approval mancante, out-of-scope diff, errore Git unsafe |
| Bridge | Conserva prompt, stato, log, report e semafori | Registrare `state.json`, flag, log, report e pacchetti diagnostici | Non e' fonte autorevole al posto di Git e non autorizza azioni | File Bridge numerati, `state.json`, semafori, log append-only | File bloccato persistente, stato incoerente, scrittura non autorizzata |
| GitHub | Ospita PR, checks, merge history e stato remoto | Ricevere branch/PR autorizzati, esporre checks e stato remoto | Non sostituisce i gate locali prima della pubblicazione | PR, checks, commit history, merge evidence | Checks falliti o assenti senza evidence alternativa, branch remoto inatteso |

## Separazione delle lane

La Reasoning lane produce piani, review e diagnosi. La Deterministic lane esegue comandi meccanici ammessi. La Code-editing lane delega modifiche locali a Codex.

Ogni passaggio deve lasciare evidence nel Bridge o nel repository:

- input ricevuto;
- lane scelta;
- comando, prompt o task envelope;
- output;
- exit code;
- classificazione;
- decisione successiva.

## Decision policy

`PASS`: gate obbligatori passati, scope coerente, nessuna approval mancante.

`FIX`: problema chiaro, rischio basso, fix dentro scope e retry disponibili.

`STOP`: fallimento bloccante, rischio elevato, comando distruttivo, credenziali, scope drift o evidence insufficiente.

`ASK_ALBERTO`: serve decisione strategica, approval publish/merge/deploy, cambio scope o giudizio umano.

## Regole non negoziabili

- Output operativo su file Bridge o file versionati coerenti.
- Nessuna scrittura automatica negli appunti.
- Nessuna pubblicazione senza approval esplicita.
- `stderr` informativo sicuro con exit code `0` e' warning non bloccante.
- `stderr` inatteso o exit code nonzero resta errore.
- Warning LF/CRLF non bloccano se `git --no-pager diff --check`, test e verify gate passano.
