# STEP 0923 - Publish Runner LF/CRLF Warning Stderr Handling

## Scopo

Questo step corregge una fragilita' del publish runner quando Git scrive su
stderr warning noti di conversione line ending, per esempio:

```text
warning: in the working copy of 'scripts/asf_next_step.py', CRLF will be replaced by LF the next time Git touches it
warning: in the working copy of 'scripts/asf_publish_step.ps1', LF will be replaced by CRLF the next time Git touches it
```

Questi warning non sono whitespace error reali se il comando Git termina con
exit code `0`.

## Comportamento precedente

Alcuni comandi del runner mescolavano stdout e stderr oppure accettavano stderr
in modo troppo generico durante la discovery dei path.

Durante la pubblicazione dello STEP 0922, `git --no-pager diff --check` ha
restituito exit code `0` ma ha scritto un warning LF/CRLF su stderr. Il caso e'
stato gestito manualmente per chiudere lo step senza saltare i gate reali.

## Comportamento nuovo

Il runner distingue ora:

1. comando Git con exit code `0` e solo warning LF/CRLF whitelisted su stderr:
   PASS con warning visibile;
2. comando Git con exit code diverso da `0`: FAIL bloccante;
3. comando Git con exit code `0` e stderr non whitelisted: FAIL fail-closed;
4. path discovery Git con exit code `0` e warning LF/CRLF whitelisted:
   warning visibile, nessun path spurio;
5. vero output di `git diff --check` con whitespace error e exit code non zero:
   FAIL bloccante.

Il check interno `git --no-pager diff --check` non passa piu' dal wrapper Git
generico per questa policy: Phase A usa `Invoke-GitDiffCheck`, che chiama
`Invoke-NativeChecked` con il flag esplicito
`AllowGitLfCrlfWarningsWithZeroExit`.

Lo stesso flag viene applicato anche quando un check configurato in
`phase_a_checks` passa dal percorso argv generico, ma solo se il comando e'
riconosciuto in modo stretto come `name = "Diff check"` con argv Git
`git --no-pager diff --check` o `git diff --check`. La whitelist resta quindi
limitata ai percorsi Git in cui e' stata dichiarata intenzionalmente.

La whitelist accetta solo le due forme Git note:

```text
CRLF will be replaced by LF the next time Git touches it
LF will be replaced by CRLF the next time Git touches it
```

associate al prefisso:

```text
warning: in the working copy of '<path>',
```

## Guardrail invariati

- I warning LF/CRLF non vengono silenziati: sono registrati come WARNING.
- Stderr Git diverso dalla whitelist resta bloccante con exit code `0`.
- Exit code Git diverso da `0` resta bloccante, anche se stderr contiene un
  warning LF/CRLF.
- Non viene normalizzato alcun line ending in questo step.
- Phase B e Phase C restano human-gated con `-ApprovePublish` e
  `-ApproveMerge`.
- La policy `gh pr checks --watch` dello STEP 0922 resta invariata.

## Follow-up M2: stderr informativo git switch

Durante Phase B, `git switch -c <branch>` puo' terminare con exit code `0` e
scrivere su stderr:

```text
Switched to a new branch '<branch>'
```

Il runner tratta ora questo messaggio come info non bloccante solo per
`git switch -c <branch>` e solo se `<branch>` coincide con l'argv del comando.
La stessa regola stretta vale per `git switch <branch>` con:

```text
Switched to branch '<branch>'
```

Stderr Git diverso da questi pattern resta fail-closed; exit code non zero resta
bloccante.

## Follow-up N2: warning LF/CRLF su git add

Durante Phase B, `git add -- <expected files>` puo' terminare con exit code `0`
e scrivere su stderr un warning LF/CRLF sulla working copy. Il runner tratta ora
questo warning come non bloccante solo quando:

- la label e' `Stage expected files`;
- il comando e' `git add -- <expected files>`;
- l'exit code e' `0`;
- ogni riga stderr e' un warning LF/CRLF whitelisted.

Stderr generico su `git add`, label diverse o exit code non zero restano
bloccanti.

## Follow-up O2: stderr informativo git push

Durante Phase B, `git push -u origin <branch>` puo' terminare con exit code `0`
e scrivere su stderr messaggi informativi di Git/GitHub, come:

```text
remote:
remote: Create a pull request for '<branch>' on GitHub by visiting:
To <remote-url>
* [new branch]      <branch> -> <branch>
branch '<branch>' set up to track 'origin/<branch>'.
```

Il runner li tratta come info non bloccanti solo quando:

- la label e' `Push branch`;
- il comando e' `git push -u origin <branch>`;
- l'exit code e' `0`;
- ogni riga stderr e' uno dei pattern safe ammessi.

Stderr non whitelisted o exit code non zero restano bloccanti.

## Follow-up R2: stderr update branch su git push

Durante retry o riesecuzioni di Phase B, il branch remoto puo' gia' esistere.
In questo caso `git push -u origin <branch>` puo' terminare con exit code `0`
e scrivere su stderr una riga informativa di update:

```text
<oldsha>..<newsha>  <branch> -> <branch>
<oldsha>...<newsha>  <branch> -> <branch>
```

Il runner tratta queste righe come info non bloccanti solo quando:

- la label e' `Push branch`;
- il comando e' `git push -u origin <branch>`;
- l'exit code e' `0`;
- gli SHA sono esadecimali abbreviati;
- il branch a sinistra e a destra di `->` coincide con il branch pushato.

Per rendere la whitelist verificabile anche su Windows PowerShell 5.1,
`Invoke-NativeChecked` cattura stdout e stderr raw con `ProcessStartInfo`
prima di applicare la policy stderr. Non viene reso non bloccante tutto stderr
di `git push`: ogni riga resta classificata singolarmente.

## Test

Copertura aggiunta senza chiamate reali a GitHub:

- `LF -> CRLF` warning con exit code `0`: PASS con warning.
- `CRLF -> LF` warning con exit code `0`: PASS con warning.
- warning LF/CRLF con exit code non zero: FAIL.
- stderr Git non whitelisted con exit code `0`: FAIL.
- vero whitespace error da `git diff --check`: FAIL.
- path discovery con warning LF/CRLF: PASS con warning e nessun path spurio.
- Phase A usa il percorso esplicito `Invoke-GitDiffCheck` per il Diff check
  interno.
- `phase_a_checks` con `name = "Diff check"` e argv Git `diff --check` usa la
  stessa policy LF/CRLF senza renderla globale per gli altri comandi.
- Phase B con fake `git switch -c` e stderr informativo sicuro: PASS.
- Phase B con fake `git switch` e stderr informativo sicuro: PASS.
- Phase B con stderr non whitelisted o exit code non zero su `git switch -c`:
  FAIL.
- Phase B con fake `git add -- README.md` e warning LF/CRLF: PASS.
- Phase B con stderr non whitelisted o exit code non zero su `git add --`:
  FAIL.
- Phase B con fake `git push -u origin <branch>` e stderr informativo safe:
  PASS.
- Phase B con fake `git push -u origin <branch>` e stderr update branch con
  `..` o `...`: PASS.
- Phase B con stderr update branch riferito a un branch diverso: FAIL.
- Phase B con stderr push non whitelisted o exit code non zero: FAIL.

Test dedicato:

```powershell
python -m pytest tests/unit/test_asf_publish_step_lf_crlf_warning_handling.py -q
```

## Prossimo step consigliato

```text
0930) External Repo Push Pattern Generalization
```
