# Workflow Command Cookbook

## 1. Scopo

Il Workflow Command Cookbook e' un ricettario operativo di comandi e procedure per casi specifici del workflow AI Software Factory.

La Workflow Quick Reference e' una scheda breve dei comandi principali. Questo Cookbook raccoglie scenari pratici, diagnosi e troubleshooting. I comandi sono riferimenti manuali: non sono script e non automatizzano commit, push, PR o merge.

---

## 2. Come leggere una ricetta

Ogni ricetta indica, dove possibile:

- Quando usarla;
- Comandi;
- Esito atteso;
- Se qualcosa va storto;
- Cosa non fare.

Prima di lanciare comandi che cambiano stato remoto o history, verificare branch, diff e vincoli dello step.

---

## 3. Ricetta - Stato iniziale prima di uno step

### Quando usarla

Prima di creare il branch di uno step o lanciare Codex.

### Comandi

```powershell
Set-Location "C:\Users\alberto.ferrari\source\repos\AI_Software_Factory"
git branch --show-current
git status --short
git --no-pager log --oneline --max-count=10
python scripts/check_workflow_health.py
```

### Esito atteso

- branch atteso;
- working tree pulita;
- log coerente con lo step precedente;
- Workflow Health Check passato.

### Se qualcosa va storto

Fermarsi e diagnosticare prima di creare un nuovo branch.

### Cosa non fare

Non iniziare uno step nuovo se `main` non e' aggiornato o se la working tree e' sporca.

---

## 4. Ricetta - Verificare che lo step precedente sia su main

### Quando usarla

Quando un task packet dichiara un prerequisito bloccante.

### Comandi

```powershell
git switch main
git pull origin main
git --no-pager log --oneline --max-count=12
```

### Esito atteso

Il log deve contenere il merge o commit dello step precedente.

### Se qualcosa va storto

Se il commit non compare, fermarsi. Non modificare file dello step nuovo.

### Cosa non fare

Non creare il branch dello step successivo sopra un prerequisito mancante.

---

## 5. Ricetta - Generare un task packet strict-ready

### Quando usarla

Quando step, titolo, branch e obiettivo sono gia' chiari.

### Comandi

```powershell
python scripts/generate_task_packet.py --step 260 --title "Workflow Command Cookbook" --branch step-260-workflow-command-cookbook --objective "Add a practical command cookbook for workflow operations." --output tmp/generated_step_260_task_packet.md --force --strict-ready
```

### Esito atteso

Un task packet temporaneo viene creato sotto `tmp/`.

### Se qualcosa va storto

Controllare argomenti, branch senza spazi e path di output.

### Cosa non fare

Non committare file temporanei sotto `tmp/`.

---

## 6. Ricetta - Validare un task packet Lite/Strict

### Quando usarla

Dopo la generazione o scrittura di un task packet.

### Comandi

```powershell
python scripts/validate_task_packet.py tmp/generated_step_260_task_packet.md
python scripts/validate_task_packet.py --strict tmp/generated_step_260_task_packet.md
```

### Esito atteso

Lite Mode e Strict Mode riportano `Result: PASS`.

### Se qualcosa va storto

Correggere il task packet prima di lanciare Codex.

### Cosa non fare

Non aggirare il validatore rimuovendo sezioni o vincoli dal task.

---

## 7. Ricetta - Dopo il report Codex

### Quando usarla

Quando Codex ha completato il lavoro locale sul branch dedicato.

### Comandi

```powershell
git branch --show-current
git status --short
git --no-pager diff --stat
git --no-pager diff --check
python scripts/check_workflow_health.py
python -m pytest
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify.ps1
```

### Esito atteso

Diff leggibile, file attesi, test passati, health check passato e Verification Gate passato.

### Se qualcosa va storto

Risolvere la causa minima prima del commit.

### Cosa non fare

Il report Codex non equivale a merge su main. Non avviare lo step successivo solo perche' Codex ha finito.

---

## 8. Ricetta - Commit/push/PR presidiati

### Quando usarla

Dopo verifiche locali positive e review del diff.

### Comandi

```powershell
git add .
git commit -m "260) add workflow command cookbook"
git push -u origin step-260-workflow-command-cookbook
gh pr create --base main --head step-260-workflow-command-cookbook --title "260) Workflow Command Cookbook" --body "Adds a practical command cookbook for workflow operations and troubleshooting."
```

