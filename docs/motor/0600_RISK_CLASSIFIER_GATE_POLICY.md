# 0600 - Risk Classifier + Gate Policy

## 1. Scopo

Lo STEP 0600 introduce un classificatore di rischio locale, deterministico e fail-closed per il MVP Motore ASF.

Il classificatore:

- legge testo libero oppure JSON leggero;
- assegna il livello massimo L0-L4;
- restituisce una gate policy strutturata;
- non chiama provider esterni;
- non legge secret;
- non esegue comandi Git, pubblicazione, deploy o cancellazioni;
- non sostituisce la review umana.

Lo script e':

```text
scripts/asf_risk_classifier.py
```

Gli esempi sono:

```text
examples/risk_classifier/sample_l0_docs_only.json
examples/risk_classifier/sample_l2_code_change.json
examples/risk_classifier/sample_l3_publish.json
examples/risk_classifier/sample_l4_deploy_or_destructive.json
```

---

## 2. Livelli di rischio

| Livello | Definizione | Esempi |
|---|---|---|
| L0 | Documentation, read-only, no-op | docs-only, inspect, README, Markdown |
| L1 | Local generated artifacts, examples, dry-run outputs | examples, sample JSON, tmp artifacts, local verification commands |
| L2 | Source/test changes without external side effects | Python scripts, tests, local parser logic |
| L3 | Repository publication or sensitive workflow surface | commit, push, PR, CI/workflow/policy/dependency surface |
| L4 | Destructive, deployment, secrets, external side effects, production impact | merge, deploy, delete, secrets, live provider, network side effects |

La regola operativa e' prudente: il livello finale e' il massimo livello trovato tra tutte le regole.

Se l'input e' vuoto, incompleto o non riconosciuto, il risultato e' fail-closed.

---

## 3. Gate policy

Il risultato include sempre:

```json
{
  "risk_level": "L0",
  "allowed": true,
  "required_gate": "none",
  "reasons": [],
  "matched_rules": [],
  "fail_closed": false,
  "recommended_next_action": ""
}
```

Gate correnti:

| Livello | Gate richiesto | Allowed di default |
|---|---|---|
| L0 | `none` | true |
| L1 | `implicit_or_local_approval` | true |
| L2 | `local_verification` | false |
| L3 | `explicit_publish_approval` | false |
| L4 | `elevated_manual_approval` | false |

Per L2, L3 e L4 lo script puo' ricevere gate gia' soddisfatti con `--gate`, ad esempio:

```powershell
python scripts/asf_risk_classifier.py --text "implement script and tests" --gate local_verification --json
```

Il flag `--gate` non esegue verifiche reali. Dichiara solo che un gate esterno e' gia' stato soddisfatto.

---

## 4. CLI

Uso testuale:

```powershell
python scripts/asf_risk_classifier.py --text "modify docs only"
python scripts/asf_risk_classifier.py --text "commit and push branch" --json
```

Uso con JSON:

```powershell
python scripts/asf_risk_classifier.py --input-file examples/risk_classifier/sample_l3_publish.json --json
```

Output testuale default:

```text
risk_level: L3
allowed: false
required_gate: explicit_publish_approval
fail_closed: false
recommended_next_action: Stop until explicit publish approval is present.
```

Output JSON:

```json
{
  "allowed": false,
  "fail_closed": false,
  "matched_rules": [],
  "reasons": [],
  "recommended_next_action": "Stop until explicit publish approval is present.",
  "required_gate": "explicit_publish_approval",
  "risk_level": "L3"
}
```

---

## 5. Input JSON supportato

Lo script accetta un oggetto JSON con campi leggeri, per esempio:

```json
{
  "description": "Implement a local Python script and unit tests without external side effects.",
  "files_changed": [
    "scripts/asf_risk_classifier.py",
    "tests/unit/test_asf_risk_classifier.py"
  ],
  "commands": [
    "python -m pytest"
  ]
}
```

Campi riconosciuti:

- testo: `text`, `description`, `summary`, `objective`, `title`, `step_description`, `notes`;
- file: `files`, `file_paths`, `files_changed`, `modified_files`, `expected_files`;
- comandi: `commands`, `proposed_commands`, `phase_a_checks`, `phase_b_commands`, `phase_c_checks`;
- parole chiave: `keywords`, `actions`, `operation_keywords`, `forbidden_actions`.

Le stringhe non riconosciute vengono comunque considerate. Se contengono path riconoscibili, vengono trattate come file; altrimenti come testo.

---

## 6. Fail-closed coperti

Il classificatore fallisce chiuso quando:

- l'input e' vuoto;
- l'input non contiene segnali riconosciuti;
- l'input contiene segnali distruttivi;
- l'input contiene merge/deploy/produzione;
- l'input contiene secret, token, credenziali o `.env`;
- l'input contiene live provider, rete o side effect esterni;
- l'input contiene install comandi per dipendenze che possono usare rete.

Nel fail-closed per input vuoto o non riconosciuto il livello restituito e' L4, `allowed` e' `false` e l'azione consigliata e' fermarsi per review umana.

---

## 7. Relazione con runner 0580 e publish runner 0590

Lo STEP 0600 non modifica `scripts/asf_dry_run_loop_runner.py`.

Il runner 0580 mantiene la propria classificazione minima interna. L'integrazione diretta con `scripts/asf_risk_classifier.py` resta lo step successivo consigliato, per evitare di cambiare il comportamento del loop dry-run mentre si introduce la policy stabile.

Lo STEP 0600 non modifica `scripts/asf_publish_step.ps1`.

Il publish runner 0590 resta lo strumento standard per pubblicare step dopo report Codex, review umana e gate locali.

---

## 8. Verifica

Test mirati:

```powershell
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

## 9. Limiti

- Il classificatore e' rule-based: non capisce intenzioni complesse non espresse nel testo.
- Le parole pericolose presenti anche in un contesto descrittivo possono alzare il livello.
- `allowed` indica solo la coerenza con i gate dichiarati, non esegue test o approval.
- L'integrazione con il dry-run loop runner resta separata.

---

## 10. Prossimo step

```text
0610) Risk Classifier Integration with Dry-run Loop Runner
```

Lo step dovrebbe collegare il nuovo classificatore al checkpoint `RISK_CLASSIFY` del runner 0580 mantenendo comportamento fail-closed e senza introdurre write, publish o live run.
