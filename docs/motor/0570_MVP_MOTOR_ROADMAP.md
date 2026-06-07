# 0570 - MVP Motor Roadmap

## 1. Scopo

Questa roadmap ri-prioritizza ASF verso un motore minimo capace di fare un giro supervisionato a gate.

Non introduce runner operativo, executor Codex write, nuove live OpenAI, commit automatici, push, PR, merge o deploy. Lo STEP 0580 sara' il primo step esecutivo, in dry-run.

---

## 2. Regola di congelamento meta-processo

Fino a quando il motore non completa almeno un giro end-to-end dry-run:

- non creare nuovi step di meta-processo non indispensabili;
- non introdurre nuove convenzioni di naming;
- non aggiungere packaging o validazioni strict isolate;
- non creare guardrail scollegati dal loop;
- non spostare la priorita' su retry live OpenAI o automazioni Git.

Le eccezioni ammesse sono solo correzioni bloccanti emerse dai test o dalla review del motore.

---

## 3. Roadmap MVP Motore

| Step | Obiettivo | Rischio atteso | File/aree coinvolte | Criterio di accettazione | Test/verifiche | Condizione di STOP |
|---:|---|---|---|---|---|---|
| 0570 | Formalizzare ADR, roadmap motore, loop a gate e nodo review indipendente | L0 docs safe | `docs/adr/`, `docs/motor/`, README, changelog, roadmap, decision log, indice workflow | Documenti presenti, coerenti e senza runner operativo | `python -m pytest`, workflow health check, verify gate, `git diff --check` | Branch 0560 attivo, working tree sporco fuori scope, tentazione di implementare runner |
| 0580 | Creare Dry-run Loop Runner che attraversa gli stati senza modificare target repo | L2 codice/test ordinario | `scripts/`, `templates/`, `docs/motor/`, `tests/` | Runner produce task packet, state log e gate summary inertizzati sotto `tmp/` | pytest mirati, workflow health, verify gate, status target clean | Qualunque write su target, chiamata live, commit/push/PR/merge, output fuori `tmp/` |
| 0590 | Implementare Risk Classifier + Gate Policy deterministici | L2 codice/test ordinario, con aspetti L3 per policy | `scripts/`, `policies/` se necessario, `docs/motor/`, `tests/` | Classificazione L0-L4 stabile e fail-closed con casi golden minimi | pytest classifier, casi L0-L4, diff check, verify gate | Rischio non classificabile, L3/L4 non human-gated, policy ambigua |
| 0600 | Aggiungere Independent Review Node come controllo separato dal report Codex | L2 codice/test ordinario | `scripts/`, `templates/`, `docs/motor/`, `tests/` | Nodo produce JSON review con verdict, risk, scope/test checks e finding espliciti | pytest schema/criteri, fixture PASS/FAIL/NEEDS_HUMAN | Review che promuove scope fail, test fail o diff non spiegato |
| 0610 | Preparare Controlled Codex Executor dry-run/readonly-first | L3 runner/Codex automation | `scripts/`, `docs/motor/`, invocation docs esistenti, `tests/` | Executor default preview/dry-run, read-only solo con gate esplicito, nessun write automatico | pytest mock, check target clean, verify gate | Sandbox write default, danger-full-access, CODEX_NOT_AVAILABLE trattato come target failure |
| 0620 | Eseguire First End-to-End Dry Run su target controllato | L3 runner/Git automation controllata | `tmp/`, docs results, runner/executor/review | Loop completo produce evidence, tests, review e gate decision senza write | pytest, workflow health, verify gate, controllo target clean | Stato mancante, evidence incompleta, target dirty, review FAIL o NEEDS_HUMAN non gestito |
| 0630 | First Controlled Write Pilot su modifica minima e reversibile | L3 write controllato; L4 se deploy/costi/live/merge automatici | target pilota esplicito, runner, review, tests, docs result | Una modifica minima resta in working tree per review umana, senza commit/push/PR/merge automatico | test target, diff review, gate decision, status scoped | L4 richiesto, target non clean, scope ambiguo, rollback non chiaro, gate non PASS |

---

## 4. Sequenza operativa prevista

```text
0570 docs -> 0580 dry-run loop -> 0590 risk gate -> 0600 independent review -> 0610 controlled executor -> 0620 e2e dry run -> 0630 controlled write pilot
```

Il criterio di maturita' minima non e' "il runner esiste". Il criterio e': un loop completo produce evidence leggibile, classifica rischio, esegue test disponibili, passa review indipendente e ferma correttamente il flusso quando un gate non passa.

---

## 5. Ambiti congelati fino a 0620

- Retry live OpenAI, salvo step separato e autorizzato da Alberto.
- Nuove integrazioni MCP operative.
- Automazione commit, push, PR, merge o deploy.
- Validatori strict non necessari al loop.
- Nuovi package o dipendenze runtime.
- Refactor dei documenti storici non necessari.
