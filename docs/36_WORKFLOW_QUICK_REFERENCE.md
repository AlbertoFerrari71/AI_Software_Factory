# Workflow Quick Reference

## 1. Scopo

Questa quick reference e' una scheda rapida per l'uso quotidiano del workflow AI Software Factory.

Contiene i comandi essenziali per generare task packet, validarli, eseguire smoke workflow, controllare il workflow health check, lanciare il Verification Gate e gestire il passaggio presidiato verso PR e merge.

Non sostituisce il Project Workflow Index, la Prompt Packet Lifecycle Checklist o la Developer Onboarding Guide. Li collega quando serve approfondire.

---

## 2. Quando usarla

Usarla:

- prima di lanciare Codex;
- dopo il report Codex;
- prima del commit;
- prima del push;
- prima del merge;
- prima dello step successivo.

---

## 3. Prerequisiti rapidi

Controllare branch, working tree e log recente:

```powershell
git branch --show-current
git status --short
git --no-pager log --oneline --max-count=10
```

Se lo step precedente non risulta su `main`, fermarsi e completare il lifecycle dello step precedente.

---

## 4. Generare un task packet strict-ready

Esempio per STEP 240:

```powershell
python scripts/generate_task_packet.py --step 240 --title "Workflow Quick Reference" --branch step-240-workflow-quick-reference --objective "Create a short operational quick reference for the workflow." --output tmp/generated_step_240_task_packet.md --force --strict-ready
```

Il file sotto `tmp/` e' temporaneo e non deve essere committato.

---

## 5. Validare il task packet

Lite Mode:

```powershell
python scripts/validate_task_packet.py tmp/generated_step_240_task_packet.md
```

Strict Mode:

```powershell
python scripts/validate_task_packet.py --strict tmp/generated_step_240_task_packet.md
```

Lite controlla i requisiti minimi. Strict e' piu' severo ed e' consigliato per task complessi o sensibili.

---

## 6. Eseguire release smoke workflow

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\smoke_prompt_packet_release.ps1
```

Lo smoke workflow verifica localmente wrapper, generatore e validazione Lite/Strict del task packet generato.

---

## 7. Eseguire workflow health check

```powershell
python scripts/check_workflow_health.py
```

Il Workflow Health Check e' read-only e controlla documenti, riferimenti centrali, template e sicurezza minima degli script operativi.

---

## 8. Eseguire Verification Gate

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify.ps1
```

Il Verification Gate resta il controllo locale principale prima del passaggio a commit, push e PR.

---

## 9. Controllare soft guardrails

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\git\check_soft_guardrails.ps1
```

Il controllo e' read-only. Non installa hook e non modifica `core.hooksPath`.

---

## 10. Pre-commit manuale

Comandi di riferimento prima del commit:

```powershell
git status --short
git --no-pager diff --stat
git --no-pager diff --check
python -m pytest
python scripts/check_workflow_health.py
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify.ps1
```

Commit, push, PR e merge sono operazioni di Alberto. Codex non fa commit, Codex non fa push, Codex non apre PR e Codex non fa merge.

---

## 11. Commit / push / PR presidiati

Questi sono comandi di riferimento presidiati, non uno script automatico e non automazione cieca:

```powershell
git add .
git commit -m "240) add workflow quick reference"
git push -u origin step-240-workflow-quick-reference
gh pr create --base main --head step-240-workflow-quick-reference --title "240) Workflow Quick Reference" --body "Adds a short operational quick reference for the AI Software Factory workflow."
```

Alberto decide cosa aggiungere, verifica il diff e lancia questi comandi solo dopo i controlli locali.

---

## 12. PR checks e merge presidiato

```powershell
gh pr status
gh pr checks --watch
gh pr merge --merge --delete-branch
```

Il merge va fatto solo dopo check positivi e revisione del contenuto della PR.

---

## 13. Verifica finale su main

Dopo il merge:

```powershell
git switch main
git pull origin main
python scripts/check_workflow_health.py
python -m pytest
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify.ps1
git status --short
git --no-pager log --oneline --max-count=10
```

Compilare lo Step Closure Report:

```text
docs/37_STEP_CLOSURE_REPORT.md
templates/codex_tasks/step_closure_report_template.md
```

Solo dopo questa verifica lo step puo' essere considerato presente su `main`.

---

## 14. Errori rapidi da evitare

- Partire con uno step nuovo se il precedente non e' su `main`.
- Confondere il report Codex con merge avvenuto: il report Codex non equivale a merge su `main`.
- Ignorare `git status --short`.
- Fare `git reset --hard` senza diagnosi.
- Fare commit direttamente su `main`.
- Far fare commit, push, PR o merge a Codex.
- Saltare `gh pr checks --watch`.
- Saltare Verification Gate.
- Committare file temporanei sotto `tmp/`.

---

## 15. Dove approfondire

- `docs/32_PROMPT_PACKET_LIFECYCLE_CHECKLIST.md`: lifecycle completo dallo step al merge su `main`.
- `docs/33_PROMPT_PACKET_GENERATOR_DEVELOPER_ONBOARDING.md`: onboarding pratico per generator, validazione e ruoli.
- `docs/34_PROJECT_WORKFLOW_INDEX.md`: mappa centrale di documenti, script e template.
- `docs/35_WORKFLOW_HEALTH_CHECK.md`: controllo locale read-only del workflow.
- `docs/37_STEP_CLOSURE_REPORT.md`: standard per distinguere lavoro locale da step chiuso su `main`.
- `docs/20_VERIFICATION_GATE.md`: criteri di verifica locale e CI.
- `docs/28_PROMPT_PACKET_VALIDATION_STRICT_MODE.md`: dettagli della validazione Strict.
