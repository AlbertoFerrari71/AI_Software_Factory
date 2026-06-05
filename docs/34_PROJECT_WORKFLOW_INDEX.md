# Project Workflow Index

## 1. Scopo

Questo documento e' l'indice operativo centrale del workflow AI Software Factory.

Serve a capire rapidamente quale documento leggere, quale script usare, quale template copiare, quale checklist seguire e quale verifica eseguire per una specifica attivita' del Codex Alchemy Method.

L'indice orienta il lavoro. Non sostituisce i documenti specifici, il Verification Gate, la Prompt Packet Lifecycle Checklist o il controllo umano di Alberto.

---

## 2. Mappa rapida: devo fare X

| Attivita' | Documento principale | Script/template collegati | Quando usarlo | Note |
|---|---|---|---|---|
| Capire il metodo generale | `README.md`, `docs/10_ROADMAP.md` | Nessuno | Primo orientamento sul progetto | Roadmap e decision log restano fonti di evoluzione e scelte |
| Creare un Codex Task Packet | `docs/19_PROMPT_PACKET_GENERATOR.md` | `templates/codex_tasks/codex_task_packet_template.md` | Quando serve un task packet controllato | Il packet deve includere scope, forbidden actions e report finale |
| Generare un Task Packet via CLI | `docs/29_PROMPT_PACKET_GENERATOR_CLI_HARDENING.md` | `scripts/generate_task_packet.py` | Quando step, titolo, branch e obiettivo sono gia' chiari | Produce una bozza Markdown da rivedere |
| Usare il wrapper PowerShell | `docs/30_PROMPT_PACKET_GENERATOR_PACKAGING.md` | `scripts/generate_task_packet.ps1` | Quando si lavora in PowerShell su Windows | Il wrapper delega alla CLI Python |
| Validare in Lite Mode | `docs/26_PROMPT_PACKET_VALIDATION_LITE.md` | `scripts/validate_task_packet.py` | Check rapido su task packet salvato | Non sostituisce revisione umana |
| Validare in Strict Mode | `docs/28_PROMPT_PACKET_VALIDATION_STRICT_MODE.md` | `scripts/validate_task_packet.py --strict` | Task importanti, complessi o sensibili | Strict Mode resta manuale e opt-in |
| Usare golden samples | `docs/27_PROMPT_PACKET_GOLDEN_SAMPLES.md` | `examples/task_packets/valid/`, `examples/task_packets/invalid/` | Quando si modifica validatore o template | Copiare solo i sample validi come riferimento |
| Eseguire il Release Smoke Workflow | `docs/31_PROMPT_PACKET_GENERATOR_RELEASE_SMOKE_WORKFLOW.md` | `scripts/smoke_prompt_packet_release.ps1` | Dopo modifiche a generator, wrapper o packaging | Verifica generazione, Lite Mode e Strict Mode |
| Seguire il lifecycle completo | `docs/32_PROMPT_PACKET_LIFECYCLE_CHECKLIST.md` | `templates/codex_tasks/prompt_packet_lifecycle_checklist.md` | Da preparazione step a merge su `main` | Alberto esegue commit, push, PR e merge |
| Compilare Step Closure Report | `docs/37_STEP_CLOSURE_REPORT.md` | `templates/codex_tasks/step_closure_report_template.md` | Dopo merge, pull di `main` e test finale | Distingue report Codex locale da step chiuso su `main` |
| Fare Developer Onboarding | `docs/33_PROMPT_PACKET_GENERATOR_DEVELOPER_ONBOARDING.md` | Comandi PowerShell documentati | Quando una persona interna deve iniziare a usare il workflow | Entry point pratico per generator e checklist |
| Consultare Workflow Quick Reference | `docs/36_WORKFLOW_QUICK_REFERENCE.md` | Comandi PowerShell documentati | Quando serve una scheda breve per uso quotidiano | Non sostituisce la lifecycle checklist |
| Consultare Workflow Command Cookbook | `docs/38_WORKFLOW_COMMAND_COOKBOOK.md` | Ricette PowerShell/Git/Python documentate | Quando serve gestire scenari specifici o troubleshooting | Non automatizza commit, push, PR o merge |
| Usare Workflow Status Dashboard | `docs/39_WORKFLOW_STATUS_DASHBOARD.md` | `scripts/show_workflow_status.py` | Quando serve vedere branch, working tree, commit recenti e file workflow presenti | Read-only; non usa GitHub API |
| Valutare Release Readiness | `docs/40_RELEASE_READINESS.md` | `templates/codex_tasks/release_readiness_checklist.md` | Prima di applicare il metodo a un progetto pilota reale | Readiness per pilot interno, non release pubblica o SaaS |
| Preparare Existing Project Pilot Onboarding | `docs/41_EXISTING_PROJECT_PILOT_ONBOARDING.md` | `templates/codex_tasks/existing_project_intake_template.md`, `templates/codex_tasks/first_pilot_step_packet_template.md` | Dopo readiness e prima del primo pilot reale | Intake, fotografia repo, rischi e primo task packet pilot |
| Preparare ASF Next Step Runner | `docs/42_ASF_NEXT_STEP_RUNNER.md` | `scripts/asf_next_step.py`, `templates/codex_tasks/asf_next_step_runner_handoff_template.md` | Quando step, titolo, branch e obiettivo sono chiari | Prepara task packet, handoff, report e Verification Pack senza invocare Codex |
| Usare ASF Runner Project Profiles | `docs/43_ASF_RUNNER_PROJECT_PROFILES.md` | `config/asf_project_profiles.json` | Quando il progetto target ha default riusabili | Riduce argomenti ripetitivi e porta note safety nel packet |
| Interpretare ASF Runner Codex Handoff Improvements | `docs/44_ASF_RUNNER_CODEX_HANDOFF_IMPROVEMENTS.md` | `templates/codex_tasks/asf_next_step_runner_handoff_template.md` | Quando si copia l'handoff generato verso Codex | Mantiene FASE 1, FASE 2 e Human gate espliciti |
| Usare ASF Runner Verification Pack | `docs/45_ASF_RUNNER_VERIFICATION_PACK.md` | `templates/codex_tasks/asf_runner_verification_pack_template.md` | Quando si vogliono controlli read-only prima e dopo Codex | Non contiene automazione commit, push, PR o merge |
| Usare ASF Runner Verification Pack Hardening | `docs/46_ASF_RUNNER_VERIFICATION_PACK_HARDENING.md` | `scripts/asf_next_step.py` | Quando serve seguire tutto il ciclo prima/dopo Codex e prima/dopo PR | Aggiunge report checks, PR checks handling, LF/CRLF handling e human gates |
| Fare ASF Codex Report Intake | `docs/47_ASF_CODEX_REPORT_INTAKE.md` | `scripts/asf_codex_report_intake.py`, `templates/codex_tasks/asf_codex_report_intake_template.md` | Dopo aver salvato il report finale Codex in Markdown | Produce intake read-only, non approval |
| Generare ASF Human-Gated Closure Pack | `docs/48_ASF_HUMAN_GATED_CLOSURE_PACK.md` | `scripts/asf_generate_closure_pack.py`, `templates/codex_tasks/asf_human_gated_closure_pack_template.md` | Dopo report intake e review umana | Genera comandi manuali, non li esegue |
| Generare ASF Human Approval Gate | `docs/49_ASF_HUMAN_APPROVAL_GATE.md` | `scripts/asf_human_approval_gate.py`, `templates/codex_tasks/asf_human_approval_gate_template.md` | Dopo intake, verification pack o closure pack, prima di preview/chiusura | Produce GO/WARNING/HOLD/NO-GO, non approval automatica |
| Leggere ASF Codex Invocation Design | `docs/50_ASF_CODEX_INVOCATION_DESIGN.md` | Nessuno | Prima di progettare invocazioni Codex controllate | Definisce livelli, sandbox, input/output e stop condition |
| Generare ASF Codex Invocation Dry Run Pack | `docs/51_ASF_CODEX_INVOCATION_DRY_RUN_PACK.md` | `scripts/asf_codex_invocation_dry_run.py`, `templates/codex_tasks/asf_codex_invocation_dry_run_template.md` | Dopo Human Approval Gate e prima di qualunque prototipo Codex | Genera preview `codex exec`, non la esegue |
| Preparare ASF Codex Read-Only Invocation Prototype | `docs/52_ASF_CODEX_READONLY_INVOCATION_PROTOTYPE.md` | `scripts/asf_codex_readonly_invoke.py`, `templates/codex_tasks/asf_codex_readonly_invocation_template.md` | Dopo dry-run pack e Human Approval Gate `GO` | Default preview; execute-readonly solo con conferma esplicita e sandbox read-only |
| Fare ASF Codex Invocation Result Capture | `docs/53_ASF_CODEX_INVOCATION_RESULT_CAPTURE.md` | `scripts/asf_codex_result_capture.py`, `templates/codex_tasks/asf_codex_invocation_result_capture_template.md` | Dopo una invocation read-only o output simulati | Normalizza stdout, stderr, exit code e working tree in PASS/WARNING/FAIL |
| Valutare ASF Codex Read-Only Safety Gate | `docs/54_ASF_CODEX_READONLY_SAFETY_GATE.md` | `scripts/asf_codex_readonly_safety_gate.py`, `templates/codex_tasks/asf_codex_readonly_safety_gate_template.md` | Dopo result capture | Decide GO_TO_WORKSPACE_WRITE_DESIGN/WARNING/HOLD/NO_GO senza autorizzare execution diretta |
| Eseguire ASF Codex Read-Only First Manual Trial | `docs/55_ASF_CODEX_READONLY_FIRST_MANUAL_TRIAL.md`, `docs/56_ASF_CODEX_READONLY_FIRST_TRIAL_RESULTS.md` | `scripts/asf_next_step.py`, `scripts/asf_human_approval_gate.py`, `scripts/asf_codex_readonly_invoke.py`, `scripts/asf_codex_result_capture.py`, `scripts/asf_codex_readonly_safety_gate.py` | Dopo il pack 400-420 su `main` | Primo trial locale; resta preview-only se gate non e' `GO`; non autorizza workspace-write |
| Eseguire ASF Codex Read-Only Clean Target Trial | `docs/57_ASF_CODEX_READONLY_CLEAN_TARGET_TRIAL.md`, `docs/58_ASF_CODEX_READONLY_CLEAN_TARGET_TRIAL_RESULTS.md` | `scripts/asf_human_approval_gate.py`, `scripts/asf_codex_readonly_invoke.py`, `scripts/asf_codex_result_capture.py`, `scripts/asf_codex_readonly_safety_gate.py` | Dopo STEP 430 su `main` | Usa repo temporanea sotto `tmp/`; execute-readonly solo con gate `GO`, target `CLEAN` e sandbox read-only |
| Eseguire ASF Codex Read-Only Repeatable Trial Pack / ASF Codex Read-Only Trial Compare | `docs/59_ASF_CODEX_READONLY_REPEATABLE_TRIAL_PACK.md`, `docs/60_ASF_CODEX_READONLY_REPEATABLE_TRIAL_RESULTS.md` | `scripts/asf_codex_readonly_repeatable_trial.py`, `scripts/asf_codex_readonly_trial_compare.py` | Dopo STEP 440 su `main` | Prepara trial ripetibili, gestisce `CODEX_NOT_AVAILABLE` e confronta run senza autorizzare workspace-write |
| Eseguire ASF Codex Read-Only Diagnostics Hardening / ASF Codex CLI Compatibility Probe / ASF Codex Read-Only Decision Gate | `docs/61_ASF_CODEX_READONLY_DIAGNOSTICS_HARDENING.md`, `docs/62_ASF_CODEX_CLI_COMPATIBILITY_PROBE.md`, `docs/63_ASF_CODEX_READONLY_DECISION_GATE.md` | `scripts/asf_codex_readonly_diagnostics.py`, `scripts/asf_codex_cli_compatibility_probe.py`, `scripts/asf_codex_readonly_decision_gate.py` | Dopo STEP 450 su `main` | Produce JSON stabile per diagnosi, compatibilita' CLI e decisione conservativa senza autorizzare workspace-write |
| Eseguire Verification Gate | `docs/20_VERIFICATION_GATE.md` | `scripts/verify.ps1` | Prima di commit/push/PR e dopo merge quando richiesto | Include test, `git diff --check`, `git status --short` |
| Controllare Documentation Sync | `docs/21_DOCUMENTATION_SYNC.md` | Nessuno | Ogni step documentale o operativo | Valuta changelog, roadmap, decisions e documenti specifici |
| Controllare Soft Protection Guardrails | `docs/24_SOFT_PROTECTION_GUARDRAILS.md` | `scripts/git/check_soft_guardrails.ps1` | Prima del commit o come controllo locale | Read-only; non installa hook |
| Eseguire Workflow Health Check | `docs/35_WORKFLOW_HEALTH_CHECK.md` | `scripts/check_workflow_health.py` | Quando workflow docs, script o riferimenti centrali cambiano | Read-only; non sostituisce Verification Gate |
| Gestire troubleshooting Git/PR/merge | `docs/32_PROMPT_PACKET_LIFECYCLE_CHECKLIST.md` | `git status --short`, `gh pr status`, `gh pr checks --watch` | Quando branch, PR o `main` non sono nello stato atteso | Non usare reset distruttivi senza diagnosi |

