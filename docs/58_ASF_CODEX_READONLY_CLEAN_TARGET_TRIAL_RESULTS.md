# ASF Codex Read-Only Clean Target Trial Results

## 1. Data e step

- Data: 2026-06-04
- Step: 440) ASF Codex Read-Only Invocation Clean Target Trial
- Branch ASF: `step-440-asf-codex-readonly-invocation-clean-target-trial`

---

## 2. Target temporaneo

Target temporaneo:

```text
tmp/asf_clean_target_trial/step_440/clean_repo
```

Contenuto sintetico:

- `README.md`;
- `docs/NOTES.md`.

La repo temporanea e' sotto `tmp/`, ignorata da Git, e non e' un repository target esterno.

Branch temporaneo:

```text
step-440-clean-target-trial
```

Working tree prima del trial:

```text
CLEAN
```

---

## 3. Approval gate

Comando usato:

```powershell
python scripts/asf_human_approval_gate.py --project-name ASF_Clean_Target_Trial --repo-path tmp/asf_clean_target_trial/step_440/clean_repo --step 440 --branch step-440-clean-target-trial --codex-report-intake tmp/asf_clean_target_trial/step_440/evidence/codex_report_intake.md --verification-pack tmp/asf_clean_target_trial/step_440/evidence/verification_pack.md --closure-pack tmp/asf_clean_target_trial/step_440/evidence/closure_pack.md --output-dir tmp/asf_clean_target_trial/step_440/approval_gate
```

Esito:

```text
Decision: GO
```

Il gate era GO perche' branch, working tree ed evidenze sintetiche erano coerenti.

---

## 4. Preview

Comando usato:

```powershell
python scripts/asf_codex_readonly_invoke.py --mode preview --project-name ASF_Clean_Target_Trial --repo-path tmp/asf_clean_target_trial/step_440/clean_repo --step 440 --branch step-440-clean-target-trial --handoff-path tmp/asf_clean_target_trial/step_440/handoff/codex_handoff.md --approval-gate tmp/asf_clean_target_trial/step_440/approval_gate/ASF_Clean_Target_Trial/step_440/human_approval_gate.md --output-dir tmp/asf_clean_target_trial/step_440/readonly_invocation
```

Esito:

- `readonly_invocation_preview.md` generato;
- `codex_readonly_command_preview.ps1` generato;
- Codex non eseguito in preview.

---

## 5. Execute-readonly

Stato:

```text
Tentato ed eseguito read-only
```

Condizioni presenti:

- comando `codex` disponibile;
- Human Approval Gate `GO`;
- repo temporanea `CLEAN`;
- conferma esplicita `YES_I_APPROVE_READONLY_CODEX_EXECUTION`;
- comando eseguito con `--sandbox read-only`;
- nessuna esecuzione workspace-write;
- nessun uso danger-full-access.

Comando usato:

```powershell
python scripts/asf_codex_readonly_invoke.py --mode execute-readonly --project-name ASF_Clean_Target_Trial --repo-path tmp/asf_clean_target_trial/step_440/clean_repo --step 440 --branch step-440-clean-target-trial --handoff-path tmp/asf_clean_target_trial/step_440/handoff/codex_handoff.md --approval-gate tmp/asf_clean_target_trial/step_440/approval_gate/ASF_Clean_Target_Trial/step_440/human_approval_gate.md --output-dir tmp/asf_clean_target_trial/step_440/readonly_invocation --confirm-readonly-execution YES_I_APPROVE_READONLY_CODEX_EXECUTION
```

Risultato:

- exit code: `0`;
- working tree dopo: `CLEAN`;
- nessuna modifica target;
- stdout presente;
- stderr presente.

Nota: prima dell'esito positivo sono stati corretti due problemi del prototipo:

- parsing del report Human Approval Gate completo con decisione `GO`;
- gestione UTF-8 esplicita per stdin/stdout/stderr della subprocess.

---

## 6. stdout, stderr, exit code

Path:

```text
tmp/asf_clean_target_trial/step_440/readonly_invocation/ASF_Clean_Target_Trial/step_440/
```

File generati:

- `stdout.txt`;
- `stderr.txt`;
- `exit_code.txt`;
- `codex_readonly_invocation_result.md`.

Sintesi stdout:

