# 06 — API Design

## 1. Stato

Nello STEP 030 non vengono implementate API. Il Safety Model definisce però i vincoli che le API future dovranno rispettare.

Questo documento prepara lo spazio concettuale per gli step futuri.

---

## 2. API candidate future

Nel Local Orchestrator MVP potrebbero comparire API locali per:

- project intake;
- roadmap generation;
- Codex Task Packet generation;
- validation of structured outputs;
- verification checklist;
- audit log.

---

## 3. Principi

- API locale prima di API cloud.
- Nessuna API distruttiva senza safety model.
- Output JSON validabile.
- Input con Pydantic o schema equivalente.
- Separazione tra comando richiesto e comando approvato.
- Log di ogni azione tool/agent.

---

## 4. Esempi futuri non implementati

```text
POST /projects/intake
POST /projects/{id}/roadmap
POST /tasks/codex-packet
POST /verification/check
GET  /audit/events
```

Questi endpoint sono solo indicativi.