---

## 3. Workflow ordinario consigliato

Sequenza operativa:

```text
preparazione step -> task packet -> validazione -> Codex -> report -> verifica -> commit -> push -> PR -> checks -> merge -> pull main -> test finale -> prossimo step
```

Il riferimento completo e' `docs/32_PROMPT_PACKET_LIFECYCLE_CHECKLIST.md`.

Regole operative:

- ChatGPT prepara il task packet e coordina il metodo.
- Codex lavora localmente sul branch dedicato.
- Codex non deve fare commit, push, aprire PR o fare merge.
- Codex non modifica GitHub, hook Git o `core.hooksPath`.
- Alberto verifica, committa, pusha, apre la PR, attende i check, esegue il merge, aggiorna `main` e lancia il test finale.
- Il report Codex non equivale a merge su `main`.

---

## 4. Documenti principali

- `docs/19_PROMPT_PACKET_GENERATOR.md`: contratto generale per Prompt Packet, Codex Task Packet e prompt operativi.
- `docs/20_VERIFICATION_GATE.md`: definisce cosa significa che una modifica e' verificata.
- `docs/21_DOCUMENTATION_SYNC.md`: regola per mantenere changelog, roadmap, decision log e documenti specifici allineati.
- `docs/24_SOFT_PROTECTION_GUARDRAILS.md`: fallback locale quando la hard branch protection GitHub non e' disponibile.
- `docs/25_PROMPT_PACKET_HARDENING.md`: sezioni minime, forbidden actions, scope e report finale dei task packet.
- `docs/26_PROMPT_PACKET_VALIDATION_LITE.md`: validazione leggera dei task packet.
- `docs/27_PROMPT_PACKET_GOLDEN_SAMPLES.md`: esempi validi e invalidi per il validatore.
- `docs/28_PROMPT_PACKET_VALIDATION_STRICT_MODE.md`: validazione Strict Mode opzionale.
- `docs/29_PROMPT_PACKET_GENERATOR_CLI_HARDENING.md`: uso e limiti della CLI Python del generatore.
- `docs/30_PROMPT_PACKET_GENERATOR_PACKAGING.md`: packaging locale, wrapper PowerShell e sample generati.
- `docs/31_PROMPT_PACKET_GENERATOR_RELEASE_SMOKE_WORKFLOW.md`: smoke workflow locale del generatore.
- `docs/32_PROMPT_PACKET_LIFECYCLE_CHECKLIST.md`: ciclo operativo completo fino allo step su `main`.
- `docs/33_PROMPT_PACKET_GENERATOR_DEVELOPER_ONBOARDING.md`: onboarding per sviluppatori e utilizzatori interni.
- `docs/35_WORKFLOW_HEALTH_CHECK.md`: controllo locale read-only sulla navigabilita' del workflow.
- `docs/36_WORKFLOW_QUICK_REFERENCE.md`: scheda breve con comandi quotidiani e handoff presidiato.
- `docs/37_STEP_CLOSURE_REPORT.md`: standard per dichiarare uno step chiuso e verificato su `main`.
- `docs/38_WORKFLOW_COMMAND_COOKBOOK.md`: ricettario di comandi per scenari operativi e troubleshooting.
- `docs/39_WORKFLOW_STATUS_DASHBOARD.md`: dashboard locale read-only per branch, working tree, commit recenti e file workflow centrali.
- `docs/40_RELEASE_READINESS.md`: checklist go/warning/no-go per pilot interno local-first su un progetto reale.
- `docs/41_EXISTING_PROJECT_PILOT_ONBOARDING.md`: protocollo di intake per applicare il metodo a un progetto esistente gia' avviato.
- `docs/42_ASF_NEXT_STEP_RUNNER.md`: runner locale prepare mode per generare task packet, handoff Codex e report senza modificare il repo target.
- `docs/43_ASF_RUNNER_PROJECT_PROFILES.md`: profili progetto locali per il runner.
- `docs/44_ASF_RUNNER_CODEX_HANDOFF_IMPROVEMENTS.md`: struttura dell'handoff Codex migliorato.
- `docs/45_ASF_RUNNER_VERIFICATION_PACK.md`: pacchetto di verifiche read-only consigliate dal runner.
- `docs/46_ASF_RUNNER_VERIFICATION_PACK_HARDENING.md`: hardening del Verification Pack lungo tutto il ciclo.
- `docs/47_ASF_CODEX_REPORT_INTAKE.md`: intake read-only del report finale Codex.
- `docs/48_ASF_HUMAN_GATED_CLOSURE_PACK.md`: closure pack con comandi manuali e gate umani.
- `docs/49_ASF_HUMAN_APPROVAL_GATE.md`: approval gate read-only con decisione GO/WARNING/HOLD/NO-GO.
- `docs/50_ASF_CODEX_INVOCATION_DESIGN.md`: design dei livelli di futura invocazione Codex controllata.
- `docs/51_ASF_CODEX_INVOCATION_DRY_RUN_PACK.md`: dry-run pack con preview `codex exec` non eseguita.
- `docs/52_ASF_CODEX_READONLY_INVOCATION_PROTOTYPE.md`: prototipo preview/execute-readonly con approval gate e sandbox read-only.
- `docs/53_ASF_CODEX_INVOCATION_RESULT_CAPTURE.md`: normalizzazione stdout, stderr, exit code e classificazione PASS/WARNING/FAIL.
- `docs/54_ASF_CODEX_READONLY_SAFETY_GATE.md`: safety gate read-only per decidere se progettare uno step futuro piu' ampio.
- `docs/55_ASF_CODEX_READONLY_FIRST_MANUAL_TRIAL.md`: procedura del primo trial manuale controllato Codex read-only.
- `docs/56_ASF_CODEX_READONLY_FIRST_TRIAL_RESULTS.md`: risultati del primo trial, inclusi preview-only, capture simulato e safety gate.
- `docs/57_ASF_CODEX_READONLY_CLEAN_TARGET_TRIAL.md`: procedura del trial read-only su repo temporanea pulita sotto `tmp/`.
- `docs/58_ASF_CODEX_READONLY_CLEAN_TARGET_TRIAL_RESULTS.md`: risultati del clean target trial, inclusi execute-readonly, capture e safety gate.
- `docs/59_ASF_CODEX_READONLY_REPEATABLE_TRIAL_PACK.md`: runbook del Repeatable Trial Pack read-only.
- `docs/60_ASF_CODEX_READONLY_REPEATABLE_TRIAL_RESULTS.md`: risultati STEP 450, inclusa gestione `CODEX_NOT_AVAILABLE`.
- `docs/61_ASF_CODEX_READONLY_DIAGNOSTICS_HARDENING.md`: ASF Codex Read-Only Diagnostics Hardening con diagnostica JSON stabile per evidenze read-only.
- `docs/62_ASF_CODEX_CLI_COMPATIBILITY_PROBE.md`: ASF Codex CLI Compatibility Probe metadata-only.
- `docs/63_ASF_CODEX_READONLY_DECISION_GATE.md`: ASF Codex Read-Only Decision Gate conservativo su diagnostica, CLI probe e trial ripetibili.

