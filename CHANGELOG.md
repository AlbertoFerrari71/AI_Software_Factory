# Changelog

Formato ispirato a Keep a Changelog, adattato al metodo interno.

---

## [0.39.0] - 2026-06-03

### Added

- MEGA-STEP 370-390 - ASF Automation Bridge Pack.
- Script read-only `scripts/asf_human_approval_gate.py`.
- Script `scripts/asf_codex_invocation_dry_run.py` per generare solo preview dry-run di futura invocazione Codex.
- Documenti `docs/49_ASF_HUMAN_APPROVAL_GATE.md`, `docs/50_ASF_CODEX_INVOCATION_DESIGN.md` e `docs/51_ASF_CODEX_INVOCATION_DRY_RUN_PACK.md`.
- Template `templates/codex_tasks/asf_human_approval_gate_template.md` e `templates/codex_tasks/asf_codex_invocation_dry_run_template.md`.
- Test automatici per Human Approval Gate, Codex Invocation Dry Run Pack e copertura Automation Bridge Pack.

### Changed

- Aggiornati Workflow Health Check e Workflow Status Dashboard per includere i nuovi documenti, script e template.
- Aggiornati Project Workflow Index, Quick Reference, Command Cookbook, Release Readiness, Existing Project Pilot Onboarding e documenti runner con il nuovo ponte verso l'invocazione Codex controllata.
- Aggiornata roadmap: STEP 370, 380 e 390 completati; STEP 400 consigliato come ASF Codex Invocation Read-Only Prototype.
- Aggiornato decision log con la scelta di mantenere l'invocazione Codex al livello dry-run preview.

### Not included

- Nessuna invocazione automatica di Codex.
- Nessuna esecuzione di `codex exec`.
- Nessuna esecuzione automatica di commit, push, PR o merge.
- Nessuna modifica a repository target esterni.
- Nessuna modifica a GitHub o GitHub API.
- Nessuna modifica a CI, hook Git, `core.hooksPath`, dipendenze, secret, `.env`, PATH o profili PowerShell.
- Nessuna modifica a `src/**` o `policies/**`.
- Nessuna pubblicazione PyPI o registry.

---

## [0.36.0] - 2026-05-29

### Added

- MEGA-STEP 340-360 - ASF Runner Automation Readiness Pack.
- Script read-only `scripts/asf_codex_report_intake.py`.
- Script `scripts/asf_generate_closure_pack.py` per generare closure pack Markdown human-gated.
- Documenti `docs/46_ASF_RUNNER_VERIFICATION_PACK_HARDENING.md`, `docs/47_ASF_CODEX_REPORT_INTAKE.md` e `docs/48_ASF_HUMAN_GATED_CLOSURE_PACK.md`.
- Template `templates/codex_tasks/asf_codex_report_intake_template.md` e `templates/codex_tasks/asf_human_gated_closure_pack_template.md`.
- Test automatici per hardening Verification Pack, Codex Report Intake e Human-Gated Closure Pack.

### Changed

- Rafforzato `verification_pack.md` generato da `scripts/asf_next_step.py` con controlli Pre-Codex, Post-Codex, scope checks, report checks, PR checks handling, LF/CRLF handling e human gates.
- Aggiornati Workflow Health Check, Workflow Status Dashboard, Project Workflow Index, Quick Reference e Cookbook con i nuovi strumenti.
- Aggiornata roadmap: STEP 340, 350 e 360 completati; STEP 370 consigliato come ASF Runner Human Approval Gate.
- Aggiornato decision log con la scelta dell'automation readiness pack senza automazione Codex/Git/GitHub.

### Not included

- Nessuna invocazione automatica di Codex.
- Nessuna esecuzione automatica di commit, push, PR o merge.
- Nessuna modifica a repository target esterni.
- Nessuna modifica a GitHub o GitHub API.
- Nessuna modifica a CI, hook Git, `core.hooksPath`, dipendenze, secret, `.env`, PATH o profili PowerShell.

---

## [0.33.0] - 2026-05-29

### Added

- MEGA-STEP 310-330 - ASF Runner Upgrade Pack.
- Config `config/asf_project_profiles.json` con profili iniziali `AI_Software_Factory` e `Family_Photo_Organizer`.
- Documenti `docs/43_ASF_RUNNER_PROJECT_PROFILES.md`, `docs/44_ASF_RUNNER_CODEX_HANDOFF_IMPROVEMENTS.md` e `docs/45_ASF_RUNNER_VERIFICATION_PACK.md`.
- Template `templates/codex_tasks/asf_runner_verification_pack_template.md`.
- Test automatici per profili progetto, handoff Codex migliorato e Verification Pack.

### Changed

- Potenziato `scripts/asf_next_step.py` con `--profile`, override manuali, handoff piu' completo e generazione di `verification_pack.md`.
- Aggiornato `templates/codex_tasks/asf_next_step_runner_handoff_template.md` con FASE 1, FASE 2, stato Git, note safety e Step Closure Report.
- Aggiornati Project Workflow Index, Health Check, Quick Reference, Cookbook, Dashboard, Readiness e Existing Project Pilot Onboarding con i nuovi riferimenti runner.
- Aggiornati `scripts/check_workflow_health.py` e `scripts/show_workflow_status.py` per includere documenti e config del runner upgrade nei controlli locali read-only.
- Aggiornata roadmap: STEP 310, 320 e 330 completati; STEP 340 consigliato come ASF Runner Verification Pack Hardening.
- Aggiornato decision log con la scelta di mantenere il runner local-first, read-only verso repository target e senza automazione Codex/GitHub.

### Not included

- Nessuna invocazione automatica di Codex.
- Nessuna modifica a repository target.
- Nessuna creazione branch nel repository target.
- Nessun commit, push, PR o merge automatico.
- Nessuna modifica a GitHub o GitHub API.
- Nessuna modifica a CI, hook Git, `core.hooksPath`, dipendenze, secret, `.env`, PATH o profili PowerShell.

---

## [0.30.0] - 2026-05-29

### Added

