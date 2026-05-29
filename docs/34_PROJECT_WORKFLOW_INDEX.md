# Project Workflow Index

## 1. Scopo

Questo documento e' l'indice operativo centrale del workflow AI Software Factory.

Serve a capire rapidamente quale documento leggere, quale script usare, quale template copiare, quale checklist seguire e quale verifica eseguire per una specifica attivita' del Codex Alchemy Method.

L'indice orienta il lavoro. Non sostituisce i documenti specifici, il Verification Gate, la Prompt Packet Lifecycle Checklist o il controllo umano di Alberto.

---

## 2. Mappa rapida: devo fare X

| Attivita' | Documento principale | Script/template collegati | Quando usarlo | Note |
|---|---|---|---|---|
| Capire il metodo generale | `README.md`, `docs/10_ROADMAP.md` | Nessuno | Primo orientamento sul progetto | Roadmap e decision log restano fonti di evoluzione e scelte |
| Creare un Codex Task Packet | `docs/19_PROMPT_PACKET_GENERATOR.md` | `templates/codex_tasks/codex_task_packet_template.md` | Quando serve un task packet controllato | Il packet deve includere scope, forbidden actions e report finale |
| Generare un Task Packet via CLI | `docs/29_PROMPT_PACKET_GENERATOR_CLI_HARDENING.md` | `scripts/generate_task_packet.py` | Quando step, titolo, branch e obiettivo sono gia' chiari | Produce una bozza Markdown da rivedere |
| Usare il wrapper PowerShell | `docs/30_PROMPT_PACKET_GENERATOR_PACKAGING.md` | `scripts/generate_task_packet.ps1` | Quando si lavora in PowerShell su Windows | Il wrapper delega alla CLI Python |
| Validare in Lite Mode | `docs/26_PROMPT_PACKET_VALIDATION_LITE.md` | `scripts/validate_task_packet.py` | Check rapido su task packet salvato | Non sostituisce revisione umana |
| Validare in Strict Mode | `docs/28_PROMPT_PACKET_VALIDATION_STRICT_MODE.md` | `scripts/validate_task_packet.py --strict` | Task importanti, complessi o sensibili | Strict Mode resta manuale e opt-in |
| Usare golden samples | `docs/27_PROMPT_PACKET_GOLDEN_SAMPLES.md` | `examples/task_packets/valid/`, `examples/task_packets/invalid/` | Quando si modifica validatore o template | Copiare solo i sample validi come riferimento |
| Eseguire il Release Smoke Workflow | `docs/31_PROMPT_PACKET_GENERATOR_RELEASE_SMOKE_WORKFLOW.md` | `scripts/smoke_prompt_packet_release.ps1` | Dopo modifiche a generator, wrapper o packaging | Verifica generazione, Lite Mode e Strict Mode |
| Seguire il lifecycle completo | `docs/32_PROMPT_PACKET_LIFECYCLE_CHECKLIST.md` | `templates/codex_tasks/prompt_packet_lifecycle_checklist.md` | Da preparazione step a merge su `main` | Alberto esegue commit, push, PR e merge |
| Compilare Step Closure Report | `docs/37_STEP_CLOSURE_REPORT.md` | `templates/codex_tasks/step_closure_report_template.md` | Dopo merge, pull di `main` e test finale | Distingue report Codex locale da step chiuso su `main` |
| Fare Developer Onboarding | `docs/33_PROMPT_PACKET_GENERATOR_DEVELOPER_ONBOARDING.md` | Comandi PowerShell documentati | Quando una persona interna deve iniziare a usare il workflow | Entry point pratico per generator e checklist |
| Consultare Workflow Quick Reference | `docs/36_WORKFLOW_QUICK_REFERENCE.md` | Comandi PowerShell documentati | Quando serve una scheda breve per uso quotidiano | Non sostituisce la lifecycle checklist |
| Consultare Workflow Command Cookbook | `docs/38_WORKFLOW_COMMAND_COOKBOOK.md` | Ricette PowerShell/Git/Python documentate | Quando serve gestire scenari specifici o troubleshooting | Non automatizza commit, push, PR o merge |
| Eseguire Verification Gate | `docs/20_VERIFICATION_GATE.md` | `scripts/verify.ps1` | Prima di commit/push/PR e dopo merge quando richiesto | Include test, `git diff --check`, `git status --short` |
| Controllare Documentation Sync | `docs/21_DOCUMENTATION_SYNC.md` | Nessuno | Ogni step documentale o operativo | Valuta changelog, roadmap, decisions e documenti specifici |
| Controllare Soft Protection Guardrails | `docs/24_SOFT_PROTECTION_GUARDRAILS.md` | `scripts/git/check_soft_guardrails.ps1` | Prima del commit o come controllo locale | Read-only; non installa hook |
| Eseguire Workflow Health Check | `docs/35_WORKFLOW_HEALTH_CHECK.md` | `scripts/check_workflow_health.py` | Quando workflow docs, script o riferimenti centrali cambiano | Read-only; non sostituisce Verification Gate |
| Gestire troubleshooting Git/PR/merge | `docs/32_PROMPT_PACKET_LIFECYCLE_CHECKLIST.md` | `git status --short`, `gh pr status`, `gh pr checks --watch` | Quando branch, PR o `main` non sono nello stato atteso | Non usare reset distruttivi senza diagnosi |