---

## 5. Script principali

- `scripts/generate_task_packet.py`: CLI Python del Prompt Packet Generator.
- `scripts/generate_task_packet.ps1`: wrapper PowerShell sottile per la CLI Python.
- `scripts/validate_task_packet.py`: validatore Lite Mode e Strict Mode dei task packet.
- `scripts/smoke_prompt_packet_release.ps1`: release smoke workflow locale del generatore.
- `scripts/verify.ps1`: Verification Gate locale.
- `scripts/git/check_soft_guardrails.ps1`: controllo read-only dei Soft Protection Guardrails.
- `scripts/check_workflow_health.py`: controllo read-only di documenti, riferimenti e script operativi del workflow.
- `scripts/show_workflow_status.py`: dashboard read-only dello stato workflow locale.
- `scripts/asf_next_step.py`: runner prepare mode locale per il prossimo step.
- `scripts/asf_codex_report_intake.py`: intake read-only di un report finale Codex salvato in Markdown.
- `scripts/asf_generate_closure_pack.py`: generatore di closure pack Markdown human-gated.
- `scripts/asf_human_approval_gate.py`: gate read-only per classificare GO/WARNING/HOLD/NO-GO.
- `scripts/asf_codex_invocation_dry_run.py`: generatore di preview dry-run per futura invocazione Codex controllata.
- `scripts/asf_codex_readonly_invoke.py`: preview e execute-readonly human-approved con output sotto `tmp/`.
- `scripts/asf_codex_readonly_repeatable_trial.py`: orchestratore repeatable per trial read-only su repo sintetica temporanea.
- `scripts/asf_codex_result_capture.py`: capture read-only di stdout, stderr, exit code e working tree.
- `scripts/asf_codex_readonly_safety_gate.py`: safety gate read-only su result capture.
- `scripts/asf_codex_readonly_trial_compare.py`: confronto Markdown di due o piu' report repeatable trial.
- `scripts/asf_codex_readonly_diagnostics.py`: diagnostica JSON stabile per report read-only.
- `scripts/asf_codex_cli_compatibility_probe.py`: probe metadata-only del Codex CLI locale.
- `scripts/asf_codex_readonly_decision_gate.py`: decision gate conservativo per progressione read-only.

