# ASF Runner Codex Handoff Improvements

## 1. Scopo

Questo documento descrive il nuovo `codex_handoff.md` generato da ASF Next Step Runner.

L'obiettivo e' rendere l'handoff piu' utile per Codex senza trasformare il runner in un orchestratore automatico.

---

## 2. Perche' migliorare l'handoff

Il task packet contiene il contratto operativo. L'handoff serve invece come testo pronto da rivedere e copiare manualmente in Codex.

Un handoff migliore riduce errori ricorrenti:

- branch non chiaro;
- working tree non considerata;
- prerequisito su main saltato;
- note safety dimenticate;
- scope allargato;
- confusione tra report runner e Step Closure Report.

---

## 3. Struttura del nuovo handoff

Il file `codex_handoff.md` contiene:

- titolo step;
- contesto progetto target;
- repo path;
- branch principale;
- branch di lavoro previsto;
- stato Git letto dal runner;
- prerequisito;
- obiettivo;
- FASE 1 sintetica;
- FASE 2 operativa;
- vincoli;
- forbidden actions;
- note safety del profilo;
- riferimento al verification pack;
- richiesta di Step Closure Report.

---

## 4. FASE 1 / FASE 2

La FASE 1 sintetica contiene:

- riepilogo;
- assunzioni numerate da `[100]`;
- domande chiuse A/B/C/D con default A;
- criticita'.

La FASE 2 operativa contiene:

- istruzioni per Codex;
- file da ispezionare;
- scope incluso;
- scope escluso;
- forbidden actions;
- comandi di verifica;
- output finale richiesto.

Questa struttura mantiene il protocollo AI Software Factory anche quando il testo viene generato da uno script.

---

## 5. Human gate

Il nuovo handoff include la frase:

```text
Questo handoff e' stato generato dal runner; deve comunque essere revisionato da Alberto/ChatGPT prima dell'uso.
```

Il runner non decide che lo step sia pronto. Alberto o ChatGPT devono rivedere:

- obiettivo;
- scope;
- prerequisito;
- working tree;
- note safety;
- verifiche richieste.

---

## 6. Ruolo di Codex

Codex riceve un handoff piu' completo, ma resta vincolato:

- non fa commit;
- non fa push;
- non crea PR;
- non fa merge;
- non modifica GitHub;
- non modifica hook/core.hooksPath;
- non tocca secret o `.env`;
- non allarga scope.

Codex deve produrre un report finale e richiedere Step Closure Report.

---

## 7. Ruolo di Alberto/ChatGPT

Alberto e ChatGPT mantengono il controllo su:

- review dell'handoff;
- conferma FASE 2;
- scelta se proseguire con working tree sporca;
- commit, push, PR e merge manuali;
- chiusura dello step con Step Closure Report.

---

## 8. Cosa resta manuale

Restano manuali:

- revisione del task packet;
- copia dell'handoff in Codex;
- verifica diff;
- test;
- PR checks;
- commit, push, PR e merge presidiati;
- Step Closure Report;
- decisione sul prossimo step.

