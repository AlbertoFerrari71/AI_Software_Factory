# Workflow Quick Reference

## 1. Scopo

Questa quick reference e' una scheda rapida per l'uso quotidiano del workflow AI Software Factory.

Contiene i comandi essenziali per generare task packet, validarli, eseguire smoke workflow, controllare il workflow health check, lanciare il Verification Gate e gestire il passaggio presidiato verso PR e merge.

Non sostituisce il Project Workflow Index, la Prompt Packet Lifecycle Checklist o la Developer Onboarding Guide. Li collega quando serve approfondire.

Per scenari operativi specifici, troubleshooting e varianti diagnostiche usare il Workflow Command Cookbook in `docs/38_WORKFLOW_COMMAND_COOKBOOK.md`.

---

## 2. Quando usarla

Usarla:

- prima di lanciare Codex;
- dopo il report Codex;
- prima del commit;
- prima del push;
- prima del merge;
- prima dello step successivo.

---

## 3. Prerequisiti rapidi

Controllare branch, working tree e log recente:

```powershell
git branch --show-current
git status --short
git --no-pager log --oneline --max-count=10
```

Se lo step precedente non risulta su `main`, fermarsi e completare il lifecycle dello step precedente.

---

## 4. Generare un task packet strict-ready

Esempio per STEP 240:

```powershell
python scripts/generate_task_packet.py --step 240 --title "Workflow Quick Reference" --branch step-240-workflow-quick-reference --objective "Create a short operational quick reference for the workflow." --output tmp/generated_step_240_task_packet.md --force --strict-ready
```

Il file sotto `tmp/` e' temporaneo e non deve essere committato.

---

## 5. Validare il task packet

Lite Mode:

```powershell
python scripts/validate_task_packet.py tmp/generated_step_240_task_packet.md
```

Strict Mode:

```powershell
python scripts/validate_task_packet.py --strict tmp/generated_step_240_task_packet.md
```

Lite controlla i requisiti minimi. Strict e' piu' severo ed e' consigliato per task complessi o sensibili.

---

## 5.1 Preparare prompt Codex clean-first

Default:

```text
Clean Codex prompt first by default.
PowerShell only when archiving, auditing, or publishing.
```

Prima di lanciare Codex, preparare un prompt Codex pulito, autosufficiente e direttamente copiabile, senza wrapper PowerShell e senza comandi Git o pubblicazione nello stesso blocco.

Usare il Codex command pack PowerShell solo se Alberto chiede salvataggio nel Bridge Dropbox / ChatGPT Bridge, artefatti progressivi `NNNN-II-Tipo_Nome.ext` o audit trail formale. Non generare o leggere file `LAST-*`.

Dopo il report Codex, fare intake gate e verifiche locali. Solo dopo, se serve pubblicare, usare il pwsh/publication command pack per commit, push, PR/merge e verifica finale presidiata.

Non mischiare prompt Codex e script PowerShell nello stesso blocco, salvo richiesta esplicita.

---

## 5.2 Safe bootstrap PowerShell command pack

Quando serve un PowerShell command pack per Bridge, audit trail o pubblicazione controllata, usare il nuovo standard:

```text
bootstrap corto -> scrive .ps1 completo -> [scriptblock]::Create(...) -> pwsh -NoProfile -ExecutionPolicy Bypass -File
```

Regole rapide:

