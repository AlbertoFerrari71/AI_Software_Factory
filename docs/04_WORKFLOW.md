# 04 - Workflow

## 1. Pipeline operativa

```text
Idea naturale
  -> FASE 1 - Allineamento
  -> Requirement Alchemy
  -> Architecture Forge
  -> Work Package Generator
  -> Codex Task Packet
  -> Codex Execution Layer
  -> Verification Gate
  -> Documentation Sync
  -> Human Approval Gate
  -> Release / Learning Loop
```

---

## 2. FASE 1 - Allineamento

La FASE 1 serve a evitare false partenze.

Output obbligatorio:

A) Sintesi obiettivo
B) Assunzioni numerate da `[100]`
C) Domande chiuse A/B/C/D con default A
D) Criticita, rischi e ottimizzazioni

Non si scrive codice in FASE 1.

---

## 3. FASE 2 - Esecuzione

La FASE 2 parte solo dopo conferma.

Output possibili:

- roadmap;
- documenti;
- task packet;
- issue;
- branch plan;
- test plan;
- codice;
- checklist;
- changelog;
- decision log.

---

## 4. Work package

Ogni work package deve avere:

- step numerato;
- obiettivo;
- scope incluso;
- scope escluso;
- file modificabili;
- file da non toccare;
- test;
- criteri di accettazione;
- rischi;
- rollback;
- output atteso.

---

## 5. Completion rule

Uno step e' completato solo se:

- i deliverable esistono;
- i test automatici o manuali sono indicati;
- i rischi residui sono dichiarati;
- la documentazione e' aggiornata;
- il decision log e' aggiornato se necessario.

---

## 6. Verification Gate

Il Verification Gate e' il controllo operativo tra lavoro locale e ingresso su `main`.

Flusso standard:

1. Codex lavora localmente su branch dedicato.
2. Alberto verifica diff, test e stato Git.
3. Solo dopo verifica locale si procede con commit, push e PR.
4. PR e CI GitHub sono gate prima del merge.
5. Dopo il merge si fa pull di `main` e test finale.

Il processo completo e' definito in `docs/20_VERIFICATION_GATE.md`.
