# 0650 - Verification Profile Driven Publish Config Generator

## 1. Scopo

Lo STEP 0650 introduce un generatore locale di bozze config JSON per:

```text
scripts/asf_publish_step.ps1
```

Il generatore usa il Verification Profile Selector dello STEP 0630 per scegliere un profilo prudente e tradurlo in check `phase_a_checks` e `phase_c_checks` compatibili con il Publish Runner 0590/0640.

Il generatore non esegue il runner e non esegue azioni di pubblicazione. Produce solo:

- una config JSON da revisionare;
- un riepilogo Markdown;
- un output JSON su stdout quando richiesto.

---

## 2. Script

```text
scripts/asf_publish_config_generator.py
```

Lo script e' deterministico, standard-library only e usa il selector locale tramite import sicuro da file.

---

## 3. Input

Input JSON minimo:

```text
step
name
branch
commit_message
pr_title
pr_body
next_step
expected_files
risk_level
verification_phase
intent
provided_gates
allow_profile_check_reduction
```

Campi opzionali:

```text
repo_path
bridge_root
changed_files
checks_already_run
profile_selector_expected_profile
log_max_count
allow_no_github_checks_reported
```

Se un input JSON manca di campi essenziali, lo script fallisce chiuso e non scrive una config apparentemente valida.

La CLI diretta puo' derivare branch, commit message, titolo PR, corpo PR e intent da `--step` e `--name` per smoke locali semplici. L'input JSON resta la forma consigliata per pubblicazioni reali.

---

## 4. Output

Default:

```text
tmp/publish_config/<step>_publish_config.json
tmp/publish_config/<step>_publish_config_summary.md
```

Con `--out-dir`, i file vengono scritti nella directory indicata.

Da STEP 0660 il comportamento legacy resta invariato se `--write-bridge` non viene usato.
Con `--write-bridge`, il generator scrive anche un pacchetto audit dedicato nel Bridge `publish_config`:

```text
NNNN-II-Richiesta_Generazione_<nome>.txt
NNNN-II-Publish_Config_<nome>.json
NNNN-II-Output_Compatto_<nome>.md
NNNN-II-Output_Completo_<nome>.txt
LAST-Richiesta_Generazione.txt
LAST-Publish_Config.json
LAST-Output_Compatto.md
LAST-Output_Completo.txt
```

Il Bridge `publish_config` e' separato dal Bridge `pwsh_command` del runner.

La config generata include i campi richiesti dal runner:

```text
step
name
repo_path
bridge_root
branch
commit_message
pr_title
pr_body
next_step
expected_files
phase_a_checks
phase_c_checks
allow_no_github_checks_reported
log_max_count
```

Quando il runner 0640 supporta i profili, include anche:

```text
verification_profile
risk_level
changed_files
verification_phase
allow_profile_check_reduction
profile_selector_expected_profile
intent
checks_already_run
provided_gates
```

---

## 5. Regole profilo

Il selector resta la fonte della raccomandazione. Il generatore non copia la classifica completa dei profili.

Regole locali del generatore:

- se il selector restituisce `fail_closed: true`, la config ordinaria non viene prodotta;
- `high-risk` non produce config publish ordinaria;
- `final-main` non produce config Phase B ordinaria;
- L4 blocca la generazione;
- `allow_profile_check_reduction` e' accettato solo per `docs-only` e `code-unit`;
- Phase C contiene sempre full pytest, workflow health e verify gate.

Il nuovo script `scripts/asf_publish_config_generator.py` e' trattato dal selector come `motor-core`, perche' influenza la preparazione delle config publish.

---

## 6. Check generati

### docs-only

Phase A:

- workflow health per documenti indicizzati o `docs/motor/`;
- nessun full pytest automatico.

Phase C:

- full pytest;
- workflow health;
- verify gate.

### code-unit

Phase A:

- test mirati dedotti da file o test modificati;
- workflow health se sono coinvolti documenti indicizzati;
- verify gate se non si riesce a dedurre un test mirato per codice.

Phase C:

- full pytest;
- workflow health;
- verify gate.

### motor-core

Phase A:

- test mirati del componente;
- regressioni collegate per selector e publish runner;
- workflow health;
- verify gate.

Phase C:

- full pytest;
- workflow health;
- verify gate.

### publish

Il profilo `publish` puo' essere usato solo se il selector non fallisce chiuso, quindi con gate dichiarati coerenti.

Phase A:

- workflow health;
- test runner se il runner o il generator sono coinvolti;
- verify gate.

