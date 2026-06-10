# 0940 - Supervised Loop State Machine

## Scopo

Questo documento definisce stati, semafori e `state.json` minimo del supervised loop ASF V1.

I flag sono segnali semplici. `state.json` e' la verita' strutturata.

## State root

Percorso operativo previsto:

```text
D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\supervised_loop\state.json
```

I test futuri devono usare root temporanee o ignorate, non il Bridge reale.

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

## File semaforo possibili

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

## Struttura minima di state.json

```json
{
  "schema_version": "0940.1",
  "project": "AI_Software_Factory",
  "step_id": "0940",
  "state": "IDLE",
  "lane": null,
  "decision": null,
  "risk_level": "L1",
  "approval_required": [],
  "approval_granted": [],
  "retry_policy": {
    "name": "GPT-discretionary bounded retry policy",
    "max_retry_absolute": 10,
    "current_retry": 0,
    "retry_remaining": 10
  },
  "last_event": {
    "event": null,
    "timestamp_utc": null,
    "actor": null
  },
  "artifacts": {
    "plan": null,
    "prompt": null,
    "stdout": null,
    "stderr": null,
    "report": null,
    "diff_summary": null
  },
  "failure": {
    "class": null,
    "message": null,
    "safe_to_retry": false
  },
  "next_recommended_action": "PLAN_REQUESTED"
}
```

## Transizioni principali

| Da | Evento | A | Note |
|---|---|---|---|
| `IDLE` | obiettivo ricevuto | `PLAN_REQUESTED` | Alberto o planner avvia step |
| `PLAN_REQUESTED` | planner avviato | `GPT_PLANNING` | Reasoning lane |
| `GPT_PLANNING` | piano valido | `GPT_PLAN_READY` | Step plan salvato |
| `GPT_PLAN_READY` | task deterministico | `POWERSHELL_READY` | Fast Lane |
| `GPT_PLAN_READY` | modifica locale | `CODEX_READY` | Code-editing lane |
| `POWERSHELL_READY` | comando avviato | `POWERSHELL_RUNNING` | processo isolato |
| `POWERSHELL_RUNNING` | exit code atteso | `POWERSHELL_DONE` | report salvato |
| `POWERSHELL_RUNNING` | failure | `POWERSHELL_FAILED` | classificare failure |
| `POWERSHELL_RUNNING` | timeout/idle | `POWERSHELL_HUNG` | watchdog |
| `CODEX_READY` | executor avviato | `CODEX_RUNNING` | no publish |
| `CODEX_RUNNING` | report ok | `CODEX_DONE` | report Bridge |
| `CODEX_RUNNING` | failure | `CODEX_FAILED` | stop o retry |
| `POWERSHELL_DONE` | review richiesta | `REVIEW_REQUESTED` | GPT reviewer |
| `CODEX_DONE` | review richiesta | `REVIEW_REQUESTED` | GPT reviewer |
| `REVIEW_REQUESTED` | review avviata | `GPT_REVIEWING` | diff/log/report |
| `GPT_REVIEWING` | esito positivo | `REVIEW_PASS` | procedere a verify |
| `GPT_REVIEWING` | fix richiesto | `REVIEW_FIX_REQUIRED` | retry o Codex prompt |
| `REVIEW_PASS` | gate avviati | `VERIFY_RUNNING` | test e verify |
| `VERIFY_RUNNING` | gate passati | `VERIFY_PASS` | pronto per decisione |
| `VERIFY_RUNNING` | gate falliti | `VERIFY_FAIL` | stop o fix |
| `REVIEW_FIX_REQUIRED` | retry sicuro | `RETRY_READY` | policy retry |
| `RETRY_READY` | retry avviato | `RETRY_RUNNING` | decremento retry |
| `VERIFY_PASS` | approval necessaria | `NEEDS_ALBERTO_APPROVAL` | publish/merge/deploy/milestone |
| `VERIFY_PASS` | nessuna approval restante | `COMPLETED` | step locale completato |
| qualsiasi | blocker | `STOPPED` | fail-closed |

## Retry policy

Nome policy: GPT-discretionary bounded retry policy.

GPT reviewer puo' autorizzare retry automatici da 0 a 10. Ogni retry deve registrare motivazione, failure class, rischio stimato, comando/script corretto, expected effect, stop condition, retry corrente e retry rimanenti.

`10` e' il massimo assoluto. Il default puo' essere 0, 1 o un numero inferiore scelto dal reviewer in base al rischio.

Stop immediato se rischio, scope, sicurezza o approval non sono accettabili.

