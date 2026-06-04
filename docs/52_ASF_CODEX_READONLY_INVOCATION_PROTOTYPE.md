# ASF Codex Read-Only Invocation Prototype

## 1. Scopo

`scripts/asf_codex_readonly_invoke.py` introduce il primo prototipo per preparare e, solo con consenso esplicito, eseguire una invocazione Codex in sandbox read-only.

Il default e' `preview`: lo script non invoca Codex e genera solo file di revisione sotto `tmp/asf_codex_readonly_invocation/`.

---

## 2. Modalita'

Modalita' supportate:

- `preview`: default, genera preview Markdown e PowerShell commentata.
- `execute-readonly`: esegue Codex solo se tutti i gate sono favorevoli.

Esempio preview:

```powershell
python scripts/asf_codex_readonly_invoke.py --mode preview --project-name Family_Photo_Organizer --repo-path "C:\Users\alberto.ferrari\source\repos\Family_Photo_Organizer" --step 590 --branch 590-sandbox-import-static-simulation-prototype --handoff-path tmp/asf_next_step/Family_Photo_Organizer/step_590/codex_handoff.md --approval-gate tmp/asf_approval_gate/Family_Photo_Organizer/step_590/human_approval_gate.md
```

Esempio execute-readonly:

```powershell
python scripts/asf_codex_readonly_invoke.py --mode execute-readonly --project-name Family_Photo_Organizer --repo-path "C:\Users\alberto.ferrari\source\repos\Family_Photo_Organizer" --step 590 --branch 590-sandbox-import-static-simulation-prototype --handoff-path tmp/asf_next_step/Family_Photo_Organizer/step_590/codex_handoff.md --approval-gate tmp/asf_approval_gate/Family_Photo_Organizer/step_590/human_approval_gate.md --confirm-readonly-execution YES_I_APPROVE_READONLY_CODEX_EXECUTION
```

---

## 3. Preview mode

In preview lo script:

- verifica `repo-path` e `.git`;
- verifica `handoff-path`;
- legge `approval-gate` se fornito;
- legge branch, working tree e ultimi commit del repo target con comandi Git read-only;
- genera `readonly_invocation_preview.md`;
- genera `codex_readonly_command_preview.ps1`.

Il file PowerShell contiene commenti e comando commentato. Non viene eseguito dallo script.

---

## 4. Execute-readonly mode

`execute-readonly` richiede tutti questi requisiti:

- `--confirm-readonly-execution YES_I_APPROVE_READONLY_CODEX_EXECUTION`;
- `--approval-gate` esistente;
- decisione approval gate `GO`;
- working tree target `CLEAN`;
- comando Codex disponibile;
- sandbox Codex hard-coded `read-only`.

Se il gate contiene `WARNING`, `HOLD`, `NO-GO` o non e' leggibile, lo script fallisce prima di invocare Codex.

---

## 5. Output

Output predefinito:

```text
tmp/asf_codex_readonly_invocation/<project-name>/step_<step>/
```

Preview:

- `readonly_invocation_preview.md`;
- `codex_readonly_command_preview.ps1`.

Execute-readonly:

- `stdout.txt`;
- `stderr.txt`;
- `exit_code.txt`;
- `codex_readonly_invocation_result.md`.

`tmp/` resta ignorato da Git.

---

## 6. Cosa non fa

Lo script non:

- esegue Codex in default mode;
- usa sandbox diverse da read-only in execution mode;
- modifica GitHub;
- crea branch nel repo target;
- fa commit, push, PR o merge;
- modifica CI, hook, `core.hooksPath`, PATH, profili PowerShell, dipendenze, secret o `.env`;
- modifica repository target esterni in preview.

---

## 7. Limiti

La sintassi `codex exec --sandbox read-only -` e' implementata in modo prudente per prompt via stdin.

Se la CLI Codex locale non supporta questa forma, l'esecuzione reale fallira' con stdout/stderr/exit code salvati. I test dello step non eseguono Codex.

Prima di qualunque futura esecuzione piu' ampia serve uno step separato, con nuovo gate umano.

---

## 8. Relazione con il first manual trial

Il primo trial manuale e' documentato in `docs/55_ASF_CODEX_READONLY_FIRST_MANUAL_TRIAL.md` e `docs/56_ASF_CODEX_READONLY_FIRST_TRIAL_RESULTS.md`.

Nel trial 430 `execute-readonly` resta non tentato se il Human Approval Gate non e' `GO` o se la working tree target non e' `CLEAN`. Questo e' comportamento previsto del prototipo, non fallimento del trial.

---

## 9. Relazione con il clean target trial

Il clean target trial e' documentato in `docs/57_ASF_CODEX_READONLY_CLEAN_TARGET_TRIAL.md` e `docs/58_ASF_CODEX_READONLY_CLEAN_TARGET_TRIAL_RESULTS.md`.

Nel trial 440 `execute-readonly` e' stato tentato su repo temporanea pulita con gate `GO`. Lo script ha richiesto una correzione per leggere correttamente report completi del Human Approval Gate e per usare UTF-8 esplicito nella subprocess.
