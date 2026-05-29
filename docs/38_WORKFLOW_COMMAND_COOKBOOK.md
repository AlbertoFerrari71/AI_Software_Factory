# Workflow Command Cookbook

## 1. Scopo

Il Workflow Command Cookbook e' un ricettario operativo di comandi e procedure per casi specifici del workflow AI Software Factory.

La Workflow Quick Reference e' una scheda breve dei comandi principali. Questo Cookbook raccoglie scenari pratici, diagnosi e troubleshooting. I comandi sono riferimenti manuali: non sono script e non automatizzano commit, push, PR o merge.

---

## 2. Come leggere una ricetta

Ogni ricetta indica, dove possibile:

- Quando usarla;
- Comandi;
- Esito atteso;
- Se qualcosa va storto;
- Cosa non fare.

Prima di lanciare comandi che cambiano stato remoto o history, verificare branch, diff e vincoli dello step.

---

## 3. Ricetta - Stato iniziale prima di uno step

### Quando usarla

Prima di creare il branch di uno step o lanciare Codex.

### Comandi

```powershell
Set-Location "C:\Users\alberto.ferrari\source\repos\AI_Software_Factory"
git branch --show-current
git status --short
git --no-pager log --oneline --max-count=10
python scripts/check_workflow_health.py
```

### Esito atteso

- branch atteso;
- working tree pulita;
- log coerente con lo step precedente;
- Workflow Health Check passato.

### Se qualcosa va storto

Fermarsi e diagnosticare prima di creare un nuovo branch.

### Cosa non fare

Non iniziare uno step nuovo se `main` non e' aggiornato o se la working tree e' sporca.

---

## 4. Ricetta - Verificare che lo step precedente sia su main

### Quando usarla

Quando un task packet dichiara un prerequisito bloccante.

### Comandi

```powershell
git switch main
git pull origin main
git --no-pager log --oneline --max-count=12
```

### Esito atteso

Il log deve contenere il merge o commit dello step precedente.

### Se qualcosa va storto

Se il commit non compare, fermarsi. Non modificare file dello step nuovo.

### Cosa non fare

Non creare il branch dello step successivo sopra un prerequisito mancante.

---

## 5. Ricetta - Generare un task packet strict-ready

### Quando usarla

Quando step, titolo, branch e obiettivo sono gia' chiari.

### Comandi

```powershell
python scripts/generate_task_packet.py --step 260 --title "Workflow Command Cookbook" --branch step-260-workflow-command-cookbook --objective "Add a practical command cookbook for workflow operations." --output tmp/generated_step_260_task_packet.md --force --strict-ready
```

### Esito atteso

Un task packet temporaneo viene creato sotto `tmp/`.

### Se qualcosa va storto

Controllare argomenti, branch senza spazi e path di output.

### Cosa non fare

Non committare file temporanei sotto `tmp/`.

---

## 6. Ricetta - Validare un task packet Lite/Strict

### Quando usarla

Dopo la generazione o scrittura di un task packet.

### Comandi

```powershell
python scripts/validate_task_packet.py tmp/generated_step_260_task_packet.md
python scripts/validate_task_packet.py --strict tmp/generated_step_260_task_packet.md
```

### Esito atteso

Lite Mode e Strict Mode riportano `Result: PASS`.

### Se qualcosa va storto

Correggere il task packet prima di lanciare Codex.

### Cosa non fare

Non aggirare il validatore rimuovendo sezioni o vincoli dal task.

---

## 7. Ricetta - Dopo il report Codex

### Quando usarla

Quando Codex ha completato il lavoro locale sul branch dedicato.

### Comandi

```powershell
git branch --show-current
git status --short
git --no-pager diff --stat
git --no-pager diff --check
python scripts/check_workflow_health.py
python -m pytest
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify.ps1
```

### Esito atteso

Diff leggibile, file attesi, test passati, health check passato e Verification Gate passato.

### Se qualcosa va storto

Risolvere la causa minima prima del commit.

### Cosa non fare

Il report Codex non equivale a merge su main. Non avviare lo step successivo solo perche' Codex ha finito.

---

## 8. Ricetta - Commit/push/PR presidiati

### Quando usarla

Dopo verifiche locali positive e review del diff.

### Comandi

```powershell
git add .
git commit -m "260) add workflow command cookbook"
git push -u origin step-260-workflow-command-cookbook
gh pr create --base main --head step-260-workflow-command-cookbook --title "260) Workflow Command Cookbook" --body "Adds a practical command cookbook for workflow operations and troubleshooting."
```

### Esito atteso

Commit sul branch, branch remoto presente e PR creata.

### Se qualcosa va storto

Usare le ricette di troubleshooting su branch remoto assente, PR non creata o check non disponibili.

### Cosa non fare

Questi comandi li esegue Alberto, non Codex. Non sono automazione non presidiata e non devono essere messi in uno script automatico.

---

## 9. Ricetta - Gestire PR checks non disponibili

### Quando usarla

Quando il comando:

```powershell
gh pr checks --watch
```

