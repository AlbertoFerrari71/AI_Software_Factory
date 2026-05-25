# 09 — Test Strategy

## 1. Stato

Nello STEP 030 sono presenti CI minima, smoke test e unit test sulla Safety Policy.

---

## 2. Tipi di test futuri

| Tipo | Scopo |
|---|---|
| Smoke test | Verificare che il progetto sia importabile e strutturalmente integro |
| Unit test | Testare moduli isolati |
| Integration test | Testare adapter e flussi tra moduli |
| Contract test | Validare schema JSON e output strutturati |
| Security test | Verificare policy L0-L4, secret scan, denylist |
| Manual checklist | Verificare casi non automatizzabili |

---

## 3. Regola

Ogni step deve indicare almeno uno tra:

- test automatico;
- checklist manuale;
- motivo per cui il test non è applicabile.

---

## 4. CI STEP 030

La CI minimale deve:

- installare il package;
- lanciare pytest;
- validare smoke test e policy JSON;
- non usare secret;
- non fare deploy;
- non scrivere su repository remoto.

---

## 5. Evoluzione prevista

Negli step successivi aggiungere:

- lint;
- type check;
- dependency review;
- security scan;
- coverage se utile;
- test fixture per output JSON.
