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

Un messaggio positivo tipo `COMPLETATO` non deve essere scritto prima di questi
gate.

## 8. Caso speciale gh pr checks --watch

ASF mantiene la policy speciale per `gh pr checks --watch`:

- exit code `0` e' successo;
- exit code `1` con testo "no checks reported" e config
  `allow_no_github_checks_reported=true` diventa warning controllato;
- exit code `1` con altro testo fallisce;
- altri exit code falliscono;
- `$PSNativeCommandUseErrorActionPreference` viene salvato e ripristinato dal
  wrapper.

Questo caso non indebolisce gli altri comandi `gh`, che restano controllati con
exit code ammesso `0`.

## 9. Esempi

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

## 10. Superfici aggiornate

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

## 11. Fuori scope

Restano fuori scope:

- riscrittura generale del runner;
- nuove dipendenze runtime;
- modifiche a CI, branch protection, hook Git o secret;
- installazione automatica di skill esterne;
- esecuzione reale di Phase B o Phase C;
- commit, push, PR, merge, deploy o tag.

## 12. Prossimo step consigliato

```text
0810) Publish Runner Recovery UX and No-False-Completed Guard
```

Motivo: dopo aver reso fail-closed i comandi nativi, il rischio successivo e'
migliorare messaggi di recovery, report di errore e UX di ripresa senza ridurre
i gate umani.
