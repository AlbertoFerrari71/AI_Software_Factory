# 0570 - Independent Review Node

## 1. Scopo

Il nodo di revisione indipendente valuta se l'output di Codex/runner puo' superare il gate o deve fermarsi.

La review non sostituisce Alberto. Serve a separare la produzione del lavoro dalla valutazione critica di scope, rischio, test e diff.

---

## 2. Input

Il nodo riceve:

- task packet;
- git diff;
- report Codex;
- test report;
- risk report;
- file manifest.

Input mancanti o parziali devono ridurre confidence e, se bloccanti, produrre `NEEDS_HUMAN` o `FAIL`.

---

## 3. Output JSON

```json
{
  "verdict": "PASS | FAIL | NEEDS_HUMAN",
  "risk_level": "L0 | L1 | L2 | L3 | L4",
  "confidence": "low | medium | high",
  "blocking_findings": [],
  "non_blocking_warnings": [],
  "scope_check": "PASS | FAIL",
  "tests_check": "PASS | FAIL",
  "diff_summary": [],
  "rollback_hint": "",
  "next_recommended_action": ""
}
```

---

## 4. Criteri PASS

`PASS` e' ammesso solo quando:

- il task packet e' presente e coerente con lo step;
- il diff tocca solo file in scope;
- il file manifest corrisponde al diff;
- il risk report classifica correttamente il livello massimo;
- i test obbligatori sono passati o gli skip sono motivati e non bloccanti;
- non ci sono blocking findings;
- `scope_check` e' `PASS`;
- `tests_check` e' `PASS`;
- confidence e' almeno `medium`;
- L3 richiede human gate esplicito prima dell'azione successiva;
- L4 non procede senza doppia conferma e dry-run separato.

---

## 5. Criteri FAIL

`FAIL` e' obbligatorio quando:

- il diff contiene file vietati o fuori scope;
- i test richiesti falliscono;
- il risk report sottostima un rischio L3/L4;
- compaiono secret, token o dati sensibili;
- viene proposta una live call, cancellazione, deploy, merge automatico o costo API senza autorizzazione;
- il target repository diventa dirty dopo una fase dichiarata read-only;
- il report Codex dichiara azioni non supportate dal diff/evidence;
- manca rollback o hold possibile per una modifica write.

---

## 6. Criteri NEEDS_HUMAN

`NEEDS_HUMAN` e' richiesto quando:

- l'evidence e' incompleta ma non prova un failure;
- confidence e' `low`;
- il rischio e' L3 o L4 e manca approval esplicita;
- scope o intento sono ambigui;
- i test non sono disponibili e la modifica non e' puramente documentale;
- la review trova warning non bloccanti ma rilevanti per decisione operativa;
- il prossimo passo include commit, push, PR, merge, deploy, live API o modifiche esterne.

---

## 7. Diff summary e rollback hint

`diff_summary` deve descrivere solo fatti osservabili:

- file aggiunti;
- file modificati;
- file cancellati se presenti;
- aree funzionali toccate;
- eventuali file fuori manifest.

`rollback_hint` deve restare pratico e non distruttivo. Nel MVP puo' indicare "hold and review diff manually" oppure "revert only the listed files after Alberto approval"; non deve emettere comandi distruttivi automatici.

---

## 8. STEP 1100 operational protocol

For FULL or ESCALATED steps, the reviewer must be independent from the planner
context. The reviewer can be a different model, a fresh GPT context with only
the evidence pack, or a separate human-assisted review context.

Every review records:

- reviewer_actor;
- reviewer_context_type;
- evidence_pack_path;
- verdict;
- rationale;
- disagreement_status.

Disagreement rules:

- L0-L2 disagreement: the more conservative verdict wins with rationale;
- L3+ disagreement: ASK_ALBERTO is mandatory;
- publish/merge/deploy/scope disagreement: ASK_ALBERTO is mandatory.

Templates:

- `docs/templates/independent_review_packet.md`;
- `docs/templates/disagreement_comparison.md`.