### Esito atteso

Commit sul branch, branch remoto presente e PR creata.

### Se qualcosa va storto

Usare le ricette di troubleshooting su branch remoto assente, PR non creata o check non disponibili.

### Cosa non fare

Questi comandi li esegue Alberto, non Codex. Non sono automazione non presidiata e non devono essere messi in uno script automatico.

---

## 9. Ricetta - Gestire PR checks non disponibili

### Quando usarla

Quando il comando:

```powershell
gh pr checks --watch
```

restituisce:

```text
no checks reported on the branch
```

### Comandi

```powershell
python scripts/check_workflow_health.py
python -m pytest
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify.ps1
git status --short
```

### Esito atteso

Le verifiche locali obbligatorie passano e la situazione dei check PR viene registrata nello Step Closure Report.

### Se qualcosa va storto

Aprire la PR su GitHub per controllo manuale o usare altri comandi `gh` read-only per diagnosticare. Procedere solo in contesto controllato.

### Cosa non fare

Non ignorare ciecamente `no checks reported on the branch`. Non dichiarare check verdi senza evidenza.

---

## 10. Ricetta - Merge e verifica finale main

### Quando usarla

Dopo review e check PR positivi o dopo gestione documentata dei check non disponibili.

### Comandi

```powershell
gh pr merge --merge --delete-branch
git switch main
git pull origin main
python scripts/check_workflow_health.py
python -m pytest
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify.ps1
git status --short
git --no-pager log --oneline --max-count=10
```

### Esito atteso

Lo step compare nel log di `main`, le verifiche finali passano e la working tree e' pulita.

### Se qualcosa va storto

Non dichiarare chiuso lo step. Registrare lo stato nello Step Closure Report.

### Cosa non fare

Non fare merge se i check sono falliti o non sono stati valutati.

---

## 11. Ricetta - Branch locale presente ma branch remoto assente

### Quando usarla

Quando il lavoro esiste localmente ma GitHub non mostra il branch o la PR. Scenario gia' incontrato con STEP 180.

### Comandi

```powershell
git branch --list "*180*"
git branch -r --list "*180*"
git --no-pager log --oneline --decorate --all --max-count=20
git stash list
```

### Esito atteso

Si capisce se esiste un commit locale e se manca solo il branch remoto.

### Se qualcosa va storto

Se esiste commit locale ma branch remoto assente, non rifare lo step: pushare branch, creare PR, mergiare.

### Cosa non fare

Non duplicare il lavoro e non cancellare branch locali senza diagnosi.

---

## 12. Ricetta - Modifiche sul branch sbagliato

### Quando usarla

Quando `git status --short` mostra modifiche su un branch diverso da quello previsto.

### Comandi

```powershell
git branch --show-current
git status --short
git --no-pager diff --stat
```

### Esito atteso

Si conoscono branch corrente, file modificati e dimensione del diff.

### Se qualcosa va storto

Se le modifiche possono essere portate sul branch corretto, usare `git switch <branch>` solo se Git lo consente senza conflitti. In caso di dubbio fermarsi e chiedere diagnosi.

### Cosa non fare

Non usare `reset --hard` senza diagnosi e senza capire quali modifiche verrebbero perse.

---

## 13. Ricetta - working tree sporca su main

### Quando usarla

Quando si e' su `main` e compaiono modifiche locali.

### Comandi

```powershell
git branch --show-current
git status --short
git --no-pager diff --stat
```

### Esito atteso

Si capisce se `main` e' pulito o se contiene modifiche locali da gestire.

### Se qualcosa va storto

Fermarsi e diagnosticare. Non iniziare uno step nuovo su `main` sporco.

### Cosa non fare

Non creare branch nuovi sopra modifiche non comprese.

---

## 14. Ricetta - Health check fallito

### Quando usarla

Quando il workflow health check segnala `FAILED`.

### Comandi

```powershell
python scripts/check_workflow_health.py
```

### Esito atteso

L'output indica area fallita, file coinvolto, requisito mancante e suggerimento breve.

### Se qualcosa va storto

Correggere il riferimento o documento mancante prima di proseguire. Rilanciare il check dopo la correzione.

### Cosa non fare

Non ignorare il failure solo perche' `python -m pytest` passa.

---

## 14.1 Ricetta - Dashboard stato workflow

### Quando usarla

Quando serve una vista rapida di branch corrente, working tree, commit recenti e file workflow centrali senza aprire tutti i documenti.

