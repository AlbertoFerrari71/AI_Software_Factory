# STEP 0870 - Codex_Skills Rollback Plan

## Scopo

Questo rollback plan documenta come rimuovere la micro-modifica locale creata
dallo STEP 0870 nella repo esterna `Codex_Skills`.

Il rollback non deve essere eseguito automaticamente da Codex nello STEP 0870.
Deve essere eseguito solo dopo review umana.

## File locale interessato

```text
C:\Users\alberto.ferrari\.agents\skills\docs\asf_external_pilot\0870_CONTROLLED_WRITE_PILOT.md
```

Path relativo alla repo esterna:

```text
docs/asf_external_pilot/0870_CONTROLLED_WRITE_PILOT.md
```

## Stato atteso prima del rollback

Status Git atteso in `Codex_Skills` dopo lo STEP 0870:

```text
?? docs/asf_external_pilot/
```

Il file e' untracked, locale, non committato e non pushato.

## Comando rollback

Comando PowerShell esplicito da eseguire solo dopo review umana:

```powershell
Remove-Item -Path "C:\Users\alberto.ferrari\.agents\skills\docs\asf_external_pilot\0870_CONTROLLED_WRITE_PILOT.md"
```

Questo comando rimuove solo il file creato dal pilot.

Non usare comandi di cleanup ampio come `git clean`, `git reset`, rimozioni
ricorsive o delete generici.

## Verifica dopo rollback

Dopo aver eseguito il rollback manuale, controllare:

```powershell
git -C "C:\Users\alberto.ferrari\.agents\skills" status --short
```

Se resta solo la directory vuota, valutarne la rimozione manuale separata dopo
review. Non automatizzare cleanup ricorsivi.

## Alternative al rollback

In alternativa, lo step 0880 puo' decidere di mantenere il file locale e
preparare una pubblicazione controllata separata. Questa decisione richiede un
nuovo gate umano e non e' parte dello STEP 0870.

## Divieti

Durante il rollback non eseguire:

- `git reset`;
- `git clean`;
- `git checkout`;
- `git switch`;
- `git pull`;
- `git fetch`;
- commit;
- push;
- PR;
- merge;
- deploy;
- tag;
- sync skill.
