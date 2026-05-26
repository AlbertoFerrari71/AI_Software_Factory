# 060 - Codex Workflow Checklist

## 1. Obiettivo

Verificare che STEP 060 renda operativo il workflow Codex CLI e Codex Web/Cloud senza introdurre logica applicativa reale.

---

## 2. Checklist

### 010 - Contesto e branch

- [ ] Branch dedicato `060-codex-workflow` verificato.
- [ ] Task packet approvato.
- [ ] Safety level massimo L2 confermato.
- [ ] File da leggere, file modificabili e file da non toccare espliciti.

### 020 - Documentazione workflow

- [ ] `docs/08_CODEX_WORKFLOW.md` distingue Codex CLI locale e Codex Web/Cloud.
- [ ] Ask/Suggest e' descritto come L0-L1.
- [ ] Auto Edit controllato e' descritto come L2.
- [ ] Review e' descritta come read-only.
- [ ] Repair e' descritta come fix minimo controllato.
- [ ] Full Auto e' vietato salvo sandbox esplicita.
- [ ] Regole no commit, no push, no merge presenti.
- [ ] Output finale obbligatorio presente.
- [ ] Relazione con GitHub Workflow STEP 050 presente.
- [ ] Relazione con Safety Model L0-L4 presente.
- [ ] Safe stop e rollback presenti.

### 030 - Template e prompt

- [ ] `templates/codex_tasks/codex_task_packet_template.md` include safety level, file da non toccare e output atteso.
- [ ] Prompt Ask Only aggiornato con keyword minime.
- [ ] Prompt Code Controlled aggiornato con keyword minime.
- [ ] Prompt Review aggiornato con keyword minime.
- [ ] Prompt Repair aggiornato con keyword minime.
- [ ] Esempio STEP 060 presente in `templates/codex_tasks/example_060_codex_workflow_task.md`.

### 040 - Test e documentazione viva

- [ ] `tests/unit/test_codex_workflow.py` presente.
- [ ] Test su sezioni minime del workflow presenti.
- [ ] Test su checklist 060 ed esempio 060 presenti.
- [ ] Test su keyword robuste nei prompt Codex presenti.
- [ ] Roadmap aggiornata con STEP 060 completato.
- [ ] Changelog aggiornato.
- [ ] TREE aggiornato.

### 050 - Verifica finale

- [ ] `python -m pytest -q` eseguito.
- [ ] `git diff --check` eseguito.
- [ ] `git status` eseguito.
- [ ] Nessuna modifica a CI.
- [ ] Nessuna modifica a policy.
- [ ] Nessuna modifica a `src/**`.
- [ ] Nessuna nuova dipendenza.
- [ ] Nessun secret o file `.env` toccato.

---

## 3. Criterio di completamento

STEP 060 e' completato quando la documentazione Codex e' operativa, i prompt sono allineati ai guardrail, i test passano e il diff resta limitato ai file ammessi dal task packet.
