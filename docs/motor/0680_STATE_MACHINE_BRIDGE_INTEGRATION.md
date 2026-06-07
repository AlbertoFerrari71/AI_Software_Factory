# 0680 - State Machine Bridge Integration

## 1. Scopo

Lo STEP 0680 estende la Step Execution State Machine con output Bridge opzionale.

La state machine resta un componente dichiarativo: valida eventi, aggiorna lo stato e produce report, ma non esegue pubblicazione.

Obiettivi:

- rendere recuperabile lo stato corrente dello step tra ChatGPT, Codex e PowerShell;
- scrivere un audit trail consultabile nel Bridge ASF;
- produrre output compatto e completo per review operativa;
- mantenere compatibile `--state-file`;
- non eseguire Phase B, Phase C, commit, push, PR, merge o deploy.

---

## 2. Separazione Bridge

Le cartelle Bridge restano separate per evitare confusione tra prompt, config, comandi e stato:

```text
codex_command  -> prompt Codex
pwsh_command   -> output del publish runner
publish_config -> output del Publish Config Generator
state_machine  -> stato e report della Step Execution State Machine
```

Bridge consigliato per la state machine:

```text
D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\state_machine
```

I test usano solo directory temporanee e non dipendono dal Bridge reale.

---

## 3. CLI

Modalita' legacy invariata:

```powershell
python scripts/asf_step_state_machine.py --step 0680 --event prompt_saved --state-file tmp/state_machine/0680_state.json --json
```

Output Bridge:

```powershell
python scripts/asf_step_state_machine.py --step 0680 --event prompt_saved --write-bridge --bridge-root "D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\state_machine" --markdown
```

Bridge con root temporanea:

```powershell
python scripts/asf_step_state_machine.py --step 0680 --event phase_c_failed --write-bridge --bridge-root tmp/state_machine_bridge --json
```

Metadati opzionali:

```powershell
python scripts/asf_step_state_machine.py --step 0680 --event prompt_saved --write-bridge --step-title "State Machine Bridge Integration" --next-step "0690) State Machine Integration with Publish Config Generator"
```

---

## 4. File prodotti

Con `--write-bridge`, lo script produce file progressivi per lo step e file `LAST-*`:

```text
NNNN-State_<nome>.json
NNNN-Event_<nome>.json
NNNN-Output_Compatto_<nome>.md
NNNN-Output_Completo_<nome>.txt
LAST-State.json
LAST-Event.json
LAST-Output_Compatto.md
LAST-Output_Completo.txt
```

Esempio per STEP 0680:

```text
0680-State_step_0680.json
0680-Event_step_0680.json
0680-Output_Compatto_step_0680.md
0680-Output_Completo_step_0680.txt
```

Non vengono prodotti DOCX nello STEP 0680.

---

## 5. Compatibilita' state file

`--state-file` resta la persistenza primaria locale quando viene indicato:

```text
tmp/state_machine/0680_state.json
```

Se `--write-bridge` e' attivo e `--state-file` non viene passato, lo script usa:

```text
<bridge-root>\LAST-State.json
```

Questo permette di riprendere lo stato corrente dal Bridge senza creare una seconda state machine.

Se `--write-bridge` non e' attivo, il comportamento 0670 resta invariato.

---

## 6. Contenuto Bridge

`LAST-State.json` contiene almeno:

- `step`;
- `current_state`;
- `last_event`;
- `last_update`;
- `history`;
- `warnings`;
- `blockers`;
- `recommended_next_action`;
- `fail_closed`;
- `step_title`;
- `next_step`;
- `source`;
- `state_file`;
- `bridge_root`.

`LAST-Event.json` contiene almeno:

- `step`;
- `event`;
- `from_state`;
- `to_state`;
- `allowed`;
- `fail_closed`;
- `timestamp`;
- `reasons`;
- `warnings`;
- `required_gates`;
- `missing_gates`.

`LAST-Output_Compatto.md` contiene riepilogo leggibile, warning/blocker, prossima azione e puntatori a `LAST-State.json` e `LAST-Output_Completo.txt`.

`LAST-Output_Completo.txt` contiene input normalizzato, stato precedente, evento, stato successivo, history completa, warning, blocker, file Bridge scritti e nota di sicurezza.

---

## 7. Clipboard

Lo STEP 0680 non implementa copia automatica cross-platform.

Il Markdown compatto include il comando manuale sicuro:

```powershell
Get-Content -Path "<LAST-Output_Compatto.md>" -Raw | Set-Clipboard
```

Non usare `Set-Clipboard -Path`.

---

## 8. Guardrail

La state machine con Bridge non esegue:

- Phase B;
- Phase C;
- commit;
- push;
- PR;
- merge;
- deploy;
- chiamate GitHub;
- chiamate OpenAI/API esterne.

Transizioni incoerenti e stato ambiguo continuano a fallire chiusi. In modalita' Bridge vengono comunque scritti `LAST-Event.json` e output di diagnosi fail-closed.

---

## 9. Verifica

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

Smoke Bridge temporaneo:

```powershell
python scripts/asf_step_state_machine.py --step 0680 --event prompt_saved --write-bridge --bridge-root tmp/state_machine_bridge --json
python scripts/asf_step_state_machine.py --step 0680 --event phase_c_started --write-bridge --bridge-root tmp/state_machine_bridge_invalid --json
```

---

## 10. Prossimo step

Prossimo step consigliato:

```text
0690) State Machine Integration with Publish Config Generator
```

Motivo: dopo STEP 0680 lo stato e' persistente nel Bridge. Il passo successivo piu' utile e' far dialogare generator e state machine, senza ancora aggiungere hook automatici al publish runner.
