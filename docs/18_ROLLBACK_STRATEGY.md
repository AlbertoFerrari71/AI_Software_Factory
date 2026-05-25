# 18 — Rollback Strategy

## 1. Scopo

Ogni modifica rilevante deve poter essere annullata o neutralizzata. Questo documento definisce la strategia minima di rollback per repository, documentazione, codice, CI, dati, API e tool esterni.

---

## 2. Principi

- Prima di procedere, sapere come tornare indietro.
- Preferire branch e PR a modifiche dirette.
- Preferire quarantena a cancellazione.
- Non toccare dati reali senza backup.
- Non modificare produzione dal MVP.
- Registrare rollback nel task packet e nella PR.

---

## 3. Rollback per livello

| Livello | Strategia |
|---|---|
| L0 | nessun rollback, nessuna modifica |
| L1 | eliminare bozza o ignorare output |
| L2 | revert commit, discard branch, restore file, chiudere PR |
| L3 | revert branch + ripristino config/dipendenze + test regressione |
| L4 | backup/snapshot verificato + procedura documentata + conferma umana |

---

## 4. Repository rollback

Per modifiche L2:

1. lavorare su branch dedicato;
2. verificare diff;
3. eseguire test;
4. se fallisce, ripristinare file o eliminare branch;
5. non fare merge finché CI e review non passano.

Comandi tipici, da usare solo consapevolmente:

```powershell
git status
git diff
git restore <file>
git switch main
git branch -D <branch-locale>

```

`git reset --hard`, `git clean -fd`, force push e cancellazioni remote sono L4.

---

## 5. Documentazione rollback

Per documenti e template:

- mantenere modifiche piccole;
- usare changelog;
- registrare decisioni importanti;
- se un documento diventa errato, correggere in nuova modifica invece di cancellare history.

---

## 6. CI/CD rollback

Modifiche a `.github/workflows/**` sono L3 perché possono bloccare PR o alterare supply chain.

Rollback minimo:

- branch dedicato;
- test locale quando possibile;
- PR separata;
- confronto con workflow precedente;
- ripristino file workflow precedente se fallisce.

---

## 7. Dati e database

Nel MVP:

- database reali sono fuori automazione;
- migrazioni reali sono vietate;
- scritture su dati reali sono L4;
- letture read-only di dati reali sono almeno L3.

Per fasi future:

- backup prima di migrazione;
- migration dry-run;
- piano down/revert;
- test su copia sandbox;
- approvazione esplicita.

---

## 8. Quarantena al posto di delete

Per file/dati candidati alla cancellazione:

- spostare in cartella `_quarantine/` o rinominare con suffisso `.disabled` quando tecnicamente sicuro;
- registrare motivo;
- indicare data e task ID;
- cancellare definitivamente solo dopo approvazione L4.

---

## 9. Criterio di stop

Fermarsi immediatamente se:

- il diff contiene file non previsti;
- compaiono secret;
- falliscono test critici;
- la modifica richiede livello superiore a quello approvato;
- il rollback non è chiaro;
- il tool prova a uscire dal path consentito.
