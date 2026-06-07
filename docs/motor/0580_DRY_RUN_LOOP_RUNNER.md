# 0580 - Dry-run Loop Runner

## 1. Scopo

Lo STEP 0580 introduce il primo runner locale del MVP Motore.

Il runner dimostra un ciclo end-to-end supervisionato a gate, ma resta inertizzato:

- legge una richiesta/step simulato in JSON;
- genera oppure legge un piano di esecuzione `dry-run`;
- attraversa gli stati definiti nello STEP 0570;
- usa il Risk Classifier 0600 nel checkpoint `RISK_CLASSIFY`;
- produce log e report strutturati;
- ferma il flusso su `NEEDS_HUMAN` oppure `FAIL`;
- non chiama provider esterni;
- non usa secret o API key;
- non modifica il repository target;
- non esegue commit, push, PR, merge, deploy o release.

Questo step costruisce il motore minimo prima di aggiungere nuovi raffinamenti di meta-processo.

---

## 2. Script

```text
scripts/asf_dry_run_loop_runner.py
```

Uso minimo con la richiesta e il piano di esempio:

```powershell
python scripts/asf_dry_run_loop_runner.py --request-json examples/dry_run_loop/step_0580_simulated_request.json --plan-json examples/dry_run_loop/step_0580_execution_plan.json
```

Output default:

```text
tmp/asf_dry_run_loop/<project>/step_<step>/
```

Il runner scrive solo artifact locali nel percorso di output. Se il percorso resta sotto `tmp/`, gli output runtime sono ignorati da Git.

---

## 3. Input

Richiesta simulata:

```text
examples/dry_run_loop/step_0580_simulated_request.json
```

Campi principali:

- `project_name`;
- `repo_path`;
- `step`;
- `title`;
- `branch`;
- `objective`;
- `allowed_scope`;
- `forbidden_actions`;
- `checks`.

Piano opzionale:

```text
examples/dry_run_loop/step_0580_execution_plan.json
```

Se `--plan-json` non viene passato, lo script genera un piano deterministico con gli stati minimi.

---

## 4. Stati attraversati

Il runner percorre gli stati dello STEP 0570:

```text
PLAN_NEXT_STEP
BUILD_TASK_PACKET
RISK_CLASSIFY
EXECUTE_DRY_OR_WRITE
RUN_TESTS
INDEPENDENT_REVIEW
GATE_DECISION
COMMIT_OR_HOLD
```

Ogni stato produce un checkpoint nello `state_log.jsonl`.

---

## 5. Artifact prodotti

Per ogni run vengono prodotti:

- `normalized_request.json`;
- `execution_plan.json`;
- `state_log.jsonl`;
- `dry_run_task_packet.md`;
- `risk_report.json`;
- `risk_report.md`;
- `execution_preview.md`;
- `test_report.md`;
- `independent_review.json`;
- `gate_decision.json`;
- `gate_decision.md`;
- `final_report.md`.

Questi artifact sono evidence leggibile. Non autorizzano da soli un passaggio a write, executor, pubblicazione o live run.

---

## 6. Gate e decisioni

Decisioni possibili:

- `NEEDS_HUMAN`: il dry-run locale e' completo, ma serve review umana prima di qualunque passo successivo;
- `FAIL`: il piano contiene segnali vietati o l'evidence e' incompleta.

Il runner usa `FAIL` quando rileva:

- piano non `dry-run`;
- piano senza tutti gli stati del loop;
- segnali di chiamate provider live;
- segnali di pubblicazione Git;
- segnali di write sul repository target;
- sandbox vietata;
- cambio di stato Git target durante il dry-run.

Una working tree target sporca produce `NEEDS_HUMAN` di default. Con `--fail-on-dirty` diventa `FAIL`.

Il checkpoint `RISK_CLASSIFY` produce `risk_report.json` con:

- `checkpoint: RISK_CLASSIFY`;
- `status`;
- blocco `risk` restituito da `scripts/asf_risk_classifier.py`;
- blocco `gate` con gate richiesto, gate dichiarati e indicazione se risultano soddisfatti nell'input;
- blocco `dry_run` con conferma che il runner non esegue live call, write target o pubblicazione Git.

Il runner non esegue i gate reali. L2 e L3 senza gate dichiarato restano evidence di pianificazione e portano comunque a hold umano. L4 senza gate elevato dichiarato blocca il dry-run con `FAIL`.

---

## 7. Limiti intenzionali

- La review indipendente e' deterministica nello stesso script; lo STEP 0620 dovra' renderla un pacchetto di decisione piu' esplicito.
- Il checkpoint `RUN_TESTS` registra i comandi richiesti, ma non esegue test del repository target.
- Non esiste ancora Gate Decision Report separato.
- Non esiste ancora Controlled Codex Executor.
- Non c'e' passaggio automatico a write anche quando il dry-run passa.

---

## 8. Verifica

Test mirati:

```powershell
python -m pytest tests/unit/test_asf_dry_run_loop_runner.py
```

Gate repository:

```powershell
python -m pytest
python scripts/check_workflow_health.py
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git --no-pager diff --check
git --no-pager status --short
```

---

## 9. Evoluzione successiva

```text
0620) Gate Decision Report and Human Approval Packet
```

Lo STEP 0600 ha estratto la classificazione L0-L4.

Lo STEP 0610 collega `scripts/asf_risk_classifier.py` al checkpoint `RISK_CLASSIFY` del runner, mantenendo il loop dry-run senza write, live run o pubblicazione Git.
