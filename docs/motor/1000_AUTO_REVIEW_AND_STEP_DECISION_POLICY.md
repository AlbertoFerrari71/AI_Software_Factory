# 1000 - Auto Review and Step Decision Policy

## Scopo

Questo step introduce una policy deterministica per decidere cosa fare dopo una fase del supervised loop.

Il modulo non chiama GPT e non esegue azioni operative. Applica regole locali e restituisce una decisione.

## Script

```text
scripts/asf_step_decision_policy.py
```

CLI minima:

```text
python scripts/asf_step_decision_policy.py --input-file path\to\decision_input.json --json
```

## Decisioni

La policy restituisce solo:

- `PASS`;
- `FIX`;
- `STOP`;
- `ASK_ALBERTO`.

## Input

Template:

```text
docs/templates/1000_STEP_DECISION_INPUT_TEMPLATE.json
```

Campi principali:

- `step_id`;
- `current_state`;
- `risk_level`;
- `phase`;
- `verification_profile`;
- `verification_result`;
- `failure_class`;
- `retry_count`;
- `max_retry_absolute`;
- `changed_files`;
- `allowed_paths`;
- `forbidden_actions_detected`;
- `requires_approval`;
- `milestone`;
- `publish_requested`;
- `merge_requested`;
- `deploy_requested`.

## Regole

`PASS` richiede verifica passata, rischio accettabile, nessuna azione vietata, nessun file fuori scope e nessuna approval richiesta.

`FIX` richiede failure recuperabile, retry disponibile, rischio `L0`/`L1`/`L2`, nessuna credenziale o input umano e nessuna azione vietata.

`STOP` scatta su azioni vietate, file fuori scope, failure grave sconosciuta, retry esauriti, comandi distruttivi o segnali di segreti/credenziali.

`ASK_ALBERTO` scatta su publish, merge, deploy, milestone, approval richiesta, rischio `L3+`, scope ambiguo, scelta strategica o input umano/credenziale.

## Retry policy

La policy integra:

```text
GPT-discretionary bounded retry policy
max retry assoluto: 10
10 non e' default automatico
```

Il default locale del modulo, se l'input non dichiara altro, e' piu' basso. Il valore configurato viene comunque limitato dal tetto assoluto 10.

## Guardrail

- nessuna chiamata GPT;
- nessuna rete;
- nessuna esecuzione tool;
- nessuna pubblicazione Git;
- nessun merge;
- nessun deploy;
- no OS appunti.

## Test

```text
tests/unit/test_asf_step_decision_policy.py
```

Copertura minima:

- `PASS` su verifica passata a basso rischio;
- `FIX` su errore recuperabile con retry disponibile;
- `STOP` su forbidden action;
- `STOP` su retry esauriti;
- `ASK_ALBERTO` su publish, merge, deploy e rischio `L3+`;
- `STOP` su failure sconosciuta grave.
