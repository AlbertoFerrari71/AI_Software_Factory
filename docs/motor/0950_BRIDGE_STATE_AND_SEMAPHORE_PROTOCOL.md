# 0950 - Bridge State and Semaphore Protocol

## Scopo

Questo documento trasforma la state machine 0940 in un protocollo Bridge operativo per il futuro ASF Supervised Loop.

Il protocollo e' locale, supervisionato e file-based. Non fa API live, non invoca Codex exec, non pubblica e non sostituisce Git come fonte autorevole.

## Root operativo

Root logica prevista:

```text
D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\supervised_loop
```

Fonte primaria:

```text
state.json
```

I file `.flag` sono solo segnali semplici per lane e watcher. Non contengono la verita' strutturata.

## Regole

- `state.json` e' la verita' strutturata.
- I `.flag` non possono correggere o sovrascrivere `state.json`.
- Ogni cambio stato deve aggiungere una riga all'event log append-only.
- La scrittura di `state.json` deve essere atomica dove possibile: scrivere un file temporaneo nello stesso root e poi sostituire il file finale.
- Nessun cambio stato silenzioso: ogni transizione richiede evento, actor, timestamp e reason.
- Regola equivalente per i test: nessun cambio stato silenzioso.
- `stop_reason` e' obbligatorio negli stati `STOPPED`, `POWERSHELL_FAILED`, `POWERSHELL_HUNG`, `CODEX_FAILED`, `VERIFY_FAIL`.
- `approval_reason` e' obbligatorio nello stato `NEEDS_ALBERTO_APPROVAL`.
- `COMPLETED` richiede che i gate obbligatori siano registrati in `verification`.
- Il Bridge e' operational storage; Git e i file versionati restano autorevoli.

## Stati minimi

- `IDLE`
- `PLAN_REQUESTED`
- `GPT_PLANNING`
- `GPT_PLAN_READY`
- `POWERSHELL_READY`
- `POWERSHELL_RUNNING`
- `POWERSHELL_DONE`
- `POWERSHELL_FAILED`
- `POWERSHELL_HUNG`
- `CODEX_READY`
- `CODEX_RUNNING`
- `CODEX_DONE`
- `CODEX_FAILED`
- `REVIEW_REQUESTED`
- `GPT_REVIEWING`
- `REVIEW_PASS`
- `REVIEW_FIX_REQUIRED`
- `VERIFY_RUNNING`
- `VERIFY_PASS`
- `VERIFY_FAIL`
- `RETRY_READY`
- `RETRY_RUNNING`
- `NEEDS_ALBERTO_APPROVAL`
- `STOPPED`
- `COMPLETED`

## Flag minimi

- `READY_FOR_GPT.flag`
- `GPT_PROMPT_DONE.flag`
- `POWERSHELL_RUNNING.flag`
- `POWERSHELL_DONE.flag`
- `POWERSHELL_FAILED.flag`
- `POWERSHELL_HUNG.flag`
- `CODEX_RUNNING.flag`
- `CODEX_DONE.flag`
- `CODEX_FAILED.flag`
- `VERIFY_RUNNING.flag`
- `VERIFY_DONE.flag`
- `NEEDS_ALBERTO_APPROVAL.flag`
- `STOPPED.flag`
- `COMPLETED.flag`

## File template

- `docs/templates/0950_SUPERVISED_LOOP_STATE_JSON_TEMPLATE.json`
- `docs/templates/0950_SUPERVISED_LOOP_EVENT_LOG_TEMPLATE.jsonl`

I test devono usare root temporanee o file versionati. Non devono richiedere il Bridge reale.

## Stop policy

Il loop deve fermarsi quando stato, flag ed event log non sono coerenti, quando manca una ragione di stop obbligatoria, quando serve approvazione di Alberto o quando un retry non e' motivato.

La policy di retry resta:

- GPT-discretionary bounded retry policy;
- max retry assoluto: 10;
- 10 non e' default automatico;
- stop immediato su rischio, scope o sicurezza non accettabili.