---

## 3. Workflow ordinario consigliato

Sequenza operativa:

```text
preparazione step -> task packet -> validazione -> Codex -> report -> verifica -> commit -> push -> PR -> checks -> merge -> pull main -> test finale -> prossimo step
```

Il riferimento completo e' `docs/32_PROMPT_PACKET_LIFECYCLE_CHECKLIST.md`.

Regole operative:

- ChatGPT prepara il task packet e coordina il metodo.
- Codex lavora localmente sul branch dedicato.
- Codex non deve fare commit, push, aprire PR o fare merge.
- Codex non modifica GitHub, hook Git o `core.hooksPath`.
- Alberto verifica, committa, pusha, apre la PR, attende i check, esegue il merge, aggiorna `main` e lancia il test finale.
- Il report Codex non equivale a merge su `main`.

---

## 4. Documenti principali

- `docs/19_PROMPT_PACKET_GENERATOR.md`: contratto generale per Prompt Packet, Codex Task Packet e prompt operativi.
- `docs/20_VERIFICATION_GATE.md`: definisce cosa significa che una modifica e' verificata.
- `docs/21_DOCUMENTATION_SYNC.md`: regola per mantenere changelog, roadmap, decision log e documenti specifici allineati.
- `docs/24_SOFT_PROTECTION_GUARDRAILS.md`: fallback locale quando la hard branch protection GitHub non e' disponibile.
- `docs/25_PROMPT_PACKET_HARDENING.md`: sezioni minime, forbidden actions, scope e report finale dei task packet.
- `docs/26_PROMPT_PACKET_VALIDATION_LITE.md`: validazione leggera dei task packet.
- `docs/27_PROMPT_PACKET_GOLDEN_SAMPLES.md`: esempi validi e invalidi per il validatore.
- `docs/28_PROMPT_PACKET_VALIDATION_STRICT_MODE.md`: validazione Strict Mode opzionale.
- `docs/29_PROMPT_PACKET_GENERATOR_CLI_HARDENING.md`: uso e limiti della CLI Python del generatore.
- `docs/30_PROMPT_PACKET_GENERATOR_PACKAGING.md`: packaging locale, wrapper PowerShell e sample generati.
- `docs/31_PROMPT_PACKET_GENERATOR_RELEASE_SMOKE_WORKFLOW.md`: smoke workflow locale del generatore.
- `docs/32_PROMPT_PACKET_LIFECYCLE_CHECKLIST.md`: ciclo operativo completo fino allo step su `main`.
- `docs/33_PROMPT_PACKET_GENERATOR_DEVELOPER_ONBOARDING.md`: onboarding per sviluppatori e utilizzatori interni.
- `docs/35_WORKFLOW_HEALTH_CHECK.md`: controllo locale read-only sulla navigabilita' del workflow.
- `docs/36_WORKFLOW_QUICK_REFERENCE.md`: scheda breve con comandi quotidiani e handoff presidiato.
- `docs/37_STEP_CLOSURE_REPORT.md`: standard per dichiarare uno step chiuso e verificato su `main`.
- `docs/38_WORKFLOW_COMMAND_COOKBOOK.md`: ricettario di comandi per scenari operativi e troubleshooting.

---

## 5. Script principali

- `scripts/generate_task_packet.py`: CLI Python del Prompt Packet Generator.
- `scripts/generate_task_packet.ps1`: wrapper PowerShell sottile per la CLI Python.
- `scripts/validate_task_packet.py`: validatore Lite Mode e Strict Mode dei task packet.
- `scripts/smoke_prompt_packet_release.ps1`: release smoke workflow locale del generatore.
- `scripts/verify.ps1`: Verification Gate locale.
- `scripts/git/check_soft_guardrails.ps1`: controllo read-only dei Soft Protection Guardrails.
- `scripts/check_workflow_health.py`: controllo read-only di documenti, riferimenti e script operativi del workflow.

Questi script non devono essere usati per automatizzare commit, push, PR o merge.

---

## 6. Template principali

- `templates/codex_tasks/codex_task_packet_template.md`: template centrale del Codex Task Packet.
- `templates/codex_tasks/prompt_packet_lifecycle_checklist.md`: checklist spuntabile per seguire il lifecycle operativo.
- `templates/codex_tasks/step_closure_report_template.md`: template compilabile per chiusura step e conferma su `main`.

