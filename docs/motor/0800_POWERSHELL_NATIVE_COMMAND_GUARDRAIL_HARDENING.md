# 0800 - PowerShell Native Command Guardrail Hardening

## 1. Scopo dello step

Lo STEP 0800 rafforza il controllo dei comandi nativi PowerShell nel publish
runner ASF e nei template command-pack repository-local.

Obiettivo operativo:

- impedire che `git`, `gh`, `python`, `pwsh` o altri eseguibili esterni
  falliscano in silenzio;
- leggere `$LASTEXITCODE` subito dopo ogni invocazione nativa;
- bloccare input critici vuoti prima dell'esecuzione;
- fermare Phase C se il numero PR non e' esplicito o configurato;
- validare `expected_files` e bloccare file fuori scope;
- dichiarare successo solo dopo gate e verifiche finali realmente passati.

Questo step resta local-first e human-gated: non esegue publish, merge,
commit, push, deploy o tag automatici.

## 2. Problema emerso durante il recovery 0780

Durante il recovery dello STEP 0780 e' emerso un rischio reale: uno script
PowerShell poteva proseguire dopo un fallimento nativo. In particolare, una
Phase C poteva fallire con `$PrNumber` vuoto e continuare fino a un messaggio
positivo tipo `COMPLETATO`.

La causa tecnica e' che `$ErrorActionPreference = "Stop"` intercetta gli
errori PowerShell, ma non basta da sola per trattare tutti gli exit code degli
eseguibili nativi come errori bloccanti. Anche `$?` non e' una regola
sufficiente: il runner deve leggere e classificare `$LASTEXITCODE` subito dopo
il comando nativo.

## 3. Regola ASF per comandi nativi

Regola operativa:

```text
Ogni comando nativo critico passa da Invoke-NativeChecked o da un wrapper
equivalente che valida input, esegue il comando, legge subito LASTEXITCODE,
logga label/exit code e fallisce chiuso sugli exit code non ammessi.
```

Nel publish runner, `Invoke-ArgvCommand`, `Invoke-Git`, `Invoke-Gh` e i check
configurati passano dal wrapper centrale `Invoke-NativeChecked`.

Il wrapper:

- rifiuta comando vuoto;
- rifiuta argomenti nulli, vuoti o solo whitespace;
- rifiuta `AllowedExitCodes` vuoto, salvo probe dichiarati con
  `AllowAnyExitCode`;
- imposta temporaneamente `$PSNativeCommandUseErrorActionPreference = $false`;
- esegue `& $Command @Arguments`;
- legge immediatamente `$LASTEXITCODE`;
- registra `RUN`, output ed `EXIT`;
- lancia errore bloccante se l'exit code non e' nella lista ammessa.

I probe tolleranti sono ammessi solo quando il chiamante ispeziona subito
`ExitCode`. Nel runner questo vale per controlli come "branch exists" o "find
existing PR", dove il risultato determina il ramo successivo.

## 4. Validazione di PrNumber

Phase C richiede un numero PR non vuoto prima di qualsiasi comando collegato
alla PR.

Sono ammessi:

- parametro `-PrNumber`;
- campo config `pr_number`.

Non e' piu' affidato a Phase C il recupero automatico del numero PR tramite
`gh pr list`. Se il numero manca, Phase C fallisce prima di `phase_c_started`,
prima di `gh pr view`, prima di `gh pr checks --watch` e prima di `gh pr merge`.

## 5. Validazione expected_files

`expected_files` e' un campo obbligatorio della publish config. Deve essere un
array non vuoto di stringhe non vuote.

Il runner usa `Assert-ExpectedFiles` sia nella validazione config sia nello
scope check operativo. Questo evita due problemi:

- una fase che pubblica senza scope dichiarato;
- un `git add --` costruito con lista vuota o incoerente.

## 6. File fuori scope

Quando una fase prevede uno scope atteso, il runner usa
`Assert-NoOutOfScopeFiles`.

La regola e':

```text
Se git status --porcelain=v1 --untracked-files=all mostra file non coperti da
expected_files, la fase fallisce prima di staging, commit, push o merge.
```

`expected_files` puo' includere path esatti, wildcard o suffissi `/**` per
scope espliciti di cartella.

## 7. Policy su successo e COMPLETATO

Il runner scrive output Bridge con `Status: PASS` solo dopo che la fase
selezionata e' tornata senza errori.

Per Phase C questo significa che sono gia' passati:

