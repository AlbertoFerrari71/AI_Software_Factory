# ASF Next Step Runner Handoff Template

Questo handoff e' generato dal runner, ma deve comunque essere revisionato da Alberto/ChatGPT prima dell'uso.

## 1. Titolo step

- Step:
- Titolo:

## 2. Contesto progetto target

- Progetto:
- Repository:
- Repo path:
- Branch principale:
- Branch di lavoro previsto:
- Profilo runner:

## 3. Stato Git letto dal runner

- Branch corrente target:
- Working tree: CLEAN / DIRTY-WARNING
- Ultimi commit:

```text

```

## 4. Prerequisito

- [ ] Step precedente su main verificato.
- [ ] Se non deducibile, prerequisito controllato manualmente.
- [ ] Working tree compresa.
- [ ] Alberto ha deciso se proseguire in caso di DIRTY-WARNING.

## 5. Obiettivo

```text

```

## 6. FASE 1 - Allineamento sintetico

### Riepilogo

```text

```

### Assunzioni

- [100]
- [101]
- [102]

### Domande chiuse

- A) Procedere dopo review umana. Default A.
- B) Rigenerare task packet con scope piu' stretto.
- C) Fermarsi per working tree non chiara.
- D) Fermarsi per prerequisito non verificato.

### Criticita'

- TBD.

## 7. FASE 2 - Istruzioni operative per Codex

### Istruzioni

- Leggere il task packet.
- Usare il verification pack come checklist.
- Lavorare solo sul branch previsto dopo conferma umana.
- Fermarsi se serve allargare scope.

### File da ispezionare

- README.md
- AGENTS.md se presente
- docs rilevanti
- test rilevanti

### Scope incluso

- TBD.

### Scope escluso

- CI.
- Dipendenze.
- Secret e `.env`.
- Dati sensibili.
- Produzione.

### Forbidden actions

- Codex non deve fare commit/push/PR/merge.
- Codex non deve modificare GitHub.
- Codex non deve modificare hook/core.hooksPath.
- Codex non deve toccare secret/.env.
- Codex non deve allargare scope.

### Comandi di verifica

```powershell
git branch --show-current
git status --short
git --no-pager log --oneline --max-count=10
python -m pytest
git --no-pager diff --stat
git --no-pager diff --check
```

### Output finale richiesto

- step eseguito;
- stato;
- branch corrente;
- file creati;
- file modificati;
- comandi eseguiti e risultati;
- verifiche non eseguite;
- rischi o note;
- conferme vincoli;
- prossimo step consigliato;
- richiesta Step Closure Report.

## 8. Note safety dal profilo

```text

```

## 9. Step Closure Report

Richiedere esplicitamente la compilazione di:

```text
templates/codex_tasks/step_closure_report_template.md
```
