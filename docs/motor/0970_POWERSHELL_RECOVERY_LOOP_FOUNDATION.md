# 0970 - PowerShell Recovery Loop Foundation

## Scopo

Lo STEP 0970 introduce una foundation per classificare failure PowerShell e decidere retry, stop o richiesta ad Alberto.

Non e' un recovery loop automatico completo. Non rilancia comandi da solo.

## Script

```text
scripts/asf_powershell_recovery_classifier.py
```

## Classi minime

- `POWERSHELL_PARSE_ERROR`
- `POWERSHELL_PROMPT_CONTINUATION`
- `GIT_PAGER_BLOCK`
- `GIT_SAFE_WARNING`
- `GIT_UNSAFE_ERROR`
- `FILE_LOCKED`
- `GH_NO_CHECKS_REPORTED`
- `LF_CRLF_SAFE_WARNING`
- `CREDENTIAL_PROMPT`
- `API_QUOTA_OR_RATE_LIMIT`
- `TEST_FAILURE`
- `VERIFY_FAILURE`
- `WORKFLOW_HEALTH_FAILURE`
- `UNKNOWN_FAILURE`
- `TIMEOUT`
- `IDLE_TIMEOUT`
- `POTENTIALLY_DESTRUCTIVE_COMMAND`

## Output

Ogni classificazione produce:

- `classification`;
- `safe_to_retry`;
- `requires_alberto`;
- `recommended_next_action`;
- `risk_level`;
- `retry_allowed`;
- `stop_reason`;
- `diagnostic_summary`.

## Retry policy

- GPT-discretionary bounded retry policy.
- Max retry assoluto: 10.
- Regola testuale: max retry assoluto: 10.
- 10 non e' default automatico.
- Ogni retry deve avere una differenza motivata rispetto al tentativo precedente.
- Stop immediato su rischio, scope o sicurezza non accettabili.

## Stop immediato

Il classifier richiede stop quando rileva:

- comando potenzialmente distruttivo;
- prompt credenziali o input umano;
- errore Git unsafe;
- failure sconosciuta;
- retry ceiling raggiunto.

## Uso CLI

```powershell
python scripts/asf_powershell_recovery_classifier.py --stderr "Workflow Health Check FAILED" --exit-code 1 --json
```

Il comando sopra classifica il testo passato. Non esegue workflow health.
