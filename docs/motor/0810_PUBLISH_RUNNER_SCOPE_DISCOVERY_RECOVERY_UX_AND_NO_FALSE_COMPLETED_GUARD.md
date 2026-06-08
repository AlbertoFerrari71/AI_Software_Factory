# 0810 - Publish Runner Scope Discovery, Recovery UX and No-False-Completed Guard

## 1. Contesto 0800/0805

Lo STEP 0800 ha rafforzato il publish runner PowerShell con guardrail per
comandi nativi, `PrNumber`, `expected_files`, file fuori scope e no false
`COMPLETATO`.

Lo STEP 0805 ha sincronizzato template e skill PowerShell sul flusso stabile:

```text
config JSON esplicito + scripts/asf_publish_step.ps1 + Phase B -> recupero PR -> Phase C
```

Durante la pubblicazione reale degli step 0800 e 0805 sono emersi due problemi
accessori da consolidare:

- config con `expected_files` o `changed_files` incompleti;
- errore DOCX/accessorio dopo publish 0805 gia' verificato: `A parameter cannot be found that matches parameter name 'Encoding'.`

## 2. Problema ricorrente dello scope

Il runner faceva bene a bloccare file fuori scope, ma il processo di
preparazione era troppo manuale:

1. Codex modifica piu' file;
2. la config JSON dichiara lo scope a mano;
3. un file viene dimenticato;
4. Phase A/B blocca con `Out-of-scope changes detected`;
5. serve rigenerare manualmente la config.

Il difetto non e' il blocco. Il blocco e' corretto. Il difetto e' la recovery
faticosa quando lo scope atteso e' incompleto.

## 3. Regola fail-closed

Lo scope discovery non rende il runner permissivo.

Regola:

```text
Il runner puo' scoprire e proporre file, ma non approva automaticamente lo scope.
```

Se un file modificato non e' coperto da `expected_files`, la pubblicazione resta
bloccata prima di staging, commit, push, PR, merge o deploy.

## 4. Discovery dei file modificati

Lo STEP 0810 aggiunge `Get-RepositoryChangedFiles`.

La funzione usa solo stdout di questi comandi Git:

```powershell
git --no-pager diff --name-only --
git --no-pager diff --cached --name-only --
git ls-files --others --exclude-standard --
```

Policy tecnica:

- stdout e stderr sono separati;
- stderr Git non diventa lista file;
- path normalizzati con slash `/`;
- righe vuote rimosse;
- duplicati rimossi;
- path assoluti, `../` e righe tipo `warning:`, `fatal:`, `error:` o `hint:` ignorati;
- warning LF/CRLF non sono file fuori scope.

## 5. PrepareConfig

Il runner supporta la Phase `PrepareConfig`.

Esempio:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\asf_publish_step.ps1 `
  -Phase PrepareConfig `
  -StepNumber 0810 `
  -StepName "Publish_Runner_Scope_Discovery_Recovery_UX_And_No_False_Completed_Guard" `
  -BranchName "step-0810-publish-runner-scope-discovery-recovery-ux" `
  -CommitMessage "0810 add publish runner scope discovery and recovery UX" `
  -PrTitle "0810 add publish runner scope discovery and recovery UX" `
  -NextStep "0820) Bridge Output Retry, Fallback and LAST Validation" `
  -RiskLevel L1