Questi script non devono essere usati per automatizzare commit, push, PR o merge.

Config centrale:

- `config/asf_project_profiles.json`: profili locali per ASF Next Step Runner, senza secret e senza autorizzare azioni aggiuntive.

---

## 6. Template principali

- `templates/codex_tasks/codex_task_packet_template.md`: template centrale del Codex Task Packet.
- `templates/codex_tasks/prompt_packet_lifecycle_checklist.md`: checklist spuntabile per seguire il lifecycle operativo.
- `templates/codex_tasks/step_closure_report_template.md`: template compilabile per chiusura step e conferma su `main`.
- `templates/codex_tasks/release_readiness_checklist.md`: template compilabile per valutare GO, WARNING o NO-GO di un pilot.
- `templates/codex_tasks/existing_project_intake_template.md`: template compilabile per Project Intake di un progetto esistente.
- `templates/codex_tasks/first_pilot_step_packet_template.md`: template per creare il primo task packet pilot piccolo e reversibile.
- `templates/codex_tasks/asf_next_step_runner_handoff_template.md`: struttura handoff manuale da copiare in Codex.
- `templates/codex_tasks/asf_runner_verification_pack_template.md`: struttura del Verification Pack read-only del runner.
- `templates/codex_tasks/asf_codex_report_intake_template.md`: struttura dell'intake report Codex.
- `templates/codex_tasks/asf_human_gated_closure_pack_template.md`: struttura del closure pack human-gated.
- `templates/codex_tasks/asf_human_approval_gate_template.md`: struttura del report Human Approval Gate.
- `templates/codex_tasks/asf_codex_invocation_dry_run_template.md`: struttura del dry-run pack per preview Codex.
- `templates/codex_tasks/asf_codex_readonly_invocation_template.md`: struttura del prototipo read-only invocation.
- `templates/codex_tasks/asf_codex_invocation_result_capture_template.md`: struttura del result capture.
- `templates/codex_tasks/asf_codex_readonly_safety_gate_template.md`: struttura del safety gate read-only.
- `templates/codex_tasks/asf_codex_readonly_repeatable_trial_template.md`: struttura del report repeatable trial.
- `templates/codex_tasks/asf_codex_readonly_trial_compare_template.md`: struttura del report di confronto trial.
- `templates/codex_tasks/asf_codex_readonly_diagnostics_template.md`: template per diagnostica read-only.
- `templates/codex_tasks/asf_codex_cli_compatibility_probe_template.md`: template per probe CLI metadata-only.
- `templates/codex_tasks/asf_codex_readonly_decision_gate_template.md`: template per decision gate read-only.

