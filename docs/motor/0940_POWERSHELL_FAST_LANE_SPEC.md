# 0940 - PowerShell Fast Lane Spec

## Scopo

PowerShell Fast Lane e' la lane deterministica del supervised loop ASF V1. Serve a eseguire attivita' meccaniche senza usare AI quando non serve ragionamento.

## Perche' non usare AI per attivita' meccaniche

Comandi come status, test, diff check e raccolta log sono gia' deterministici. Usare AI per sceglierli ogni volta aumenta costo, latenza e variabilita'. ASF deve usare AI per pianificare, diagnosticare e rivedere, non per sostituire controlli locali ripetibili.

## Attivita' ammesse

Esempi ammessi quando scope e working directory sono autorizzati:

- `git --no-pager status --short`
- `git --no-pager diff --check`
- `python -m pytest`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify.ps1`
- `python scripts/check_workflow_health.py`
- raccolta log locale;
- creazione report Bridge autorizzato;
- validazioni read-only;
- generazione envelope JSON da template;
- Phase A locale.

## Attivita' vietate senza approval esplicita

- reset distruttivi;
- clean distruttivi;
- rebase;
- checkout distruttivi;
- push;
- merge;
- deploy;
- scrittura fuori repository o Bridge non autorizzata;
- modifica massiva line endings;
- scrittura negli appunti di sistema;
- lettura o esfiltrazione di segreti.

## Autorizzazione comandi

Ogni task Fast Lane deve avere un envelope con:

- working directory;
- comando o script;
- argomenti;
- path ammessi;
- pattern vietati;
- timeout;
- idle timeout;
- exit code attesi;
- pattern stderr sicuri;
- output paths;
- classificazione rischio;
- next action.

Il runner locale deve confrontare envelope, policy e stato corrente prima dell'esecuzione.

## Output e report

Ogni esecuzione deve salvare:

- stdout;
- stderr;
- exit code;
- durata;
- comando normalizzato;
- classificazione finale;
- warning non bloccanti;
- failure class se presente.

Il Bridge conserva log e report operativi. Git e file versionati restano fonte autorevole per il contenuto del progetto.

## Timeout e guardrail

La Fast Lane deve usare:

- timeout assoluto;
- idle timeout;
- kill controllato del processo;
- heartbeat quando il comando e' lungo;
- stop immediato per comandi rischiosi o fuori scope;
- retry solo secondo la GPT-discretionary bounded retry policy.

## Terminale non interattivo

I comandi PowerShell devono preferire:

```powershell
pwsh -NoProfile -NonInteractive -ExecutionPolicy Bypass
```

Gli script lunghi devono essere salvati come `.ps1`, validati e poi eseguiti. Evitare mega-blocchi incollati in terminale.

## Exit code e stderr

- Exit code `0` piu' stderr informativo sicuro = warning non bloccante.
- Stderr inatteso = errore.
- Exit code nonzero = errore.
- Warning LF/CRLF Git restano non bloccanti solo se il comando Git ha exit code `0` e i gate reali passano.