### Comandi

```powershell
python scripts/show_workflow_status.py
```

### Esito atteso

La Workflow Status Dashboard mostra stato locale e prossimi controlli consigliati.

### Se qualcosa va storto

Se mancano documenti o script centrali, correggere il riferimento o ripristinare il file prima di proseguire.

### Cosa non fare

Non usare la dashboard come sostituto di Workflow Health Check, Verification Gate o PR checks.

Documento: `docs/39_WORKFLOW_STATUS_DASHBOARD.md`.

---

## 14.2 Ricetta - Valutare Release Readiness

### Quando usarla

Prima di applicare AI Software Factory a un progetto reale, soprattutto se il progetto e' gia' avviato o a meta' sviluppo.

### Comandi

Usare la checklist:

```text
docs/40_RELEASE_READINESS.md
templates/codex_tasks/release_readiness_checklist.md
```

### Esito atteso

La decisione finale e' una tra `GO pilot`, `GO pilot with warnings`, `HOLD` o `NO-GO`.

### Se qualcosa va storto

Se emergono dati sensibili, working tree non compresa, refactor massivo o assenza di Git, fermarsi e preparare un Project Intake prima di proseguire.

### Cosa non fare

Non trattare la readiness per pilot come release pubblica, SaaS, installer, PyPI package o GitHub Release.

---

## 14.3 Ricetta - Preparare Existing Project Pilot Onboarding

### Quando usarla

Dopo Release Readiness e prima del primo pilot reale su un progetto esistente.

### Comandi

Usare il protocollo e i template:

```text
docs/41_EXISTING_PROJECT_PILOT_ONBOARDING.md
templates/codex_tasks/existing_project_intake_template.md
templates/codex_tasks/first_pilot_step_packet_template.md
```

Nel repository del progetto pilota usare solo comandi diagnostici read-only finche' il task packet pilot non e' approvato:

```powershell
git branch --show-current
git status --short
git --no-pager log --oneline --max-count=12
git branch --list
git branch -r --list
git stash list
```

### Esito atteso

Il Project Intake produce una decisione GO, WARNING, HOLD o NO-GO e un primo step pilota piccolo e reversibile.

### Se qualcosa va storto

Se emergono working tree sporca non compresa, dati sensibili, secret, assenza Git, richiesta di lavoro diretto su `main` o refactor massivo, fermarsi e non modificare il repository esterno.

### Cosa non fare

Non trasformare l'onboarding in refactor architetturale. Non creare automazioni cross-repository. Non modificare CI, secret, dati sensibili o repository esterne durante l'intake.

---

## 14.4 Ricetta - Preparare ASF Next Step Runner

### Quando usarla

Quando step, titolo, branch e obiettivo del prossimo step sono gia' chiari e serve preparare un handoff Codex senza modificare il repository target.

### Comandi

Esempio locale su AI Software Factory:

```powershell
python scripts/asf_next_step.py --mode prepare --profile AI_Software_Factory --step 340 --title "ASF Runner Verification Pack Hardening" --branch step-340-asf-runner-verification-pack-hardening --objective "Harden verification pack generation for the ASF runner."
```

Esempio con override manuale del profilo:

```powershell
python scripts/asf_next_step.py --mode prepare --profile AI_Software_Factory --repo-path . --step 340 --title "ASF Runner Verification Pack Hardening" --branch step-340-asf-runner-verification-pack-hardening --objective "Harden verification pack generation for the ASF runner."
```

### Esito atteso

Il runner crea sotto `tmp/asf_next_step/`:

- `task_packet.md`;
- `codex_handoff.md`;
- `runner_report.md`;
- `verification_pack.md`.

Il report indica profilo usato o argomenti manuali, branch target, working tree `CLEAN` o `DIRTY/WARNING`, ultimi commit, validazione Lite, validazione Strict, stato degli handoff improvements, path Verification Pack e prossimo comando consigliato.

### Se qualcosa va storto

Se il repo target non esiste, non contiene `.git`, lo step non e' numerico, lo step non e' multiplo di 10, il branch contiene spazi, il profilo non esiste o il JSON profili e' malformato, correggere l'input e rilanciare.

Se la working tree target e' `DIRTY/WARNING`, non e' un fallimento automatico: Alberto deve decidere se proseguire.

### Cosa non fare

