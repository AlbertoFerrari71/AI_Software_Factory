# Prompt Packet Lifecycle Checklist

## 1. Scopo

La Prompt Packet Lifecycle Checklist governa l'intero ciclo operativo di uno step: dalla preparazione del prompt packet fino alla conferma che lo step e' su `main` e che il prossimo step puo' iniziare.

Serve a evitare errori pratici come:

- step completato localmente ma non pushato;
- branch locale presente ma branch remoto assente;
- PR non creata;
- merge non eseguito;
- `main` non aggiornato;
- step successivo avviato prima del merge del prerequisito.

Questa checklist non automatizza commit, push, PR o merge. Codex la usa come riferimento operativo; Alberto esegue le azioni Git/GitHub che cambiano stato remoto o history.

---

## 2. Quando usarla

Usare la checklist:

- prima di lanciare Codex;
- dopo il report Codex;
- prima del commit;
- prima del push;
- prima del merge;
- prima di avviare lo step successivo.

Se un controllo bloccante fallisce, fermarsi e correggere la causa minima prima di proseguire.

---

## 3. Checklist fase 1 - Preparazione step

- Verificare che lo step precedente sia mergiato su `main`.
- Eseguire `git checkout main`.
- Eseguire `git pull origin main`.
- Verificare il log con `git --no-pager log --oneline --max-count=12`.
- Verificare che il merge o commit prerequisito sia presente nel log.
- Verificare working tree pulita con `git status --short`.
- Definire branch dedicato dello step.
- Definire obiettivo step chiaro.
- Esplicitare vincoli, forbidden actions e forbidden scope.
- Stabilire quali documenti vanno aggiornati secondo Documentation Sync.

Non iniziare uno step se il prerequisito non e' su `main`.

---

## 4. Checklist fase 2 - Task Packet

Il Codex Task Packet deve indicare:

- branch previsto;
- obiettivo;
- allowed scope;
- forbidden scope;
- file da ispezionare;
- file modificabili;
- vincoli;
- forbidden actions;
- verifiche richieste;
- output finale richiesto;
- report finale con step eseguito, stato, file creati/modificati, verifiche, rischi e prossimo step.

Il task packet deve chiarire che Codex non fa commit, push, PR, merge e non modifica GitHub.

---

## 5. Checklist fase 3 - Validazione packet

- Validare in Lite Mode quando il packet e' salvato su file:

```powershell
python scripts/validate_task_packet.py <task-packet.md>
```

- Validare in Strict Mode quando lo step e' importante, complesso o sensibile:

```powershell
python scripts/validate_task_packet.py --strict <task-packet.md>
```