restituisce:

```text
no checks reported on the branch
```

### Comandi

```powershell
python scripts/check_workflow_health.py
python -m pytest
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify.ps1
git status --short
```

### Esito atteso

Le verifiche locali obbligatorie passano e la situazione dei check PR viene registrata nello Step Closure Report.

### Se qualcosa va storto

Aprire la PR su GitHub per controllo manuale o usare altri comandi `gh` read-only per diagnosticare. Procedere solo in contesto controllato.

### Cosa non fare

Non ignorare ciecamente `no checks reported on the branch`. Non dichiarare check verdi senza evidenza.

---

## 10. Ricetta - Merge e verifica finale main

### Quando usarla

Dopo review e check PR positivi o dopo gestione documentata dei check non disponibili.

### Comandi

```powershell
gh pr merge --merge --delete-branch
git switch main
git pull origin main
python scripts/check_workflow_health.py
python -m pytest
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify.ps1
git status --short
git --no-pager log --oneline --max-count=10
```

### Esito atteso

Lo step compare nel log di `main`, le verifiche finali passano e la working tree e' pulita.

### Se qualcosa va storto

Non dichiarare chiuso lo step. Registrare lo stato nello Step Closure Report.

### Cosa non fare

Non fare merge se i check sono falliti o non sono stati valutati.

---

## 11. Ricetta - Branch locale presente ma branch remoto assente

### Quando usarla

Quando il lavoro esiste localmente ma GitHub non mostra il branch o la PR. Scenario gia' incontrato con STEP 180.

### Comandi

```powershell
git branch --list "*180*"
git branch -r --list "*180*"
git --no-pager log --oneline --decorate --all --max-count=20
git stash list
```

### Esito atteso

Si capisce se esiste un commit locale e se manca solo il branch remoto.

### Se qualcosa va storto

Se esiste commit locale ma branch remoto assente, non rifare lo step: pushare branch, creare PR, mergiare.

### Cosa non fare

Non duplicare il lavoro e non cancellare branch locali senza diagnosi.

---

## 12. Ricetta - Modifiche sul branch sbagliato

### Quando usarla

Quando `git status --short` mostra modifiche su un branch diverso da quello previsto.

### Comandi

```powershell
git branch --show-current
git status --short
git --no-pager diff --stat
```

### Esito atteso

Si conoscono branch corrente, file modificati e dimensione del diff.

### Se qualcosa va storto

Se le modifiche possono essere portate sul branch corretto, usare `git switch <branch>` solo se Git lo consente senza conflitti. In caso di dubbio fermarsi e chiedere diagnosi.

### Cosa non fare

Non usare `reset --hard` senza diagnosi e senza capire quali modifiche verrebbero perse.

---

## 13. Ricetta - working tree sporca su main

### Quando usarla

Quando si e' su `main` e compaiono modifiche locali.

### Comandi

```powershell
git branch --show-current
git status --short
git --no-pager diff --stat
```

### Esito atteso

Si capisce se `main` e' pulito o se contiene modifiche locali da gestire.

### Se qualcosa va storto

Fermarsi e diagnosticare. Non iniziare uno step nuovo su `main` sporco.

### Cosa non fare

Non creare branch nuovi sopra modifiche non comprese.

---

## 14. Ricetta - Health check fallito

### Quando usarla

Quando il workflow health check segnala `FAILED`.

### Comandi

```powershell
python scripts/check_workflow_health.py
```

### Esito atteso

L'output indica area fallita, file coinvolto, requisito mancante e suggerimento breve.

### Se qualcosa va storto

Correggere il riferimento o documento mancante prima di proseguire. Rilanciare il check dopo la correzione.

### Cosa non fare

Non ignorare il failure solo perche' `python -m pytest` passa.

---

## 14.1 Ricetta - Dashboard stato workflow

### Quando usarla

Quando serve una vista rapida di branch corrente, working tree, commit recenti e file workflow centrali senza aprire tutti i documenti.

### Comandi

```powershell
python scripts/show_workflow_status.py
```

### Esito atteso

La Workflow Status Dashboard mostra stato locale e prossimi controlli consigliati.

### Se qualcosa va storto

Se mancano documenti o script centrali, correggere il riferimento o ripristinare il file prima di proseguire.

### Cosa non fare

Non usare la dashboard come sostituto di Workflow Health Check, Verification Gate o PR checks.

Documento: `docs/39_WORKFLOW_STATUS_DASHBOARD.md`.

---

## 14.2 Ricetta - Valutare Release Readiness

### Quando usarla

Prima di applicare AI Software Factory a un progetto reale, soprattutto se il progetto e' gia' avviato o a meta' sviluppo.

### Comandi

Usare la checklist:

```text
docs/40_RELEASE_READINESS.md
templates/codex_tasks/release_readiness_checklist.md
```

### Esito atteso

La decisione finale e' una tra `GO pilot`, `GO pilot with warnings`, `HOLD` o `NO-GO`.

### Se qualcosa va storto

