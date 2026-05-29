# Prompt Packet Generator Developer Onboarding

## 1. Scopo della guida

Questa guida serve a far partire rapidamente un nuovo sviluppatore o utilizzatore interno sul workflow Prompt Packet.

L'obiettivo e' capire quali strumenti usare, in quale ordine usarli e quali responsabilita' restano umane prima che uno step possa essere considerato completato su `main`.

---

## 2. Contesto minimo

AI Software Factory e' il repository operativo del Codex Alchemy Method.

Il metodo e' local-first: ChatGPT prepara il Prompt Operativo o Codex Task Packet, Codex lavora localmente su branch dedicato, Alberto verifica, committa, pusha, apre la PR, attende i check, esegue il merge, aggiorna `main` e lancia il test finale.

Il Prompt Packet Generator aiuta a produrre task packet coerenti con il metodo, ma non sostituisce la revisione umana, il Verification Gate o la Prompt Packet Lifecycle Checklist.

---

## 3. Mappa degli strumenti

- `scripts/generate_task_packet.py`: CLI Python principale per generare un Codex Task Packet da parametri espliciti.
- `scripts/generate_task_packet.ps1`: wrapper PowerShell sottile che invoca la CLI Python.
- `scripts/validate_task_packet.py`: validatore Lite/Strict dei task packet salvati su file.
- `scripts/smoke_prompt_packet_release.ps1`: Release Smoke Workflow locale del generatore.
- `docs/32_PROMPT_PACKET_LIFECYCLE_CHECKLIST.md`: checklist completa dal prerequisito dello step fino al merge su `main`.
- `templates/codex_tasks/codex_task_packet_template.md`: template centrale del Codex Task Packet.
- `templates/codex_tasks/prompt_packet_lifecycle_checklist.md`: checklist spuntabile da copiare in chat, issue o task interno.

---

## 4. Quickstart operativo

Verificare branch e stato:

```powershell
git branch --show-current
git status --short
```

Generare un task packet:

```powershell
python scripts/generate_task_packet.py --step 210 --title "Prompt Packet Generator Developer Onboarding" --branch step-210-prompt-packet-generator-developer-onboarding --objective "Document developer onboarding for the prompt packet generator workflow." --output tmp/generated_step_210_task_packet.md --force --strict-ready
```

In alternativa, usare il wrapper PowerShell:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\generate_task_packet.ps1 -Step 210 -Title "Prompt Packet Generator Developer Onboarding" -Branch "step-210-prompt-packet-generator-developer-onboarding" -Objective "Document developer onboarding for the prompt packet generator workflow." -Output "tmp\generated_step_210_task_packet.md" -Force -StrictReady
```

Validare in Lite Mode:

```powershell
python scripts/validate_task_packet.py tmp/generated_step_210_task_packet.md
```

Validare in Strict Mode:

```powershell
python scripts/validate_task_packet.py --strict tmp/generated_step_210_task_packet.md
```

Eseguire il Release Smoke Workflow locale:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\smoke_prompt_packet_release.ps1
```

Seguire la Lifecycle Checklist:

```text
docs/32_PROMPT_PACKET_LIFECYCLE_CHECKLIST.md
```

Per una checklist compilabile:

```text
templates/codex_tasks/prompt_packet_lifecycle_checklist.md
```

---

## 5. Ruoli e responsabilita'

ChatGPT prepara il task packet, chiarisce obiettivo, vincoli, scope, verifiche e report finale.

Codex modifica file localmente sul branch dedicato indicato dal task packet. Codex non fa commit, Codex non fa push, Codex non apre PR e Codex non fa merge. Codex non modifica GitHub, non installa hook Git e non modifica `core.hooksPath`.

Alberto verifica diff, test, stato Git e coerenza documentale. Alberto esegue commit, push, creazione PR, attesa check, merge, pull di `main` e test finale.

---

## 6. Flusso completo consigliato

Sequenza operativa:

```text
preparazione step -> generazione packet -> validazione -> Codex -> report -> verifica -> commit -> push -> PR -> check -> merge -> pull main -> test finale -> prossimo step
```

Lo step successivo parte solo dopo aver confermato che il merge o commit dello step precedente e' presente nel log di `main`.

---

## 7. Validazioni

Lite Mode controlla che il task packet contenga sezioni e concetti minimi.

Strict Mode controlla requisiti piu' granulari per task importanti: branch, working tree, allowed scope, forbidden scope, forbidden actions, Verification Gate, Documentation Sync, Soft Protection e report finale.

Il Verification Gate controlla lo stato del repository: test, `git diff --check`, `git status --short` e gli altri controlli documentati in `scripts/verify.ps1`.

Il Release Smoke Workflow controlla solo che il Prompt Packet Generator, tramite wrapper PowerShell, generi un packet temporaneo valido in Lite Mode e Strict Mode.

---

## 8. Errori comuni

- Confondere il report Codex con merge gia' avvenuto: il report Codex non equivale a merge su `main`.
- Avviare uno step nuovo prima che il precedente sia su `main`.
- Lavorare sul branch sbagliato.
- Dimenticare push, PR o merge dopo il lavoro locale.
- Ignorare `git status --short`.
- Ignorare `gh pr checks --watch`.
- Interpretare warning CRLF/LF non bloccanti come fallimenti se non ci sono whitespace error reali.
- Committare file temporanei sotto `tmp/`.

---

## 9. Troubleshooting rapido

### Branch locale presente ma remoto assente

Diagnosticare:

```powershell
git branch --show-current
git status --short
gh pr status
```

Correzione manuale tipica, eseguita da Alberto:

```powershell
git push -u origin <branch>
```

### Working tree sporca su main

Fermarsi e diagnosticare:

```powershell
git status --short
git diff --stat
```

Non usare `git reset --hard` senza diagnosi e senza decisione esplicita.

### PR non creata

Diagnosticare:

```powershell
gh pr status
```

Creazione manuale tipica, eseguita da Alberto:

```powershell
gh pr create --base main --head <branch>
```

### Main non aggiornato

Diagnosticare:

```powershell
git switch main
git pull origin main
git --no-pager log --oneline --max-count=12
```

### Prerequisito bloccante non soddisfatto

Se il log di `main` non contiene lo step richiesto dal task packet, fermarsi. Non modificare file dello step successivo.

### Origin branch rimasti da potare

Dopo merge e cancellazione remota, alcuni riferimenti possono restare locali:

```powershell
git remote prune origin
```

Usare questo comando solo dopo aver verificato che i riferimenti remoti siano obsoleti.

---

## 10. Comandi di riferimento

Comandi utili, da eseguire manualmente quando previsto dalla checklist:

```powershell
git checkout main
git pull origin main
git --no-pager log --oneline --max-count=12
git status --short
git diff --check
python -m pytest
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\git\check_soft_guardrails.ps1
gh pr checks --watch
```

Questi comandi non devono essere racchiusi in uno script che automatizza commit, push, PR o merge.

---

## 11. Limiti attuali

- Nessuna pubblicazione PyPI.
- Nessuna pubblicazione su registry.
- Nessuna GitHub Release.
- Strict Mode non e' un required check CI se non introdotto da uno step futuro.
- La branch protection reale non e' disponibile sul repository privato con il piano GitHub attuale.
- Il workflow resta local-first e manual-gated.

---

## 12. Collegamenti interni

- `docs/19_PROMPT_PACKET_GENERATOR.md`
- `docs/28_PROMPT_PACKET_VALIDATION_STRICT_MODE.md`
- `docs/29_PROMPT_PACKET_GENERATOR_CLI_HARDENING.md`
- `docs/30_PROMPT_PACKET_GENERATOR_PACKAGING.md`
- `docs/31_PROMPT_PACKET_GENERATOR_RELEASE_SMOKE_WORKFLOW.md`
- `docs/32_PROMPT_PACKET_LIFECYCLE_CHECKLIST.md`
