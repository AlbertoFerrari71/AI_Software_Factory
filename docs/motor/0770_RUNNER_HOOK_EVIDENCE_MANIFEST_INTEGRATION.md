# 0770 - Runner Hook Evidence Manifest Integration

## 1. Scopo

Lo STEP 0770 collega gli output degli hook del publish runner alla sezione
manifest/evidence del Motore ASF.

Script coinvolto:

```text
scripts/asf_motor_run_manifest.py
```

Lo step estende il manifest 0710 con una sezione `runner_hooks` che legge in
modo read-only lo state file prodotto da `scripts/asf_step_state_machine.py`
quando il runner 0750 emette eventi durante Phase B e Phase C.

Il publish runner non viene modificato in questo step.

## 2. CLI

Opzioni aggiunte al manifest:

```text
--include-runner-hooks
--state-file
--state-bridge-root
--publish-runner-output
--publish-config
--require-closed-state
--expected-step
--expected-final-state
--expected-events
```

Esempio positivo:

```powershell
python scripts/asf_motor_run_manifest.py `
  --input-file examples/motor_run_manifest/sample_manifest_input_runner_hooks_closed.json `
  --out-dir tmp/motor_run_manifest_0770_closed `
  --include-runner-hooks `
  --state-file examples/state_machine/sample_closed_with_runner_hooks_state.json `
  --expected-step 0770-sample `
  --expected-final-state CLOSED `
  --expected-events phase_b_started phase_b_passed pr_created phase_c_started phase_c_passed main_verified close_step
```

Il comando genera solo manifest e summary: no Phase B, no Phase C,
no commit, no push, no PR, no merge e no deploy.

## 3. Sezione runner_hooks

Quando `--include-runner-hooks` e' attivo, il manifest include:

```json
{
  "runner_hooks": {
    "enabled": true,
    "state_file": "...",
    "state_bridge_root": "...",
    "publish_runner_output": "...",
    "publish_config": "...",
    "state_step": "0770-sample",
    "expected_step": "0770-sample",
    "final_state": "CLOSED",
    "expected_final_state": "CLOSED",
    "last_event": "close_step",
    "events": [
      "phase_b_started",
      "phase_b_passed",
      "pr_created",
      "phase_c_started",
      "phase_c_passed",
      "main_verified",
      "close_step"
    ],
    "expected_events": [
      "phase_b_started",
      "phase_b_passed",
      "pr_created",
      "phase_c_started",
      "phase_c_passed",
      "main_verified",
      "close_step"
    ],
    "required_events_present": true,
    "missing_events": [],
    "bridge_files": [],
    "warnings": [],
    "blockers": [],
    "fail_closed": false,
    "decision_impact": "CLOSED"
  }
}
```

La sezione usa `history`, `current_state`, `last_event`, `bridge_root`,
`state_file` e `bridge_files` dello state file. Non ricalcola le transizioni
della state machine.

## 4. Decision policy

La policy resta prudente:

- state file mancante: decisione `INCOMPLETE`;
- state file non JSON o non oggetto: decisione `FAIL_CLOSED`;
- `--expected-step` diverso dallo step nello state file: decisione
  `FAIL_CLOSED`;
- `--expected-final-state` diverso da `current_state`: decisione
  `FAIL_CLOSED`;
- eventi richiesti da `--expected-events` mancanti: decisione `INCOMPLETE`;
- final state `CLOSED` con eventi richiesti presenti: decisione `CLOSED`;
- final state `PUBLISHED` con eventi richiesti presenti: decisione
  `PUBLISHED_VERIFIED`;
- final state `READY_TO_PUBLISH` con eventi coerenti: decisione
  `READY_TO_PUBLISH`.

Il manifest non produce successo pieno quando gli hook sono dichiarati ma
incompleti.

## 5. Bridge output

Se `--write-bridge` e' attivo, i file Bridge del manifest includono anche la
sezione `runner_hooks` nel JSON, nel Markdown e nell'output completo:

```text
LAST-Run_Manifest.json
LAST-Run_Summary.md
LAST-Output_Completo.txt
```

Il summary riporta:

- final state;
- last event;
- eventi trovati;
- eventi mancanti;
- state file;
- state bridge root;
- publish runner output;
- publish config;
- decisione finale.

I test usano solo Bridge temporanei sotto `tmp_path`; non richiedono Dropbox
reale.

## 6. Esempi

Input manifest:

```text
examples/motor_run_manifest/sample_manifest_input_runner_hooks_closed.json
examples/motor_run_manifest/sample_manifest_input_runner_hooks_missing_event.json
examples/motor_run_manifest/sample_manifest_input_runner_hooks_step_mismatch.json
```

State file sintetico:

```text
examples/state_machine/sample_closed_with_runner_hooks_state.json
```

Gli esempi sono piccoli e locali. I campi `runner_hook_options` sono descrittivi:
le opzioni effettive restano passate alla CLI per evitare side effect impliciti.

## 7. Guardrail

Lo STEP 0770:

- non modifica `scripts/asf_publish_step.ps1`;
- non esegue Phase B;
- non esegue Phase C;
- non chiama GitHub reale;
- non richiede Dropbox reale nei test;
- non fa commit, push, PR, merge o deploy;
- non introduce dipendenze runtime;
- non chiama OpenAI/API esterne.

`publication_actions_executed`, `phase_b_executed` e `phase_c_executed` nel
manifest restano `false`: il manifest osserva eventi gia' prodotti, ma non li
esegue.

## 8. Test

Test dedicato:

```powershell
python -m pytest tests/unit/test_asf_motor_run_manifest.py -q
```

Regressioni consigliate:

```powershell
python -m pytest tests/unit/test_asf_step_state_machine.py -q
python -m pytest tests/unit/test_asf_publish_step_runner.py -q
python scripts/check_workflow_health.py
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify.ps1
```

## 9. Valore operativo

Prima dello STEP 0770, lo STEP 0760 dimostrava che gli hook potevano aggiornare
la state machine, ma il manifest non raccoglieva direttamente quella traccia.

Dopo STEP 0770 diventa auditabile:

- quali eventi runner sono stati osservati;
- quale final state ha prodotto la state machine;
- se gli eventi attesi sono completi;
- dove si trovano state file, Bridge state machine, publish runner output e
  publish config;
- se una pubblicazione human-gated ha chiuso lo step in modo coerente.

Restano manuali approval Phase B, approval Phase C, pubblicazione, merge,
verifica finale su `main` e decisione umana.

## 10. Prossimo step consigliato

```text
0780) MVP Real Step Pilot 3 with Manifest Hooks
```

Motivo: ora che il manifest puo' leggere gli hook, conviene provarlo su una
pubblicazione reale piccola e human-gated, senza aggiungere nuove automazioni.

## 11. Aggiornamento STEP 0780

Lo STEP 0780 prepara il pilot consigliato:

```text
docs/motor/0780_MVP_REAL_STEP_PILOT_3_WITH_MANIFEST_HOOKS.md
```

Il pilot documenta state file iniziale `READY_TO_PUBLISH`, config publish con
hook state machine, eventi attesi fino a `close_step` e manifest post-publish
con `--include-runner-hooks`, `--expected-final-state CLOSED` e
`--expected-events`.

La decisione prudente resta:

```text
PILOT STATUS: GO WITH WARNINGS
```

Il prossimo passo consigliato diventa:

```text
0790) Post-MVP Roadmap and Hardening Plan
```
