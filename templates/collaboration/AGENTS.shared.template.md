# AGENTS.md - Shared Collaboration Template

Scope: replace this line with the repository scope.

## Scopo

[F] Questo template definisce regole minime per agenti AI in un repository condiviso Alberto-Luca.

[S] Deve essere specializzato per il repository prima dell'uso.

[O] Tenere il file breve, operativo e senza segreti.

## Regole Codex

- [F] Prima di modificare file, ispezionare branch, working tree e istruzioni locali.
- [F] Non fare commit, push, PR, merge, tag, release o deploy senza istruzione esplicita.
- [F] Non usare clipboard salvo istruzione esplicita.
- [F] Non modificare file fuori scope.
- [F] Non cancellare, resettare, pulire o forzare branch senza consenso esplicito.
- [F] Distinguere `[F]` fatto/verifica, `[S]` stima/ipotesi e `[O]` opinione/raccomandazione quando richiesto.

## Regole Git

- [F] Usare `git --no-pager` per output lunghi.
- [F] Non usare `--no-verify`.
- [F] Non fare force-push.
- [F] Trattare `main` come branch protetto.
- [F] Usare branch di step e PR draft quando il workflow lo richiede.

## Regole test

- [F] Eseguire test/verifiche coerenti con il cambio.
- [F] Non inventare PASS.
- [F] Se un comando non esiste, riportare `NOT_AVAILABLE` con motivo.
- [F] Classificare warning e fallimenti.

## Regole Bridge

- [F] Il Bridge e' spazio operativo per prompt/report/log, non fonte ufficiale del codice.
- [F] Usare nomi numerati/datati secondo policy repo.
- [F] Non usare `LAST-*` o `latest-*` se la policy repo li vieta.
- [F] Non mettere repository Git in Dropbox.

## Regole sicurezza

- [F] Non committare segreti, token, API key, password o private key.
- [F] Non leggere o stampare valori segreti senza autorizzazione esplicita.
- [F] `.env` reale resta locale e non versionato.
- [F] `.env.example` contiene solo placeholder.

## Regole operative

- [F] Tenere modifiche piccole e verificabili.
- [F] Aggiornare docs/roadmap/decisioni quando il cambio modifica workflow o policy.
- [F] Report finale con file modificati, test, warning, vincoli rispettati e prossimo step.

## Rischi

- [S] Istruzioni locali possono cambiare tra repo.
- [S] Feature GitHub disponibili dipendono dal piano e dalle impostazioni reali.
- [O] In caso di dubbio su permessi o segreti, fermarsi e chiedere ad Alberto.

## Checklist

- [ ] [F] Branch verificato.
- [ ] [F] Working tree verificato.
- [ ] [F] Scope letto.
- [ ] [F] Test definiti.
- [ ] [F] Segreti assenti.
- [ ] [F] Azioni vietate non eseguite.

## Prossimo step consigliato

[O] Adattare questo template nel `AGENTS.md` del repository pilota e farlo revisionare prima del primo step operativo.