```

La Phase:

- legge i file modificati reali;
- genera una bozza JSON nel Bridge;
- popola `expected_files` e `changed_files`;
- include campi standard publish;
- genera un report Markdown di review;
- non esegue Phase B/C;
- non fa commit, push, PR, merge, deploy o tag.

La bozza e' da rivedere prima di Phase B.

## 6. Recovery out-of-scope

Se Phase A/B trova file fuori scope, il runner:

- blocca comunque;
- stampa i file fuori scope;
- stampa lo scope dichiarato;
- stampa i changed files reali;
- scrive un recovery report Markdown nel Bridge;
- scrive un suggested config JSON con `expected_files` e `changed_files` aggiornati;
- non procede automaticamente.

Istruzione operativa:

```text
Review the suggested config. If the files are expected, rerun Phase B with the updated config.
```

Il recovery report distingue:

- file realmente modificati;
- file dichiarati nella config;
- file fuori scope;
- warning/non-file ignorati.

## 7. LF/CRLF

Warning Git su line ending non sono path.

Sono warning non bloccanti quando passano:

- test;
- Workflow Health Check;
- Verification Gate;
- `git --no-pager diff --check`.

Non usare output Git catturato con `2>&1` come lista file: i warning possono
contaminare lo scope.

## 8. No-false-COMPLETATO

Il runner deve stampare `PHASE completed`, `COMPLETATO` o Bridge `PASS` solo
dopo la fase realmente completata.

Hardening 0810:

- Phase B richiede `-ApprovePublish`;
- Phase B fallisce se non risolve un numero PR non vuoto e numerico;
- Phase C richiede `-ApproveMerge`;
- Phase C richiede `PrNumber` non vuoto e numerico prima di qualunque comando PR;
- Phase C fallisce se `gh pr view`, `gh pr checks`, `gh pr merge`, `git switch`, `git pull`, check finali, diff check o working tree finale falliscono.

Il report Bridge distingue:

- `COMPLETATO`;
- `COMPLETATO CON WARNING`;
- `COMPLETATO CON WARNING NON BLOCCANTE`;
- `BLOCCATO`.

## 9. Output accessori e DOCX best-effort

Output primari obbligatori:

- output completo TXT;
- output compatto Markdown;
- `LAST-Output_Compatto.md`.

DOCX e output accessori sono best-effort.

Se DOCX fallisce dopo i gate finali:

- lo stato non diventa `BLOCCATO`;
- lo stato operativo e' `COMPLETATO CON WARNING NON BLOCCANTE`;
- il warning viene scritto nel compatto;
- viene scritto un marker `.docx.failed.txt`;
- PR mergiata, commit finale, health PASS, verify PASS, diff check PASS e working tree pulito non vengono oscurati.

Word COM non e' requisito bloccante.

## 10. Impatto su skill/template

I template `templates/pwsh_command_pack/` ora raccomandano:

1. `PrepareConfig` o scope discovery;
2. review umana dello scope;
3. Phase B con config JSON revisionato;
4. recupero PR con `gh pr list --head`;
5. validazione PR non vuoto e numerico;
6. Phase C con `PrNumber`;
7. verifiche finali;
8. output Bridge numerati e `LAST-*`;
9. clipboard con `Get-Content -Path ... -Raw | Set-Clipboard`;
10. DOCX/accessori best-effort;
11. mai `COMPLETATO` prima dei gate finali.

## 11. Esempi operativi

Generare bozza scope:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\asf_publish_step.ps1 -Phase PrepareConfig -StepNumber 0810 -StepName "Name" -BranchName "step-0810-name" -CommitMessage "0810 name" -PrTitle "0810 name" -NextStep "0820) ..."
```

Quando Phase B segnala out-of-scope:

```text
1. Aprire il recovery report.
2. Confrontare changed files, expected_files e out-of-scope files.
3. Se i file sono attesi, usare la suggested config o aggiornare manualmente la config.
4. Rieseguire Phase B.
```

## 12. Fuori scope

Lo STEP 0810 non introduce:

- publish automatico;
- auto-commit;
- push diretto a `main`;
- apertura PR automatica fuori Phase B autorizzata;
- merge automatico fuori Phase C autorizzata;
- nuove dipendenze pesanti;
- Word COM obbligatorio;
- parser fragile di `git status --short`;
- uso di `2>&1` come lista file;
- riscrittura generale del publish runner.

Prossimo step consigliato:

```text
0820) Bridge Output Retry, Fallback and LAST Validation
```
