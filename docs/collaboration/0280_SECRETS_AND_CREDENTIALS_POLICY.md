# 0280 - Secrets and Credentials Policy

## Scopo

[F] Questo documento definisce regole minime per token, API key, password, credenziali e file `.env` nei repository e Bridge condivisi.

[F] Token, API key e credenziali non devono mai essere committati o scambiati in Dropbox.

[O] Ogni persona usa account e token propri, con permessi minimi.

## Decisioni

- [F] Divieto di committare token, API key, password, private key o file `.env` reali.
- [F] Divieto di scambio token personali in Dropbox, chat o report.
- [F] Ogni utente usa account proprio.
- [F] `.env` locale resta non versionato.
- [F] `.env.example` puo' essere versionato solo con nomi variabile e valori finti.
- [F] GitHub Secrets e' il posto corretto per valori necessari ai workflow.
- [F] Se una credenziale viene esposta, deve essere ruotata.

## Regole operative

- [F] Non stampare valori segreti nei log.
- [F] Non allegare `.env` al Bridge.
- [F] Non salvare token in prompt, report o screenshot.
- [F] Non chiedere a Codex di leggere o usare token reali salvo step live esplicitamente autorizzato e con redazione output.
- [F] Non usare credenziali di Alberto sul PC di Luca o viceversa.
- [O] Usare permessi minimi e token a scadenza quando disponibili.

## `.env` e `.env.example`

Esempio ammesso in `.env.example`:

```text
OPENAI_API_KEY=replace-with-your-local-key
GITHUB_TOKEN=replace-with-your-local-token
```

[F] Valori reali non sono ammessi.

[S] Ogni repo dovrebbe avere `.gitignore` coerente per `.env`, `.env.*` sensibili e output temporanei.

## GitHub Secrets

[F] I workflow GitHub devono leggere segreti da GitHub Secrets o ambiente sicuro equivalente.

[F] Nei documenti si possono citare i nomi dei secrets, non i valori.

[S] Se un repo viene trasferito a Organization, i secrets potrebbero dover essere ricreati manualmente.

## Rotazione credenziali

Se un segreto viene esposto:

1. [F] Fermare publish/merge collegati.
2. [F] Revocare o ruotare il segreto dal provider.
3. [F] Rimuovere il valore dai file e dai report condivisi.
4. [F] Valutare se serve history rewrite con decisione umana separata.
5. [F] Documentare l'incidente senza riportare il valore.

## Scan minimo consigliato

[F] Prima di commit/PR, cercare pattern sospetti nel diff:

```powershell
git --no-pager diff --check
git --no-pager diff -- . ':!*.lock'
```

[S] Cercare manualmente stringhe come:

```text
api_key
apikey
token
secret
password
private key
BEGIN ... PRIVATE KEY
OPENAI_API_KEY
GITHUB_TOKEN
```

[O] Per step futuri si puo' aggiungere uno scanner deterministico, ma non deve stampare valori segreti.

## Checklist prima di commit/PR

- [ ] [F] `git status --short` letto.
- [ ] [F] Diff letto.
- [ ] [F] Nessun `.env` reale nel diff.
- [ ] [F] Nessun token/password/API key nel diff.
- [ ] [F] Report Bridge sanitizzato.
- [ ] [F] `.env.example` contiene solo placeholder.
- [ ] [F] Secrets GitHub citati solo per nome.

## Rischi

| Rischio | Mitigazione |
|---|---|
| Token in Git | Scan diff, `.gitignore`, review |
| Token in Dropbox | Divieto Bridge + report sanitizzati |
| Account condivisi | Ogni persona usa account proprio |
| Secret in log | Redazione output e no print valori |
| Repo transfer perde secrets | Checklist post-trasferimento |

## Prossimo step consigliato

[O] Nel pilot 0290, verificare solo nomi e policy segreti, senza leggere o copiare valori reali.