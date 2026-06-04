# ASF Codex Read-Only First Trial Results

## 1. Data e step

- Data: 2026-06-04
- Step: 430) ASF Codex Read-Only Invocation First Manual Trial
- Branch: `step-430-asf-codex-readonly-invocation-first-manual-trial`

---

## 2. Target

Target principale:

```text
AI_Software_Factory
```

Il target e' stato scelto perche' e' la repository del runner, e' locale, controllata e non richiede modifiche a repository esterni.

---

## 3. Prepare runner

Comando eseguito:

```powershell
python scripts/asf_next_step.py --mode prepare --profile AI_Software_Factory --step 440 --title "ASF Codex Read-Only Invocation Trial Follow-up" --branch step-440-asf-codex-readonly-invocation-trial-follow-up --objective "Follow up on the first read-only Codex invocation trial." --output-dir tmp/asf_step_430_first_manual_trial/asf_next_step
```

Esito:

- output generati sotto `tmp/asf_step_430_first_manual_trial/asf_next_step/`;
- task packet generato;
- Codex handoff generato;
- runner report generato;
- verification pack generato;
- validazione Lite `PASS`;
- validazione Strict `PASS`;
- nessuna invocazione Codex;
- nessuna modifica al repository target.

---

## 4. Approval gate

Comando eseguito:

```powershell
python scripts/asf_human_approval_gate.py --project-name AI_Software_Factory --repo-path . --step 440 --branch step-440-asf-codex-readonly-invocation-trial-follow-up --verification-pack tmp/asf_step_430_first_manual_trial/asf_next_step/AI_Software_Factory/step_440/verification_pack.md --output-dir tmp/asf_step_430_first_manual_trial/asf_approval_gate
```

Esito:

```text
Decision: HOLD
```

Motivo:

- il target era sul branch dello step 430;
- il branch atteso del trial fittizio era `step-440-asf-codex-readonly-invocation-trial-follow-up`;
- il gate ha bloccato correttamente la progressione verso `execute-readonly`.

---

## 5. Preview

Comando eseguito:

```powershell
python scripts/asf_codex_readonly_invoke.py --mode preview --project-name AI_Software_Factory --repo-path . --step 440 --branch step-440-asf-codex-readonly-invocation-trial-follow-up --handoff-path tmp/asf_step_430_first_manual_trial/asf_next_step/AI_Software_Factory/step_440/codex_handoff.md --approval-gate tmp/asf_step_430_first_manual_trial/asf_approval_gate/AI_Software_Factory/step_440/human_approval_gate.md --output-dir tmp/asf_step_430_first_manual_trial/asf_codex_readonly_invocation
```

Esito:

- `readonly_invocation_preview.md` generato;
- `codex_readonly_command_preview.ps1` generato;
- Codex non eseguito;
- preview coerente con modalità read-only.

---

## 6. Execute-readonly

Stato:

```text
Non tentato
```

Motivo:

- Human Approval Gate non era `GO`, ma `HOLD`;
- il branch target non coincideva con il branch atteso per lo step fittizio 440;
- in queste condizioni lo script richiede di non eseguire Codex.

Questo non e' fallimento del trial. Il primo trial puo' essere preview-only quando le condizioni per `execute-readonly` non sono tutte soddisfatte.

Prossimo requisito per tentarlo:

- target pulito;
- branch atteso coerente;
- Human Approval Gate `GO`;
- comando `codex` disponibile;
- conferma esplicita `YES_I_APPROVE_READONLY_CODEX_EXECUTION`;
- sandbox read-only.

---

## 7. Result capture

Sul target AI_Software_Factory sono stati usati output simulati sotto `tmp/` per validare il capture senza eseguire Codex.

Comando eseguito:

```powershell
python scripts/asf_codex_result_capture.py --project-name AI_Software_Factory --repo-path . --step 440 --invocation-dir tmp/asf_step_430_first_manual_trial/asf_codex_readonly_invocation/AI_Software_Factory/step_440 --output-dir tmp/asf_step_430_first_manual_trial/asf_codex_result_capture
```

Esito:

```text
Classification: PASS
```

---

## 8. Safety gate

Il primo safety gate sul target ASF ha evidenziato un falso positivo testuale su una frase negativa relativa alle modifiche file. Lo script `scripts/asf_codex_readonly_safety_gate.py` e il test unitario dedicato sono stati corretti in modo mirato.

Dopo la correzione, il safety gate sul target ASF ha segnalato `NO_GO` per working tree `DIRTY`, perche' lo step 430 aveva ormai modifiche locali in corso. Questo e' un comportamento corretto: un target sporco deve bloccare la progressione.

Per validare il percorso positivo del safety gate e' stata usata una repository Git temporanea sotto:

```text
tmp/asf_step_430_first_manual_trial/clean_control/
```

Esito del controllo pulito:

```text
Classification: PASS
Decision: GO_TO_WORKSPACE_WRITE_DESIGN
```

La decisione non autorizza workspace-write. Indica solo che su target pulito le evidenze simulate sono sufficienti per progettare un trial successivo piu' pulito.

---

## 9. Classificazione finale

Classificazione finale dello step:

```text
Completato come first manual trial preview-only con capture simulato e safety gate validato su controllo pulito.
```

Risultato operativo:

- runner prepare: `PASS`;
- approval gate: `HOLD` sul target ASF per branch atteso diverso;
- preview: completata;
- execute-readonly: non tentato;
- result capture simulato: `PASS`;
- safety gate: `NO_GO` su ASF sporco dopo modifiche dello step, `GO_TO_WORKSPACE_WRITE_DESIGN` su controllo pulito.

---

## 10. Test eseguiti

Verifiche eseguite prima della chiusura locale:

- `python scripts/show_workflow_status.py`: PASS; branch step 430 e working tree `DIRTY` coerente con le modifiche dello step;
- `python scripts/check_workflow_health.py`: PASS;
- `python scripts/asf_codex_readonly_invoke.py --help`: PASS;
- `python scripts/asf_codex_result_capture.py --help`: PASS;
- `python scripts/asf_codex_readonly_safety_gate.py --help`: PASS;
- `python -m pytest`: PASS, 271 test;
- `git diff --check`: PASS, solo warning LF/CRLF informativi;
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify.ps1`: PASS, 271 test;
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\git\check_soft_guardrails.ps1`: PASS.

---

## 11. Rischi residui

- `execute-readonly` non e' ancora stato provato su un target ASF pulito con gate `GO`.
- Il primo trial ha dimostrato che il branch atteso deve essere coerente prima di qualunque esecuzione reale.
- Il safety gate blocca correttamente quando la working tree target e' sporca.
- Output simulati non sostituiscono un futuro run reale read-only.

---

## 12. Prossimo step consigliato

```text
440) ASF Codex Read-Only Invocation Clean Target Trial
```

Motivo: prima di workspace-write o OpenAI API Adapter, serve un trial read-only con target pulito, branch coerente, approval gate `GO` e, solo se il comando `codex` e' disponibile, tentativo `execute-readonly` controllato.
