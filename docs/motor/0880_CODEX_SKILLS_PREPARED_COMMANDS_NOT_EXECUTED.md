# STEP 0880 - Codex_Skills Prepared Commands Not Executed

## Stato comandi

Tutti i comandi in questo documento sono preparati ma NON ESEGUITI.

Non eseguire automaticamente questi comandi. Usarli solo dopo approvazione
esplicita di Alberto e in uno step dedicato.

## Opzione A - Rollback del file 0870

Stato: NON ESEGUITO.

Comando PowerShell proposto, puntuale sul file:

```powershell
Remove-Item -Path "C:\Users\alberto.ferrari\.agents\skills\docs\asf_external_pilot\0870_CONTROLLED_WRITE_PILOT.md"
```

Eventuale rimozione cartella solo se vuota, da eseguire con cautela e solo
dopo review umana:

```powershell
$PilotDir = "C:\Users\alberto.ferrari\.agents\skills\docs\asf_external_pilot"
if ((Test-Path -Path $PilotDir) -and -not (Get-ChildItem -Path $PilotDir -Force)) {
    Remove-Item -Path $PilotDir
}
```

Divieti per il rollback:

- non usare `git clean`;
- non usare `git reset`;
- non usare cleanup ricorsivi ampi;
- non cancellare altri file.

## Opzione B - Keep local temporaneo

Stato: NON ESEGUITO.

Nessun comando richiesto. La repo esterna resta dirty con:

```text
?? docs/asf_external_pilot/
```

Questa opzione va mantenuta solo per breve review manuale.

## Opzione C - Future controlled commit

Stato: NON ESEGUITO.

Questi comandi sono solo esempio per uno step separato, da usare solo dopo
approvazione esplicita:

```powershell
git -C "C:\Users\alberto.ferrari\.agents\skills" status --short
git -C "C:\Users\alberto.ferrari\.agents\skills" add docs/asf_external_pilot/0870_CONTROLLED_WRITE_PILOT.md
git -C "C:\Users\alberto.ferrari\.agents\skills" commit -m "0870 add ASF controlled write pilot note"
```

NON ESEGUITO.

DA USARE SOLO DOPO APPROVAZIONE ESPLICITA.

Un eventuale push, PR o merge deve restare separato e human-gated. STEP 0880
non autorizza commit, push, PR, merge, deploy o tag.
