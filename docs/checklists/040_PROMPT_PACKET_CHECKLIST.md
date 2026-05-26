# 040 - Prompt Packet Checklist

## 1. Scopo

Checklist per verificare che un Prompt Packet o Codex Task Packet sia completo, sicuro e verificabile prima di usarlo.

---

## 2. Identificazione

- [ ] Task ID presente.
- [ ] Step numerato 010/020/030...
- [ ] Titolo breve e verificabile.
- [ ] Branch indicato se il task e' L2 o superiore.
- [ ] Modalita AI indicata: ChatGPT, Codex Ask, Codex Code, Codex Review o Codex Repair.

---

## 3. Sezioni obbligatorie

- [ ] Obiettivo.
- [ ] Contesto.
- [ ] Livello rischio L0-L4.
- [ ] File da leggere.
- [ ] File modificabili.
- [ ] File vietati.
- [ ] Vincoli.
- [ ] Output atteso.
- [ ] Criteri di accettazione.
- [ ] Test / verifica.
- [ ] Rollback / safe stop.
- [ ] Cosa NON fare.

---

## 4. Safety Model

- [ ] Il livello dichiarato e' coerente con `docs/05_SECURITY_MODEL.md`.
- [ ] L3 non e' presente senza approval esplicita.
- [ ] L4 non e' presente senza dry-run, backup/rollback e doppia conferma.
- [ ] I file vietati includono secret, `.env`, path fuori repository e dati reali non necessari.
- [ ] Il task specifica quando fermarsi.

---

## 5. Verifica

- [ ] Sono indicati test automatici o checklist manuale.
- [ ] I criteri di accettazione sono osservabili.
- [ ] Il task non puo' essere dichiarato completato senza verifica.
- [ ] Il rollback e' proporzionato al livello di rischio.

---

## 6. Anti-obiettivi

- [ ] Non introduce dipendenze non richieste.
- [ ] Non modifica CI/CD se non approvato come L3.
- [ ] Non modifica policy di sicurezza se non approvato come L3.
- [ ] Non usa Full Auto per task L2+.
- [ ] Non fa commit, push o merge automatici.