- il blocco incollato resta corto e termina con `# terminatore copia-incolla` seguito da una riga vuota finale reale;
- non usare `WScript.Shell`, `SendKeys` o auto-Enter come workaround automatici; `WScript.Shell` resta solo fallback esplicito per casi rari;
- niente logica Git complessa nel bootstrap;
- niente here-string annidate;
- niente `finally` fragile nel wrapper esterno;
- usare `ArgList`, non `$Args`, per parametri wrapper nativi;
- rifiutare `ArgList` nulli o vuoti, usare `AllowedExitCodes` e `ProcessStartInfo.ArgumentList`, e dichiarare successo solo dopo exit code ammesso;
- usare `git status --porcelain=v1 --untracked-files=all` per parser/scope guard;
- artefatti progressivi `NNNN-II-Tipo_Nome.ext` restano obbligatori;
- per trovare l'ultimo artefatto di un tipo per uno step, usare `max(II)` per `(step, tipo)`;
- il Bridge e' operativo, non autorevole: la fonte ufficiale e' Git + file versionato;
- DOCX e' best-effort e non blocca se TXT/MD sono validi;
- usare file Bridge per il report compatto; nessuna copia automatica negli appunti;
- usare `git --no-pager` per log, diff e output lunghi;
- warning LF/CRLF non sono bloccanti se `diff --check`, test, health e verify passano; per diagnosi `.gitattributes` usare `docs/72_ASF_GIT_LINE_ENDINGS_WARNING_CLEANUP.md`.

Per pubblicare verso `main`, default PR-first:

```text
branch step/publish -> push branch -> gh pr create -> gh pr merge -> riallinea main -> verifica finale
```

Per pubblicazioni ASF dopo STEP 0810, usare di default il flusso runner provato:

```text
PrepareConfig/scope discovery -> review umana scope -> config JSON esplicito -> scripts/asf_publish_step.ps1 -Phase B -ApprovePublish -> gh pr list --head -> PR number non vuoto e numerico -> Phase C -PrNumber -ApproveMerge -> verifiche finali
```

Il config deve dichiarare `expected_files` e `changed_files`; non dedurre lo
scope da parsing fragile di `git status --short` o da output Git `2>&1`. Se il
runner segnala out-of-scope, leggere recovery report o suggested config e
aggiungere file allo scope solo dopo review. Warning LF/CRLF non sono file fuori
scope.
`COMPLETATO` puo' essere stampato solo dopo i gate finali. Il compatto finale si
handoff su file Bridge. DOCX/Word COM resta best-effort; output accessori restano
best-effort e non invalidano un publish gia' verificato.

Dopo STEP 0820, se un output Bridge o `LAST-*` primario resta bloccato, il
runner fa retry e poi usa un fallback timestampato con warning chiaro. Il
compatto Markdown resta obbligatorio nel path primario o fallback. Wrapper
esterni non devono usare `Start-Transcript` sullo stesso `Output_Completo` del
runner; usare un file separato `NNNN-Wrapper_Log_*.txt`.

Dopo STEP 0830, il pilot operativo di riferimento per provare questo flusso e'
`docs/motor/0830_MVP_REAL_STEP_PILOT_4_SLIGHTLY_MORE_OPERATIONAL.md`, con
manifest esempio `examples/publish_runner/0830_prepare_config_pilot.json`.

Dopo STEP 0840, una pubblicazione ASF riuscita dovrebbe includere o puntare a
un post-publish evidence pack. Il pack deve indicare PR, merge commit, checks
finali, Bridge outputs, LAST files, warning accettati, manifest/evidence e
prossimo step. Non autorizza commit, push, PR, merge o deploy automatici.

Dopo STEP 0850, il primo pilot esterno consigliato e' `Codex_Skills`. Il pilot
successivo resta read-only/dry-run, richiede human gate e non deve fare commit,
push, PR, merge, deploy o tag.

Dopo STEP 0860, il dry-run `Codex_Skills` dispone di readiness report,
changed-files preview ipotetica, dry-run plan ed evidence manifest. Il prossimo
step 0870 richiede gate umano prima di qualunque scrittura esterna e non abilita
commit, push, PR, merge o deploy automatici.

Dopo STEP 0870, il controlled write pilot `Codex_Skills` ha creato solo una
micro-modifica Markdown locale e non committata. Il prossimo step 0880 deve
decidere con human gate se fare rollback o preparare una pubblicazione separata.

Dopo STEP 0880, la decision matrix raccomanda come default il rollback del file
0870. Keep local e future controlled commit richiedono scelta esplicita di
Alberto; lo step 0880 non esegue comandi.

