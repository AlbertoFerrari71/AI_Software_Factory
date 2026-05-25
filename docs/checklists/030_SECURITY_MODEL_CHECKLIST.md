# Checklist — STEP 030 Safety Model

## Documenti

- [x] `docs/05_SECURITY_MODEL.md` esteso in forma operativa.
- [x] `docs/16_APPROVAL_POLICY.md` creato.
- [x] `docs/17_TOOL_RISK_CLASSIFICATION.md` creato.
- [x] `docs/18_ROLLBACK_STRATEGY.md` creato.
- [x] `docs/10_ROADMAP.md` aggiornato.
- [x] `docs/11_DECISIONS.md` aggiornato.
- [x] `CHANGELOG.md` aggiornato.

## Policy

- [x] `policies/safety_policy.v0.json` creato.
- [x] `policies/safety_policy.v0.yaml` creato.
- [x] `policies/path_policy.v0.json` creato.
- [x] L0-L4 definiti.
- [x] L3 richiede approvazione esplicita.
- [x] L4 richiede approvazione, dry-run, rollback e doppia conferma.
- [x] Path allowlist/denylist definita.
- [x] Secret policy definita.

## Tool

- [x] Codex classificato.
- [x] GitHub classificato.
- [x] OpenAI API classificata.
- [x] MCP classificato.
- [x] Database e filesystem classificati.

## Test

- [x] Test automatici su policy JSON.
- [x] Test smoke repository aggiornato.
- [x] `python -m pytest -q` eseguito.

## Esclusioni corrette

- [x] Nessuna API reale implementata.
- [x] Nessun MCP reale configurato.
- [x] Nessuna integrazione GitHub remota eseguita.
- [x] Nessuna automazione distruttiva introdotta.
- [x] Nessuna credenziale reale inserita.
