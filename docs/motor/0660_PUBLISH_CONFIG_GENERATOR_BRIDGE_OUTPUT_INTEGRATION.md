# 0660 - Publish Config Generator Bridge Output Integration

## 1. Scopo

Lo STEP 0660 estende il Publish Config Generator dello STEP 0650 con un output Bridge dedicato e auditabile.

Il generator resta un componente di preparazione: produce config e riepiloghi, ma non esegue Phase B, Phase C, commit, push, PR, merge o deploy.

---

## 2. Separazione Bridge

Il Bridge del generator e' separato dal Bridge del publish runner:

```text
D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\publish_config
```

Il runner continua a usare il proprio Bridge operativo:

```text
D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\pwsh_command
```

La state machine usa un Bridge separato introdotto dopo STEP 0680:

```text
D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\state_machine
```

Questa separazione evita di mischiare:

- prompt Codex salvati in `codex_command`;
- audit della generazione config;
- stato corrente dello step;
- output del publish runner;
- comandi effettivi Phase B/Phase C.

---

## 3. CLI

Legacy `--out-dir` invariato:

```powershell
python scripts/asf_publish_config_generator.py --input-file examples/publish_config_generator/sample_motor_core_input.json --out-dir tmp/publish_config --json
```

Output Bridge dedicato:

```powershell
python scripts/asf_publish_config_generator.py --input-file examples/publish_config_generator/sample_bridge_output_input.json --write-bridge --bridge-root "D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\publish_config" --validate-plan
```

Quando `--write-bridge` e' attivo, `--bridge-root` indica il Bridge audit del generator.
Per impostare il Bridge che verra' scritto dentro la config del runner usare:

```powershell
--runner-bridge-root "<path>"
```

Se `--write-bridge` non e' attivo, `--bridge-root` resta compatibile con la CLI 0650 e continua a impostare il campo `bridge_root` della config generata.

---

## 4. File prodotti

Con `--write-bridge`, il generator crea artifact progressivi `step-II` e file `LAST-*`:

```text
0660-01-Richiesta_Generazione_<nome>.txt
0660-01-Publish_Config_<nome>.json
0660-01-Output_Compatto_<nome>.md
0660-01-Output_Completo_<nome>.txt
LAST-Richiesta_Generazione.txt
LAST-Publish_Config.json
LAST-Output_Compatto.md
LAST-Output_Completo.txt
```

Non vengono prodotti DOCX nello STEP 0660. Il formato Markdown e testo e' sufficiente per audit, copia e review.

---

## 5. Contenuto operativo

`LAST-Richiesta_Generazione.txt` contiene:

- step;
- name;
- risk level;
- verification profile;
- expected files;
- next step;
- timestamp;
- comando generator;
- nota di sicurezza.

`LAST-Publish_Config.json` contiene la config effettiva pronta per:

```text
scripts/asf_publish_step.ps1
```

`LAST-Output_Compatto.md` contiene i comandi corti consigliati:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\asf_publish_step.ps1 -Config "<path-config>" -Phase B -ApprovePublish
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\asf_publish_step.ps1 -Config "<path-config>" -Phase C -PrNumber <PR_NUMBER> -ApproveMerge
```

`LAST-Output_Completo.txt` contiene input normalizzato, profilo selezionato, check generati, config, warning, validazione Plan e path scritti.

---

## 6. Validazione Plan

Con `--validate-plan`, il generator invoca solo:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\asf_publish_step.ps1 -Config "<path-config>" -Phase Plan
```

La validazione Plan:

- non usa Phase B;
- non usa Phase C;
- non richiede `-ApprovePublish`;
- non richiede `-ApproveMerge`;
- non apre PR;
- non fa merge.

Se Plan fallisce, il generator esce con errore non-zero e il Bridge output indica chiaramente il fallimento.

Se `--validate-plan` non e' usato, l'output completo indica:

```text
Plan validation not executed.
```

---

## 7. Clipboard

`--copy-compact-to-clipboard` prova a copiare `LAST-Output_Compatto.md` usando PowerShell senza dipendenze esterne.

Se la copia fallisce, gli artifact restano validi e il warning viene riportato nell'output JSON/stdout.

Comando manuale equivalente:

```powershell
Get-Content -Path "<LAST-Output_Compatto.md>" -Raw | Set-Clipboard
```

---

## 8. Guardrail

Lo STEP 0660 non cambia il publish runner e non concede autorizzazioni operative.

Restano manuali e human-gated:

- review della config;
- Phase B con `-ApprovePublish`;
- inserimento del numero PR;
- Phase C con `-ApproveMerge`;
- pubblicazione GitHub tramite runner standard.

---

## 9. Verifica

Check mirati:

```powershell
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

## 10. Stato successivo

Lo STEP 0670 ha aggiunto la Step Execution State Machine locale per modellare stati, transizioni e recovery del ciclo step.

Lo STEP 0680 ha aggiunto l'output Bridge della state machine in `state_machine`, con `LAST-State.json`, `LAST-Event.json`, output compatto e output completo.

Prossimo step consigliato dopo 0680:

```text
0690) State Machine Integration with Publish Config Generator
```

Motivo: dopo STEP 0660 il generator lascia un pacchetto Bridge ordinato e riusabile, e dopo STEP 0680 lo stato step e' persistente nel Bridge. Il prossimo collo di bottiglia e' collegare i due componenti senza rendere automatica la pubblicazione.