Se emergono dati sensibili, working tree non compresa, refactor massivo o assenza di Git, fermarsi e preparare un Project Intake prima di proseguire.

### Cosa non fare

Non trattare la readiness per pilot come release pubblica, SaaS, installer, PyPI package o GitHub Release.

---

## 14.3 Ricetta - Preparare Existing Project Pilot Onboarding

### Quando usarla

Dopo Release Readiness e prima del primo pilot reale su un progetto esistente.

### Comandi

Usare il protocollo e i template:

```text
docs/41_EXISTING_PROJECT_PILOT_ONBOARDING.md
templates/codex_tasks/existing_project_intake_template.md
templates/codex_tasks/first_pilot_step_packet_template.md
```

Nel repository del progetto pilota usare solo comandi diagnostici read-only finche' il task packet pilot non e' approvato:

```powershell
git branch --show-current
git status --short
git --no-pager log --oneline --max-count=12
git branch --list
git branch -r --list
git stash list
```

### Esito atteso

Il Project Intake produce una decisione GO, WARNING, HOLD o NO-GO e un primo step pilota piccolo e reversibile.

### Se qualcosa va storto

Se emergono working tree sporca non compresa, dati sensibili, secret, assenza Git, richiesta di lavoro diretto su `main` o refactor massivo, fermarsi e non modificare il repository esterno.

### Cosa non fare

Non trasformare l'onboarding in refactor architetturale. Non creare automazioni cross-repository. Non modificare CI, secret, dati sensibili o repository esterne durante l'intake.

---

## 15. Ricetta - Verification Gate fallito

### Quando usarla

Quando il gate locale non passa.

### Comandi

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify.ps1
```

### Esito atteso

Il gate distingue test falliti, whitespace/diff check e working tree non pulita.

### Se qualcosa va storto

Leggere quale sezione fallisce e correggere la causa minima.

### Cosa non fare

Non dichiarare lo step verificato se il Verification Gate fallisce.

---

## 16. Ricetta - Pulizia riferimenti remoti vecchi

### Quando usarla

Quando branch remoti gia' chiusi compaiono ancora localmente.

### Comandi

```powershell
git fetch --all --prune
```

### Esito atteso

I riferimenti remoti locali obsoleti vengono potati.

### Se qualcosa va storto

Rileggere l'output e verificare con `git branch -r`.

### Cosa non fare

Questo comando non modifica i branch remoti gia' eliminati. Non usarlo come sostituto della diagnosi su branch, PR o merge.

---

## 17. Ricetta - CRLF/LF warning

### Quando usarla

Quando Git mostra warning di conversione fine riga.

### Comandi

```powershell
git --no-pager diff --check
python -m pytest
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify.ps1
```

### Esito atteso

I warning CRLF/LF non sono automaticamente bloccanti se:

- `git diff --check` ha exit code 0;
- Verification Gate passa;
- i test passano.

### Se qualcosa va storto

Se `git diff --check` segnala errori reali, correggere whitespace o fine riga.

### Cosa non fare

Non confondere warning non bloccanti con fallimenti dei test.

---

## 18. Ricetta - Preparare il report finale di chiusura step

### Quando usarla

Dopo merge, pull di `main` e verifiche finali.

### Comandi

Usare il template:

```text
templates/codex_tasks/step_closure_report_template.md
```

Campi chiave:

- step;
- stato;
- commit;
- PR;
- merge commit;
- health check;
- Verification Gate;
- working tree;
- prossimo step.

### Esito atteso

Il report dichiara se lo step e' chiuso e verificato su `main` oppure non chiuso con motivo.

### Se qualcosa va storto

Usare lo stato piu' preciso disponibile, ad esempio `In attesa check`, `Mergiato su main` o `Non completato`.

### Cosa non fare

Non scrivere "chiuso" se mancano merge, pull `main` o verifiche finali.

---

## 19. Anti-pattern finali

- Usare `reset --hard` per "pulire" senza diagnosi.
- Iniziare lo step successivo senza merge su `main`.
- Considerare report Codex come step chiuso.
- Ignorare `git status --short`.
- Saltare PR checks.
- Saltare health check.
- Far fare commit, push, PR o merge a Codex.
- Committare `tmp/`.

Codex non deve fare commit, Codex non deve fare push, Codex non deve aprire PR e Codex non deve fare merge.

---

## 20. Collegamenti utili

- `docs/32_PROMPT_PACKET_LIFECYCLE_CHECKLIST.md`
- `docs/34_PROJECT_WORKFLOW_INDEX.md`
- `docs/35_WORKFLOW_HEALTH_CHECK.md`
- `docs/36_WORKFLOW_QUICK_REFERENCE.md`
- `docs/37_STEP_CLOSURE_REPORT.md`
- `docs/39_WORKFLOW_STATUS_DASHBOARD.md`
- `docs/40_RELEASE_READINESS.md`
- `docs/41_EXISTING_PROJECT_PILOT_ONBOARDING.md`
- `templates/codex_tasks/step_closure_report_template.md`
