# ASF Human-Gated Closure Pack

## 1. Scopo

`scripts/asf_generate_closure_pack.py` genera un `closure_pack.md` con comandi consigliati per chiudere uno step.

Il closure pack e' manuale e human-gated: lo script genera testo, non esegue i comandi.

---

## 2. Closure pack

Output predefinito:

```text
tmp/asf_closure_pack/<project-name>/step_<step>/closure_pack.md
```

Il file contiene:

- project-name;
- repo-path;
- step;
- branch;
- commit message;
- PR title;
- PR body;
- stato Git target letto;
- checklist prima del commit;
- comandi verifica;
- comandi commit/push/PR/merge manuali;
- gestione PR checks;
- test finale su main;
- richiesta Step Closure Report.

---

## 3. Comandi generati ma non eseguiti

I comandi di chiusura sono nel template Markdown:

```text
templates/codex_tasks/asf_human_gated_closure_pack_template.md
```

Questo evita che lo script operativo contenga o esegua comandi Git di pubblicazione o merge. Alberto li copia ed esegue solo dopo review umana.

---

## 4. Human gate

Prima di ogni fase servono gate separati:

- review diff;
- approvazione commit;
- approvazione push;
- approvazione PR;
- approvazione merge;
- verifica finale su `main`.

Il closure pack non approva nulla e non sostituisce Alberto/ChatGPT.

Dal mega-step 370-390, un closure pack puo' essere letto dal Human Approval Gate come evidenza opzionale. Questo non trasforma i comandi manuali del closure pack in automazione.

---

## 5. Gestione PR checks

Il template include gestione robusta di:

```powershell
gh pr checks --watch
```

Se il comando restituisce exit code non zero per check mancanti o non disponibili, il caso va registrato come attenzione e verificato manualmente.

---

## 6. Gestione LF/CRLF

I warning LF/CRLF non sono bloccanti se:

- `git diff --check` passa;
- i test passano;
- il Verification Gate passa.

---

## 7. Limiti

Il closure pack non:

- invoca Codex;
- modifica repository target esterni;
- chiama GitHub API;
- esegue test automaticamente;
- esegue commit, push, PR o merge;
- sostituisce PR checks, review umana o Step Closure Report.

Riferimento successivo:

```text
docs/49_ASF_HUMAN_APPROVAL_GATE.md
```
