# 0610 - Risk Classifier Dry-run Integration

## 1. Scopo

Lo STEP 0610 collega il classificatore di rischio dello STEP 0600 al checkpoint `RISK_CLASSIFY` del Dry-run Loop Runner dello STEP 0580.

L'integrazione resta locale e inertizzata:

- usa `scripts/asf_risk_classifier.py` come fonte unica delle regole L0-L4;
- non duplica le regole nel runner;
- non chiama provider esterni;
- non legge secret o API key;
- non modifica il repository target;
- non esegue commit, push, PR, merge, deploy o release;
- non esegue gate reali di pubblicazione.

---

## 2. Punto di integrazione

Il runner e':

```text
scripts/asf_dry_run_loop_runner.py
```

Nel checkpoint `RISK_CLASSIFY` il runner importa il classifier reale:

```text
scripts/asf_risk_classifier.py
```

Il runner costruisce un input classificabile da:

- `title` e `objective` del request JSON;
- `allowed_scope` come file/path previsti;
- `checks` come comandi di verifica dichiarati;
- azioni o comandi dichiarati nel piano dry-run, quando presenti;
- `provided_gates`, `declared_gates` o `satisfied_gates`, se dichiarati dal request o dal piano.

I `forbidden_actions` non sono trattati come intento operativo: restano guardrail dichiarati dal request e non devono alzare il rischio da soli.

---

## 3. Output rischio

`risk_report.json` contiene un checkpoint strutturato:

```json
{
  "checkpoint": "RISK_CLASSIFY",
  "status": "PASS",
  "risk": {
    "risk_level": "L2",
    "allowed": false,
    "required_gate": "local_verification",
    "reasons": [],
    "matched_rules": [],
    "fail_closed": false,
    "recommended_next_action": "Run local verification before proceeding."
  },
  "gate": {
    "required_gate": "local_verification",
    "provided_gates": [],
    "declared_satisfied": false,
    "dry_run_enforced": true,
    "runner_executes_gate": false
  },
  "dry_run": {
    "fail_closed": false,
    "blocked_in_dry_run": false,
    "no_live_provider_calls": true,
    "no_target_repo_writes": true,
    "no_git_publication": true
  },
  "plan_blockers": []
}
```

`allowed` indica solo che il gate dichiarato nell'input corrisponde alla policy del classifier. Non autorizza il runner a eseguire test, publish, merge o deploy.

---

## 4. Fail-closed

Il runner fallisce chiuso quando:

- il classifier non e' importabile o restituisce uno schema non valido;
- il classifier restituisce `fail_closed: true`;
- il piano non e' `dry-run`;
- il piano dichiara provider live, pubblicazione Git o write sul target;
- il piano contiene segnali proibiti dalla safety dry-run;
- il rischio e' L4 senza gate elevato dichiarato.

In questi casi il checkpoint ha `status: FAIL`, `dry_run.fail_closed: true` e il runner si ferma con decisione finale `FAIL`.

L2 e L3 senza gate dichiarato restano classificazioni valide: il dry-run produce evidence e segnala il gate richiesto, ma termina comunque su hold umano e non esegue azioni operative.

---

## 5. Esempi

Esempi request dry-run:

```text
examples/dry_run_loop/step_0610_docs_only_request.json
examples/dry_run_loop/step_0610_code_change_request.json
examples/dry_run_loop/step_0610_publish_intent_request.json
examples/dry_run_loop/step_0610_l4_blocked_request.json
```

Esecuzione esempio L2:

```powershell
python scripts/asf_dry_run_loop_runner.py --request-json examples/dry_run_loop/step_0610_code_change_request.json
```

Gli artifact vengono scritti sotto:

```text
tmp/asf_dry_run_loop/<project>/step_<step>/
```

Se il percorso resta sotto `tmp/`, gli output runtime sono ignorati da Git.

---

## 6. Gate policy riportata

Il runner riporta:

- livello L0-L4;
- gate richiesto;
- gate dichiarati nell'input;
- se il gate e' dichiarato come soddisfatto;
- prossima azione consigliata.

Il runner non verifica ne' esegue i gate reali. La pubblicazione resta fuori da questo script e passa dal runner standard:

```text
scripts/asf_publish_step.ps1
```

---

## 7. Verifica

Test mirati:

```powershell
python -m pytest tests/unit/test_asf_dry_run_loop_runner.py
python -m pytest tests/unit/test_asf_risk_classifier.py
```

Gate repository:

```powershell
python -m pytest
python scripts/check_workflow_health.py
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git --no-pager diff --check
git status --short
```

---

## 8. Evoluzione dopo STEP 0620

```text
0620) Gate Decision Report and Human Approval Packet
```

Lo STEP 0620 consuma il risk report 0610 come input stabile e produce un Approval Packet umano con decisione, risk level, gate richiesto, check evidence, blocker, warning e prossima azione consigliata.

Il prossimo step consigliato dopo 0620 e':

```text
0630) Verification Profile Selector + Test Cost Policy
```
