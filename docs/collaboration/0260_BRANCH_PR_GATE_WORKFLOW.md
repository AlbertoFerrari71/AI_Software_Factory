# 0260 - Branch, PR and Gate Workflow

## Scopo

[F] Questo documento definisce il workflow consigliato per sviluppare a quattro mani con branch di step, PR draft, review GPT, review umana e gate locali/remoti.

[S] Il branch esempio per questo backbone e' `step-0200-shared-four-hands-backbone`.

[O] Codex deve restare executor locale; il merge finale resta decisione umana.

## Decisioni

- [F] `main` deve essere trattato come branch protetto.
- [F] Ogni lavoro reale avviene su branch di step.
- [F] PR draft e' il default per review iniziale.
- [F] GPT puo' fare review indipendente.
- [F] Alberto e Luca fanno review umana e decidono merge.
- [F] Codex non fa merge autonomo.
- [F] `no checks reported` e' un warning/attenzione: non e' sempre errore automatico, ma richiede classificazione.

## Workflow

1. [F] Verificare repo, branch, HEAD e working tree.
2. [F] Creare o usare branch di step autorizzato.
3. [F] Eseguire modifiche solo nello scope.
4. [F] Eseguire test light coerenti con lo step.
5. [F] Eseguire `git --no-pager diff --check`.
6. [F] Preparare report Codex.
7. [S] Pubblicare PR draft solo se lo step lo autorizza.
8. [F] Far fare review GPT e review umana.
9. [F] Eseguire test full/escalated se rischio o file critici lo richiedono.
10. [F] Merge controllato solo dopo approval umana e gate PASS.

## Profili test

| Profilo | Quando | Esempi |
|---|---|---|
| Light | Documenti/template piccoli | `git diff --check`, script read-only, test mirati |
| Full | Codice, runner, workflow | `python -m pytest`, health check, `scripts/verify.ps1` |
| Escalated | Permessi, scheduler, secrets, GitHub settings | Richiede consenso esplicito e review manuale estesa |

## Criteri PASS/FAIL

### PASS

- [F] Scope rispettato.
- [F] Nessun segreto introdotto.
- [F] Test richiesti PASS o warning classificati.
- [F] `git diff --check` PASS.
- [F] Report completo con azioni non eseguite.

### FAIL

- [F] File fuori scope non autorizzati.
- [F] Test falliti per causa dello step.
- [F] Segreti o token esposti.
- [F] Azioni vietate eseguite.
- [F] Warning non classificati su gate critici.

## Gestione no checks reported

[F] Se GitHub CLI riporta `no checks reported`, il reviewer deve distinguere:

- [S] repo senza CI configurata;
- [S] check non ancora partiti;
- [S] branch non collegato alla PR attesa;
- [S] errore reale nella pipeline remota.

[O] In assenza di CI, i gate locali e la review umana diventano ancora piu' importanti.

## Checklist autore

- [ ] [F] Branch corretto.
- [ ] [F] Working tree iniziale verificato.
- [ ] [F] File modificati in scope.
- [ ] [F] Test light/full eseguiti.
- [ ] [F] `git diff --check` eseguito.
- [ ] [F] Nessun segreto.
- [ ] [F] Report scritto.
- [ ] [F] Azioni vietate non eseguite.

## Checklist reviewer

- [ ] [F] Diff letto.
- [ ] [F] File fuori scope assenti.
- [ ] [F] Test e output plausibili.
- [ ] [F] Documentazione coerente.
- [ ] [F] Segreti assenti.
- [ ] [F] Runner/script critici controllati con attenzione.
- [ ] [S] Warning remoti classificati.

## Regole operative

- [F] Non usare `--no-verify`.
- [F] Non fare force-push.
- [F] Non fare merge se i gate sono falliti o non classificati.
- [F] Non fare commit/push/PR/merge da Codex senza istruzione esplicita.

## Rischi

| Rischio | Mitigazione |
|---|---|
| Merge su `main` troppo presto | PR draft e review umana |
| Falsi PASS | Reviewer controlla output e file modificati |
| Test costosi saltati | Profilo test dichiarato e motivato |
| Check remoti assenti | Classificazione esplicita `no checks reported` |

## Prossimo step consigliato

[O] Applicare questo workflow al pilot `0290) Apply Collaboration Backbone to ASF Blueprint Studio Pilot`.