# Changelog

Formato ispirato a Keep a Changelog, adattato al metodo interno.

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
