# 0250 - Dropbox Bridge Shared Specification

## Scopo

[F] Questo documento propone una struttura Dropbox Bridge condivisa per prompt, report, log e handoff operativi Alberto-Luca.

[F] Il Bridge non e' repository Git e non deve diventare la fonte ufficiale del codice.

[S] Separare cartelle per progetto e utente riduce conflitti, overwrite e file `conflicted copy`.

## Decisioni

- [F] I repository Git non devono stare in Dropbox come working copy principale.
- [F] Il Bridge contiene prompt, report, log, template operativi e handoff.
- [F] File condivisi usano nomi numerati/datati; niente `LAST-*` o `latest-*` nelle cartelle condivise.
- [S] La root proposta e' `D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge_Shared`.
- [O] Ogni utente scrive nella propria sotto-cartella e pubblica solo report finali in `shared_reports`.

## Struttura proposta

```text
D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge_Shared
  _shared_docs
  _handoff
  _templates
  AI_Software_Factory
    alberto
      codex_command
      pwsh_command
    luca
      codex_command
      pwsh_command
    shared_reports
  AI_Release_Radar
    alberto
      codex_command
      pwsh_command
    luca
      codex_command
      pwsh_command
    shared_reports
  ASF_Blueprint_Studio
    alberto
      codex_command
      pwsh_command
    luca
      codex_command
      pwsh_command
    shared_reports
  Codex_Skills
    alberto
      codex_command
      pwsh_command
    luca
      codex_command
      pwsh_command
    shared_reports
```

## Perche' non mettere repo Git in Dropbox

[F] Dropbox puo' sincronizzare file parziali, creare copie in conflitto, bloccare file aperti e modificare timing di scrittura.

[F] Git richiede un working tree coerente e una directory `.git` integra.

[O] Tenere i repo in `C:\Users\...\source\repos` e usare Dropbox solo per Bridge riduce rischi difficili da diagnosticare.

## Naming file

[F] Vietati nelle cartelle condivise:

```text
LAST-*
latest-*
```

[S] Formati consigliati:

```text
NNNN-AF-Tipo_Nome.md
NNNN-LF-Tipo_Nome.md
NNNN-YYYYMMDD-HHMMSS-Autore-Tipo_Nome.md
```

Esempi:

```text
0290-AF-Prompt_Codex.md
0290-LF-Report_Readonly.md
0290-20260611-153000-AF-Handoff.md
```

## Regole per report Codex e PowerShell

- [F] Report Codex in `codex_command`.
- [F] Report PowerShell in `pwsh_command`.
- [F] Report condivisi finali o sintetici in `shared_reports`.
- [F] Ogni report deve indicare repo, branch, commit/HEAD, test eseguiti e azioni non eseguite.
- [F] Nessun report deve contenere token, password, chiavi o valori `.env`.

## Regole per file condivisi

- [F] `_shared_docs` contiene documenti operativi non versionati, solo se non appartengono a un repo.
- [F] `_handoff` contiene passaggi temporanei tra Alberto e Luca.
- [F] `_templates` contiene copie operative di template, non la fonte ufficiale se esiste template versionato.
- [O] Se un file diventa stabile, spostare il contenuto nel repository e lasciare nel Bridge solo il riferimento.

## Cosa mettere e cosa non mettere nel Bridge

| Mettere | Non mettere |
|---|---|
| Prompt Codex numerati | Repository Git |
| Report Codex/PowerShell | `.git`, working tree, checkout |
| Log operativi sanitizzati | Token, API key, password |
| Handoff temporanei | File `.env` reali |
| Output review | Branch protection export con segreti |

## Regole operative

- [F] Uno scrittore per file.
- [F] Nessun overwrite manuale su file dell'altro utente.
- [F] Se nasce una `conflicted copy`, fermarsi e confrontare contenuto prima di proseguire.
- [F] Creare cartelle con script safe-by-default in dry-run prima dell'apply.
- [O] Usare `shared_reports` solo per report consolidati, non per bozze rumorose.

## Rischi

| Rischio | Mitigazione |
|---|---|
| Conflicted copy Dropbox | Cartelle per utente e file timestampati |
| Repo Git danneggiato | Repo fuori Dropbox |
| Report con segreti | Scan minimo e redazione manuale |
| Ultimo file ambiguo | Nome numerato/datato, niente LAST/latest condivisi |

## Checklist

- [ ] [S] Root condivisa scelta.
- [ ] [F] Dry-run struttura eseguito.
- [ ] [F] Apply struttura autorizzato, se necessario.
- [ ] [F] Cartelle per Alberto e Luca separate.
- [ ] [F] Naming senza `LAST-*` e `latest-*` applicato.
- [ ] [F] Nessun repo Git in Dropbox.

## Prossimo step consigliato

[O] Eseguire `scripts/collaboration/New-SharedBridgeStructure.ps1` in dry-run durante il pilot 0290.