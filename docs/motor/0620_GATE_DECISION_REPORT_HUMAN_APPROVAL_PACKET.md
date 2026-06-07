# 0620 - Gate Decision Report and Human Approval Packet

## 1. Scopo

Lo STEP 0620 introduce il primo pacchetto decisionale umano del MVP Motore ASF.

Il pacchetto trasforma evidence tecnica del Dry-run Loop Runner e del Risk Classifier in un report leggibile per Alberto:

- rischio L0-L4 gia' classificato;
- gate richiesto;
- stato del gate;
- file in scope;
- verifiche richieste e riportate;
- blocker e warning;
- decisione consigliata;
- testo umano di approvazione;
- blocco machine-readable.

Lo script non classifica di nuovo il rischio e non copia le regole L0-L4. Consuma l'output gia' prodotto da `scripts/asf_risk_classifier.py` o dal checkpoint `RISK_CLASSIFY` del dry-run runner 0610.

---

## 2. Script

```text
scripts/asf_gate_decision_report.py
```

Lo script legge un JSON prodotto o compatibile con:

- `risk_report.json` del Dry-run Loop Runner;
- un bundle JSON che include `risk_report`, `files_in_scope`, `checks_required` e `checks_reported`;
- un JSON minimale con `risk.risk_level`, `risk.required_gate`, `risk.allowed` e `risk.fail_closed`.

Input non valido, ambiguo o senza `risk_level` produce sempre `FAIL_CLOSED`.

---

## 3. Output Approval Packet

Il pacchetto contiene sempre:

- `step`;
- `title`;
- `decision`;
- `risk_level`;
- `required_gate`;
- `gate_status`;
- `allowed`;
- `fail_closed`;
- `summary`;
- `files_in_scope`;
- `checks_required`;
- `checks_reported`;
- `blockers`;
- `warnings`;
- `recommended_next_action`;
- `human_approval_text`;
- `machine_readable`.

`allowed` nel pacchetto significa che il report propone una prossima azione locale o di publish human-gated. Non significa che lo script abbia eseguito l'azione.

`machine_readable.no_operational_actions_executed` resta sempre `true`.

---

## 4. Decisioni

| Decisione | Significato |
|---|---|
| `APPROVE_LOCAL_ONLY` | Evidence coerente per review o prosecuzione locale. Nessuna pubblicazione viene eseguita. |
| `NEEDS_HUMAN` | Serve decisione umana o evidence aggiuntiva prima di procedere. |
| `APPROVE_PUBLISH` | L3 con approvazione esplicita e check locali passati. E' solo un report: la pubblicazione resta al runner 0590. |
| `BLOCKED` | Sono presenti blocker, check falliti o rischio L4 da gestire separatamente. |
| `FAIL_CLOSED` | Input o evidence non sicuri, incompleti o dichiarati fail-closed. |

---

## 5. Policy prudente

### L0/L1

L0/L1 possono produrre `APPROVE_LOCAL_ONLY` se non ci sono blocker o check falliti.

Non e' richiesta approvazione di pubblicazione quando non ci sono azioni Git operative.

### L2

L2 richiede evidence di verifica locale:

- se i check richiesti non sono dichiarati, la decisione e' `NEEDS_HUMAN`;
- se i check non sono riportati o non sono passati, la decisione e' `NEEDS_HUMAN` o `BLOCKED`;
- se i check richiesti risultano passati, la decisione e' `APPROVE_LOCAL_ONLY`.

### L3

L3 richiede:

- check locali completi;
- `explicit_publish_approval` dichiarata.

Senza approval dichiarata la decisione resta `NEEDS_HUMAN`.

Con approval dichiarata e check passati la decisione diventa `APPROVE_PUBLISH`, ma lo script non esegue pubblicazione. Per pubblicare si usa:

```text
scripts/asf_publish_step.ps1
```

con `-ApprovePublish`.

### L4

L4 resta `BLOCKED` oppure `FAIL_CLOSED` di default.

Anche se un input dichiara `elevated_manual_approval`, il report richiede review separata, rollback planning e conferma manuale elevata prima di qualunque passo operativo.

### Input ambiguo

Se l'input non contiene rischio riconoscibile, lo script non assume sicurezza e produce `FAIL_CLOSED`.

---

## 6. CLI

JSON machine-readable:

```powershell
python scripts/asf_gate_decision_report.py --input-file examples/gate_decision/sample_l2_code_change_checked.json --json
```

Markdown leggibile:

```powershell
python scripts/asf_gate_decision_report.py --input-file examples/gate_decision/sample_l3_publish_needs_approval.json --markdown
```

Scrittura di tutti i formati:

```powershell
python scripts/asf_gate_decision_report.py --input-file examples/gate_decision/sample_l4_blocked.json --out-dir tmp/gate_decision
```

Output in `--out-dir`:

- `approval_packet.json`;
- `approval_packet.md`;
- `approval_packet.txt`.

Se nessun formato viene richiesto, lo script stampa un output testuale compatto.

---

## 7. Esempi

Esempi minimali:

```text
examples/gate_decision/sample_l1_local_docs.json
examples/gate_decision/sample_l2_code_change_checked.json
examples/gate_decision/sample_l3_publish_needs_approval.json
examples/gate_decision/sample_l3_publish_approved.json
examples/gate_decision/sample_l4_blocked.json
examples/gate_decision/sample_invalid_fail_closed.json
```

Gli esempi sono piccoli e pensati per test automatici e verifica manuale.

---

## 8. Relazione con 0580, 0600 e 0610

Lo STEP 0580 produce il primo loop dry-run.

Lo STEP 0600 introduce il Risk Classifier + Gate Policy.

Lo STEP 0610 collega il classifier al checkpoint `RISK_CLASSIFY` del dry-run runner.

Lo STEP 0620 consuma quell'evidence e produce un Approval Packet piu' esplicito.

Lo STEP 0620 non modifica il publish runner 0590 e non sostituisce Alberto nel gate umano.

---

## 9. Non azioni

Lo script:

- non chiama provider esterni;
- non legge secret;
- non modifica repository target;
- non esegue test target;
- non esegue publish;
- non fa commit, push, PR, merge, deploy o release.

---

## 10. Verifica

Test mirati:

```powershell
python -m pytest tests/unit/test_asf_gate_decision_report.py -q
```

Gate repository:

```powershell
python -m pytest
python scripts/check_workflow_health.py
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git --no-pager diff --check
git status --short --untracked-files=all
```

---

## 11. Prossimo step

```text
0630) Verification Profile Selector + Test Cost Policy
```

Motivo: prima di introdurre un executor Codex piu' operativo, ASF deve distinguere meglio i profili di verifica per ridurre ridondanze senza ridurre sicurezza.
