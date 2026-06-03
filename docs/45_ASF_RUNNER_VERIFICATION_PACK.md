# ASF Runner Verification Pack

## 1. Scopo

Il Verification Pack e' un file generato da `scripts/asf_next_step.py` in `prepare mode`.

Serve come checklist read-only di controlli consigliati prima e dopo l'uso di Codex, prima della pubblicazione manuale e dopo la verifica finale su `main`.

---

## 2. Output

Il file viene generato in:

```text
tmp/asf_next_step/<project>/step_<step>/verification_pack.md
```

La stessa cartella contiene anche:

- `task_packet.md`;
- `codex_handoff.md`;
- `runner_report.md`.

---

## 3. Cosa contiene

Il Verification Pack contiene:

- progetto target;
- step;
- branch previsto;
- stato Git target letto dal runner;
- Pre-Codex checks consigliati;
- Post-Codex local checks consigliati;
- scope checks;
- Codex report checks;
- PR checks handling;
- LF/CRLF handling;
- validazione task packet Lite;
- validazione task packet Strict;
- runner report review;
- Human gates;
- riferimenti a Quick Reference, Command Cookbook e Step Closure Report.

---

## 4. Cosa non contiene

Il Verification Pack non contiene comandi per automatizzare:

- commit;
- push;
- PR;
- merge.

Non sostituisce test, review umana, PR checks o Step Closure Report.

Per il hardening dettagliato vedere:

```text
docs/46_ASF_RUNNER_VERIFICATION_PACK_HARDENING.md
```

---

## 5. Perche' non contiene commit/push/PR/merge

Il workflow AI Software Factory mantiene il gate umano sulle azioni Git che cambiano storia locale, remoto o stato GitHub.

Il runner prepara contesto e checklist. Non deve trasformarsi in un orchestratore automatico che decide quando pubblicare o chiudere uno step.

La fase Git presidiata resta documentata in:

- `docs/36_WORKFLOW_QUICK_REFERENCE.md`;
- `docs/38_WORKFLOW_COMMAND_COOKBOOK.md`;
- `docs/37_STEP_CLOSURE_REPORT.md`.

---

## 6. Esempio contenuto

Esempio di controlli Pre-Codex:

```powershell
git branch --show-current
git status --short
git --no-pager log --oneline --max-count=10
```

Esempio di controlli Post-Codex:

```powershell
git status --short
git --no-pager diff --stat
git --no-pager diff --check
python -m pytest
```

Esempio di controlli lato AI Software Factory:

```powershell
python scripts/validate_task_packet.py tmp/asf_next_step/AI_Software_Factory/step_340/task_packet.md
python scripts/validate_task_packet.py --strict tmp/asf_next_step/AI_Software_Factory/step_340/task_packet.md
```

---

## 7. Human gates

Prima di procedere manualmente con il ciclo Git presidiato, verificare:

- diff;
- scope;
- vincoli;
- note safety;
- test;
- Step Closure Report richiesto.

I gate umani includono approvazione commit, push, PR e merge. Il Verification Pack puo' citare `gh pr checks --watch`, ma tratta check non disponibili come attenzione da registrare.