Non usare il runner come sostituto di review ChatGPT/Alberto, Codex, test, PR, merge o Step Closure Report. Il runner non invoca Codex, non crea branch nel repository target e non fa commit, push, PR o merge.

Documenti:

- `docs/42_ASF_NEXT_STEP_RUNNER.md`;
- `docs/43_ASF_RUNNER_PROJECT_PROFILES.md`;
- `docs/44_ASF_RUNNER_CODEX_HANDOFF_IMPROVEMENTS.md`;
- `docs/45_ASF_RUNNER_VERIFICATION_PACK.md`.

---

## 14.5 Ricetta - Fare intake report Codex

### Quando usarla

Quando Codex ha prodotto un report finale e Alberto lo ha salvato in Markdown.

### Comandi

```powershell
python scripts/asf_codex_report_intake.py --report-path tmp/asf_codex_reports/step_340_codex_report.md --project-name AI_Software_Factory --repo-path . --step 340
```

### Esito atteso

Lo script crea `codex_report_intake.md` sotto `tmp/asf_codex_intake/` con sezioni trovate, sezioni mancanti, stato Git target e classificazione `PASS`, `WARNING` o `FAIL`.

### Cosa non fare

Non trattare l'intake come approval. Non saltare review diff, test, Verification Gate o Step Closure Report.

---

## 14.6 Ricetta - Generare closure pack human-gated

### Quando usarla

Dopo intake report, review umana e verifiche locali positive, quando serve preparare una sequenza manuale di chiusura step.

### Comandi

```powershell
python scripts/asf_generate_closure_pack.py --project-name AI_Software_Factory --repo-path . --step 340 --branch step-340-360-asf-runner-automation-readiness-pack --commit-message "340-360) add ASF runner automation readiness pack" --pr-title "340-360) ASF Runner Automation Readiness Pack"
```

### Esito atteso

Lo script crea `closure_pack.md` sotto `tmp/asf_closure_pack/` con checklist, comandi verifica, comandi Git/GitHub manuali, gestione `gh pr checks --watch`, test finale main e Step Closure Report.

### Cosa non fare

Non eseguire il closure pack come script. I comandi contenuti sono manuali e human-gated.

---

## 14.7 Ricetta - Generare Human Approval Gate

### Quando usarla

Dopo intake report, verification pack o closure pack, quando serve una decisione esplicita prima di preview o chiusura.

### Comandi

```powershell
python scripts/asf_human_approval_gate.py --project-name AI_Software_Factory --repo-path . --step 390 --branch step-370-390-asf-automation-bridge-pack --codex-report-intake tmp/asf_codex_intake/AI_Software_Factory/step_390/codex_report_intake.md --verification-pack tmp/asf_next_step/AI_Software_Factory/step_390/verification_pack.md --output-dir tmp/asf_approval_gate
```

### Esito atteso

Lo script crea `human_approval_gate.md` sotto `tmp/asf_approval_gate/` con decisione `GO`, `WARNING`, `HOLD` o `NO-GO`.

### Cosa non fare

Non trattare `GO` come automazione. Alberto deve comunque leggere il gate e approvare le azioni successive.

---

## 14.8 Ricetta - Generare Codex invocation dry-run pack

### Quando usarla

Dopo Human Approval Gate, quando serve revisionare una futura invocazione Codex senza eseguirla.

### Comandi

```powershell
python scripts/asf_codex_invocation_dry_run.py --project-name AI_Software_Factory --repo-path . --step 390 --branch step-370-390-asf-automation-bridge-pack --handoff-path tmp/asf_next_step/AI_Software_Factory/step_390/codex_handoff.md --approval-gate tmp/asf_approval_gate/AI_Software_Factory/step_390/human_approval_gate.md --output-dir tmp/asf_codex_invocation
```

### Esito atteso

Lo script crea:

- `codex_invocation_dry_run.md`;
- `codex_exec_preview.ps1`.

Il comando `codex exec` compare solo come testo di preview. Non viene eseguito.

### Cosa non fare

Non eseguire il preview senza approval esplicita di Alberto. Non usare `workspace-write-preview` come autorizzazione implicita a modificare repository target.

---

## 14.9 Ricetta - Codex read-only invocation prototype

### Quando usarla

Dopo dry-run pack e Human Approval Gate, quando serve generare una preview read-only o normalizzare output di una prova read-only controllata.

### Comandi

Preview default:

```powershell
python scripts/asf_codex_readonly_invoke.py --mode preview --project-name AI_Software_Factory --repo-path . --step 400 --branch step-400-420-asf-codex-readonly-invocation-prototype-pack --handoff-path tmp/asf_next_step/AI_Software_Factory/step_400/codex_handoff.md --approval-gate tmp/asf_approval_gate/AI_Software_Factory/step_400/human_approval_gate.md
```

Result capture:

```powershell
python scripts/asf_codex_result_capture.py --project-name AI_Software_Factory --repo-path . --step 400 --invocation-dir tmp/asf_codex_readonly_invocation/AI_Software_Factory/step_400
```

Safety gate:

```powershell
python scripts/asf_codex_readonly_safety_gate.py --project-name AI_Software_Factory --repo-path . --step 400 --result-capture tmp/asf_codex_result_capture/AI_Software_Factory/step_400/codex_result_capture.md
```

### Esito atteso

Preview genera `readonly_invocation_preview.md` e `codex_readonly_command_preview.ps1`. Capture genera `codex_result_capture.md`. Safety gate genera `readonly_safety_gate.md`.

### Cosa non fare

Non eseguire Codex durante test o sviluppo dello step. Non trattare `GO_TO_WORKSPACE_WRITE_DESIGN` come autorizzazione diretta a execution piu' ampia.

---

## 15. Ricetta - First manual trial read-only

### Quando usarla

Quando si vuole ripetere il primo trial locale controllato della pipeline Codex read-only.

### Comandi

Seguire:

```text
docs/55_ASF_CODEX_READONLY_FIRST_MANUAL_TRIAL.md
```

Registrare l'esito in:

```text
docs/56_ASF_CODEX_READONLY_FIRST_TRIAL_RESULTS.md
```

### Esito atteso

Runner prepare, Human Approval Gate, preview read-only, result capture e safety gate producono evidenze sotto `tmp/`.

### Cosa non fare

Non tentare `execute-readonly` se il gate non e' `GO`, se la working tree target e' sporca o se il comando richiederebbe workspace-write.

---

## 16. Ricetta - Clean target trial read-only

### Quando usarla

Quando si vuole ripetere il trial Codex read-only su una repo temporanea pulita sotto `tmp/`.

### Comandi

Seguire:

```text
docs/57_ASF_CODEX_READONLY_CLEAN_TARGET_TRIAL.md
```

Registrare l'esito in:

```text
docs/58_ASF_CODEX_READONLY_CLEAN_TARGET_TRIAL_RESULTS.md
```

### Esito atteso

Human Approval Gate `GO`, preview, `execute-readonly` solo se sicuro, result capture e safety gate. Il target deve restare `CLEAN`.

### Cosa non fare

Non trattare exit code `0` come GO automatico se stderr e' non vuoto o l'output Codex e' incompleto. Non usare workspace-write o danger-full-access.

---

## 16.1 Ricetta - Repeatable trial pack read-only

### Quando usarla

Quando serve ripetere un trial Codex read-only su repo sintetica temporanea e confrontare l'esito tra run.

### Comandi

Prepare-only:

```powershell
python scripts/asf_codex_readonly_repeatable_trial.py --mode prepare-only --trial-name step_450_prepare_only --step 450
```

Run diagnostico con comando Codex non disponibile:

```powershell
python scripts/asf_codex_readonly_repeatable_trial.py --mode run-readonly-if-safe --trial-name step_450_missing_codex --step 450 --codex-command codex-command-that-does-not-exist --confirm-readonly-execution YES_I_APPROVE_READONLY_CODEX_EXECUTION
```

Compare:

```powershell
python scripts/asf_codex_readonly_trial_compare.py --reports tmp/asf_codex_readonly_repeatable_trials/step_450_prepare_only/reports/repeatable_trial_report.md tmp/asf_codex_readonly_repeatable_trials/step_450_missing_codex/reports/repeatable_trial_report.md --output-dir tmp/asf_codex_readonly_repeatable_trials/comparison
```

### Esito atteso

- `PREPARED_ONLY` per prepare-only;
- `CODEX_NOT_AVAILABLE` quando il comando Codex finto non esiste;
- target sintetico finale `CLEAN`;
- report confrontabile in `trial_comparison_report.md`.

### Cosa non fare

Non usare il repeatable trial come autorizzazione a workspace-write. Non modificare repository target esterni. Non trasformare i comandi di confronto in Git/GitHub automation.