---

## 7. Sequenze operative pronte

Generare un task packet strict-ready:

```powershell
python scripts/generate_task_packet.py --step 220 --title "Project Workflow Index" --branch step-220-project-workflow-index --objective "Create the central project workflow index." --output tmp/generated_step_220_task_packet.md --force --strict-ready
```

Validare in Lite Mode:

```powershell
python scripts/validate_task_packet.py tmp/generated_step_220_task_packet.md
```

Validare in Strict Mode:

```powershell
python scripts/validate_task_packet.py --strict tmp/generated_step_220_task_packet.md
```

Eseguire il Release Smoke Workflow:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\smoke_prompt_packet_release.ps1
```

Eseguire il Verification Gate:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify.ps1
```

Eseguire il Workflow Health Check:

```powershell
python scripts/check_workflow_health.py
```

Controllare Soft Protection Guardrails:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\git\check_soft_guardrails.ps1
```

Controllare stato Git finale:

```powershell
git status --short
git diff --check
```

Per una scheda compatta con i comandi piu' usati, usare `docs/36_WORKFLOW_QUICK_REFERENCE.md`.

Per formalizzare la chiusura dello step, usare `docs/37_STEP_CLOSURE_REPORT.md`.

Per scenari operativi specifici e troubleshooting, usare `docs/38_WORKFLOW_COMMAND_COOKBOOK.md`.

Per uno snapshot locale rapido del workflow, usare `docs/39_WORKFLOW_STATUS_DASHBOARD.md`.

Per decidere se avviare un pilot interno su un progetto reale, usare `docs/40_RELEASE_READINESS.md`.

Per preparare intake, rischio e primo task packet pilot su un progetto esistente, usare `docs/41_EXISTING_PROJECT_PILOT_ONBOARDING.md`.

Per preparare automaticamente task packet, handoff e report temporanei del prossimo step senza invocare Codex, usare `docs/42_ASF_NEXT_STEP_RUNNER.md`.

Per valutare l'approvazione umana prima della preview di invocazione, usare `docs/49_ASF_HUMAN_APPROVAL_GATE.md`.

Per generare una preview dry-run non eseguita di futura invocazione Codex, usare `docs/51_ASF_CODEX_INVOCATION_DRY_RUN_PACK.md`.

Per preparare il primo prototipo Codex read-only con default preview, usare `docs/52_ASF_CODEX_READONLY_INVOCATION_PROTOTYPE.md`.

Per normalizzare stdout/stderr/exit code e valutare il safety gate read-only, usare `docs/53_ASF_CODEX_INVOCATION_RESULT_CAPTURE.md` e `docs/54_ASF_CODEX_READONLY_SAFETY_GATE.md`.

Per il primo trial manuale controllato della pipeline Codex read-only, usare `docs/55_ASF_CODEX_READONLY_FIRST_MANUAL_TRIAL.md` e registrare l'esito in `docs/56_ASF_CODEX_READONLY_FIRST_TRIAL_RESULTS.md`.

Per il clean target trial con repo temporanea sotto `tmp/`, usare `docs/57_ASF_CODEX_READONLY_CLEAN_TARGET_TRIAL.md` e registrare l'esito in `docs/58_ASF_CODEX_READONLY_CLEAN_TARGET_TRIAL_RESULTS.md`.

Per preparare o ripetere un trial read-only confrontabile, usare `docs/59_ASF_CODEX_READONLY_REPEATABLE_TRIAL_PACK.md` e registrare l'esito in `docs/60_ASF_CODEX_READONLY_REPEATABLE_TRIAL_RESULTS.md`.

Per confrontare due o piu' run, usare `scripts/asf_codex_readonly_trial_compare.py`.

Per normalizzare evidenze JSON, verificare la compatibilita' CLI e produrre la decisione conservativa, usare `docs/61_ASF_CODEX_READONLY_DIAGNOSTICS_HARDENING.md`, `docs/62_ASF_CODEX_CLI_COMPATIBILITY_PROBE.md` e `docs/63_ASF_CODEX_READONLY_DECISION_GATE.md`.

I comandi di commit, push, PR e merge restano azioni manuali di Alberto e non sono raccolti qui in una sequenza automatica.

---

## 8. Troubleshooting rapido

### Branch locale presente ma remoto assente

Sintomo: il branch esiste localmente, ma GitHub o `gh pr create` non lo trova.

Diagnosi:

```powershell
git branch --show-current
git status --short
gh pr status
```

Correzione manuale tipica:

```powershell
git push -u origin <branch>
```

### PR non creata

Sintomo: il lavoro e' committato e pushato, ma non esiste PR.

Diagnosi:

```powershell
gh pr status
```

Creazione manuale tipica:

```powershell
gh pr create --base main --head <branch>
```

### Main non aggiornato

Sintomo: lo step sembra mergiato su GitHub, ma non compare localmente.

Diagnosi:

```powershell
git switch main
git pull origin main
git --no-pager log --oneline --max-count=12
```

### Working tree sporca su main

Sintomo: `git status --short` mostra modifiche mentre si e' su `main`.

Diagnosi:

```powershell
git status --short
git diff --stat
```

Fermarsi prima di creare un nuovo step. Non usare `git reset --hard` senza diagnosi, senza capire le modifiche e senza decisione esplicita.

### Step successivo bloccato da prerequisito mancante

Sintomo: il task packet richiede uno step precedente su `main`, ma il log non lo mostra.

Correzione: fermarsi. Completare lo step precedente con commit, push, PR, checks, merge, pull di `main` e test finale.

### Warning CRLF/LF non bloccanti

Sintomo: Git segnala conversioni LF/CRLF.

Correzione: considerarli warning non bloccanti se `git diff --check` non segnala whitespace error reali.

### Tmp ignorato

Sintomo: file sotto `tmp/` non appaiono in `git status --short`.

Spiegazione: `tmp/` e' ignorato intenzionalmente. Usarlo per task packet temporanei e prove locali.

### Riferimenti remoti vecchi

Sintomo: branch remoti gia' chiusi compaiono ancora localmente.

Diagnosi e pulizia:

```powershell
git fetch --all --prune
```

Usarlo solo come pulizia dei riferimenti remoti, non come sostituto di diagnosi su branch o PR.

---

## 9. Anti-pattern da evitare

- Iniziare uno step se il precedente non e' su `main`.
- Confondere il report Codex con merge avvenuto.
- Ignorare `git status --short`.
- Fare `git reset --hard` senza diagnosi.
- Fare commit direttamente su `main`.
- Far fare commit, push, PR o merge a Codex.
- Saltare PR checks o `gh pr checks --watch`.
- Saltare Verification Gate.
- Saltare Workflow Health Check quando cambiano documenti o script del workflow.
- Saltare Documentation Sync perche' i test passano.
- Usare il Release Smoke Workflow come sostituto della suite `python -m pytest`.

---

## 10. Relazione con roadmap e decision log

Questo indice orienta l'uso operativo quotidiano del workflow.

La roadmap `docs/10_ROADMAP.md` descrive evoluzione, step completati e prossimi step.

Il decision log `docs/11_DECISIONS.md` registra le decisioni stabili che spiegano perche' il metodo funziona in questo modo.

Quando un futuro step cambia flussi, script, checklist o documenti centrali, aggiornare questo indice solo se il punto di ingresso operativo cambia davvero.