Dopo STEP 0890, Alberto ha scelto B e ASF ha eseguito un commit locale
controllato del solo file 0870 in `Codex_Skills`. Nessun push, PR, merge,
deploy o tag e' stato eseguito; qualunque push futuro richiede human gate
separato nello step 0900.

Dopo STEP 0900, il commit locale `b488745` in `Codex_Skills` ha un decision
pack read-only: A) push controllato, B) rollback locale, C) keep local
temporaneo. Nessuna opzione e' stata eseguita; lo step 0910 richiede decisione
esplicita di Alberto.

Dopo STEP 0920, ASF registra la closure/evidence del primo push reale
controllato su `Codex_Skills`: `36b065d..bec96ff main -> main`, exit code 0,
commit `b488745` e `bec96ff`, verifica read-only via `$env:USERPROFILE` e
nota no-fetch/no-pull. Il prossimo step consigliato e' la generalizzazione 0930.

Se `main...origin/main [ahead N]` contiene merge locali gia' verificati, non fare push diretto a `main`: creare un publish branch da `main`, pushare quel branch, aprire PR, mergiare, riallineare `main` e verificare.

Template:

```text
templates/pwsh_command_pack/safe_bootstrap_template.ps1
templates/pwsh_command_pack/safe_command_pack_script_template.ps1
templates/pwsh_command_pack/README.md
templates/pwsh_command_pack/as-common-pwsh-command-pack-SKILL.md
templates/pwsh_command_pack/export/as-common-pwsh-command-pack/SKILL.md
scripts/install_pwsh_command_pack_skill.py
docs/70_ASF_PWSH_COMMAND_PACK_SKILL_FINALIZATION.md
docs/71_ASF_PWSH_COMMAND_PACK_SKILL_EXPORT_INSTALL.md
docs/motor/0805_POWERSHELL_PUBLISH_SKILL_SYNC_WITH_PROVEN_RUNNER_FLOW.md
docs/motor/0810_PUBLISH_RUNNER_SCOPE_DISCOVERY_RECOVERY_UX_AND_NO_FALSE_COMPLETED_GUARD.md
docs/motor/0830_MVP_REAL_STEP_PILOT_4_SLIGHTLY_MORE_OPERATIONAL.md
docs/motor/0840_RUNNER_HOOK_EVIDENCE_MANIFEST_POST_PUBLISH_PACK.md
docs/motor/0850_FIRST_REAL_EXTERNAL_WORKFLOW_PILOT.md
docs/motor/0860_CODEX_SKILLS_EXTERNAL_WORKFLOW_DRY_RUN_PILOT.md
docs/motor/0870_CODEX_SKILLS_FIRST_CONTROLLED_WRITE_PILOT.md
docs/motor/0880_CODEX_SKILLS_CONTROLLED_WRITE_REVIEW_AND_DECISION.md
docs/motor/0890_CODEX_SKILLS_CONTROLLED_LOCAL_COMMIT_EXECUTION.md
docs/motor/0900_CODEX_SKILLS_CONTROLLED_PUSH_OR_ROLLBACK_DECISION.md
docs/motor/0920_CODEX_SKILLS_REMOTE_VERIFICATION_AND_EVIDENCE_CLOSURE.md
docs/motor/0920_CODEX_SKILLS_REMOTE_PUSH_EVIDENCE_REPORT.md
```

---

