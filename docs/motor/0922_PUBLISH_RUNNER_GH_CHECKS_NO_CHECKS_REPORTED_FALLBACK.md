# STEP 0922 - Publish Runner Gh Checks No Checks Reported Fallback

## Scopo

Questo step corregge la gestione Phase C del publish runner quando:

```powershell
gh pr checks <PR> --watch
```

termina con output:

```text
no checks reported on the branch
```

Il caso non deve essere trattato come successo automatico, ma nemmeno come
fallimento bloccante quando esiste evidenza GitHub alternativa sufficiente sul
commit head della PR.

## Comportamento precedente

`Invoke-GhPrChecks` accettava `exit code 1` con `no checks reported` quando la
config aveva `allow_no_github_checks_reported = true`.

Questo era troppo debole per Phase C: registrava un warning, ma non verificava
se GitHub Actions avesse effettivamente prodotto run completati con successo.

## Comportamento nuovo

`Invoke-GhPrChecks` ora distingue quattro casi:

1. `gh pr checks --watch` con exit code `0`: PASS remoto normale.
2. Exit code non zero con check realmente falliti o errore gh/API: FAIL
   bloccante.
3. Exit code non zero con `no checks reported`: WARNING visibile e fallback.
4. `no checks reported` senza run GitHub alternativi `completed/success`:
   FAIL esplicito.

Il fallback prudente:

1. recupera il commit head della PR con:

   ```powershell
   gh pr view <PR> --json headRefOid --jq .headRefOid
   ```

2. interroga i workflow run sul commit:

   ```powershell
   gh run list --commit <headSha> --json status,conclusion,name,databaseId,workflowName,headSha,url --limit 20
   ```

3. accetta il remoto come equivalente PASS solo se trova almeno un run con:

   ```text
   status = completed
   conclusion = success
   headSha = <headSha PR>
   ```

In tutti gli altri casi Phase C fallisce.

## Guardrail invariati

- I gate locali non cambiano: full pytest, Workflow Health Check,
  `scripts/verify.ps1` e `git diff --check` restano obbligatori dove previsti.
- Lo STEP 0923 gestisce separatamente i warning Git LF/CRLF su stderr: restano
  warning visibili solo con exit code `0` e whitelist stretta.
- `no checks reported` resta sempre visibile nei warning del runner e nel
  Bridge output.
- Una PR senza evidenza remota alternativa non viene marcata PASS.
- Check falliti, JSON non valido, head SHA mancante o errore `gh run list`
  restano bloccanti.
- Non sono stati eseguiti commit, push, PR, merge, tag o deploy nello step.

## Test

Copertura aggiunta senza chiamate GitHub reali:

- `no checks reported` + workflow run `completed/success` sul commit head:
  PASS con warning.
- `no checks reported` + nessun workflow run success: FAIL.
- check falliti: FAIL.
- check success normale: PASS senza fallback.

Test dedicato:

```powershell
python -m pytest tests/unit/test_asf_publish_step_gh_checks_fallback.py -q
```

## Prossimo step consigliato

```text
0930) External Repo Push Pattern Generalization
```
