# 0270 - Review and Merge Policy

## Scopo

[F] Questo documento definisce come Alberto, Luca, GPT e Codex collaborano nella review e nel merge controllato.

[F] Codex e' executor: produce modifiche e report, ma non decide il merge finale.

[O] Quando possibile, autore e reviewer devono essere persone diverse.

## Decisioni

- [F] Alberto e Luca possono alternarsi tra autore e reviewer.
- [F] GPT puo' fare review indipendente, ma non sostituisce l'approvazione umana.
- [F] Codex non e' decisore finale.
- [F] Merge autonomo di Codex e' vietato salvo policy futura esplicita e limitata.
- [S] Per step L0 documentali, una review umana leggera puo' bastare se i gate sono PASS.

## Cosa controlla il reviewer

- [F] File fuori scope.
- [F] Falsi PASS o output test non coerenti.
- [F] Test mancanti rispetto al rischio.
- [F] Documentazione non aggiornata.
- [F] Secrets accidentalmente esposti.
- [F] Line endings e whitespace.
- [F] Modifiche a runner/script critici.
- [F] AGENTS.md, workflow GitHub, branch protection o policy operative.
- [S] Effetti indiretti su altri repository o Bridge.

## Criteri per rifiutare uno step

- [F] Segreti, token, password o chiavi nel diff o nei report.
- [F] Azioni vietate eseguite.
- [F] File fuori scope non giustificati.
- [F] Test falliti per causa dello step.
- [F] Warning critici non classificati.
- [F] Documenti obbligatori assenti.
- [F] Script non safe-by-default.
- [F] Report finale incompleto.

## Criteri per approvare uno step

- [F] Scope rispettato.
- [F] Test richiesti PASS o warning classificati.
- [F] `git diff --check` PASS.
- [F] Nessun segreto.
- [F] Documentazione e indici aggiornati se coerente.
- [F] Report finale chiaro.
- [F] Prossimo step consigliato esplicito.

## Regole operative

- [F] Il reviewer legge il diff, non solo il report.
- [F] Il reviewer puo' chiedere fix prima del merge.
- [F] Il merge controllato avviene solo dopo gate e approval.
- [F] Se autore e reviewer coincidono, GPT review indipendente e checklist devono essere piu' rigorose.
- [O] Per file high-risk, usare due review umane se possibile.

## Rischi

| Rischio | Mitigazione |
|---|---|
| Reviewer si fida del report | Leggere diff e test output |
| Autore mergea il proprio step | Separare ruoli quando possibile |
| GPT approva senza contesto Git | Fornire diff, file, test e vincoli |
| Script critici cambiati senza test | Richiedere full gate o test mirati |

## Checklist

- [ ] [F] Diff completo letto.
- [ ] [F] Report letto.
- [ ] [F] Test verificati.
- [ ] [F] Nessun segreto.
- [ ] [F] Scope rispettato.
- [ ] [F] File high-risk identificati.
- [ ] [F] Decisione approve/reject motivata.

## Prossimo step consigliato

[O] Usare questa policy come checklist di review per il pilot 0290.