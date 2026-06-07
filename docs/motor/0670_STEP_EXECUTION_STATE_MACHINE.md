# 0670 - Step Execution State Machine

## 1. Scopo

Lo STEP 0670 aggiunge una macchina a stati locale per modellare l'avanzamento di uno step ASF.

La state machine risponde a tre domande operative:

- dove siamo nello step;
- se il prossimo evento e' ammesso;
- quali gate mancano prima di procedere.

Non sostituisce il publish runner e non esegue azioni operative.

---

## 2. File principali

```text
scripts/asf_step_state_machine.py
tests/unit/test_asf_step_state_machine.py
examples/state_machine/
```

La persistenza consigliata resta sotto `tmp/`, ad esempio:

```text
tmp/state_machine/0670_state.json
```

`tmp/` resta output operativo locale e ignorato da Git.

---

## 3. Stati supportati

Stati minimi:

- `PLANNED`
- `PROMPT_PREPARED`
- `CODEX_RUNNING`
- `IMPLEMENTED`
- `LOCAL_VERIFIED`
- `READY_TO_PUBLISH`
- `PUBLISHING`
- `PR_CREATED`
- `MERGING`
- `PUBLISHED`
- `CLOSED`
- `BLOCKED`
- `FAILED`
- `RECOVERY_REQUIRED`

Gli stati `FAILED`, `BLOCKED` e `RECOVERY_REQUIRED` non sono stati di successo. Servono a fermare il flusso e rendere esplicita la ripartenza.

---

## 4. Eventi supportati

Eventi minimi:

- `prompt_saved`
- `codex_started`
- `codex_completed`
- `local_checks_passed`
- `local_checks_failed`
- `publish_config_generated`
- `phase_b_started`
- `phase_b_passed`
- `phase_b_failed`
- `pr_created`
- `phase_c_started`
- `phase_c_passed`
- `phase_c_failed`
- `main_verified`
- `manual_block`
- `manual_unblock`
- `recovery_started`
- `recovery_completed`
- `close_step`

Gli eventi sono dichiarativi. La state machine non verifica GitHub, non legge PR remote e non avvia il runner.

---

## 5. Transizioni principali

Flusso ordinario:

```text
PLANNED -> PROMPT_PREPARED -> CODEX_RUNNING -> IMPLEMENTED -> LOCAL_VERIFIED
LOCAL_VERIFIED -> READY_TO_PUBLISH -> PUBLISHING -> PR_CREATED -> MERGING -> PUBLISHED -> CLOSED
```

Transizioni chiave:

- `PLANNED` + `prompt_saved` -> `PROMPT_PREPARED`
- `PROMPT_PREPARED` + `codex_started` -> `CODEX_RUNNING`
- `CODEX_RUNNING` + `codex_completed` -> `IMPLEMENTED`
- `IMPLEMENTED` + `local_checks_passed` -> `LOCAL_VERIFIED`
- `LOCAL_VERIFIED` + `publish_config_generated` -> `READY_TO_PUBLISH`
- `READY_TO_PUBLISH` + `phase_b_started` -> `PUBLISHING`
- `PUBLISHING` + `phase_b_passed` -> `PR_CREATED`
- `PR_CREATED` + `phase_c_started` -> `MERGING`
- `MERGING` + `phase_c_passed` -> `PUBLISHED`
- `PUBLISHED` + `main_verified` -> `CLOSED`

Fail-closed:

- `phase_c_started` senza `PR_CREATED` viene bloccato;
- `close_step` prima di `PUBLISHED` viene bloccato;
- `publish_config_generated` prima di `LOCAL_VERIFIED` viene bloccato;
- state file corrotto o ambiguo viene bloccato;
- mismatch dichiarato tra step/config o branch/expected branch suggerisce `RECOVERY_REQUIRED`.

---

## 6. Recovery

Fallimenti gestiti:

- `local_checks_failed` porta a `FAILED`;
- `phase_b_failed` da `PUBLISHING` porta a `RECOVERY_REQUIRED`;
- `phase_c_failed` da `MERGING` porta a `RECOVERY_REQUIRED`.

Ripartenza:

```powershell
python scripts/asf_step_state_machine.py --step 0670 --event recovery_started --state-file tmp/state_machine/0670_state.json --json
python scripts/asf_step_state_machine.py --step 0670 --event recovery_completed --target-state READY_TO_PUBLISH --state-file tmp/state_machine/0670_state.json --json
```

Se `recovery_completed` non riceve un `--target-state` sufficiente, lo stato resta `RECOVERY_REQUIRED`.