- STEP 300 - ASF Next Step Runner.
- Script `scripts/asf_next_step.py` con `prepare mode` locale e standard library only.
- Documento `docs/42_ASF_NEXT_STEP_RUNNER.md`.
- Template `templates/codex_tasks/asf_next_step_runner_handoff_template.md`.
- Test automatici in `tests/unit/test_asf_next_step_runner.py`.

### Changed

- Aggiornato `docs/34_PROJECT_WORKFLOW_INDEX.md` con il nuovo runner come entry point operativo.
- Aggiornato `docs/35_WORKFLOW_HEALTH_CHECK.md` e `scripts/check_workflow_health.py` per includere documento, script e template runner tra i riferimenti workflow centrali.
- Aggiornato `docs/36_WORKFLOW_QUICK_REFERENCE.md`, `docs/38_WORKFLOW_COMMAND_COOKBOOK.md`, `docs/39_WORKFLOW_STATUS_DASHBOARD.md`, `docs/40_RELEASE_READINESS.md` e `docs/41_EXISTING_PROJECT_PILOT_ONBOARDING.md` con i riferimenti al runner.
- Aggiornato `scripts/show_workflow_status.py` per mostrare il runner tra documenti e script centrali.
- Aggiornato `docs/21_DOCUMENTATION_SYNC.md` con il documento STEP 300.
- Aggiornato `README.md` con un rimando breve al runner.
- Aggiornata roadmap: STEP 300 completato e STEP 310 consigliato come ASF Next Step Runner Project Profiles.
- Aggiornato decision log con la scelta del prepare runner locale e prudente.

### Not included

- Nessuna invocazione automatica di Codex.
- Nessuna modifica a repository target durante prepare mode.
- Nessuna creazione branch nel repository target.
- Nessun commit, push, PR o merge automatico.
- Nessuna modifica a GitHub.
- Nessuna GitHub Release.
- Nessuna modifica a hook Git o `core.hooksPath`.
- Nessuna modifica a CI.
- Nessuna modifica a `src/**`.
- Nessuna modifica a `policies/**`.
- Nessuna nuova dipendenza.
- Nessuna modifica a secret, `.env`, PATH o profili PowerShell.
- Nessuna pubblicazione PyPI o registry.

---

## [0.29.0] - 2026-05-29

### Added

- STEP 290 - Existing Project Pilot Onboarding.
- Documento `docs/41_EXISTING_PROJECT_PILOT_ONBOARDING.md`.
- Template `templates/codex_tasks/existing_project_intake_template.md`.
- Template `templates/codex_tasks/first_pilot_step_packet_template.md`.
- Test automatici in `tests/unit/test_existing_project_pilot_onboarding.py`.

### Changed

- Aggiornato `docs/34_PROJECT_WORKFLOW_INDEX.md` con il protocollo Existing Project Pilot Onboarding.
- Aggiornato `docs/38_WORKFLOW_COMMAND_COOKBOOK.md` con la ricetta di intake per progetto esistente.
- Aggiornato `docs/40_RELEASE_READINESS.md` con il collegamento allo STEP 290 e al prossimo pilot reale.
- Aggiornato `docs/35_WORKFLOW_HEALTH_CHECK.md` e `scripts/check_workflow_health.py` per includere documento e template pilot onboarding tra i riferimenti workflow centrali.
- Aggiornato `docs/36_WORKFLOW_QUICK_REFERENCE.md` e `docs/39_WORKFLOW_STATUS_DASHBOARD.md` con i riferimenti al nuovo onboarding.
- Aggiornato `scripts/show_workflow_status.py` per mostrare i documenti readiness e pilot onboarding tra i documenti centrali.
- Aggiornato `docs/21_DOCUMENTATION_SYNC.md` con il documento STEP 290.
- Aggiornato `README.md` con un rimando breve al protocollo di onboarding.
- Aggiornata roadmap: STEP 290 completato e STEP 300 consigliato come First Existing Project Pilot.
- Aggiornato decision log con la scelta dell'onboarding specifico per progetti esistenti.

### Not included

- Nessuna applicazione del metodo a repository esterne.
- Nessuna modifica a repository esterne.
- Nessuna automazione cross-repository.
- Nessun refactor o migrazione.
- Nessuna modifica a CI.
- Nessuna modifica a `src/**`.
- Nessuna modifica a `policies/**`.
- Nessuna nuova dipendenza.
- Nessuna modifica a secret o `.env`.
- Nessun commit, push, PR o merge automatico.
- Nessuna modifica a GitHub.
- Nessuna GitHub Release.
- Nessuna pubblicazione PyPI o registry.

---

## [0.28.0] - 2026-05-29

### Added

- STEP 280 - Release Readiness.
- Documento `docs/40_RELEASE_READINESS.md`.
- Template `templates/codex_tasks/release_readiness_checklist.md`.
- Test automatici in `tests/unit/test_release_readiness.py`.

### Changed

- Aggiornato `docs/34_PROJECT_WORKFLOW_INDEX.md` con Release Readiness.
- Aggiornato `docs/36_WORKFLOW_QUICK_REFERENCE.md` con il riferimento alla readiness per pilot.
- Aggiornato `docs/38_WORKFLOW_COMMAND_COOKBOOK.md` con la ricetta Release Readiness.
- Aggiornato `docs/39_WORKFLOW_STATUS_DASHBOARD.md` con il link alla readiness.
- Aggiornato `docs/37_STEP_CLOSURE_REPORT.md` con la relazione tra closure e readiness.
- Aggiornato `docs/35_WORKFLOW_HEALTH_CHECK.md` e `scripts/check_workflow_health.py` per includere documento e template readiness tra i riferimenti workflow centrali.
- Aggiornato `docs/21_DOCUMENTATION_SYNC.md` con il documento STEP 280.
- Aggiornato `README.md` con un rimando breve alla checklist readiness.
- Aggiornata roadmap: STEP 280 completato e STEP 290 consigliato come Existing Project Pilot Onboarding.
- Aggiornato decision log con la scelta della readiness per pilot interno local-first.

