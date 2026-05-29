# ASF Next Step Runner Handoff Template

Usare questo template come struttura di handoff manuale da ChatGPT/Alberto verso Codex.

## 1. Progetto

- Progetto:
- Repo path:
- Branch principale:
- Branch corrente rilevato:
- Working tree: CLEAN / DIRTY-WARNING

## 2. Step

- Step:
- Titolo:
- Branch previsto:
- Obiettivo:

## 3. Prerequisito

- [ ] Task packet letto.
- [ ] Branch principale verificato.
- [ ] Branch di lavoro previsto verificato.
- [ ] Working tree compresa.
- [ ] Alberto ha deciso se proseguire in caso di DIRTY-WARNING.

## 4. Vincoli

- Usare branch dedicato.
- Mantenere diff piccolo, reversibile e testabile.
- Non modificare repository target fuori dallo scope.
- Non modificare CI.
- Non modificare dipendenze.
- Non modificare secret, `.env` o dati sensibili.
- Non installare hook Git.
- Non modificare `core.hooksPath`.

## 5. Forbidden actions

- Nessun commit/push/PR/merge da parte di Codex.
- Non fare commit.
- Non fare push.
- Non creare PR.
- Non fare merge.
- Non modificare GitHub.
- Non creare release.
- Non eseguire reset distruttivi.
- Non cancellare dati.
- Non invocare altri agenti o Codex automaticamente.

## 6. Test

Test automatici richiesti:

```text

```

Verifiche manuali richieste:

```text

```

Verifiche non eseguibili e motivo:

```text

```

## 7. Report finale

Il report finale deve indicare:

- step eseguito;
- stato;
- branch corrente;
- file creati;
- file modificati;
- descrizione tecnica sintetica;
- comandi eseguiti e risultati;
- verifiche non eseguite;
- rischi o note;
- conferme vincoli;
- prossimo step consigliato;
- richiesta Step Closure Report.

## 8. Conferma nessun commit/push/PR/merge

```text
Confermato: Codex non deve fare commit, push, PR o merge.
```

