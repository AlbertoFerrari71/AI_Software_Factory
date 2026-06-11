# 0245 - AGENTS.md Policy

## Scopo

[F] Questo documento definisce lo scopo di `AGENTS.md` globale e di repository per il lavoro Alberto-Luca con Codex.

[F] `AGENTS.md` contiene istruzioni persistenti operative per agenti AI nel perimetro dichiarato.

[S] Una struttura comune riduce errori quando Luca lavora su piu' repository.

## Decisioni

- [F] Ogni repository condiviso deve avere un `AGENTS.md` locale.
- [F] Le regole locali del repo prevalgono sulle preferenze generiche quando sono piu' restrittive.
- [F] Nessun `AGENTS.md` deve contenere segreti, token, policy nascoste o credenziali.
- [F] Commit/push/PR/merge restano vietati senza istruzione esplicita.
- [O] Usare un template comune e poi specializzarlo per repo.

## Struttura proposta

```text
~/.codex/AGENTS.md          # preferenze personali/globali, se supportate
repo/AGENTS.md              # regole operative del repository
repo/.agents/skills         # eventuali skills locali versionate/autorizzate
```

[F] Le skills personali/comuni possono stare in area utente.

[S] Le skills locali versionate possono stare nel repository solo se non contengono segreti e sono utili al progetto.

## Regole minime per Codex

- [F] Non fare commit, push, PR, merge, tag o deploy senza istruzione esplicita.
- [F] Non usare `--no-verify`.
- [F] Non fare reset, clean, force-push o azioni distruttive senza consenso esplicito.
- [F] Usare `git --no-pager` per output lunghi.
- [F] Ispezionare branch e working tree prima delle modifiche.
- [F] Eseguire test/verifiche coerenti con il tipo di cambio.
- [F] Scrivere report Bridge deterministico quando richiesto.
- [F] Non usare clipboard salvo richiesta esplicita.
- [F] Non committare segreti, token, password o chiavi.
- [F] Distinguere fatti, stime/ipotesi e opinioni/raccomandazioni con `[F]`, `[S]`, `[O]` quando richiesto.

## Template AGENTS.md condiviso

[F] Il template versionabile si trova in:

```text
templates/collaboration/AGENTS.shared.template.md
```

[S] Il template e' una base: ogni repo deve aggiungere test, branch policy, Bridge e limiti propri.

## Regole operative

- [F] Aggiornare `AGENTS.md` e' un cambio di policy: richiede review esplicita.
- [F] Non copiare istruzioni di sistema o policy nascoste nel repository.
- [F] Non usare `AGENTS.md` per conservare token o endpoint sensibili.
- [F] Se due istruzioni confliggono, applicare la piu' restrittiva e chiedere conferma.

## Rischi

| Rischio | Mitigazione |
|---|---|
| Regole diverse tra repo | Template comune + specializzazione locale |
| Policy obsolete | Review periodica e riferimento a decision log |
| Segreti in istruzioni | Scan e divieto esplicito |
| Codex esegue Git remoto | Forbidden actions nel prompt e in AGENTS.md |

## Checklist

- [ ] [F] `AGENTS.md` locale esiste.
- [ ] [F] Scope del file dichiarato.
- [ ] [F] Regole Git e safety presenti.
- [ ] [F] Test/verifiche indicate.
- [ ] [F] Policy segreti presente.
- [ ] [F] Nessuna credenziale nel file.
- [ ] [S] Template comune confrontato con regole repo.

## Prossimo step consigliato

[O] Durante il pilot 0290, verificare se `ASF_Blueprint_Studio` ha un `AGENTS.md` locale coerente con questo template.