## 6. Eseguire release smoke workflow

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\smoke_prompt_packet_release.ps1
```

Lo smoke workflow verifica localmente wrapper, generatore e validazione Lite/Strict del task packet generato.

---

## 7. Eseguire workflow health check

```powershell
python scripts/check_workflow_health.py
```

Il Workflow Health Check e' read-only e controlla documenti, riferimenti centrali, template e sicurezza minima degli script operativi.

---

## 7.1 Mostrare workflow status dashboard

```powershell
python scripts/show_workflow_status.py
```

La dashboard mostra branch corrente, working tree, commit recenti, documenti/script centrali e prossimi controlli locali.

---

## 7.2 Valutare release readiness per pilot

```text
docs/40_RELEASE_READINESS.md
templates/codex_tasks/release_readiness_checklist.md
```

Usare questa checklist prima di applicare il metodo a un progetto reale. La readiness vale per pilot interno local-first, non per release pubblica, SaaS o distribuzione esterna.

## 7.3 Preparare existing project pilot onboarding

```text
docs/41_EXISTING_PROJECT_PILOT_ONBOARDING.md
templates/codex_tasks/existing_project_intake_template.md
templates/codex_tasks/first_pilot_step_packet_template.md
```

Usare questi file dopo la readiness e prima del primo pilot reale. Servono a fare Project Intake, fotografare Git, test, documentazione e rischi, poi scegliere un primo step pilota piccolo e reversibile.

## 7.4 Preparare ASF Next Step Runner

```powershell
python scripts/asf_next_step.py --mode prepare --profile AI_Software_Factory --step 340 --title "ASF Runner Verification Pack Hardening" --branch step-340-asf-runner-verification-pack-hardening --objective "Harden verification pack generation for the ASF runner."
```

Il runner genera `task_packet.md`, `codex_handoff.md`, `runner_report.md` e `verification_pack.md` sotto `tmp/asf_next_step/`.

`--profile` legge default locali da `config/asf_project_profiles.json`. Non invoca Codex, non modifica il repo target e non fa commit, push, PR o merge.

## 7.5 Fare intake del report Codex

Salvare manualmente il report finale Codex in un file Markdown, poi eseguire:

```powershell
python scripts/asf_codex_report_intake.py --report-path tmp/asf_codex_reports/step_340_codex_report.md --project-name AI_Software_Factory --repo-path . --step 340
```

L'intake genera `codex_report_intake.md` sotto `tmp/asf_codex_intake/`. Classifica il report come `PASS`, `WARNING` o `FAIL`, ma non equivale ad approval.

## 7.6 Generare closure pack human-gated

```powershell
python scripts/asf_generate_closure_pack.py --project-name AI_Software_Factory --repo-path . --step 340 --branch step-340-360-asf-runner-automation-readiness-pack --commit-message "340-360) add ASF runner automation readiness pack" --pr-title "340-360) ASF Runner Automation Readiness Pack"
```

Il closure pack genera `closure_pack.md` sotto `tmp/asf_closure_pack/`. I comandi di commit, push, PR e merge sono testo manuale human-gated e non vengono eseguiti dallo script.

## 7.7 Generare Human Approval Gate

```powershell
python scripts/asf_human_approval_gate.py --project-name AI_Software_Factory --repo-path . --step 390 --branch step-370-390-asf-automation-bridge-pack --codex-report-intake tmp/asf_codex_intake/AI_Software_Factory/step_390/codex_report_intake.md --verification-pack tmp/asf_next_step/AI_Software_Factory/step_390/verification_pack.md --output-dir tmp/asf_approval_gate
```

Il gate genera `human_approval_gate.md` sotto `tmp/asf_approval_gate/` e propone `GO`, `WARNING`, `HOLD` o `NO-GO`. Non approva automaticamente lo step.

## 7.8 Generare Codex invocation dry-run pack

```powershell
python scripts/asf_codex_invocation_dry_run.py --project-name AI_Software_Factory --repo-path . --step 390 --branch step-370-390-asf-automation-bridge-pack --handoff-path tmp/asf_next_step/AI_Software_Factory/step_390/codex_handoff.md --approval-gate tmp/asf_approval_gate/AI_Software_Factory/step_390/human_approval_gate.md --output-dir tmp/asf_codex_invocation
```

Il dry-run pack genera `codex_invocation_dry_run.md` e `codex_exec_preview.ps1` sotto `tmp/asf_codex_invocation/`. Il comando `codex exec` e' solo testo di preview e non viene eseguito.

## 7.9 Preparare Codex read-only invocation prototype

Default preview:

```powershell
python scripts/asf_codex_readonly_invoke.py --mode preview --project-name AI_Software_Factory --repo-path . --step 400 --branch step-400-420-asf-codex-readonly-invocation-prototype-pack --handoff-path tmp/asf_next_step/AI_Software_Factory/step_400/codex_handoff.md --approval-gate tmp/asf_approval_gate/AI_Software_Factory/step_400/human_approval_gate.md
```

Capture output simulati o reali:

```powershell
python scripts/asf_codex_result_capture.py --project-name AI_Software_Factory --repo-path . --step 400 --invocation-dir tmp/asf_codex_readonly_invocation/AI_Software_Factory/step_400
```

Safety gate:

```powershell
python scripts/asf_codex_readonly_safety_gate.py --project-name AI_Software_Factory --repo-path . --step 400 --result-capture tmp/asf_codex_result_capture/AI_Software_Factory/step_400/codex_result_capture.md
```

`execute-readonly` richiede conferma esplicita, approval gate `GO`, working tree `CLEAN` e sandbox read-only. Non usarlo come autorizzazione a workspace-write.

## 7.10 Review first manual trial

Documenti:

```text
docs/55_ASF_CODEX_READONLY_FIRST_MANUAL_TRIAL.md
docs/56_ASF_CODEX_READONLY_FIRST_TRIAL_RESULTS.md
```

Output locale previsto:

```text
tmp/asf_step_430_first_manual_trial/
```

Il first manual trial collega runner prepare, Human Approval Gate, preview read-only, result capture e safety gate. Se il gate non e' `GO` o la working tree target non e' `CLEAN`, restare in preview/capture simulato: non e' fallimento del trial e non autorizza workspace-write.

## 7.11 Review clean target trial

Documenti:

```text
docs/57_ASF_CODEX_READONLY_CLEAN_TARGET_TRIAL.md
docs/58_ASF_CODEX_READONLY_CLEAN_TARGET_TRIAL_RESULTS.md
```

Output locale previsto:

```text
tmp/asf_clean_target_trial/step_440/
```

Il clean target trial usa una repo temporanea sotto `tmp/`, Human Approval Gate `GO`, preview, eventuale `execute-readonly`, result capture e safety gate. Anche con exit code `0`, stderr non vuoto o output incompleto devono restare `WARNING_REVIEW_REQUIRED`.

## 7.12 Preparare repeatable trial pack

Prepare-only:

```powershell
python scripts/asf_codex_readonly_repeatable_trial.py --mode prepare-only --trial-name step_450_prepare_only --step 450
```

Run diagnostico con Codex non disponibile:

```powershell
python scripts/asf_codex_readonly_repeatable_trial.py --mode run-readonly-if-safe --trial-name step_450_missing_codex --step 450 --codex-command codex-command-that-does-not-exist --confirm-readonly-execution YES_I_APPROVE_READONLY_CODEX_EXECUTION
```

Compare:

```powershell
python scripts/asf_codex_readonly_trial_compare.py --reports tmp/asf_codex_readonly_repeatable_trials/step_450_prepare_only/reports/repeatable_trial_report.md tmp/asf_codex_readonly_repeatable_trials/step_450_missing_codex/reports/repeatable_trial_report.md --output-dir tmp/asf_codex_readonly_repeatable_trials/comparison
```

Il Repeatable Trial Pack usa repo sintetiche sotto `tmp/`, richiede approval gate GO e target CLEAN per l'esecuzione, gestisce `CODEX_NOT_AVAILABLE` e non autorizza workspace-write.

## 7.13 Generare OpenAI API Adapter evidence

Check ambiente senza esporre chiavi:

```powershell
python scripts/asf_openai_api_adapter.py --mode check-env --output-json tmp/asf_openai_adapter_env.json
```

Dry-run payload Responses-style:

```powershell
python scripts/asf_openai_api_adapter.py --mode dry-run --input "ping" --output-json tmp/asf_openai_adapter_dry_run.json
```

Mock deterministico:

```powershell
python scripts/asf_openai_api_adapter.py --mode mock --input "ping" --output-json tmp/asf_openai_adapter_mock.json
```

Questi comandi non usano network, non richiedono `OPENAI_API_KEY`, non usano SDK OpenAI e devono riportare `network_performed: false`.

## 7.14 Generare OpenAI API Adapter live boundary gate

Gate report no-network con credenziale assente:

```powershell
python scripts/asf_openai_api_adapter.py --mode live --input "ping" --output-json tmp/asf_openai_live_boundary_gate.json
```

Gate report per readiness futura, sempre senza chiamata live:

```powershell
$env:OPENAI_API_KEY = "<set locally, never paste into chat or commit>"
$env:ASF_OPENAI_LIVE_ENABLED = "1"
python scripts/asf_openai_api_adapter.py --mode live --input "ping" --allow-live --live-confirm I_UNDERSTAND_THIS_CALLS_OPENAI_API --output-json tmp/asf_openai_live_boundary_gate_ready.json
```

L'esito `LIVE_READY_FOR_SEPARATE_SMOKE_STEP` non esegue una chiamata OpenAI. Lo STEP 510 deve riportare `network_performed: false`, `network_call_performed: false` e `LIVE_CALLS_NOT_IMPLEMENTED_IN_STEP_510`.

## 7.15 Eseguire OpenAI API Adapter first controlled live smoke

La smoke live e' permessa solo se tutti i test locali sono passati, la API key e' impostata localmente e i gate espliciti sono presenti.

Preflight no-network:

```powershell
$env:OPENAI_API_KEY = "<your local OpenAI API key>"
$env:ASF_OPENAI_LIVE_ENABLED = "1"
python scripts/asf_openai_api_adapter.py --mode live --gate-only --allow-live --live-confirm I_UNDERSTAND_THIS_CALLS_OPENAI_API --input "Return exactly ASF_OPENAI_LIVE_SMOKE_OK." --reasoning-effort none --text-verbosity low --max-output-tokens 32 --output-json tmp/asf_openai_live_smoke_gate.json --output-markdown tmp/asf_openai_live_smoke_gate.md
```

Una sola chiamata live, senza retry automatico:

```powershell
python scripts/asf_openai_api_adapter.py --mode live --allow-live --live-confirm I_UNDERSTAND_THIS_CALLS_OPENAI_API --input "Return exactly ASF_OPENAI_LIVE_SMOKE_OK." --reasoning-effort none --text-verbosity low --max-output-tokens 32 --output-json tmp/asf_openai_live_smoke_result.json --output-markdown tmp/asf_openai_live_smoke_result.md
```

L'evidenza resta sotto `tmp/`, la richiesta usa `store: false` e la chiave non deve comparire in output, log o file.

Dopo STEP 530 i report live includono `status`, `classification`, `safe_details`, `credential_present`, `live_enabled`, `duration_ms` e `timestamp`. Per step di hardening risultato usare solo test mockati: Codex non deve eseguire chiamate live reali.

## 7.16 Preparare OpenAI API Adapter controlled live execution pack

Dry-run default, senza rete e senza richiedere credenziali reali:

```powershell
python scripts/asf_openai_controlled_live_execution_pack.py
```

Mock provider no-network, solo per validare gate e artifact:

```powershell
$env:OPENAI_API_KEY = "<set in environment, never printed>"
$env:ASF_OPENAI_LIVE_ENABLED = "1"
python scripts/asf_openai_controlled_live_execution_pack.py --execution-mode mock --confirm-live-openai
```

Live reale futura: usare solo in uno step separato autorizzato da Alberto, con `--execution-mode live`, `ASF_OPENAI_LIVE_ENABLED=1`, `--confirm-live-openai`, artifact sotto `tmp/` e una sola chiamata prevista. Codex non deve eseguire questo comando live.

## 7.17 Eseguire OpenAI API Adapter first authorized live run

Usare solo in uno step autorizzato. Il wrapper passa sempre da `scripts/asf_openai_api_adapter.py` e non crea JSON evidence se il risultato non e' success.

```powershell
$env:OPENAI_API_KEY = "<set locally, never print>"
$env:ASF_OPENAI_LIVE_RUN = "1"
# Optional: $env:ASF_OPENAI_MODEL = "<model id>"
python scripts/asf_openai_first_authorized_live_run.py --live
```

Output versionato:

```text
docs/0560-01-Report_OpenAI_API_Adapter_First_Authorized_Live_Run.md
docs/0560-02-Evidence_OpenAI_API_Live_Run_Sanitized.json
docs/0560-03-Diagnostic_OpenAI_Provider_HTTP_Error_And_Rate_Limit.md
```

Il JSON evidence viene scritto solo se `status=COMPLETATO`, `request_count=1` e il marker `ASF_OPENAI_LIVE_SMOKE_OK` e' presente.

Se il report indica `provider_http_error`, `rate_limited`, `quota_exceeded`, `model_access_denied`, `authentication_error` o `project_limit_or_billing_block`, non ripetere retry manuali nello stesso step. Verificare prima quota, billing, organization/project e accesso modello nella dashboard OpenAI, poi aprire uno step separato autorizzato.

---

## 8. Eseguire Verification Gate

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify.ps1
```