### Not included

- Nessuna dichiarazione di readiness pubblica o SaaS.
- Nessuna GitHub API.
- Nessuna connessione internet richiesta.
- Nessuna integrazione in CI.
- Nessuna modifica a `scripts/verify.ps1`.
- Nessuno script per automatizzare commit, push, PR o merge.
- Nessuna modifica a GitHub.
- Nessuna GitHub Release.
- Nessuna pubblicazione PyPI o registry.
- Nessuna nuova dipendenza.
- Nessuna modifica a CI, `src/**`, `policies/**`, hook, script Git/GitHub esistenti, secret o `.env`.
- Nessuna installazione hook Git.
- Nessuna modifica a `git config core.hooksPath`.
- Nessuna modifica a PATH o profili PowerShell.

---

## [0.27.0] - 2026-05-29

### Added

- STEP 270 - Workflow Status Dashboard.
- Script read-only `scripts/show_workflow_status.py`.
- Documento `docs/39_WORKFLOW_STATUS_DASHBOARD.md`.
- Test automatici in `tests/unit/test_workflow_status_dashboard.py`.

### Changed

- Aggiornato `docs/34_PROJECT_WORKFLOW_INDEX.md` con la Workflow Status Dashboard.
- Aggiornato `docs/38_WORKFLOW_COMMAND_COOKBOOK.md` con la ricetta dashboard.
- Aggiornato `docs/35_WORKFLOW_HEALTH_CHECK.md` e `scripts/check_workflow_health.py` per includere documento e script dashboard tra i controlli workflow centrali.
- Aggiornato `docs/36_WORKFLOW_QUICK_REFERENCE.md` con il comando dashboard.
- Aggiornato `docs/21_DOCUMENTATION_SYNC.md` con il documento STEP 270.
- Aggiornato `README.md` con un rimando breve alla dashboard.
- Aggiornata roadmap: STEP 270 completato e STEP 280 consigliato come Release Readiness.
- Aggiornato decision log con la scelta della dashboard locale read-only.

### Not included

- Nessuna GitHub API.
- Nessuna connessione internet richiesta.
- Nessuna integrazione in CI.
- Nessuna modifica a `scripts/verify.ps1`.
- Nessuno script per automatizzare commit, push, PR o merge.
- Nessuna modifica a GitHub.
- Nessuna GitHub Release.
- Nessuna pubblicazione PyPI o registry.
- Nessuna nuova dipendenza.
- Nessuna modifica a CI, `src/**`, `policies/**`, hook, script Git/GitHub esistenti, secret o `.env`.
- Nessuna installazione hook Git.
- Nessuna modifica a `git config core.hooksPath`.
- Nessuna modifica a PATH o profili PowerShell.

---

## [0.26.0] - 2026-05-29

### Added

- STEP 260 - Workflow Command Cookbook.
- Documento `docs/38_WORKFLOW_COMMAND_COOKBOOK.md`.
- Test automatici in `tests/unit/test_workflow_command_cookbook.py`.

### Changed

- Aggiornato `docs/34_PROJECT_WORKFLOW_INDEX.md` con il Workflow Command Cookbook.
- Aggiornato `docs/36_WORKFLOW_QUICK_REFERENCE.md` con il riferimento al Cookbook per scenari specifici.
- Aggiornato `docs/37_STEP_CLOSURE_REPORT.md` con il riferimento al Cookbook per troubleshooting operativo.
- Aggiornato `docs/35_WORKFLOW_HEALTH_CHECK.md` e `scripts/check_workflow_health.py` per includere il Cookbook tra i documenti workflow centrali.
- Aggiornato `docs/21_DOCUMENTATION_SYNC.md` con il documento STEP 260.
- Aggiornato `README.md` con un rimando breve al Cookbook.
- Aggiornata roadmap: STEP 260 completato e STEP 270 consigliato come Workflow Status Dashboard.
- Aggiornato decision log con la scelta del ricettario operativo.

### Not included

- Nessuno script per automatizzare commit, push, PR o merge.
- Nessuna modifica a GitHub.
- Nessuna GitHub Release.
- Nessuna pubblicazione PyPI o registry.
- Nessuna nuova dipendenza.
- Nessuna modifica a CI, `src/**`, `policies/**`, hook, script Git/GitHub esistenti, secret o `.env`.
- Nessuna installazione hook Git.
- Nessuna modifica a `git config core.hooksPath`.
- Nessuna modifica a PATH o profili PowerShell.
- Nessun commit, push, PR o merge automatico.

---

## [0.25.0] - 2026-05-29

### Added

- STEP 250 - Step Closure Report.
- Documento `docs/37_STEP_CLOSURE_REPORT.md`.
- Template `templates/codex_tasks/step_closure_report_template.md`.
- Test automatici in `tests/unit/test_step_closure_report.py`.

### Changed

- Aggiornato `docs/32_PROMPT_PACKET_LIFECYCLE_CHECKLIST.md` con il riferimento alla chiusura step.
- Aggiornato `docs/34_PROJECT_WORKFLOW_INDEX.md` con documento e template Step Closure Report.
- Aggiornato `docs/36_WORKFLOW_QUICK_REFERENCE.md` con il passaggio di compilazione closure report.
- Aggiornato `docs/35_WORKFLOW_HEALTH_CHECK.md` e `scripts/check_workflow_health.py` per includere documento e template di closure.
- Aggiornato `docs/21_DOCUMENTATION_SYNC.md` con il documento STEP 250.
- Aggiornato `README.md` con un rimando breve allo Step Closure Report.
- Aggiornata roadmap: STEP 250 completato e STEP 260 consigliato come Workflow Command Cookbook.
- Aggiornato decision log con la scelta dello standard di chiusura step.

### Not included

- Nessuno script per automatizzare commit, push, PR o merge.
- Nessuna modifica a GitHub.
- Nessuna GitHub Release.
- Nessuna pubblicazione PyPI o registry.
- Nessuna nuova dipendenza.
- Nessuna modifica a CI, `src/**`, `policies/**`, hook, script Git/GitHub esistenti, secret o `.env`.
- Nessuna installazione hook Git.
- Nessuna modifica a `git config core.hooksPath`.
- Nessuna modifica a PATH o profili PowerShell.
- Nessun commit, push, PR o merge automatico.

