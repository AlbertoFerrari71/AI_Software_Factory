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
| 0590 | Stabilizzare la pubblicazione step con runner PowerShell versionato | L3 Git automation human-gated | `scripts/`, `examples/publish_step/`, `docs/motor/`, `tests/` | Runner FASE A/B/C con config JSON, Bridge output e flag espliciti per publish/merge | pytest mirati, self-test DOCX, workflow health, verify gate | Pubblicazione senza flag, scope ambiguo, no checks non autorizzato, comandi distruttivi |
| 0600 | Implementare Risk Classifier + Gate Policy deterministici | L2 codice/test ordinario, con aspetti L3 per policy | `scripts/`, `policies/` se necessario, `docs/motor/`, `tests/` | Classificazione L0-L4 stabile e fail-closed con casi golden minimi | pytest classifier, casi L0-L4, diff check, verify gate | Rischio non classificabile, L3/L4 non human-gated, policy ambigua |
| 0610 | Integrare Risk Classifier nel Dry-run Loop Runner | L2 codice/test ordinario | `scripts/asf_dry_run_loop_runner.py`, `scripts/asf_risk_classifier.py`, `tests/`, `docs/motor/` | Il checkpoint RISK_CLASSIFY usa la policy stabile senza cambiare autorizzazioni write/publish/live | pytest classifier + runner, workflow health, verify gate | Regressione runner 0580, L3/L4 sottostimati, integrazione non fail-closed |
| 0620 | Aggiungere Gate Decision Report and Human Approval Packet | L2 codice/test ordinario | `scripts/`, `templates/`, `docs/motor/`, `tests/` | Pacchetto gate produce verdict, risk, scope/test checks, finding e azione umana esplicita | pytest schema/criteri, fixture PASS/FAIL/NEEDS_HUMAN | Report che promuove scope fail, test fail, L3/L4 senza approval o diff non spiegato |
| 0630 | Preparare Controlled Codex Executor dry-run/readonly-first | L3 runner/Codex automation | `scripts/`, `docs/motor/`, invocation docs esistenti, `tests/` | Executor default preview/dry-run, read-only solo con gate esplicito, nessun write automatico | pytest mock, check target clean, verify gate | Sandbox write default, danger-full-access, CODEX_NOT_AVAILABLE trattato come target failure |
| 0640 | Eseguire First End-to-End Dry Run su target controllato | L3 runner/Git automation controllata | `tmp/`, docs results, runner/executor/review | Loop completo produce evidence, tests, review e gate decision senza write | pytest, workflow health, verify gate, controllo target clean | Stato mancante, evidence incompleta, target dirty, review FAIL o NEEDS_HUMAN non gestito |
| 0650 | First Controlled Write Pilot su modifica minima e reversibile | L3 write controllato; L4 se deploy/costi/live/merge automatici | target pilota esplicito, runner, review, tests, docs result | Una modifica minima resta in working tree per review umana, senza commit/push/PR/merge automatico | test target, diff review, gate decision, status scoped | L4 richiesto, target non clean, scope ambiguo, rollback non chiaro, gate non PASS |

---

## 4. Sequenza operativa prevista

```text
0570 docs -> 0580 dry-run loop -> 0590 stable publish runner -> 0600 risk gate -> 0610 risk integration -> 0620 gate decision packet -> 0630 controlled executor -> 0640 e2e dry run -> 0650 controlled write pilot
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

---

## 6. Stato dopo STEP 0610

Lo STEP 0580 ha introdotto il primo Dry-run Loop Runner:

```text
scripts/asf_dry_run_loop_runner.py
docs/motor/0580_DRY_RUN_LOOP_RUNNER.md
examples/dry_run_loop/
```

Il runner attraversa gli stati del loop e produce evidence sotto `tmp/asf_dry_run_loop/`, ma non autorizza ancora write, executor Codex, live run o pubblicazione Git.

Lo STEP 0590 ha introdotto il publish runner stabile `scripts/asf_publish_step.ps1`.

Lo STEP 0600 ha introdotto:

```text
scripts/asf_risk_classifier.py
docs/motor/0600_RISK_CLASSIFIER_GATE_POLICY.md
examples/risk_classifier/
```

Lo STEP 0610 collega il classifier al checkpoint `RISK_CLASSIFY` del runner 0580 e produce risk report strutturato con blocchi `risk`, `gate` e `dry_run`.

Il prossimo step resta:

```text
0620) Gate Decision Report and Human Approval Packet
```
