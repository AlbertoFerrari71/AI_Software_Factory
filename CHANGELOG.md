# Changelog

Formato ispirato a Keep a Changelog, adattato al metodo interno.

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
- Aggiornato `AGENTS.md` con regole repository e CI.
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