---

## [0.24.0] - 2026-05-29

### Added

- STEP 240 - Workflow Quick Reference.
- Documento `docs/36_WORKFLOW_QUICK_REFERENCE.md`.
- Test automatici in `tests/unit/test_workflow_quick_reference.py`.

### Changed

- Aggiornato `docs/34_PROJECT_WORKFLOW_INDEX.md` con la quick reference.
- Aggiornato `docs/35_WORKFLOW_HEALTH_CHECK.md` e `scripts/check_workflow_health.py` per includere la quick reference tra i documenti workflow centrali.
- Aggiornato `docs/21_DOCUMENTATION_SYNC.md` con il documento STEP 240.
- Aggiornato `README.md` con un rimando breve alla quick reference.
- Aggiornata roadmap: STEP 240 completato e STEP 250 consigliato come Step Closure Report.
- Aggiornato decision log con la scelta della quick reference operativa.

### Not included

- Nessuno script per automatizzare commit, push, PR o merge.
- Nessuna modifica a GitHub.
- Nessuna GitHub Release.
- Nessuna pubblicazione PyPI o registry.
- Nessuna nuova dipendenza.
- Nessuna modifica a CI, `src/**`, `policies/**`, hook, script Git/GitHub esistenti, secret o `.env`.
- Nessuna installazione hook Git.
- Nessuna modifica a `git config core.hooksPath`.
- Nessuna modifica a PATH o profili PowerShell.
- Nessun commit, push, PR o merge automatico.

---

## [0.23.0] - 2026-05-29

### Added

- STEP 230 - Workflow Health Check.
- Script read-only `scripts/check_workflow_health.py`.
- Documento `docs/35_WORKFLOW_HEALTH_CHECK.md`.
- Test automatici in `tests/unit/test_workflow_health_check.py`.

### Changed

- Aggiornato `docs/34_PROJECT_WORKFLOW_INDEX.md` con il Workflow Health Check.
- Aggiornato `docs/21_DOCUMENTATION_SYNC.md` con il documento STEP 230.
- Aggiornato `README.md` con un rimando breve al Workflow Health Check.
- Aggiornata roadmap: STEP 230 completato e STEP 240 consigliato come Workflow Quick Reference.
- Aggiornato decision log con la scelta del controllo locale read-only.

### Not included

- Nessuna integrazione in CI.
- Nessuna modifica a `scripts/verify.ps1`.
- Nessuno script per automatizzare commit, push, PR o merge.
- Nessuna modifica a GitHub.
- Nessuna GitHub Release.
- Nessuna pubblicazione PyPI o registry.
- Nessuna nuova dipendenza.
- Nessuna modifica a CI, `src/**`, `policies/**`, hook, script Git/GitHub esistenti, secret o `.env`.
- Nessuna installazione hook Git.
- Nessuna modifica a `git config core.hooksPath`.
- Nessuna modifica a PATH o profili PowerShell.
- Nessun commit, push, PR o merge automatico.

---

## [0.22.0] - 2026-05-29

### Added

- STEP 220 - Project Workflow Index.
- Documento `docs/34_PROJECT_WORKFLOW_INDEX.md`.
- Test automatici in `tests/unit/test_project_workflow_index.py`.

### Changed

- Aggiornato `README.md` con un rimando breve all'indice operativo.
- Aggiornato `docs/33_PROMPT_PACKET_GENERATOR_DEVELOPER_ONBOARDING.md` con il collegamento al Project Workflow Index.
- Aggiornato `docs/21_DOCUMENTATION_SYNC.md` con il documento STEP 220.
- Aggiornata roadmap: STEP 220 completato e STEP 230 consigliato come Workflow Health Check.
- Aggiornato decision log con la scelta dell'indice operativo centrale.

### Not included

- Nessuno script per automatizzare commit, push, PR o merge.
- Nessuna modifica a GitHub.
- Nessuna GitHub Release.
- Nessuna pubblicazione PyPI o registry.
- Nessuna nuova dipendenza.
- Nessuna modifica a CI, `src/**`, `policies/**`, hook, script Git/GitHub, secret o `.env`.
- Nessuna installazione hook Git.
- Nessuna modifica a `git config core.hooksPath`.
- Nessuna modifica a PATH o profili PowerShell.
- Nessun commit, push, PR o merge automatico.

---

## [0.21.0] - 2026-05-29

### Added

- STEP 210 - Prompt Packet Generator Developer Onboarding.
- Documento `docs/33_PROMPT_PACKET_GENERATOR_DEVELOPER_ONBOARDING.md`.
- Test automatici in `tests/unit/test_prompt_packet_generator_developer_onboarding.py`.

### Changed

- Aggiornato `docs/19_PROMPT_PACKET_GENERATOR.md` con il riferimento alla guida onboarding.
- Aggiornato `docs/30_PROMPT_PACKET_GENERATOR_PACKAGING.md` con l'entry point onboarding.
- Aggiornato `docs/31_PROMPT_PACKET_GENERATOR_RELEASE_SMOKE_WORKFLOW.md` con il collegamento alla guida.
- Aggiornato `docs/32_PROMPT_PACKET_LIFECYCLE_CHECKLIST.md` con il riferimento onboarding.
- Aggiornato `docs/21_DOCUMENTATION_SYNC.md` con il documento STEP 210.
- Aggiornata roadmap: STEP 210 completato e STEP 220 consigliato come Project Workflow Index.
- Aggiornato decision log con la scelta della guida onboarding.

### Not included

- Nessuno script per automatizzare commit, push, PR o merge.
- Nessuna modifica a GitHub.
- Nessuna GitHub Release.
- Nessuna pubblicazione PyPI o registry.
- Nessuna nuova dipendenza.
- Nessuna modifica a CI, `src/**`, `policies/**`, hook, script Git/GitHub, secret o `.env`.
- Nessuna installazione hook Git.
- Nessuna modifica a `git config core.hooksPath`.
- Nessuna modifica a PATH o profili PowerShell.
- Nessun commit, push, PR o merge automatico.

