# ASF Runner Verification Pack Hardening

## 1. Scopo

Questo documento descrive il rafforzamento del `verification_pack.md` generato da `scripts/asf_next_step.py`.

Il Verification Pack non esegue comandi automaticamente. Serve a guidare Alberto nel ciclo completo:

- prima di Codex;
- dopo Codex;
- prima del commit;
- prima del push;
- prima della PR;
- prima del merge;
- dopo il pull finale di `main`.

---

## 2. Cosa e' stato rafforzato

Il pack ora contiene:

- stato Git target letto dal runner;
- controlli Pre-Codex piu' espliciti;
- controlli Post-Codex piu' completi;
- scope checks;
- Codex report checks;
- human gates per commit, push, PR e merge;
- gestione PR checks non disponibili;
- gestione warning LF/CRLF.

---

## 3. Pre-Codex checks

Prima di usare Codex, verificare:

- branch corrente;
- working tree;
- ultimi commit;
- prerequisito dello step precedente;
- `task_packet.md`;
- `codex_handoff.md`;
- Human gate Alberto/ChatGPT.

Se il repository target e' `DIRTY/WARNING`, Alberto decide se proseguire.

---

## 4. Post-Codex checks

Dopo il report Codex, verificare:

- `git status --short`;
- `git --no-pager diff --stat`;
- `git --no-pager diff --check`;
- test command del profilo;
- health command del profilo, se presente;
- file temporanei sotto `tmp/` o percorsi ignorati.

---

## 5. Report checks

Il report finale Codex dovrebbe contenere:

- STEP ESEGUITO;
- STATO;
- BRANCH CORRENTE;
- FILE CREATI;
- FILE MODIFICATI;
- COMANDI ESEGUITI;
- VERIFICHE NON ESEGUITE;
- RISCHI / NOTE;
- CONFERME VINCOLI;
- PROSSIMO STEP;
- RIEPILOGO FINALE.

Queste sezioni alimentano `scripts/asf_codex_report_intake.py`.

---

## 6. PR checks handling

`gh pr checks --watch` puo' non trovare check disponibili.

Questo caso e' un'attenzione, non una prova automatica di fallimento. Va registrato nello Step Closure Report insieme ai controlli locali eseguiti.

---

## 7. LF/CRLF handling

I warning LF/CRLF non sono bloccanti se:

- `git diff --check` passa;
- i test passano;
- il Verification Gate passa.

---

## 8. Human gates

Restano manuali e presidiati:

- review diff;
- approvazione commit;
- approvazione push;
- approvazione PR;
- approvazione merge;
- Step Closure Report.

Il runner prepara evidenze e checklist, ma non chiude lo step.