Documenti:

- `docs/59_ASF_CODEX_READONLY_REPEATABLE_TRIAL_PACK.md`;
- `docs/60_ASF_CODEX_READONLY_REPEATABLE_TRIAL_RESULTS.md`.

---

## 16.2 Ricetta - OpenAI API Adapter dry-run/mock

### Quando usarla

Quando serve verificare payload Responses-style, environment readiness o mock deterministici senza credenziali e senza chiamate live OpenAI API.

### Comandi

Check environment:

```powershell
python scripts/asf_openai_api_adapter.py --mode check-env --output-json tmp/asf_openai_adapter_env.json
```

Dry-run:

```powershell
python scripts/asf_openai_api_adapter.py --mode dry-run --input "ping" --output-json tmp/asf_openai_adapter_dry_run.json
```

Mock:

```powershell
python scripts/asf_openai_api_adapter.py --mode mock --input "ping" --output-json tmp/asf_openai_adapter_mock.json
```

### Esito atteso

I report JSON indicano `network_performed: false`. `check-env` mostra solo se `OPENAI_API_KEY` e' presente, senza emettere il valore.

### Se qualcosa va storto

Se `live` viene selezionato, lo script deve fallire chiuso con `LIVE_MODE_NOT_IMPLEMENTED_IN_STEP_500`.

### Cosa non fare

Non incollare API key, non aggiungere SDK, non usare network e non trattare un mock positivo come integrazione live pronta.

Documenti:

- `docs/65_ASF_OPENAI_API_ADAPTER.md`;
- `templates/codex_tasks/asf_openai_api_adapter_template.md`.

---

## 16.3 Ricetta - OpenAI API Adapter live boundary gate

### Quando usarla

Quando serve verificare in modo deterministico se una futura smoke live potrebbe essere preparata, senza fare chiamate OpenAI API e senza stampare secret.

### Comandi

Gate report con default sicuro:

```powershell
python scripts/asf_openai_api_adapter.py --mode live --input "ping" --output-json tmp/asf_openai_live_boundary_gate.json
```

Gate report con tutti i segnali di readiness futura, sempre no-network:

```powershell
$env:OPENAI_API_KEY = "<set locally, never paste into chat or commit>"
$env:ASF_OPENAI_LIVE_ENABLED = "1"
python scripts/asf_openai_api_adapter.py --mode live --input "ping" --allow-live --live-confirm I_UNDERSTAND_THIS_CALLS_OPENAI_API --output-json tmp/asf_openai_live_boundary_gate_ready.json
```

### Esito atteso

Il report JSON indica una decisione tra `CREDENTIAL_MISSING`, `LIVE_ENV_FLAG_MISSING`, `LIVE_FLAG_MISSING`, `LIVE_CONFIRMATION_MISSING` e `LIVE_READY_FOR_SEPARATE_SMOKE_STEP`.

Anche con tutti i gate presenti, il report deve includere `LIVE_CALLS_NOT_IMPLEMENTED_IN_STEP_510`, `network_performed: false` e `network_call_performed: false`.

### Se qualcosa va storto

Se compaiono valore, lunghezza, prefisso, suffisso, hash o fingerprint della chiave, fermarsi: e' un safety failure.

### Cosa non fare

Non usare `setx` per credenziali OpenAI nei documenti di progetto, non incollare API key, non includere Authorization headers, non aggiungere SDK e non chiamare network nello STEP 510.

Documenti:

- `docs/66_ASF_OPENAI_API_ADAPTER_LIVE_BOUNDARY_CREDENTIAL_GATE.md`;
- `templates/codex_tasks/asf_openai_api_live_boundary_gate_template.md`.

---

## 16.4 Ricetta - OpenAI API Adapter first controlled live smoke

### Quando usarla

Quando uno step autorizza esplicitamente una singola smoke live OpenAI API dopo test locali passati e gate umani presenti.

### Comandi

Impostare la credenziale solo nella sessione locale, senza incollarla in chat o file tracciati:

```powershell
$env:OPENAI_API_KEY = "<your local OpenAI API key>"
$env:ASF_OPENAI_LIVE_ENABLED = "1"
```

Preflight no-network:

```powershell
python scripts/asf_openai_api_adapter.py --mode live --gate-only --allow-live --live-confirm I_UNDERSTAND_THIS_CALLS_OPENAI_API --input "Return exactly ASF_LIVE_SMOKE_OK." --reasoning-effort none --text-verbosity low --max-output-tokens 32 --output-json tmp/asf_openai_live_smoke_gate.json --output-markdown tmp/asf_openai_live_smoke_gate.md
```

Una sola chiamata live:

```powershell
python scripts/asf_openai_api_adapter.py --mode live --allow-live --live-confirm I_UNDERSTAND_THIS_CALLS_OPENAI_API --input "Return exactly ASF_LIVE_SMOKE_OK." --reasoning-effort none --text-verbosity low --max-output-tokens 32 --output-json tmp/asf_openai_live_smoke_result.json --output-markdown tmp/asf_openai_live_smoke_result.md
```

### Esito atteso

Il preflight restituisce `LIVE_SMOKE_READY_FOR_CALL` con `network_call_count: 0`.

La chiamata live riuscita restituisce `LIVE_SMOKE_EXECUTED_AND_PASSED`, `network_call_count: 1`, `store: false`, `expected_marker_found: true`, `status: success` e `classification: success`.

### Se qualcosa va storto

Se manca un gate, fermarsi su `LIVE_SMOKE_NOT_RUN_MISSING_GATE`.

Se la rete e' bloccata dall'ambiente, classificare `LIVE_SMOKE_NOT_RUN_NETWORK_BLOCKED` e non considerarlo crash dell'adapter.

Se l'output non contiene `ASF_LIVE_SMOKE_OK`, classificare `LIVE_SMOKE_UNEXPECTED_MODEL_OUTPUT`.

### Cosa non fare

Non incollare API key, non includere Authorization headers, non inviare contenuti privati o repository, non ritentare automaticamente e non trattare questa smoke come integrazione produttiva.

Documenti:

- `docs/67_ASF_OPENAI_API_ADAPTER_FIRST_CONTROLLED_LIVE_SMOKE_TEST.md`;
- `docs/68_ASF_OPENAI_API_ADAPTER_LIVE_SMOKE_RESULT_HARDENING.md`;
- `templates/codex_tasks/asf_openai_api_live_smoke_test_template.md`.

---

## 16.5 Ricetta - OpenAI API Adapter live smoke result hardening

### Quando usarla

Quando serve verificare classificazioni e artifact live smoke senza eseguire chiamate OpenAI API reali.

### Comandi

Test focalizzati mockati:

```powershell
python -m pytest tests/unit/test_asf_openai_api_adapter.py tests/unit/test_asf_openai_api_adapter_live_boundary_gate.py tests/unit/test_asf_openai_api_adapter_live_smoke.py
```

Artifact gate-only no-network con JSON e Markdown:

```powershell
python scripts/asf_openai_api_adapter.py --mode live --gate-only --allow-live --live-confirm I_UNDERSTAND_THIS_CALLS_OPENAI_API --input "Return exactly ASF_LIVE_SMOKE_OK." --reasoning-effort none --text-verbosity low --max-output-tokens 32 --output-json tmp/asf_openai_live_smoke_gate.json --output-markdown tmp/asf_openai_live_smoke_gate.md
```

### Esito atteso

I report includono:

- `status`;
- `classification`;
- `safe_details`;
- `provider`;
- `model`;
- `live_enabled`;
- `credential_present`;
- `duration_ms`;
- `timestamp`.

Le classificazioni attese sono `not_configured`, `disabled`, `credential_missing`, `live_not_allowed`, `success`, `provider_error`, `network_error`, `rate_limited`, `auth_error`, `schema_error` e `unknown_error`.

### Cosa non fare

Non eseguire una chiamata live reale durante result hardening. Non stampare, salvare, hashare, troncare, fingerprintare o serializzare API key. Non registrare lunghezza, prefisso o suffisso della chiave.

Documento:

- `docs/68_ASF_OPENAI_API_ADAPTER_LIVE_SMOKE_RESULT_HARDENING.md`.

---

## 17. Ricetta - Verification Gate fallito

### Quando usarla

Quando il gate locale non passa.