---

## [0.20.0] - 2026-05-29

### Added

- STEP 200 - Prompt Packet Lifecycle Checklist.
- Documento `docs/32_PROMPT_PACKET_LIFECYCLE_CHECKLIST.md`.
- Template spuntabile `templates/codex_tasks/prompt_packet_lifecycle_checklist.md`.
- Test automatici in `tests/unit/test_prompt_packet_lifecycle_checklist.py`.

### Changed

- Aggiornato `docs/19_PROMPT_PACKET_GENERATOR.md` con il riferimento alla lifecycle checklist.
- Aggiornato `docs/30_PROMPT_PACKET_GENERATOR_PACKAGING.md` con il collegamento alla checklist.
- Aggiornato `docs/31_PROMPT_PACKET_GENERATOR_RELEASE_SMOKE_WORKFLOW.md` con il riferimento alla sequenza completa.
- Aggiornato `docs/21_DOCUMENTATION_SYNC.md` con il documento STEP 200.
- Aggiornata roadmap: STEP 200 completato e STEP 210 consigliato come Prompt Packet Generator Developer Onboarding.
- Aggiornato decision log con la scelta della checklist lifecycle manuale.

### Not included

- Nessuno script per automatizzare commit, push, PR o merge.
- Nessuna modifica a GitHub.
- Nessuna GitHub Release.
- Nessuna pubblicazione PyPI o registry.
- Nessuna nuova dipendenza.
- Nessuna modifica a CI, `src/**`, `policies/**`, hook, script Git/GitHub, secret o `.env`.
- Nessuna installazione hook Git.
- Nessuna modifica a `git config core.hooksPath`.
- Nessuna modifica a PATH o profili PowerShell.
- Nessun commit, push, PR o merge automatico.

---

## [0.19.0] - 2026-05-28

### Added

- STEP 190 - Prompt Packet Generator Release Smoke Workflow.
- Script locale `scripts/smoke_prompt_packet_release.ps1`.
- Documento `docs/31_PROMPT_PACKET_GENERATOR_RELEASE_SMOKE_WORKFLOW.md`.
- Test automatici in `tests/unit/test_prompt_packet_generator_release_smoke_workflow.py`.

### Changed

- Aggiornato `docs/19_PROMPT_PACKET_GENERATOR.md` con il comando smoke locale.
- Aggiornato `docs/29_PROMPT_PACKET_GENERATOR_CLI_HARDENING.md` con il riferimento allo smoke workflow.
- Aggiornato `docs/30_PROMPT_PACKET_GENERATOR_PACKAGING.md` con il collegamento al release smoke workflow.
- Aggiornato `docs/21_DOCUMENTATION_SYNC.md` con il documento STEP 190.
- Aggiornata roadmap: STEP 190 completato e STEP 200 consigliato come Prompt Packet Generator Developer Onboarding.
- Aggiornato decision log con la scelta di smoke workflow locale.

### Not included

- Nessuna release pubblica.
- Nessuna GitHub Release.
- Nessuna pubblicazione PyPI o registry.
- Nessuna nuova dipendenza.
- Nessuna modifica a CI, `src/**`, `policies/**`, hook, script Git/GitHub, secret o `.env`.
- Nessuna installazione hook Git.
- Nessuna modifica a `git config core.hooksPath`.
- Nessuna modifica a PATH o profili PowerShell.
- Nessun commit, push, PR o merge automatico.

---

## [0.18.0] - 2026-05-28

### Added

- STEP 180 - Prompt Packet Generator Packaging.
- Wrapper PowerShell `scripts/generate_task_packet.ps1`.
- Documento `docs/30_PROMPT_PACKET_GENERATOR_PACKAGING.md`.
- Sample generato `examples/task_packets/generated/step_180_generated_packaging_sample.md`.
- Test automatici in `tests/unit/test_prompt_packet_generator_packaging.py`.

### Changed

- Aggiornato `docs/19_PROMPT_PACKET_GENERATOR.md` con il packaging locale.
- Aggiornato `docs/29_PROMPT_PACKET_GENERATOR_CLI_HARDENING.md` con il collegamento allo STEP 180.
- Aggiornato `docs/21_DOCUMENTATION_SYNC.md` con il documento di packaging locale.
- Aggiornata roadmap: STEP 180 completato e STEP 190 consigliato come Prompt Packet Generator Release Smoke Workflow.
- Aggiornato decision log con la scelta di packaging locale senza pubblicazione esterna.
- Aggiornato `.gitignore` con eccezione mirata per versionare i sample in `examples/task_packets/generated/`.

### Not included

- Nessuna pubblicazione PyPI o registry.
- Nessuna nuova dipendenza.
- Nessuna modifica a CI, `src/**`, `policies/**`, hook, script Git/GitHub, secret o `.env`.
- Nessuna installazione hook Git.
- Nessuna modifica a `git config core.hooksPath`.
- Nessuna modifica a PATH o profili PowerShell.
- Nessun commit, push, PR o merge automatico.

---

## [0.17.0] - 2026-05-28

### Added

- STEP 170 - Prompt Packet Generator CLI Hardening.
- `scripts/generate_task_packet.py`.
- `docs/29_PROMPT_PACKET_GENERATOR_CLI_HARDENING.md`.
- Test automatici in `tests/unit/test_prompt_packet_generator_cli_hardening.py`.

### Changed

- Aggiornato `docs/19_PROMPT_PACKET_GENERATOR.md` con uso della CLI locale.
- Aggiornata roadmap: STEP 170 completato e STEP 180 consigliato come Prompt Packet Generator Packaging.
- Aggiornato decision log con la scelta di un generatore CLI local-first, standard library only.

### Not included

