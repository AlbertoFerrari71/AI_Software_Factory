# Changelog

Formato ispirato a Keep a Changelog, adattato al metodo interno.

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