### Comandi

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify.ps1
```

### Esito atteso

Il gate distingue test falliti, whitespace/diff check e working tree non pulita.

### Se qualcosa va storto

Leggere quale sezione fallisce e correggere la causa minima.

### Cosa non fare

Non dichiarare lo step verificato se il Verification Gate fallisce.

---

## 18. Ricetta - Pulizia riferimenti remoti vecchi

### Quando usarla

Quando branch remoti gia' chiusi compaiono ancora localmente.

### Comandi

```powershell
git fetch --all --prune
```

### Esito atteso

I riferimenti remoti locali obsoleti vengono potati.

### Se qualcosa va storto

Rileggere l'output e verificare con `git branch -r`.

### Cosa non fare

Questo comando non modifica i branch remoti gia' eliminati. Non usarlo come sostituto della diagnosi su branch, PR o merge.

---

## 19. Ricetta - CRLF/LF warning

### Quando usarla

Quando Git mostra warning di conversione fine riga.

### Comandi

```powershell
git --no-pager diff --check
python -m pytest
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify.ps1
```

### Esito atteso

I warning CRLF/LF non sono automaticamente bloccanti se:

- `git diff --check` ha exit code 0;
- Verification Gate passa;
- i test passano.

### Se qualcosa va storto

Se `git diff --check` segnala errori reali, correggere whitespace o fine riga.

### Cosa non fare

Non confondere warning non bloccanti con fallimenti dei test.

---

## 20. Ricetta - Preparare il report finale di chiusura step

### Quando usarla

Dopo merge, pull di `main` e verifiche finali.

### Comandi

Usare il template:

```text
templates/codex_tasks/step_closure_report_template.md
```

Campi chiave:

- step;
- stato;
- commit;
- PR;
- merge commit;
- health check;
- Verification Gate;
- working tree;
- prossimo step.

### Esito atteso

Il report dichiara se lo step e' chiuso e verificato su `main` oppure non chiuso con motivo.

### Se qualcosa va storto

Usare lo stato piu' preciso disponibile, ad esempio `In attesa check`, `Mergiato su main` o `Non completato`.

### Cosa non fare

Non scrivere "chiuso" se mancano merge, pull `main` o verifiche finali.

---

## 21. Anti-pattern finali

- Usare `reset --hard` per "pulire" senza diagnosi.
- Iniziare lo step successivo senza merge su `main`.
- Considerare report Codex come step chiuso.
- Ignorare `git status --short`.
- Saltare PR checks.
- Saltare health check.
- Far fare commit, push, PR o merge a Codex.
- Committare `tmp/`.

Codex non deve fare commit, Codex non deve fare push, Codex non deve aprire PR e Codex non deve fare merge.

---

## 22. Collegamenti utili

- `docs/32_PROMPT_PACKET_LIFECYCLE_CHECKLIST.md`
- `docs/34_PROJECT_WORKFLOW_INDEX.md`
- `docs/35_WORKFLOW_HEALTH_CHECK.md`
- `docs/36_WORKFLOW_QUICK_REFERENCE.md`
- `docs/37_STEP_CLOSURE_REPORT.md`
- `docs/39_WORKFLOW_STATUS_DASHBOARD.md`
- `docs/40_RELEASE_READINESS.md`
- `docs/41_EXISTING_PROJECT_PILOT_ONBOARDING.md`
- `docs/42_ASF_NEXT_STEP_RUNNER.md`
- `docs/49_ASF_HUMAN_APPROVAL_GATE.md`
- `docs/50_ASF_CODEX_INVOCATION_DESIGN.md`
- `docs/51_ASF_CODEX_INVOCATION_DRY_RUN_PACK.md`
- `docs/52_ASF_CODEX_READONLY_INVOCATION_PROTOTYPE.md`
- `docs/53_ASF_CODEX_INVOCATION_RESULT_CAPTURE.md`
- `docs/54_ASF_CODEX_READONLY_SAFETY_GATE.md`
- `docs/55_ASF_CODEX_READONLY_FIRST_MANUAL_TRIAL.md`
- `docs/56_ASF_CODEX_READONLY_FIRST_TRIAL_RESULTS.md`
- `docs/57_ASF_CODEX_READONLY_CLEAN_TARGET_TRIAL.md`
- `docs/58_ASF_CODEX_READONLY_CLEAN_TARGET_TRIAL_RESULTS.md`
- `docs/59_ASF_CODEX_READONLY_REPEATABLE_TRIAL_PACK.md`
- `docs/60_ASF_CODEX_READONLY_REPEATABLE_TRIAL_RESULTS.md`
- `docs/65_ASF_OPENAI_API_ADAPTER.md`
- `templates/codex_tasks/step_closure_report_template.md`