Il Verification Gate resta il controllo locale principale prima del passaggio a commit, push e PR.

---

## 9. Controllare soft guardrails

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\git\check_soft_guardrails.ps1
```

Il controllo e' read-only. Non installa hook e non modifica `core.hooksPath`.

---

## 10. Pre-commit manuale

Comandi di riferimento prima del commit:

```powershell
git status --short
git --no-pager diff --stat
git --no-pager diff --check
python -m pytest
python scripts/check_workflow_health.py
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify.ps1
```

Commit, push, PR e merge sono operazioni di Alberto. Codex non fa commit, Codex non fa push, Codex non apre PR e Codex non fa merge.

---

## 11. Commit / push / PR presidiati

Questi sono comandi di riferimento presidiati, non uno script automatico e non automazione cieca:

```powershell
git add .
git commit -m "240) add workflow quick reference"
git push -u origin step-240-workflow-quick-reference
gh pr create --base main --head step-240-workflow-quick-reference --title "240) Workflow Quick Reference" --body "Adds a short operational quick reference for the AI Software Factory workflow."
```

Alberto decide cosa aggiungere, verifica il diff e lancia questi comandi solo dopo i controlli locali.

---

## 12. PR checks e merge presidiato

```powershell
gh pr status
gh pr checks --watch
gh pr merge --merge --delete-branch
```

Il merge va fatto solo dopo check positivi e revisione del contenuto della PR.

---

## 13. Verifica finale su main

Dopo il merge:

```powershell
git switch main
git pull origin main
python scripts/check_workflow_health.py
python -m pytest
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify.ps1
git status --short
git --no-pager log --oneline --max-count=10
```

Compilare lo Step Closure Report:

```text
docs/37_STEP_CLOSURE_REPORT.md
templates/codex_tasks/step_closure_report_template.md
```

Solo dopo questa verifica lo step puo' essere considerato presente su `main`.

---

## 14. Errori rapidi da evitare

- Partire con uno step nuovo se il precedente non e' su `main`.
- Confondere il report Codex con merge avvenuto: il report Codex non equivale a merge su `main`.
- Ignorare `git status --short`.
- Fare `git reset --hard` senza diagnosi.
- Fare commit direttamente su `main`.
- Far fare commit, push, PR o merge a Codex.
- Saltare `gh pr checks --watch`.
- Saltare Verification Gate.
- Committare file temporanei sotto `tmp/`.

---

## 15. Dove approfondire

- `docs/32_PROMPT_PACKET_LIFECYCLE_CHECKLIST.md`: lifecycle completo dallo step al merge su `main`.
- `docs/33_PROMPT_PACKET_GENERATOR_DEVELOPER_ONBOARDING.md`: onboarding pratico per generator, validazione e ruoli.
- `docs/34_PROJECT_WORKFLOW_INDEX.md`: mappa centrale di documenti, script e template.
- `docs/35_WORKFLOW_HEALTH_CHECK.md`: controllo locale read-only del workflow.
- `docs/37_STEP_CLOSURE_REPORT.md`: standard per distinguere lavoro locale da step chiuso su `main`.
- `docs/38_WORKFLOW_COMMAND_COOKBOOK.md`: ricette operative per casi specifici e troubleshooting.
- `docs/39_WORKFLOW_STATUS_DASHBOARD.md`: snapshot locale read-only di branch, working tree, commit recenti e file workflow.
- `docs/40_RELEASE_READINESS.md`: criteri GO/WARNING/NO-GO per pilot interno local-first.
- `docs/41_EXISTING_PROJECT_PILOT_ONBOARDING.md`: intake e primo task packet pilot per progetto esistente.
- `docs/42_ASF_NEXT_STEP_RUNNER.md`: prepare mode locale per task packet, handoff Codex e report runner.
- `docs/49_ASF_HUMAN_APPROVAL_GATE.md`: gate GO/WARNING/HOLD/NO-GO prima di preview o closure.
- `docs/50_ASF_CODEX_INVOCATION_DESIGN.md`: design della futura invocazione Codex controllata.
- `docs/51_ASF_CODEX_INVOCATION_DRY_RUN_PACK.md`: dry-run pack con preview `codex exec` non eseguita.
- `docs/52_ASF_CODEX_READONLY_INVOCATION_PROTOTYPE.md`: prototipo read-only con default preview.
- `docs/53_ASF_CODEX_INVOCATION_RESULT_CAPTURE.md`: capture di stdout, stderr, exit code e working tree.
- `docs/54_ASF_CODEX_READONLY_SAFETY_GATE.md`: safety gate read-only prima di qualunque step futuro piu' ampio.
- `docs/59_ASF_CODEX_READONLY_REPEATABLE_TRIAL_PACK.md`: repeatable trial pack per run read-only comparabili.
- `docs/60_ASF_CODEX_READONLY_REPEATABLE_TRIAL_RESULTS.md`: risultati STEP 450.
- `docs/70_ASF_PWSH_COMMAND_PACK_SKILL_FINALIZATION.md`: standard canonico PowerShell command pack e skill draft.
- `docs/71_ASF_PWSH_COMMAND_PACK_SKILL_EXPORT_INSTALL.md`: export installabile e installer dry-run/apply della skill comune.
- `docs/73_LAST_DEPRECATION_4_DIGIT_ARTIFACT_NAMING_STANDARD.md`: deprecazione `LAST-*` e standard artefatti `NNNN-II-Tipo_Nome.ext`.
- `docs/65_ASF_OPENAI_API_ADAPTER.md`: adapter OpenAI dry-run/mock senza chiamate live.
- `docs/66_ASF_OPENAI_API_ADAPTER_LIVE_BOUNDARY_CREDENTIAL_GATE.md`: live boundary e credential gate no-network.
- `docs/67_ASF_OPENAI_API_ADAPTER_FIRST_CONTROLLED_LIVE_SMOKE_TEST.md`: prima smoke live controllata.
- `docs/68_ASF_OPENAI_API_ADAPTER_LIVE_SMOKE_RESULT_HARDENING.md`: schema risultato e classificazioni live smoke.
- `docs/69_ASF_OPENAI_API_ADAPTER_CONTROLLED_LIVE_EXECUTION_PACK.md`: pack dry-run-default per futura live controllata.
- `docs/20_VERIFICATION_GATE.md`: criteri di verifica locale e CI.
- `docs/28_PROMPT_PACKET_VALIDATION_STRICT_MODE.md`: dettagli della validazione Strict.