Phase C resta completa.

---

## 7. Deduzione test mirati

Mappature principali:

```text
scripts/asf_publish_config_generator.py -> tests/unit/test_asf_publish_config_generator.py
scripts/asf_verification_profile_selector.py -> tests/unit/test_asf_verification_profile_selector.py
scripts/asf_gate_decision_report.py -> tests/unit/test_asf_gate_decision_report.py
scripts/asf_dry_run_loop_runner.py -> tests/unit/test_asf_dry_run_loop_runner.py
scripts/asf_risk_classifier.py -> tests/unit/test_asf_risk_classifier.py
scripts/asf_publish_step.ps1 -> tests/unit/test_asf_publish_step_runner.py
```

Se lo script non deduce un test mirato per un file di codice, lascia un warning nel riepilogo e mantiene `verify.ps1` in Phase A.

---

## 8. CLI

Da input JSON:

```powershell
python scripts/asf_publish_config_generator.py --input-file examples/publish_config_generator/sample_motor_core_input.json --out-dir tmp/publish_config --json
```

Con output Bridge e validazione Plan:

```powershell
python scripts/asf_publish_config_generator.py --input-file examples/publish_config_generator/sample_bridge_output_input.json --write-bridge --bridge-root "D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\publish_config" --validate-plan
```

Da argomenti CLI con metadati derivati:

```powershell
python scripts/asf_publish_config_generator.py --step 0650 --name Verification_Profile_Driven_Publish_Config_Generator --risk-level L2 --verification-phase local --expected-files scripts/asf_publish_config_generator.py tests/unit/test_asf_publish_config_generator.py --out-dir tmp/publish_config --json
```

Per una fase `publish`, dichiarare i gate solo quando sono stati realmente forniti. Anche in quel caso il runner richiede ancora i flag espliciti nelle fasi operative.

---

## 9. Esempi

```text
examples/publish_config_generator/sample_docs_only_input.json
examples/publish_config_generator/sample_code_unit_input.json
examples/publish_config_generator/sample_motor_core_input.json
examples/publish_config_generator/sample_publish_runner_input.json
examples/publish_config_generator/sample_bridge_output_input.json
examples/publish_config_generator/sample_high_risk_fail_closed_input.json
examples/publish_config_generator/sample_missing_required_fields_fail_closed_input.json
```

I due esempi fail-closed sono intenzionali e non devono produrre config valide.

---

## 10. Uso con il Publish Runner

Smoke Plan:

```powershell
python scripts/asf_publish_config_generator.py --input-file examples/publish_config_generator/sample_motor_core_input.json --out-dir tmp/publish_config --json
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/asf_publish_step.ps1 -Config tmp/publish_config/0650_publish_config.json -Phase Plan
```

`-Phase Plan` valida la config e il profilo, ma non esegue Phase A/B/C.

Per pubblicare realmente, usare il runner standard con review umana e flag espliciti. Il generator non autorizza alcuna fase.

---

## 11. Workflow Health

`scripts/check_workflow_health.py` riconosce:

- script generator;
- test dedicato;
- runbook 0650;
- esempi JSON.

Il controllo resta statico e read-only.

---

## 12. Verifica

Test mirati:

```powershell
python -m pytest tests/unit/test_asf_publish_config_generator.py -q
python -m pytest tests/unit/test_asf_publish_step_runner.py -q
python -m pytest tests/unit/test_asf_verification_profile_selector.py -q
```

Gate repository:

```powershell
python -m pytest -q
python scripts/check_workflow_health.py
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git --no-pager diff --check
git status --short --untracked-files=all
```

---

## 13. Prossimo step

```text
0670) Step Execution State Machine
```

Motivo: con STEP 0660 il generator produce anche artifact Bridge auditabili. Il passo successivo naturale e' modellare stati, transizioni e stop condition dello step loop prima di aumentare l'automazione operativa.

---

## 14. Aggiornamento dopo STEP 0690

Dopo STEP 0690 il comportamento legacy del generator resta invariato senza opzioni state machine.

Quando vengono usati `--require-state` o `--update-state`, il generator consulta `scripts/asf_step_state_machine.py`, richiede uno stato coerente e puo' applicare `publish_config_generated` per portare lo step da `LOCAL_VERIFIED` a `READY_TO_PUBLISH`.

Il runbook operativo aggiornato e':

```text
docs/motor/0690_STATE_MACHINE_INTEGRATION_WITH_PUBLISH_CONFIG_GENERATOR.md
```