- Nessuno schema JSON/YAML formale.
- Nessuna nuova dipendenza.
- Nessuna modifica a `src/**`, `policies/**`, CI, hook, script Git/GitHub, secret o `.env`.
- Nessuna installazione hook Git.
- Nessuna modifica a `git config core.hooksPath`.
- Nessun commit, push, PR o merge automatico.

---

## [0.16.0] - 2026-05-28

### Added

- STEP 160 - Prompt Packet Validation Strict Mode.
- Flag `--strict` in `scripts/validate_task_packet.py`.
- `docs/28_PROMPT_PACKET_VALIDATION_STRICT_MODE.md`.
- Golden sample Strict valido in `examples/task_packets/valid/step_valid_strict_task_packet.md`.
- Golden sample Strict invalido in `examples/task_packets/invalid/strict_missing_bypass_guard.md`.
- Test automatici in `tests/unit/test_prompt_packet_validation_strict_mode.py`.

### Changed

- Aggiornati Prompt Packet Validation Lite, golden samples, Prompt Packet Hardening, Prompt Packet Generator, Codex Workflow, Verification Gate e Documentation Sync con riferimenti a Strict Mode.
- Aggiornata roadmap: STEP 160 completato e STEP 170 consigliato come Prompt Packet Generator CLI Hardening.
- Aggiornato decision log con la scelta di mantenere Lite default e Strict opt-in.
- Aggiornato pull request template con controllo opzionale Strict Mode.

### Not included

- Nessuno schema JSON/YAML.
- Nessuna integrazione automatica in CI o `scripts/verify.ps1`.
- Nessuna nuova dipendenza.
- Nessuna modifica a `src/**`, `policies/**`, CI, hook, script Git/GitHub, secret o `.env`.
- Nessuna installazione hook Git.
- Nessuna modifica a `git config core.hooksPath`.
- Nessun commit, push, PR o merge automatico.

---

## [0.15.0] - 2026-05-28

### Added

- STEP 150 - Prompt Packet Examples and Golden Samples.
- Golden sample valido in `examples/task_packets/valid/step_valid_minimal_task_packet.md`.
- Golden samples invalidi in `examples/task_packets/invalid/`.
- `docs/27_PROMPT_PACKET_GOLDEN_SAMPLES.md`.
- Test automatici in `tests/unit/test_prompt_packet_golden_samples.py`.

### Changed

- Aggiornati Prompt Packet Validation Lite, Prompt Packet Hardening, Prompt Packet Generator, Codex Workflow, Verification Gate e Documentation Sync con riferimenti ai golden samples.
- Aggiornata roadmap: STEP 150 completato e STEP 160 consigliato come Prompt Packet Validation Strict Mode.
- Aggiornato decision log con la scelta di golden samples valid/invalid senza introdurre modalita' strict.
- Aggiornato pull request template con controllo opzionale sui golden samples.

### Not included

- Nessuna modalita' strict.
- Nessuna nuova dipendenza.
- Nessuna modifica a `src/**`, `policies/**`, CI, hook, script Git/GitHub, secret o `.env`.
- Nessuna installazione hook Git.
- Nessuna modifica a `git config core.hooksPath`.
- Nessun commit, push, PR o merge automatico.

---

## [0.14.0] - 2026-05-28

### Added

- STEP 140 - Prompt Packet Validation Lite.
- `scripts/validate_task_packet.py`.
- `docs/26_PROMPT_PACKET_VALIDATION_LITE.md`.
- Test automatici in `tests/unit/test_prompt_packet_validation_lite.py`.

### Changed

- Aggiornati Prompt Packet Hardening, Prompt Packet Generator, Codex Workflow, workflow operativo, Verification Gate e Documentation Sync con il riferimento al validatore.
- Validato il template centrale `templates/codex_tasks/codex_task_packet_template.md` rispetto ai requisiti minimi.
- Aggiornata roadmap: STEP 140 completato e STEP 150 consigliato come Prompt Packet Examples and Golden Samples.
- Aggiornato decision log con la scelta di validazione Lite senza schema rigido.
- Aggiornato pull request template con controllo opzionale sul Prompt Packet Validation Lite.

### Not included

- Nessuna integrazione automatica in CI o `scripts/verify.ps1`.
- Nessuna nuova dipendenza.
- Nessuna modifica a `src/**`, `policies/**`, CI, hook, script Git/GitHub, secret o `.env`.
- Nessuna installazione hook Git.
- Nessuna modifica a `git config core.hooksPath`.
- Nessun commit, push, PR o merge automatico.

---

## [0.13.0] - 2026-05-28

### Added

- STEP 130 - Prompt Packet Hardening.
- `docs/25_PROMPT_PACKET_HARDENING.md`.
- Test automatici in `tests/unit/test_prompt_packet_hardening.py`.

### Changed

- Rafforzato `templates/codex_tasks/codex_task_packet_template.md` con allowed scope, forbidden scope, forbidden actions, Verification Gate, Documentation Sync, Soft Protection awareness e report finale standard.
- Rafforzati i prompt Codex ask/code/review/repair con riferimenti al Prompt Packet Hardening.
- Aggiornati workflow Codex, workflow operativo, Verification Gate, Documentation Sync e Soft Protection Guardrails.
- Aggiornata roadmap: STEP 130 completato e STEP 140 consigliato come Prompt Packet Validation Lite.
- Aggiornato decision log con la scelta di non introdurre ancora schema rigido.
- Aggiornato pull request template con controllo sul Prompt Packet Hardening.

### Not included

- Nessuno schema rigido o parser dedicato.
- Nessuna modifica a `src/**`, `policies/**`, CI, dipendenze, script, hook, secret o `.env`.
- Nessuna installazione hook Git.
- Nessuna modifica a `git config core.hooksPath`.
- Nessun commit, push, PR o merge automatico.

---

## [0.12.0] - 2026-05-28

### Added

- STEP 120 - Soft Protection Guardrails.
- Hook locali opt-in in `.githooks/pre-commit` e `.githooks/pre-push`.
- Script `scripts/git/install_soft_guardrails.ps1`.
- Script read-only `scripts/git/check_soft_guardrails.ps1`.
- Documento `docs/24_SOFT_PROTECTION_GUARDRAILS.md`.
- Test automatici in `tests/unit/test_soft_protection_guardrails.py`.