```text
Codex non ha completato l'ispezione per errore sandbox interno: windows sandbox: spawn setup refresh.
```

Sintesi stderr:

```text
Codex ha riportato sandbox read-only e ha registrato errori exec interni.
```

L'exit code era `0`, ma l'output non e' semanticamente completo.

---

## 7. Result capture

Comando usato:

```powershell
python scripts/asf_codex_result_capture.py --project-name ASF_Clean_Target_Trial --repo-path tmp/asf_clean_target_trial/step_440/clean_repo --step 440 --invocation-dir tmp/asf_clean_target_trial/step_440/readonly_invocation/ASF_Clean_Target_Trial/step_440 --output-dir tmp/asf_clean_target_trial/step_440/result_capture
```

Esito:

```text
Classification: PASS
```

Motivo: exit code `0` e working tree `CLEAN`. Il result capture resta meccanico; la valutazione semantica passa al safety gate.

---

## 8. Safety gate

Comando usato:

```powershell
python scripts/asf_codex_readonly_safety_gate.py --project-name ASF_Clean_Target_Trial --repo-path tmp/asf_clean_target_trial/step_440/clean_repo --step 440 --result-capture tmp/asf_clean_target_trial/step_440/result_capture/ASF_Clean_Target_Trial/step_440/codex_result_capture.md --output-dir tmp/asf_clean_target_trial/step_440/safety_gate
```

Esito finale:

```text
Decision: WARNING_REVIEW_REQUIRED
```

Motivo:

- result capture `PASS`;
- working tree `CLEAN`;
- stderr non vuoto;
- output Codex incompleto;
- serve review umana prima di qualunque step successivo.

---

## 9. Working tree dopo

Repo temporanea:

```text
CLEAN
```

Repository ASF:

```text
DIRTY solo per i file dello step 440.
```

Nessun repository target esterno e' stato modificato.

---

## 10. Classificazione finale

Classificazione finale:

```text
Completato con execute-readonly reale, target rimasto CLEAN, safety gate WARNING_REVIEW_REQUIRED.
```

Il trial ha validato:

- target pulito sotto `tmp/`;
- approval gate GO;
- preview;
- execute-readonly;
- capture stdout/stderr/exit code;
- working tree rimasta clean;
- safety gate conservativo.

Il trial non autorizza workspace-write.

Se in un ambiente futuro `codex` non e' disponibile, non e' fallimento se ambiente non disponibile: serve documentarlo e ritentare con CLI disponibile.

---

## 11. Verifiche finali

Verifiche eseguite:

- `python scripts/show_workflow_status.py`: PASS; working tree ASF `DIRTY` coerente con i file dello step 440;
- `python scripts/check_workflow_health.py`: PASS;
- `python scripts/asf_codex_readonly_invoke.py --help`: PASS;
- `python scripts/asf_codex_result_capture.py --help`: PASS;
- `python scripts/asf_codex_readonly_safety_gate.py --help`: PASS;
- `python -m pytest`: PASS, 279 test;
- `git diff --check`: PASS, solo warning LF/CRLF informativi;
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify.ps1`: PASS, 279 test;
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\git\check_soft_guardrails.ps1`: PASS.

---

## 12. Rischi residui

- Codex e' stato eseguito read-only ma non ha potuto completare l'ispezione per errore sandbox interno.
- Safety gate correttamente non ha prodotto GO finale.
- Serve un trial ripetibile per distinguere limiti ambientali da limiti del prototipo.
- Nessun avanzamento verso workspace-write e' autorizzato.

---

## 13. Prossimo step

Prossimo step consigliato:

```text
460) ASF Codex Read-Only Invocation Diagnostics Hardening
```

Motivo: lo STEP 450 ha introdotto il Repeatable Trial Pack. Prima di qualunque design workspace-write serve ora hardenizzare la diagnostica su stderr, output incompleto e disponibilita' Codex.

---

## 14. Esito STEP 450

Lo STEP 450 e' documentato in:

```text
docs/59_ASF_CODEX_READONLY_REPEATABLE_TRIAL_PACK.md
docs/60_ASF_CODEX_READONLY_REPEATABLE_TRIAL_RESULTS.md
```

Il pack rende il clean target trial ripetibile e confrontabile, gestisce `CODEX_NOT_AVAILABLE` come risultato diagnostico e mantiene workspace-write non autorizzato.