- Se il packet e' stato generato con il Prompt Packet Generator, valutare lo smoke workflow:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\smoke_prompt_packet_release.ps1
```

- Se Lite o Strict falliscono, correggere il packet prima di lanciare Codex.

---

## 6. Checklist fase 4 - Esecuzione Codex

Durante l'esecuzione:

- Codex lavora su branch dedicato.
- Codex modifica solo file in scope.
- Codex non fa commit.
- Codex non fa push.
- Codex non apre PR.
- Codex non fa merge.
- Codex non modifica direttamente GitHub.
- Codex non crea GitHub Release.
- Codex non installa hook Git.
- Codex non modifica `core.hooksPath`.
- Codex non modifica secret, `.env`, CI, dipendenze, `src/**` o `policies/**` salvo richiesta esplicita compatibile con la policy.
- Codex produce report strutturato.

Se Codex segnala che serve uscire dallo scope, fermarsi e ridefinire il task.

---

## 7. Checklist fase 5 - Verifica report Codex

Il report Codex deve essere verificato prima di qualsiasi commit:

- branch corrente;
- file creati;
- file modificati;
- test eseguiti;
- verifiche non eseguite;
- rischi/note;
- conferme vincoli;
- prossimo step suggerito.

Il report Codex non equivale a merge su `main`. Uno step e' davvero completato solo dopo commit, push, PR, controlli, merge, pull di `main` e test finale.

---

## 8. Checklist fase 6 - Pre-commit

Prima del commit Alberto verifica localmente:

```powershell
git status --short
git diff --stat
git diff --check
python -m pytest
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\git\check_soft_guardrails.ps1
```

Questa fase e' il controllo locale collegato al Verification Gate del progetto.

Controllare anche:

- file temporanei sotto `tmp/` ignorati;
- nessun file fuori scope;
- nessun secret o `.env`;
- nessuna modifica a CI, dipendenze, `src/**` o `policies/**` se non esplicitamente richiesta;
- documentazione, roadmap, changelog e decision log coerenti.

Warning CRLF/LF da `git diff --check` possono essere non bloccanti se non indicano whitespace error reali.

---

## 9. Checklist fase 7 - Commit / Push / PR

Queste azioni le esegue Alberto, non Codex.

Sequenza tipica:

```powershell
git add <file>
git commit -m "<step>) <messaggio>"
git push -u origin <branch>
gh pr create --base main --head <branch>
gh pr status
gh pr checks --watch
```

Prima del push verificare che il branch locale sia quello corretto. Dopo il push verificare che il branch remoto esista.

La PR deve descrivere:

- cosa cambia;
- perche';
- test eseguiti;
- rischi;
- rollback;
- conferma Documentation Sync.

---

## 10. Checklist fase 8 - Merge e chiusura step

Queste azioni le esegue Alberto, non Codex.

Dopo CI verde e review:

```powershell
gh pr merge
git switch main
git pull origin main
python -m pytest
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify.ps1
git status --short
git --no-pager log --oneline --max-count=12
```

Confermare:

- PR mergiata;
- merge o commit dello step presente nel log di `main`;
- `main` locale aggiornato;
- test finale passato;
- working tree pulita.

Solo dopo questa conferma lo step puo' essere considerato su `main`.

---

## 11. Checklist fase 9 - Prima dello step successivo

Prima di avviare lo step successivo:

- verificare che il merge precedente sia nel log di `main`;
- verificare working tree pulita;
- verificare branch corretto;
- verificare che non esistano modifiche locali dimenticate;
- definire prossimo step;
- creare o usare il branch dedicato dello step successivo solo dopo il prerequisito.

Se il prerequisito manca, fermarsi. Non creare modifiche dello step successivo.

---

## 12. Troubleshooting

### Branch locale presente ma remoto assente

Sintomo: `git branch` mostra il branch, ma GitHub o `gh pr create` non lo trova.

Correzione:

```powershell
git push -u origin <branch>
```

### PR non creata

Sintomo: lavoro committato e pushato, ma nessuna PR esiste.

Correzione:

```powershell
gh pr status
gh pr create --base main --head <branch>
```

### Main non aggiornato

Sintomo: lo step sembra mergiato su GitHub, ma il log locale non lo mostra.

Correzione:

```powershell
git switch main
git pull origin main
git --no-pager log --oneline --max-count=12
```

### Modifiche non committate sul branch sbagliato

Sintomo: `git status --short` mostra modifiche mentre si e' su `main` o su branch non previsto.

Correzione: fermarsi, diagnosticare con `git status --short` e `git diff --stat`. Non usare `git reset --hard` senza diagnosi, senza capire il contenuto delle modifiche e senza una decisione esplicita.

### Step successivo bloccato da prerequisito mancante

Sintomo: il task packet richiede uno step precedente su `main`, ma il log non lo mostra.

Correzione: fermarsi. Completare commit, push, PR, merge, pull `main` e test finale dello step precedente.

### Warning CRLF/LF non bloccanti

Sintomo: `git diff --check` o altri comandi mostrano warning di conversione fine riga.

Correzione: considerarli warning non bloccanti se non ci sono whitespace error reali. Annotarli nel report.

### Tmp ignorato

Sintomo: file generati sotto `tmp/` non compaiono in `git status --short`.

Spiegazione: `tmp/` e' ignorato intenzionalmente. Usarlo per task packet temporanei, smoke output e prove locali.

### Origin branch rimasti come riferimenti remoti da potare

Sintomo: branch remoti vecchi appaiono ancora localmente dopo merge o delete remoto.

Correzione manuale possibile:

```powershell
git remote prune origin
```

Usare solo dopo aver verificato che i riferimenti remoti siano davvero obsoleti.

---

## 13. Anti-pattern da evitare

- Iniziare uno step se il precedente non e' su `main`.
- Trattare un report Codex come se fosse gia' un merge su `main`.
- Fare commit direttamente su `main`.
- Far fare commit, push, PR o merge a Codex.
- Ignorare `git status --short`.
- Ignorare PR checks o CI fallita.
- Usare `git reset --hard` senza diagnosi e senza decisione esplicita.
- Avviare un nuovo branch sopra un `main` non aggiornato.
- Lasciare branch locale senza push remoto quando serve una PR.
- Saltare Documentation Sync perche' i test passano.