### Changed

- Aggiornati Branch Protection Policy, Branch Protection Implementation, GitHub Workflow, Verification Gate, Documentation Sync, Codex Workflow e workflow operativo con i soft guardrails.
- Aggiornata roadmap: STEP 120 completato e STEP 130 consigliato come Prompt Packet Hardening.
- Aggiornato decision log con la scelta di hook opt-in e bypass `ASF_ALLOW_MAIN_BYPASS=1`.
- Aggiornato pull request template con controllo opzionale sui Soft Protection Guardrails.

### Not included

- Nessuna installazione automatica degli hook.
- Nessuna modifica a `git config core.hooksPath`.
- Nessun commit, push, PR o merge automatico.
- Nessuna branch protection o ruleset applicato realmente su GitHub.
- Nessuna modifica a CI, dipendenze, `src/**`, policy o secret.

---

## [0.11.0] - 2026-05-28

### Added

- STEP 110 - Branch Protection Verification and Hardening.
- Soft protection fallback policy for the current private repository and GitHub plan limitation.
- Test automatici in `tests/unit/test_branch_protection_verification_hardening.py`.

### Changed

- Documentato il required check CI reale: `Verification Gate`.
- Documentato il limite GitHub plan: branch protection non disponibile sul repository privato corrente con HTTP 403.
- Migliorata la gestione di HTTP 403 in `scripts/github/verify_branch_protection.ps1` con exit code `2`.
- Rafforzato `scripts/github/apply_branch_protection.ps1` con warning sul piano GitHub prima di `-Apply`.
- Aggiornati GitHub Workflow, Verification Gate, Codex Workflow, workflow operativo, roadmap e decision log.

### Not included

- Nessuna branch protection o ruleset applicato realmente su GitHub.
- Nessuna esecuzione di `apply_branch_protection.ps1 -Apply`.
- Nessuna modifica a CI.
- Nessuna nuova dipendenza.
- Nessuna modifica a `src/**`, policy o secret.

---

## [0.10.0] - 2026-05-27

### Added

- STEP 100 - Branch Protection Implementation.
- `docs/23_BRANCH_PROTECTION_IMPLEMENTATION.md`.
- `scripts/github/detect_required_checks.ps1`.
- `scripts/github/apply_branch_protection.ps1`.
- `scripts/github/verify_branch_protection.ps1`.
- Test automatici in `tests/unit/test_branch_protection_implementation.py`.

### Changed

- Aggiornati Branch Protection Policy, GitHub Workflow, Verification Gate, Documentation Sync, Codex Workflow e workflow operativo con il runbook STEP 100.
- Aggiornata roadmap: STEP 100 completato e STEP 110 consigliato come Branch Protection Verification and Hardening.
- Aggiornato decision log con la scelta DryRun di default per gli script GitHub.
- Aggiornato pull request template con controllo sugli script che modificano GitHub.

### Not included

- Nessuna branch protection o ruleset applicato realmente su GitHub.
- Nessuna esecuzione di `apply_branch_protection.ps1 -Apply`.
- Nessuna modifica a CI.
- Nessuna nuova dipendenza.
- Nessuna modifica a `src/**`, policy o secret.

---

## [0.9.0] - 2026-05-27

### Added

- STEP 090 - Branch Protection Policy.
- `docs/22_BRANCH_PROTECTION_POLICY.md`.
- Test automatici in `tests/unit/test_branch_protection_policy.py`.

### Changed

- Documentato il livello minimo raccomandato per proteggere `main`.
- Integrati riferimenti alla Branch Protection Policy in GitHub Workflow, Verification Gate, Codex Workflow e workflow operativo.
- Aggiornata roadmap: STEP 090 completato e STEP 100 consigliato come Branch Protection Implementation.
- Aggiornato decision log con la policy per `main`.
- Aggiornato pull request template con controllo su bypass branch protection.

### Not included

- Nessuna branch protection o ruleset applicato realmente su GitHub.
- Nessuna modifica a CI.
- Nessuna nuova dipendenza.
- Nessuna modifica a `src/**`.
- Nessuna modifica a policy o secret.

---

## [0.8.0] - 2026-05-27

### Added

- STEP 080 - Documentation Sync.
- `docs/21_DOCUMENTATION_SYNC.md`.
- Test automatici in `tests/unit/test_documentation_sync.py`.

### Changed

- Integrato Documentation Sync nel Verification Gate.
- Aggiornati workflow generale e Codex workflow con responsabilita' documentali.
- Aggiornato pull request template con controllo su changelog, roadmap e decision log.
- Aggiornata roadmap: STEP 080 completato e STEP 090 consigliato come Branch Protection Policy.
- Aggiornato decision log con la regola Documentation Sync.

### Not included

- Nessuno script dedicato aggiunto.
- Nessuna nuova dipendenza.
- Nessuna modifica a CI.
- Nessuna modifica a `src/**`.
- Nessuna modifica a policy o secret.

---

## [0.7.0] - 2026-05-27

### Added

- STEP 070 - Verification Gate.
- `docs/20_VERIFICATION_GATE.md`.
- Script locale `scripts/verify.ps1`.
- Test automatici in `tests/unit/test_verification_gate.py`.

### Changed

- Allineata la CI al Verification Gate con `python -m pytest`, `git diff --check` e permessi minimi.
- Aggiunta sezione Verification Gate al pull request template.
- Aggiornati workflow, GitHub workflow, Codex workflow, roadmap e decision log.

### Not included

- Nessun commit, push, PR o merge automatico.
- Nessuna branch protection configurata automaticamente.
- Nessuna nuova dipendenza.
- Nessuna modifica a `src/**`.
- Nessun secret o file `.env` toccato.

---

## [0.6.0] - 2026-05-26

### Added

