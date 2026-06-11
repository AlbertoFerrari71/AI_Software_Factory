# 0630 - Verification Profile Selector + Test Cost Policy

## 1. Scopo

Lo STEP 0630 introduce un selettore locale dei profili di verifica.

Il selettore non esegue test, publish, merge, deploy o azioni operative. Produce una raccomandazione strutturata sui check da eseguire in base a:

- livello di rischio L0-L4;
- file modificati;
- fase richiesta;
- intento operativo dichiarato;
- check gia' eseguiti;
- gate eventualmente dichiarati.

La policy riduce verifiche ridondanti solo quando lo scope e' chiaro. In caso di input vuoto, ambiguo, non riconosciuto o high-risk, il sistema fallisce chiuso.

---

## 2. Script

```text
scripts/asf_verification_profile_selector.py
```

Lo script e' deterministico, standard-library only e pensato per essere testato con funzioni pure.

---

## 3. Profili supportati

| Profilo | Quando usarlo | Costo | Regola prudente |
|---|---|---|---|
| `docs-only` | Solo file Markdown/documentazione | low | `git diff --check`, workflow health se documenti indicizzati |
| `code-unit` | Codice o test circoscritti fuori dal core motore | medium | test mirati, diff check, full pytest condizionale |
| `motor-core` | runner, gate, risk classifier, selector, workflow health, publish logic | high | test mirati, regressioni collegate, full pytest, workflow health, verify |
| `publish` | rischio L3 o intento di pubblicazione | medium | usare Phase B del runner; non lanciare Phase A separata |
| `final-main` | verifica finale post-merge/main | high | Phase C, workflow health, verify, diff check, tree clean |
| `high-risk` | L4, deploy, cancellazioni, segreti, produzione, side effect esterni | high | manual review, approval elevato, fail-closed, nessuna automazione |

---

## 4. Ordine decisionale

Il selettore applica priorita' prudente:

1. L4 o keyword high-risk -> `high-risk`.
2. fase finale/post-merge -> `final-main`.
3. L3 o intento publish -> `publish`.
4. file core motore -> `motor-core`.
5. solo documentazione -> `docs-only`.
6. codice/test circoscritti -> `code-unit`.
7. input vuoto, ambiguo o non riconosciuto -> `high-risk` fail-closed.

Il path `scripts/asf_publish_step.ps1` e' trattato come `motor-core` quando viene modificato. Il profilo `publish` riguarda invece l'intento operativo di pubblicazione.

---

## 5. Output

Ogni raccomandazione contiene:

- `profile`;
- `risk_level`;
- `confidence`;
- `recommended_checks`;
- `skipped_checks`;
- `required_checks`;
- `optional_checks`;
- `reasons`;
- `warnings`;
- `estimated_cost`;
- `safety_notes`;
- `fail_closed`;
- `recommended_next_action`.

`estimated_cost` usa valori qualitativi: `low`, `medium`, `high`.

---

## 6. CLI

JSON:

```powershell
python scripts/asf_verification_profile_selector.py --risk-level L2 --changed-files scripts/asf_gate_decision_report.py tests/unit/test_asf_gate_decision_report.py --json
```

Markdown:

```powershell
python scripts/asf_verification_profile_selector.py --input-file examples/verification_profiles/sample_motor_core.json --markdown
```

Input JSON:

```powershell
python scripts/asf_verification_profile_selector.py --input-file examples/verification_profiles/sample_docs_only.json --json
```

Se nessun formato viene richiesto, lo script stampa un output testuale compatto.

---

## 7. Esempi

Esempi minimali:

```text
examples/verification_profiles/sample_docs_only.json
examples/verification_profiles/sample_code_unit.json
examples/verification_profiles/sample_motor_core.json
examples/verification_profiles/sample_publish.json
examples/verification_profiles/sample_final_main.json
examples/verification_profiles/sample_high_risk.json
examples/verification_profiles/sample_ambiguous_fail_closed.json
```

Gli esempi sono piccoli e usati dai test automatici.

---

## 8. Test Cost Policy

La policy distingue ridondanza utile da ridondanza costosa.

Ridondanze da evitare:

- lanciare Phase A separata quando Phase B del runner 0590 la riesegue gia';
- ripetere manualmente check gia' definiti nella config di publish;
- lanciare full pytest per docs-only ordinarie senza modifiche a documenti indicizzati o workflow behavior.

Verifiche che restano indispensabili:

- `git --no-pager diff --check` prima del report finale;
- test mirati per codice modificato;
- full pytest per `motor-core`;
- workflow health quando cambiano script o documenti indicizzati;
- verify gate e Phase C nelle verifiche finali su `main`;
- approval esplicita per publish e approval elevato per high-risk.

La riduzione tempi e' ammessa solo per `docs-only` e `code-unit` chiari. `motor-core`, `publish`, `final-main` e `high-risk` restano profili conservativi.

---

## 9. Relazione con Gate Decision Report

Lo STEP 0630 non modifica direttamente `scripts/asf_gate_decision_report.py`.

Motivo: il selector e' appena introdotto e deve prima stabilizzarsi come componente separato. Il Gate Decision Report puo' in futuro includere la raccomandazione del verification profile, consumando l'output del selector senza copiarne le regole.

Collegamento previsto:

- il risk report 0600/0610 continua a fornire `risk_level`;
- il Gate Decision Report 0620 continua a produrre decisione umana;
- il selector 0630 propone il profilo di verifica e il costo;
- il publish runner 0590 potra' usare la raccomandazione in uno step successivo, mantenendo fail-closed e human gate.

---

## 10. Workflow Health

`scripts/check_workflow_health.py` riconosce:

- script del selector;
- runbook 0630;
- test dedicati;
- esempi JSON.

Il controllo resta statico e read-only. Non esegue test pesanti e non effettua publish o side effect.

---

## 11. Non azioni

Il selector:

- non esegue test;
- non modifica repository target;
- non chiama provider esterni;
- non legge secret;
- non esegue publish;
- non fa commit, push, PR, merge o deploy;
- non sostituisce review umana, Gate Decision Report o publish runner.

---

## 12. Verifica

Test mirati:

```powershell
python -m pytest tests/unit/test_asf_verification_profile_selector.py -q
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

## 13. Stato dopo STEP 0640

Lo STEP 0640 ha integrato il selector nel Publish Runner:

```text
scripts/asf_publish_step.ps1
docs/motor/0640_VERIFICATION_PROFILE_INTEGRATION_PUBLISH_RUNNER.md
examples/publish_step/0640_publish_config_*.example.json
```

La logica profili resta in questo selector. Il runner la usa per validare config esplicite e bloccare profili dichiarati piu' leggeri della raccomandazione.

## 14. Stato dopo STEP 0650

Lo STEP 0650 ha introdotto il Publish Config Generator:

```text
scripts/asf_publish_config_generator.py
docs/motor/0650_VERIFICATION_PROFILE_DRIVEN_PUBLISH_CONFIG_GENERATOR.md
examples/publish_config_generator/
```

Il generator consuma il selector senza copiarne la logica completa. Per prudenza, `scripts/asf_publish_config_generator.py` e' classificato come `motor-core`, perche' influenza le config usate dal Publish Runner.

## 15. Stato dopo STEP 0660

Il selector resta la fonte deterministica della raccomandazione profilo.

Lo STEP 0660 ha aggiunto al Publish Config Generator un Bridge audit dedicato con `LAST-Publish_Config.json` e validazione `-Phase Plan` opt-in.

Il prossimo step consigliato e':

```text
0670) Step Execution State Machine
```

## 16. Stato dopo STEP 0945

Lo STEP 0945 mantiene i profili legacy ma aggiunge un layer adattivo per il supervised loop:

- `LIGHT`;
- `STANDARD`;
- `FULL`;
- `ESCALATED`.

Il JSON ora include anche `selected_profile`, `required_commands`, `optional_commands`, `skipped_commands`, `rationale`, `escalation_reasons`, `full_required` e `stop_reasons`.

`FULL` resta obbligatorio per Phase C, milestone, modifiche runner/core/test/API/security, retry sospetti e rischio alto. `ESCALATED` blocca o chiede Alberto quando il rischio, lo scope o la causa non sono chiari.
