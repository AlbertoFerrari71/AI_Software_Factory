# Step Closure Report Template

Usare questo template dopo il report Codex locale e dopo le operazioni Git/PR/main eseguite da Alberto.

## 1. Dati step

- Step:
- Stato:
- Branch:
- Commit step:
- PR:
- Merge commit:
- Main aggiornato:

## 2. Report Codex locale

- Report Codex ricevuto: [ ] si [ ] no
- File creati:
  - 
- File modificati:
  - 
- Test dichiarati da Codex:
  - 
- Rischi/note Codex:
  - 

## 3. Chiusura Git / PR / main

- Branch pushato: [ ] si [ ] no [ ] non applicabile
- PR creata: [ ] si [ ] no [ ] non applicabile
- PR checks verificati: [ ] si [ ] no [ ] non disponibili
- PR mergiata: [ ] si [ ] no [ ] non applicabile
- Main aggiornato localmente: [ ] si [ ] no
- Commit o merge dello step presente nel log di main: [ ] si [ ] no

## 4. Verifica finale

- Test:
- Workflow Health Check:
- Verification Gate:
- Working tree:
- `git status --short`:
- Ultimo log main:

## 5. Vincoli

- Nessun commit eseguito da Codex: [ ] confermato
- Nessun push eseguito da Codex: [ ] confermato
- Nessuna PR creata da Codex: [ ] confermato
- Nessun merge eseguito da Codex: [ ] confermato
- Nessuna modifica a GitHub da Codex: [ ] confermato
- Nessuna modifica a hook/core.hooksPath: [ ] confermato
- Nessuna modifica a CI non prevista: [ ] confermato
- Nessuna modifica a secret o `.env`: [ ] confermato

## 6. Esito

- Prossimo step:
- Frase finale:

```text
Step XXX chiuso e verificato su main.
```

oppure:

```text
Step XXX non chiuso: motivo.
```
