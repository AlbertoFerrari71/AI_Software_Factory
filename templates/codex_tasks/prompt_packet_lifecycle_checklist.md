# Prompt Packet Lifecycle Checklist

Usare questa checklist per uno step operativo AI Software Factory.

## Dati step

- [ ] Step: `...`
- [ ] Titolo: `...`
- [ ] Branch dedicato: `...`
- [ ] Obiettivo sintetico: `...`
- [ ] Step successivo previsto: `...`

## Prerequisito

- [ ] Alberto ha verificato `git checkout main`.
- [ ] Alberto ha eseguito `git pull origin main`.
- [ ] Alberto ha controllato `git --no-pager log --oneline --max-count=12`.
- [ ] Il merge/commit dello step precedente e' presente su `main`.
- [ ] `git status --short` e' pulito prima di iniziare.

## Branch

- [ ] Branch dedicato definito nel task packet.
- [ ] Branch creato/usato solo dopo prerequisito soddisfatto.
- [ ] Codex lavora solo sul branch dedicato.

## Task packet

- [ ] Branch previsto presente.
- [ ] Obiettivo presente.
- [ ] Allowed scope presente.
- [ ] Forbidden scope presente.
- [ ] File da ispezionare presenti.
- [ ] Vincoli presenti.
- [ ] Forbidden actions presenti.
- [ ] Verifiche richieste presenti.
- [ ] Output finale richiesto presente.
- [ ] Report finale con step eseguito, stato e prossimo step.

## Validazione

- [ ] Alberto/Codex ha eseguito Lite Mode se il packet e' su file.
- [ ] Alberto/Codex ha eseguito Strict Mode se applicabile.
- [ ] Eventuale smoke workflow del generator eseguito se rilevante.
- [ ] Errori di validazione corretti prima di lanciare Codex.

## Esecuzione Codex

- [ ] Codex non fa commit.
- [ ] Codex non fa push.
- [ ] Codex non apre PR.
- [ ] Codex non fa merge.
- [ ] Codex non modifica GitHub.
- [ ] Codex non installa hook Git.
- [ ] Codex non modifica `core.hooksPath`.
- [ ] Codex produce report strutturato.

## Codex report

- [ ] Branch corrente indicato.
- [ ] File creati indicati.
- [ ] File modificati indicati.
- [ ] Test/verifiche eseguiti indicati.
- [ ] Verifiche non eseguite indicate.
- [ ] Rischi/note indicati.
- [ ] Conferme vincoli indicate.
- [ ] Prossimo step suggerito.
- [ ] Il report Codex non viene trattato come merge su `main`.

## Pre-commit

- [ ] Alberto ha eseguito `git status --short`.
- [ ] Alberto ha eseguito `git diff --stat`.
- [ ] Alberto ha eseguito `git diff --check`.
- [ ] Alberto ha eseguito `python -m pytest`.
- [ ] Alberto ha eseguito `pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify.ps1`.
- [ ] Alberto ha eseguito `pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\git\check_soft_guardrails.ps1`.
- [ ] File temporanei sotto `tmp/` non sono tracciati.
- [ ] Documentation Sync completato.

## PR / merge

Queste azioni sono di Alberto, non di Codex.

- [ ] Alberto ha eseguito `git add <file>`.
- [ ] Alberto ha eseguito `git commit -m "<step>) <messaggio>"`.
- [ ] Alberto ha eseguito `git push -u origin <branch>`.
- [ ] Alberto ha creato PR con `gh pr create --base main --head <branch>`.
- [ ] Alberto ha verificato `gh pr status`.
- [ ] Alberto ha atteso `gh pr checks --watch`.
- [ ] Alberto ha eseguito merge solo dopo check verdi.

## Main finale

- [ ] Alberto ha eseguito `gh pr merge`.
- [ ] Alberto ha eseguito `git switch main`.
- [ ] Alberto ha eseguito `git pull origin main`.
- [ ] Alberto ha eseguito `python -m pytest`.
- [ ] Alberto ha eseguito `pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify.ps1`.
- [ ] Alberto ha verificato `git status --short`.
- [ ] Alberto ha verificato `git --no-pager log --oneline --max-count=12`.
- [ ] Lo step e' presente nel log di `main`.

## Prossimo step

- [ ] Working tree pulita.
- [ ] Branch corretto.
- [ ] Step successivo definito.
- [ ] Prerequisito del prossimo step verificabile su `main`.