- numero PR non vuoto;
- `gh pr view`;
- `gh pr checks --watch` o warning controllato "no checks reported";
- `gh pr merge`;
- riallineamento `main`;
- `phase_c_checks`;
- `git --no-pager diff --check`;
- working tree clean;
- `git --no-pager log`;
- hook di stato finali, se abilitati.
- warning Git LF/CRLF su stderr solo se whitelisted e con exit code `0`.

Un messaggio positivo tipo `COMPLETATO` non deve essere scritto prima di questi
gate.

## 8. Caso speciale gh pr checks --watch

ASF mantiene la policy speciale per `gh pr checks --watch`:

- exit code `0` e' successo;
- exit code non zero con testo "no checks reported" diventa warning
  controllato solo se `allow_no_github_checks_reported=true` e il fallback
  `gh run list --commit <headSha>` trova almeno un workflow run
  `completed/success` sul commit head della PR;
- exit code non zero con check falliti, errore gh/API o assenza di workflow run
  success resta bloccante;
- `$PSNativeCommandUseErrorActionPreference` viene salvato e ripristinato dal
  wrapper.

Questo caso non indebolisce gli altri comandi `gh`, che restano controllati con
exit code ammesso `0`.

## 9. Casi speciali stderr Git whitelisted

ASF mantiene una whitelist stretta per i warning Git LF/CRLF emessi su stderr:

- `CRLF will be replaced by LF the next time Git touches it`;
- `LF will be replaced by CRLF the next time Git touches it`.

Il runner li registra come warning non bloccanti solo se il comando Git termina
con exit code `0`. Stderr Git diverso dalla whitelist resta fail-closed; exit
code diverso da `0` resta bloccante anche se lo stderr contiene un warning
LF/CRLF.

ASF mantiene anche una whitelist distinta per lo stderr informativo sicuro di
`git switch` con exit code `0`. Sono ammessi solo questi messaggi quando il
branch nel messaggio coincide con l'argv del comando:

- `Switched to branch '<branch>'` per `git switch <branch>`;
- `Switched to a new branch '<branch>'` per `git switch -c <branch>`.

Qualsiasi altro stderr Git, incluso stderr generico con exit code `0`, resta
fail-closed. Exit code non zero resta bloccante anche se lo stderr contiene uno
dei messaggi informativi ammessi.

La stessa whitelist LF/CRLF e' ammessa durante Phase B solo per lo staging
controllato dei file attesi, cioe' label `Stage expected files` con comando
`git add -- <expected files>` ed exit code `0`. Non viene resa globale per gli
altri `git add`.

## 10. Esempi

Codice buono:

```powershell
[void](Invoke-Git -RepoPath $RepoPath -ArgList @("--no-pager", "diff", "--check") -Name "Final diff check")
```

Codice buono per check configurati:

```powershell
[void](Invoke-ArgvCommand -Name "Run pytest" -Argv @("python", "-m", "pytest") -WorkingDirectory $RepoPath)
```

Codice rischioso:

```powershell
& git diff --check
Write-Host "COMPLETATO"
```

Codice rischioso:

```powershell
& gh pr merge $PrNumber --squash
if ($?) { Write-Host "OK" }
```

## 11. Superfici aggiornate

Superfici principali:

- `scripts/asf_publish_step.ps1`;
- `tests/unit/test_asf_publish_step_native_guardrails.py`;
- `docs/motor/0800_POWERSHELL_NATIVE_COMMAND_GUARDRAIL_HARDENING.md`.

Superfici repository-local gia' rafforzate nello stesso step:

- `templates/pwsh_command_pack/safe_bootstrap_template.ps1`;
- `templates/pwsh_command_pack/safe_command_pack_script_template.ps1`;
- `templates/pwsh_command_pack/README.md`;
- `templates/pwsh_command_pack/as-common-pwsh-command-pack-SKILL.md`;
- `templates/pwsh_command_pack/export/as-common-pwsh-command-pack/SKILL.md`.

## 12. Fuori scope

Restano fuori scope:

- riscrittura generale del runner;
- nuove dipendenze runtime;
- modifiche a CI, branch protection, hook Git o secret;
- installazione automatica di skill esterne;
- esecuzione reale di Phase B o Phase C;
- commit, push, PR, merge, deploy o tag.

## 13. Prossimo step consigliato

```text
0810) Publish Runner Recovery UX and No-False-Completed Guard
```

Motivo: dopo aver reso fail-closed i comandi nativi, il rischio successivo e'
migliorare messaggi di recovery, report di errore e UX di ripresa senza ridurre
i gate umani.
