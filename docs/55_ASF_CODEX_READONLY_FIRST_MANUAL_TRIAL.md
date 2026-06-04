# ASF Codex Read-Only First Manual Trial

## 1. Scopo

Questo documento definisce il primo trial manuale controllato della pipeline Codex read-only.

Il trial verifica il flusso dal runner al result capture senza autorizzare modifiche automatiche ai repository target e senza abilitare workspace-write.

---

## 2. Target scelto

Target preferito:

```text
AI_Software_Factory
```

AI_Software_Factory e' il target piu' sicuro per questo primo trial perche':

- e' la repository del runner;
- contiene gia' gli script e i documenti del workflow;
- non contiene archivi reali o dati applicativi sensibili da modificare;
- permette di testare preview, capture e safety gate sotto controllo locale;
- gli output temporanei possono restare sotto `tmp/`, ignorati da Git.

Se la working tree del target diventa sporca durante lo step, non tentare `execute-readonly`. Usare preview e output simulati, oppure una repository temporanea sotto `tmp/` per validare il comportamento su target pulito.

---

## 3. Prerequisiti

Prima del trial:

- il mega-step 400-420 deve essere presente su `main`;
- il branch di lavoro deve essere dedicato allo step 430;
- gli script del pack 400-420 devono essere presenti;
- `tmp/` deve restare ignorato;
- il target deve essere letto con comandi Git read-only.

Comandi di prerequisito:

```powershell
git switch main
git pull origin main
git --no-pager log --oneline --max-count=15
```

---

## 4. Sequenza del trial

### Prepare runner

```powershell
python scripts/asf_next_step.py --mode prepare --profile AI_Software_Factory --step 440 --title "ASF Codex Read-Only Invocation Trial Follow-up" --branch step-440-asf-codex-readonly-invocation-trial-follow-up --objective "Follow up on the first read-only Codex invocation trial." --output-dir tmp/asf_step_430_first_manual_trial/asf_next_step
```

Il runner deve generare task packet, handoff, runner report e verification pack sotto `tmp/`. Non invoca Codex e non modifica il repository target.

### Human Approval Gate

```powershell
python scripts/asf_human_approval_gate.py --project-name AI_Software_Factory --repo-path . --step 440 --branch step-440-asf-codex-readonly-invocation-trial-follow-up --verification-pack tmp/asf_step_430_first_manual_trial/asf_next_step/AI_Software_Factory/step_440/verification_pack.md --output-dir tmp/asf_step_430_first_manual_trial/asf_approval_gate
```

Il gate puo' produrre `GO`, `WARNING`, `HOLD` o `NO-GO`. Un `HOLD` o `NO-GO` blocca `execute-readonly`.

### Preview read-only

```powershell
python scripts/asf_codex_readonly_invoke.py --mode preview --project-name AI_Software_Factory --repo-path . --step 440 --branch step-440-asf-codex-readonly-invocation-trial-follow-up --handoff-path tmp/asf_step_430_first_manual_trial/asf_next_step/AI_Software_Factory/step_440/codex_handoff.md --approval-gate tmp/asf_step_430_first_manual_trial/asf_approval_gate/AI_Software_Factory/step_440/human_approval_gate.md --output-dir tmp/asf_step_430_first_manual_trial/asf_codex_readonly_invocation
```

Preview genera `readonly_invocation_preview.md` e `codex_readonly_command_preview.ps1`. Codex non viene eseguito.

### Result capture

Se non esiste output reale di `execute-readonly`, creare output simulati sotto `tmp/` e usare:

```powershell
python scripts/asf_codex_result_capture.py --project-name AI_Software_Factory --repo-path . --step 440 --invocation-dir tmp/asf_step_430_first_manual_trial/asf_codex_readonly_invocation/AI_Software_Factory/step_440 --output-dir tmp/asf_step_430_first_manual_trial/asf_codex_result_capture
```

Il result capture non invoca Codex e non modifica il target.

### Safety gate

```powershell
python scripts/asf_codex_readonly_safety_gate.py --project-name AI_Software_Factory --repo-path . --step 440 --result-capture tmp/asf_step_430_first_manual_trial/asf_codex_result_capture/AI_Software_Factory/step_440/codex_result_capture.md --output-dir tmp/asf_step_430_first_manual_trial/asf_codex_readonly_safety_gate
```

Il safety gate non autorizza workspace-write. Anche `GO_TO_WORKSPACE_WRITE_DESIGN` permette solo di progettare uno step futuro separato.

---

## 5. Perche' il trial e' read-only

Il trial e' read-only perche':

- il runner legge stato Git e genera file sotto `tmp/`;
- Human Approval Gate legge evidenze e stato Git;
- preview genera solo file di revisione;
- result capture legge output esistenti;
- safety gate legge result capture e stato Git;
- Codex non deve modificare repo target;
- commit, push, PR e merge non sono automatici.

---

## 6. Condizioni per tentare execute-readonly

Tentare `execute-readonly` solo se tutte queste condizioni sono vere:

- comando `codex` disponibile;
- Human Approval Gate `GO`;
- working tree target `CLEAN`;
- conferma esplicita `YES_I_APPROVE_READONLY_CODEX_EXECUTION`;
- sandbox hard-coded `read-only`;
- nessuna richiesta di workspace-write;
- nessuna autorizzazione a modificare repository target.

Se una sola condizione non e' soddisfatta, restare in preview o usare output simulati sotto `tmp/`. Questo non e' fallimento del trial.

---

## 7. Stop conditions

Fermarsi se:

- il prerequisito 400-420 non e' su `main`;
- Human Approval Gate e' `HOLD` o `NO-GO`;
- working tree target e' sporca e non compresa;
- il comando richiederebbe workspace-write;
- emergono secret, `.env`, CI, dipendenze, hook o GitHub automation;
- Codex propone commit, push, PR o merge automatici.

---

## 8. Relazione con future prove workspace-write

Questo trial non autorizza workspace-write.

Un futuro step workspace-write richiedera' un design separato, branch dedicato, gate umano esplicito, working tree compresa, scope chiaro, test e rollback. Il safety gate read-only serve solo come evidenza per decidere se progettare quel futuro step.

---

## 9. Step successivo

Lo STEP 440 e' il clean target trial documentato in `docs/57_ASF_CODEX_READONLY_CLEAN_TARGET_TRIAL.md`.

Usa una repo temporanea sotto `tmp/` per ottenere target pulito, Human Approval Gate `GO`, preview, eventuale `execute-readonly`, result capture e safety gate.
