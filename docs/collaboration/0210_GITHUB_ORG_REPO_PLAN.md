# 0210 - GitHub Organization and Repository Plan

## Scopo

[F] Questo documento prepara il piano manuale per una futura GitHub Organization condivisa tra Alberto e Luca.

[S] La Organization proposta di default e' `Ferrari-AI-Lab`.

[O] L'obiettivo e' ridurre repository personali sparsi e rendere piu' semplice governance, ruoli, PR review, CODEOWNERS e status check.

## Decisioni

- [S] Organization default proposta: `Ferrari-AI-Lab`.
- [S] Alternative nome: `Ferrari-AI-Factory`, `Ferrari-Software-Lab`, `Ferrari-Codex-Lab`.
- [F] Alberto resta Owner del perimetro strategico.
- [S] Luca puo' essere Owner se deve amministrare repo e permessi; altrimenti Maintain/Admin sui singoli repo e' piu' prudente.
- [F] Nessun trasferimento repository viene eseguito da questo step.
- [F] Nessuna branch protection reale viene modificata da questo step.

## Piano repository

| Repository | Stato desiderato | Note operative |
|---|---|---|
| `AI_Software_Factory` | Repo principale del metodo | Da trasferire solo dopo backup, review remoti e policy |
| `AI_Release_Radar` | Pilot reale | Verificare policy AGENTS e branch step prima del trasferimento |
| `ASF_Blueprint_Studio` | Pilot successivo | Applicare backbone in micro-step 0290 |
| `Codex_Skills` | Skills comuni | Tenere chiaro il confine tra skills comuni e locali |

## Repo personali vs Organization

[F] Un repository personale dipende dall'account del proprietario per visibilita', permessi e governance.

[S] Una Organization consente governance piu' stabile: team, ruoli, CODEOWNERS, branch protection, PR review, GitHub Actions e audit piu' coerenti.

[O] Per collaborazione familiare stabile su piu' repo, Organization e' preferibile, ma il trasferimento deve essere manuale e controllato.

## Piano trasferimento manuale, non automatico

1. [F] Decidere nome Organization e ruoli.
2. [F] Verificare piano GitHub e disponibilita' feature necessarie.
3. [F] Fare backup locale e verificare `git status --short` pulito.
4. [F] Verificare branch principale, PR aperte, issue, Actions, secrets e branch protection.
5. [S] Trasferire un solo repo pilota per primo.
6. [F] Aggiornare manualmente remote locali solo dopo trasferimento completato.
7. [F] Eseguire test e smoke dopo il cambio remote.
8. [F] Aggiornare documentazione e handoff.

## Checklist pre-trasferimento

- [ ] [F] Working tree pulito in locale.
- [ ] [F] Ultimo commit su `main` noto e annotato.
- [ ] [F] Remote origin attuale annotato.
- [ ] [F] Branch aperti e PR elencati.
- [ ] [F] GitHub Actions e required checks verificati.
- [ ] [F] Secrets GitHub elencati per nome, senza valori.
- [ ] [F] Branch protection esportata o documentata manualmente.
- [ ] [F] CODEOWNERS e PR template verificati.
- [ ] [S] Finestra di lavoro concordata con Alberto e Luca.

## Checklist post-trasferimento

- [ ] [F] Repository visibile nella Organization.
- [ ] [F] `git remote -v` aggiornato manualmente sui PC coinvolti.
- [ ] [F] `git fetch` e `git status --short` eseguiti senza anomalie.
- [ ] [F] Branch protection e required checks ricreati se necessario.
- [ ] [F] Secrets GitHub ricreati come valori nuovi o copiati manualmente dal proprietario autorizzato.
- [ ] [F] PR template e CODEOWNERS verificati.
- [ ] [F] Primo branch di test aperto con PR draft.
- [ ] [F] Decision log aggiornato.

## Comandi documentali di esempio

[F] Questi comandi sono solo esempi documentali. Non devono essere eseguiti automaticamente da Codex.

```powershell
git remote -v
git remote set-url origin https://github.com/Ferrari-AI-Lab/AI_Software_Factory.git
git fetch origin
git status --short
git branch --show-current
```

## Regole operative

- [F] Non trasferire repo senza approvazione esplicita di Alberto.
- [F] Non modificare permessi reali in uno step documentale.
- [F] Non copiare segreti nel Bridge.
- [F] Non usare token personali di un altro utente.
- [O] Trasferire un repo per volta, partendo dal meno rischioso.

## Rischi

- [F] URL remoti locali possono restare puntati al vecchio repo.
- [F] Secrets e branch protection possono richiedere ricreazione manuale.
- [S] GitHub Actions possono cambiare comportamento dopo trasferimento.
- [S] Link in documentazione, issue e badge possono diventare obsoleti.
- [O] Il rischio maggiore e' fare il trasferimento insieme ad altre modifiche operative.

## Checklist

- [ ] [S] Nome Organization scelto.
- [ ] [S] Ruolo Luca scelto: Owner oppure Maintain/Admin.
- [ ] [F] Repo pilota scelto.
- [ ] [F] Checklist pre-trasferimento completata.
- [ ] [F] Trasferimento eseguito manualmente da account autorizzato.
- [ ] [F] Checklist post-trasferimento completata.

## Prossimo step consigliato

[O] Dopo review del backbone, scegliere se applicare prima `0290) Apply Collaboration Backbone to ASF Blueprint Studio Pilot` oppure aprire una decisione separata per creare la Organization.