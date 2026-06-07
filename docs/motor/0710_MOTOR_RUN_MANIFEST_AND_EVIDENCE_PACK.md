# 0710 - Motor Run Manifest and Evidence Pack

## 1. Scopo

Lo STEP 0710 introduce un manifest unico per le run del Motore ASF.

Script dedicato:

```text
scripts/asf_motor_run_manifest.py
```

Il manifest normalizza gli artifact prodotti dallo smoke 0700 e da input JSON esterni in due output locali:

- `motor_run_manifest.json`;
- `motor_run_summary.md`.

Il tool e' locale, standard-library only e non esegue pubblicazione.

## 2. Schema

Campi principali:

- `schema_version`;
- `run_id`;
- `created_at`;
- `step`;
- `scenario`;
- `source`;
- `status`;
- `decision`;
- `risk`;
- `gate`;
- `verification_profile`;
- `state`;
- `publish_config`;
- `artifacts`;
- `checks`;
- `warnings`;
- `blockers`;
- `recommended_next_action`;
- `fail_closed`;
- `human_summary`;
- `machine_readable`.

Ogni artifact include nome, path, tipo, esistenza, dimensione, checksum `sha256` quando il file esiste, obbligatorieta' e descrizione.

Ogni check include nome, stato, comando, exit code quando disponibile, obbligatorieta' e descrizione.

## 3. Da directory evidence

Esempio su evidence 0700:

```powershell
python scripts/asf_motor_run_manifest.py --evidence-dir tmp/e2e_mvp_smoke --step 0700-smoke --scenario code-unit-to-ready-to-publish --out-dir tmp/motor_run_manifest --json
```

Artifact noti:

- `input_step.json`;
- `risk_report.json`;
- `dry_run_report.json`;
- `gate_decision_packet.json`;
- `verification_profile.json`;
- `publish_config.json`;
- `state_before.json`;
- `state_after.json`;
- `evidence_summary.md`;
- `evidence_summary.json`;
- `negative_fail_closed.json`.

Nel percorso positivo sono richiesti gli artifact minimi necessari per giustificare `READY_TO_PUBLISH`, incluso `publish_config.json`.

Nel percorso negativo sono richiesti `input_step.json`, `state_before.json`, `state_after.json` e `negative_fail_closed.json`.

## 4. Da input JSON

Esempio:

```powershell
python scripts/asf_motor_run_manifest.py --input-file examples/motor_run_manifest/sample_manifest_input_ready.json --out-dir tmp/motor_run_manifest --markdown
```

Esempi versionati:

- `examples/motor_run_manifest/sample_manifest_input_ready.json`;
- `examples/motor_run_manifest/sample_manifest_input_fail_closed.json`;
- `examples/motor_run_manifest/sample_manifest_input_missing_artifacts.json`.

## 5. Decisione prudente

La decisione viene calcolata con priorita' fail-closed:

1. `FAIL_CLOSED` se l'input dichiara fail-closed o lo scenario negativo lo osserva.
2. `BLOCKED` se esistono blocker.
3. `INCOMPLETE` se artifact richiesti o check richiesti mancano/non passano.
4. `READY_TO_PUBLISH` solo se la run e' coerente e non mancano evidence minime.
5. `REVIEW_REQUIRED` per input validi ma non conclusivi.

Il tool non promuove mai una run a `READY_TO_PUBLISH` se un artifact richiesto manca.

## 6. Output Bridge opzionale

Il Bridge si scrive solo con `--write-bridge`.

Default consigliato:

```text
D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\motor_run
```

Output:

- `0710-Run_Manifest_<run>.json`;
- `0710-Run_Summary_<run>.md`;
- `0710-Output_Completo_<run>.txt`;
- `LAST-Run_Manifest.json`;
- `LAST-Run_Summary.md`;
- `LAST-Output_Completo.txt`.

I test usano sempre directory temporanee e non richiedono Dropbox reale.

## 7. Guardrail

Il manifest non esegue:

- Phase B;
- Phase C;
- commit;
- push;
- pull request;
- merge;
- deploy;
- operazioni GitHub;
- chiamate OpenAI/API esterne.

Lo script legge artifact, calcola checksum e scrive output locali/Bridge opzionali.

## 8. Test

Test dedicato:

```powershell
python -m pytest tests/unit/test_asf_motor_run_manifest.py -q
```

Regressioni consigliate:

```powershell
python -m pytest tests/unit/test_asf_e2e_mvp_smoke.py -q
python -m pytest tests/unit/test_asf_publish_config_generator.py -q
python -m pytest tests/unit/test_asf_step_state_machine.py -q
python -m pytest tests/unit/test_asf_verification_profile_selector.py -q
python scripts/check_workflow_health.py
```

## 9. Stato MVP

Lo STEP 0710 consolida lo smoke 0700 in un record auditabile e riusabile.

Restano simulati:

- file applicativi dello smoke;
- esito dei check dello scenario sintetico;
- review finale della config.

Restano human-gated:

- revisione del manifest;
- Phase B;
- Phase C;
- commit, push, PR, merge e verifica finale su `main`.

Per chiudere il MVP Motore serve ancora un runbook d'uso/closure che dica come usare insieme smoke, manifest, runner standard e report finale senza aggiungere pubblicazione automatica.

## 10. Prossimo step consigliato

0720) MVP Usage Runbook

Motivo: prima di aggiungere hook automatici al runner, conviene rendere chiaro il percorso manuale completo e human-gated dal run locale fino alla pubblicazione controllata.