---

## 7. Sequenze operative pronte

Generare un task packet strict-ready:

```powershell
python scripts/generate_task_packet.py --step 220 --title "Project Workflow Index" --branch step-220-project-workflow-index --objective "Create the central project workflow index." --output tmp/generated_step_220_task_packet.md --force --strict-ready
```

Validare in Lite Mode:

```powershell
python scripts/validate_task_packet.py tmp/generated_step_220_task_packet.md
```

Validare in Strict Mode:

```powershell
python scripts/validate_task_packet.py --strict tmp/generated_step_220_task_packet.md
```

Eseguire il Release Smoke Workflow:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\smoke_prompt_packet_release.ps1
```

Eseguire il Verification Gate:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify.ps1
```

Eseguire il Workflow Health Check:

```powershell
python scripts/check_workflow_health.py
```

Controllare Soft Protection Guardrails:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\git\check_soft_guardrails.ps1
```

Controllare stato Git finale:

```powershell
git status --short
git diff --check
```

Per una scheda compatta con i comandi piu' usati, usare `docs/36_WORKFLOW_QUICK_REFERENCE.md`.

Per formalizzare la chiusura dello step, usare `docs/37_STEP_CLOSURE_REPORT.md`.

Per scenari operativi specifici e troubleshooting, usare `docs/38_WORKFLOW_COMMAND_COOKBOOK.md`.

I comandi di commit, push, PR e merge restano azioni manuali di Alberto e non sono raccolti qui in una sequenza automatica.

---

## 8. Troubleshooting rapido

### Branch locale presente ma remoto assente

Sintomo: il branch esiste localmente, ma GitHub o `gh pr create` non lo trova.

Diagnosi:

```powershell
git branch --show-current
git status --short
gh pr status
```

Correzione manuale tipica:

```powershell
git push -u origin <branch>
```

### PR non creata

Sintomo: il lavoro e' committato e pushato, ma non esiste PR.

Diagnosi:

```powershell
gh pr status
```

Creazione manuale tipica:

```powershell
gh pr create --base main --head <branch>
```

### Main non aggiornato

Sintomo: lo step sembra mergiato su GitHub, ma non compare localmente.

Diagnosi:

```powershell
git switch main
git pull origin main
git --no-pager log --oneline --max-count=12
```

### Working tree sporca su main

Sintomo: `git status --short` mostra modifiche mentre si e' su `main`.

Diagnosi:

```powershell
git status --short
git diff --stat
```

Fermarsi prima di creare un nuovo step. Non usare `git reset --hard` senza diagnosi, senza capire le modifiche e senza decisione esplicita.

### Step successivo bloccato da prerequisito mancante

Sintomo: il task packet richiede uno step precedente su `main`, ma il log non lo mostra.

Correzione: fermarsi. Completare lo step precedente con commit, push, PR, checks, merge, pull di `main` e test finale.

### Warning CRLF/LF non bloccanti

Sintomo: Git segnala conversioni LF/CRLF.

Correzione: considerarli warning non bloccanti se `git diff --check` non segnala whitespace error reali.

### Tmp ignorato

Sintomo: file sotto `tmp/` non appaiono in `git status --short`.

Spiegazione: `tmp/` e' ignorato intenzionalmente. Usarlo per task packet temporanei e prove locali.

### Riferimenti remoti vecchi

Sintomo: branch remoti gia' chiusi compaiono ancora localmente.

Diagnosi e pulizia:

```powershell
git fetch --all --prune
```

Usarlo solo come pulizia dei riferimenti remoti, non come sostituto di diagnosi su branch o PR.

---

## 9. Anti-pattern da evitare

- Iniziare uno step se il precedente non e' su `main`.
- Confondere il report Codex con merge avvenuto.
- Ignorare `git status --short`.
- Fare `git reset --hard` senza diagnosi.
- Fare commit direttamente su `main`.
- Far fare commit, push, PR o merge a Codex.
- Saltare PR checks o `gh pr checks --watch`.
- Saltare Verification Gate.
- Saltare Workflow Health Check quando cambiano documenti o script del workflow.
- Saltare Documentation Sync perche' i test passano.
- Usare il Release Smoke Workflow come sostituto della suite `python -m pytest`.

---

## 10. Relazione con roadmap e decision log

Questo indice orienta l'uso operativo quotidiano del workflow.

La roadmap `docs/10_ROADMAP.md` descrive evoluzione, step completati e prossimi step.

Il decision log `docs/11_DECISIONS.md` registra le decisioni stabili che spiegano perche' il metodo funziona in questo modo.

Quando un futuro step cambia flussi, script, checklist o documenti centrali, aggiornare questo indice solo se il punto di ingresso operativo cambia davvero.