Step combinati come `0650-0660` sono rappresentabili, ma producono warning per ricordare che la recovery deve restare esplicita e revisionata.

---

## 7. CLI

Esempi:

```powershell
python scripts/asf_step_state_machine.py --step 0670 --event prompt_saved --state-file tmp/state_machine/0670_state.json --json
```

```powershell
python scripts/asf_step_state_machine.py --step 0670 --event codex_completed --state-file tmp/state_machine/0670_state.json --markdown
```

```powershell
python scripts/asf_step_state_machine.py --step 0670 --event phase_c_failed --state-file tmp/state_machine/0670_state.json --json
```

```powershell
python scripts/asf_step_state_machine.py --step 0650-0660 --event recovery_completed --target-state CLOSED --state-file tmp/state_machine/0650_0660_state.json --json
```

Se `--state-file` non esiste, lo script inizializza da `PLANNED`.

Se `--state-file` viene omesso, lo script usa:

```text
tmp/state_machine/<step>_state.json
```

---

## 8. Output

Lo script puo' generare:

- JSON machine-readable con `--json`;
- Markdown leggibile con `--markdown`;
- testo compatto come default.

Campi principali:

- `step`
- `current_state`
- `event`
- `next_state`
- `allowed`
- `fail_closed`
- `reasons`
- `warnings`
- `required_gates`
- `missing_gates`
- `recommended_next_action`
- `history`
- `machine_readable`

---

## 9. Persistenza

Lo state file contiene almeno:

- `step`;
- `current_state`;
- `history`;
- `timestamps`;
- `last_event`;
- `last_update`;
- `warnings`;
- `blockers`.

Uno state file corrotto non viene riparato automaticamente. Lo script produce output fail-closed e non avanza lo stato.

### Bridge dopo STEP 0680

Dopo STEP 0680 la state machine puo' scrivere una copia auditabile nel Bridge con:

```powershell
python scripts/asf_step_state_machine.py --step 0680 --event prompt_saved --write-bridge --bridge-root "D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\state_machine" --json
```

Con `--write-bridge` vengono prodotti `LAST-State.json`, `LAST-Event.json`, `LAST-Output_Compatto.md`, `LAST-Output_Completo.txt` e i corrispondenti file progressivi dello step.

Se `--state-file` e' omesso insieme a `--write-bridge`, lo state file usato e':

```text
<bridge-root>\LAST-State.json
```

---

## 10. Guardrail

La state machine non esegue:

- commit;
- push;
- PR;
- merge;
- deploy;
- Phase B;
- Phase C;
- chiamate OpenAI/API esterne;
- chiamate GitHub obbligatorie.

La state machine puo' solo leggere/scrivere il proprio file JSON e produrre report.

---

## 11. Caso 0650/0660

Nel caso 0650/0660 la state machine avrebbe reso visibile che:

- uno step era stato sviluppato sopra uno stato non ancora pubblicato;
- la config Phase C doveva corrispondere allo step reale;
- un fallimento Phase C doveva portare a `RECOVERY_REQUIRED`;
- la chiusura non doveva essere comunicata come completata prima della verifica finale;
- la recovery combinata doveva essere dichiarata come stato esplicito.

Resta manuale la verifica reale di branch, PR, merge e main. Lo STEP 0670 modella lo stato dichiarato; una futura integrazione potra' collegarlo a generator e runner.

---

## 12. Esempi

Esempi disponibili:

```text
examples/state_machine/sample_normal_flow_events.json
examples/state_machine/sample_phase_c_failed_recovery.json
examples/state_machine/sample_combined_recovery_step.json
examples/state_machine/sample_invalid_transition_fail_closed.json
```

---

## 13. Verifica

Check mirati:

```powershell
python -m pytest tests/unit/test_asf_step_state_machine.py -q
python -m pytest tests/unit/test_asf_publish_config_generator.py -q
python -m pytest tests/unit/test_asf_publish_step_runner.py -q
python -m pytest tests/unit/test_asf_verification_profile_selector.py -q
```

Gate repository:

```powershell
python -m pytest -q
python scripts/check_workflow_health.py
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify.ps1
git --no-pager diff --check
git status --short --untracked-files=all
```

---

## 14. Prossimo step

Prossimo step consigliato:

```text
0690) State Machine Integration with Publish Config Generator
```

Motivo: dopo STEP 0680 lo stato e' modellato e persistente nel Bridge. Il passo successivo piu' utile e' far generare al Publish Config Generator riferimenti coerenti alla state machine, senza ancora automatizzare Phase B o Phase C.
