# 0570 - Gate Loop Spec

## 1. Scopo

Questa specifica definisce il loop supervisionato a gate per il futuro MVP Motore.

Lo STEP 0570 e' documentale: non implementa il runner. Ogni stato futuro deve produrre evidence leggibile e fermarsi quando i criteri di STOP sono soddisfatti.

---

## 2. Stati formali

| Stato | Input | Output | Condizioni di STOP | Log/evidence da salvare |
|---|---|---|---|---|
| `PLAN_NEXT_STEP` | roadmap corrente, step precedente, branch/status, vincoli utente, documenti centrali | proposta step, scope incluso/escluso, prerequisiti, rischio preliminare | branch errato, working tree sporco fuori scope, prerequisito non su `main`, conflitto con step paralleli | branch/status/log, prereq check, scope memo |
| `BUILD_TASK_PACKET` | proposta step, template task packet, file ammessi/vietati, verification plan | task packet pulito e self-contained | scope ambiguo, file vietati richiesti, azioni L3/L4 non autorizzate, secret richiesti | task packet, manifest file previsti, forbidden actions |
| `RISK_CLASSIFY` | task packet, manifest, comandi previsti, policy L0-L4 | risk report con livello massimo e motivazione | rischio non classificabile, L4 non autorizzato, live/API cost/deploy/merge impliciti | risk report JSON/Markdown, fattori di rischio |
| `EXECUTE_DRY_OR_WRITE` | task packet, risk report, gate policy, modalita' dry-run/write | output Codex/runner oppure preview inertizzata, diff se write autorizzato | gate mancante, target non clean, sandbox non consentita, `CODEX_NOT_AVAILABLE` non gestito, write non autorizzato | stdout/stderr summary, exit code, command plan, diff stat, target status |
| `RUN_TESTS` | diff/output, test plan, repository target | test report con comandi, esiti, warning | test richiesti non eseguiti senza motivo, failure non spiegata, warning critico | pytest/verify output, diff check, status, eventuali skip motivati |
| `INDEPENDENT_REVIEW` | task packet, git diff, report Codex, test report, risk report, file manifest | review JSON con verdict e finding | scope fail, tests fail, risk mismatch, diff inspiegabile, confidence low su azione non banale | independent review JSON, blocking findings, non-blocking warnings |
| `GATE_DECISION` | review JSON, risk report, test report, policy, vincoli Alberto | decisione `PROCEED`, `HOLD`, `NEEDS_HUMAN` o `FAIL` | review FAIL, L3/L4 senza approval, confidence insufficiente, evidence incompleta | gate decision report, motivazione, next action |
| `COMMIT_OR_HOLD` | gate decision, diff scoped, branch/status, policy Git | hold report o istruzioni manuali per Alberto; mai commit automatico nello MVP | gate non PASS, branch `main`, scope sporco, PR/merge richiesti senza autorizzazione esplicita | final state report, git status, file changed summary, rollback hint |

---

## 3. Risk classifier L0-L4

| Livello | Nome | Definizione | Esempi | Gate minimo |
|---|---|---|---|---|
| L0 | docs safe | Lettura o scrittura documentale a basso rischio, senza nuove policy operative vincolanti e senza script | ADR, roadmap, spec, changelog coerente | review leggera, diff check, status |
| L1 | docs operative | Documenti che cambiano workflow, regole operative, prompt o checklist ma senza codice eseguibile | update workflow docs, task packet rules, operator runbook | workflow health, decision log/roadmap sync, human awareness |
| L2 | codice/test ordinario | Script o test locali deterministici, standard library, nessun network/live/Git automation | runner dry-run, parser, test unitari | pytest, verify gate, diff check, review indipendente |
| L3 | CI, security, secrets, dipendenze, runner, Git automation | Cambi che toccano esecuzione agentica, CI, credenziali, policy sensibili, dependency surface o automazione Git | Codex executor, CI check, secret handling, dependency install | human gate, fail-closed, review indipendente, no default write |
| L4 | deploy, cancellazioni, produzione, costi API live, merge automatici | Azioni con effetto esterno, costo, produzione, cancellazione, merge o pubblicazione automatica | deploy, delete, live OpenAI cost, auto merge, force push | doppia conferma esplicita, dry-run, rollback, stop default |

Se un'azione non e' classificabile, il classifier deve fermarsi e trattarla almeno come L3 fino a revisione umana.

---

## 4. Regole di transizione

- Ogni stato consuma evidence dello stato precedente.
- Nessuno stato puo' inventare evidence mancante.
- Il passaggio da dry-run a write richiede gate esplicito e target clean.
- L3/L4 non possono essere promossi da soli da test automatici.
- `COMMIT_OR_HOLD` nello MVP produce hold o istruzioni manuali; non esegue commit, push, PR, merge o deploy.

---

## 5. Evidence minima del giro end-to-end

Un giro end-to-end dry-run e' valido solo se esistono:

- task packet;
- file manifest;
- risk report;
- execution report o dry-run preview;
- test report;
- independent review JSON;
- gate decision;
- final hold/report con branch e working tree state.