- STEP 060 - Codex Workflow.
- `docs/checklists/060_CODEX_WORKFLOW_CHECKLIST.md`.
- Esempio STEP 060 in `templates/codex_tasks/example_060_codex_workflow_task.md`.
- Test automatici in `tests/unit/test_codex_workflow.py`.

### Changed

- Esteso `docs/08_CODEX_WORKFLOW.md` con Codex CLI locale, Codex Web/Cloud, Ask/Suggest, Auto Edit controllato, Review, Repair, divieto di Full Auto, safe stop e rollback.
- Rafforzati i prompt Codex con no commit, no push, no merge, safety level, file da non toccare e output atteso.
- Aggiornato il template Codex Task Packet con safety level e file da non toccare.
- Aggiornata roadmap: STEP 060 completato.
- Aggiornato TREE con checklist, esempio e test STEP 060.

### Not included

- Nessuna logica applicativa reale.
- Nessuna modifica a `.github/workflows/ci.yml`.
- Nessuna modifica a policy di sicurezza.
- Nessuna modifica a `src/**`.
- Nessuna nuova dipendenza.
- Nessun commit, push o merge automatico.

---

## [0.5.0] - 2026-05-26

### Added

- STEP 050 - GitHub Workflow.
- Issue di tracciamento per `050) GitHub Workflow`.
- `docs/checklists/050_GITHUB_WORKFLOW_CHECKLIST.md`.
- Test automatici in `tests/unit/test_github_workflow.py`.

### Changed

- Esteso `docs/15_GITHUB_WORKFLOW.md` con issue policy, branch naming policy, commit policy, PR policy, merge policy, branch protection checklist e release/tag policy.
- Aggiornata roadmap: STEP 050 completato.
- Aggiornato TREE con checklist e test STEP 050.

### Not included

- Nessuna modifica a `.github/workflows/ci.yml`.
- Nessuna branch protection applicata automaticamente.
- Nessuna modifica a policy di sicurezza.
- Nessuna modifica a `src/**`.
- Nessuna nuova dipendenza.

---

## [0.4.0] - 2026-05-25

### Added

- STEP 040 - Prompt Packet Generator.
- `docs/19_PROMPT_PACKET_GENERATOR.md`.
- `docs/checklists/040_PROMPT_PACKET_CHECKLIST.md`.
- Esempio Family Photo Organizer in `templates/codex_tasks/example_040_family_photo_organizer_prompt_packet.md`.
- Test automatici in `tests/unit/test_prompt_templates.py`.

### Changed

- Standardizzati i prompt ChatGPT, Codex Ask, Codex Code, Codex Review e Codex Repair con sezioni minime comuni.
- Rafforzato `templates/codex_tasks/codex_task_packet_template.md` con livello L0-L4, file vietati, test/verifica e safe stop.
- Aggiornata roadmap: STEP 040 completato.
- Aggiornato decision log con DEC-021 -> DEC-023.

### Not included

- Nessuna logica applicativa reale.
- Nessuna modifica a policy di sicurezza.
- Nessuna modifica CI/CD.
- Nessuna nuova dipendenza.

---

## [0.3.0] - 2026-05-25

### Added

- STEP 030 — Safety Model operativo.
- Policy L0-L4 estesa in `docs/05_SECURITY_MODEL.md`.
- `docs/16_APPROVAL_POLICY.md`.
- `docs/17_TOOL_RISK_CLASSIFICATION.md`.
- `docs/18_ROLLBACK_STRATEGY.md`.
- `policies/safety_policy.v0.json`.
- `policies/safety_policy.v0.yaml`.
- `policies/path_policy.v0.json`.
- Template safety: approval request, dry-run report, risk assessment, rollback plan.
- Test automatici in `tests/unit/test_safety_policy.py`.

### Changed

- Aggiornato `README.md` allo stato STEP 030.
- Aggiornato `AGENTS.md` con escalation policy e file policy obbligatori.
- Aggiornato PR template con dichiarazione livello L0-L4.
- Aggiornata roadmap: STEP 030 completato.
- Aggiornato decision log con DEC-016 → DEC-020.

### Security

- L4 richiede ora esplicitamente approvazione, dry-run, backup/rollback e doppia conferma.
- MCP/tool remoti richiedono approval default e allowed tools espliciti.
- Path e secret policy introdotte come configurazioni versionate.

---

## [0.2.0] — 2026-05-25 — STEP 020 Repository Genesis

### Added

- Struttura repository completa.
- `.gitignore`.
- `.env.example`.
- `LICENSE` provvisorio.
- `pyproject.toml`.
- Package skeleton `src/ai_software_factory/`.
- Sottocartelle modulo:
  - `core/`
  - `intake/`
  - `prompts/`
  - `codex/`
  - `github/`
  - `openai_api/`
  - `mcp/`
  - `safety/`
  - `verification/`
  - `docs_sync/`
  - `audit/`
  - `ui/`
- Smoke test repository.
- GitHub Actions CI minimale.
- GitHub issue templates.
- Pull request template.
- Template per issue, PR, ADR, test plan e prompt Codex.
- Documenti placeholder per architettura, workflow, sicurezza, API, MCP, Codex, test, SaaS e case study.

### Changed

- Aggiornato `README.md` a stato STEP 020.
- Aggiornata roadmap con STEP 010 e STEP 020 completati.
- Aggiornato decision log con decisioni DEC-011 — DEC-015.

### Not included

- Nessuna logica applicativa reale.
- Nessuna chiamata API.
- Nessun database.
- Nessuna automazione distruttiva.
- Nessuna integrazione OpenAI/Codex/MCP operativa.

---

## [0.1.0] — 2026-05-25 — STEP 010 Visione e contesto

### Added

- Visione iniziale del progetto.
- README.
- AGENTS.md.
- Roadmap 010-150.
- Decision log iniziale DEC-001 — DEC-010.
- Template Codex Task Packet iniziale.
- Prompt ChatGPT progetto.
- Prompt Codex ask-only.
- Riferimenti tecnici iniziali.

### Not included

- Nessun codice applicativo.
- Nessuna automazione.
- Nessun repository remoto.
