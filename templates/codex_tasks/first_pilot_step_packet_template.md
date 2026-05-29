# First Pilot Step Packet Template

Usare questo template dopo l'Existing Project Intake, solo se la decisione e' GO o WARNING accettato.

## 1. Project context

- Progetto:
- Repository:
- Cartella locale:
- Branch principale:
- Branch pilota:
- Owner/verificatore:
- Decisione intake: GO / WARNING / NO-GO / HOLD

---

## 2. Obiettivo piccolo e reversibile

Obiettivo piccolo e reversibile:

```text

```

Criterio di completamento:

```text

```

Rollback o safe stop:

```text

```

---

## 3. Scope incluso

- [ ] Documentazione.
- [ ] Diagnostica locale.
- [ ] Health/status check.
- [ ] Test discovery.
- [ ] Piccola correzione reversibile.
- [ ] Altro:

Scope incluso:

```text

```

---

## 4. Scope escluso

- [ ] Refactor architetturale.
- [ ] Migrazioni dati.
- [ ] Modifiche CI.
- [ ] Modifiche sicurezza/auth.
- [ ] Dipendenze.
- [ ] Secret.
- [ ] Dati sensibili.
- [ ] Database reale.
- [ ] Produzione.
- [ ] Repository esterne non indicate.

Scope escluso:

```text

```

---

## 5. File da ispezionare

- README:
- Documentazione:
- Test:
- Script:
- Configurazioni non sensibili:
- AGENTS.md o istruzioni AI/Codex:

File da ispezionare:

```text

```

---

## 6. Vincoli

- Usare il branch pilota dedicato.
- Verificare `git status --short` prima di modificare.
- Non lavorare direttamente su `main`.
- Limitare il diff allo scope incluso.
- Non leggere o modificare secret, `.env` o dati sensibili.
- Non modificare CI.
- Non introdurre dipendenze.
- Non modificare repository esterne.

Vincoli aggiuntivi:

```text

```

---

## 7. Forbidden actions

- Nessun commit/push/PR/merge da parte di Codex.
- Non fare commit.
- Non fare push.
- Non creare PR.
- Non fare merge.
- Non fare force push.
- Non eseguire reset distruttivi.
- Non cancellare dati.
- Non modificare GitHub.
- Non installare hook Git.
- Non modificare `core.hooksPath`.
- Non modificare CI.
- Non modificare secret o `.env`.
- Non modificare dati sensibili.
- Non automatizzare commit/push/PR/merge.

Conferma nessun commit/push/PR/merge da parte di Codex:

```text
Confermato: Codex non deve fare commit, push, PR o merge.
```

---

## 8. Test/verifiche

Test automatici:

```text

```

Verifiche manuali:

```text

```

Comandi read-only o locali ammessi:

```text
git branch --show-current
git status --short
git --no-pager log --oneline --max-count=12
```

---

## 9. Dati sensibili da non toccare

Dati sensibili da non toccare:

```text

```

Secret o configurazioni locali escluse:

```text

```

---

## 10. Report finale richiesto

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
- prossimo step consigliato.

---

## 11. Step Closure Report richiesto

Dopo il lavoro locale, chiedere la compilazione dello Step Closure Report:

```text
templates/codex_tasks/step_closure_report_template.md
```

Lo Step Closure Report deve distinguere lavoro locale, commit, push, PR, merge e verifica finale su `main`.
