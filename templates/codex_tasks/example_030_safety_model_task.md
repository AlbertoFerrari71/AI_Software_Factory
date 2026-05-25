# Codex Task Packet — Example STEP 030

## Task ID
ASF-030-SAFETY-MODEL-REVIEW

## Titolo
Review read-only del Safety Model

## Obiettivo
Far analizzare a Codex il modello di sicurezza senza modificare file, verificando coerenza tra documenti, policy JSON e test.

## Contesto
Lo STEP 030 introduce livelli L0-L4, approval gate, dry-run, rollback, path policy e secret policy.

## Branch consigliato
030-safety-model-review

## Modalità Codex consigliata
ASK ONLY

## File da leggere prima
- `README.md`
- `AGENTS.md`
- `docs/05_SECURITY_MODEL.md`
- `docs/16_APPROVAL_POLICY.md`
- `docs/17_TOOL_RISK_CLASSIFICATION.md`
- `docs/18_ROLLBACK_STRATEGY.md`
- `policies/safety_policy.v0.json`
- `tests/unit/test_safety_policy.py`

## File modificabili
Nessuno.

## File da NON toccare
Tutti.

## Vincoli
- Non modificare file.
- Non fare commit.
- Non fare push.
- Non eseguire azioni L2+.

## Step richiesti
1. Leggere i file indicati.
2. Verificare coerenza dei livelli L0-L4.
3. Segnalare punti ambigui.
4. Proporre miglioramenti senza applicarli.

## Test da eseguire
- Facoltativo: `python -m pytest -q`, se l'ambiente è pronto.

## Criteri di accettazione
- Nessun file modificato.
- Rischi e incoerenze dichiarati.
- Proposte ordinate per priorità.

## Output atteso
- Riepilogo.
- Incoerenze trovate.
- Rischi residui.
- Miglioramenti suggeriti.
