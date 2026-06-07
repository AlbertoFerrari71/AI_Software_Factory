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
| 0620 | Aggiungere Gate Decision Report and Human Approval Packet | L2 codice/test ordinario | `scripts/`, `examples/`, `docs/motor/`, `tests/` | Pacchetto gate produce decision, risk, scope/test checks, blocker e azione umana esplicita | pytest schema/criteri, fixture PASS/FAIL/NEEDS_HUMAN | Report che promuove scope fail, test fail, L3/L4 senza approval o diff non spiegato |
| 0630 | Definire Verification Profile Selector + Test Cost Policy | L2 documentazione/codice locale | `scripts/`, `docs/motor/`, `tests/`, `examples/` | Profili docs-only, code-unit, motor-core, publish, final-main e high-risk documentati e suggeribili senza publish | pytest mirati, workflow health, verify gate | Shortcut che riduce sicurezza su motor-core, publish, final-main o high-risk |
| 0640 | Integrare Verification Profile Selector nel Publish Runner | L3 runner/Git automation human-gated | `scripts/asf_publish_step.ps1`, selector 0630, docs, tests | Runner usa profili per dedup prudente di check e mantiene Phase B/C human-gated | pytest runner/selector, workflow health, verify gate | Publish senza flag, Phase C saltata, riduzione check su motor-core/high-risk |
| 0650 | Verification Profile Driven Publish Config Generator | L2/L3 config generation human-reviewed | `scripts/`, `examples/publish_step/`, docs, tests | Generatore produce bozze config publish coerenti con selector e scope, senza pubblicare | pytest mirati, workflow health, verify gate | Config che autorizza publish/merge, profilo ambiguo, Phase C indebolita |
| 0660 | Publish Config Generator Bridge Output Integration | L2 output/audit trail locale | generator 0650, Bridge, docs, tests | Output generator salvabili con audit trail dedicato senza eseguire publish | pytest mirati, workflow health, verify gate | Bridge fragile, output ambiguo, confusione tra config draft e publish approval |
| 0670 | Step Execution State Machine | L2/L3 orchestration design locale | generator, runner, docs, tests | Stati e transizioni dello step loop espliciti, auditabili e fail-closed | pytest mirati, workflow health, verify gate | Automazione publish implicita, stati ambigui, ripresa senza gate umano |
| 0680 | State Machine Bridge Integration | L2 output/audit trail locale | state machine, Bridge, docs, tests | Stato corrente e report state machine salvabili nel Bridge senza avviare publish | pytest mirati, workflow health, verify gate | Bridge reale richiesto dai test, stato implicito, recovery non dichiarata |
| 0690 | State Machine Integration with Publish Config Generator | L2/L3 integration locale | generator, state machine, docs, tests | Config draft e stato iniziale coerenti senza avviare publish | pytest mirati, workflow health, verify gate | Generator che esegue runner, stato implicito, recovery non dichiarata |
| 0700 | End-to-End MVP Smoke Scenario | L2/L3 smoke locale | generator, state machine, Bridge temporaneo, docs, tests | Un percorso locale end-to-end produce evidence senza pubblicare | pytest mirati, workflow health, verify gate | Smoke che maschera publish reale, Bridge reale richiesto |
| 0710 | Motor Run Manifest and Evidence Pack | L2 evidence locale | manifest, evidence pack, docs, tests | Una run Motore produce manifest JSON e summary Markdown auditabili | pytest mirati, workflow health, verify gate | READY_TO_PUBLISH senza artifact richiesti, Bridge reale richiesto |
| 0720 | MVP Usage Runbook | L0/L1 docs operative | docs/motor, README, changelog, roadmap, decision log, workflow index, health check | Procedura operativa MVP end-to-end documentata e human-gated | workflow health, pytest, verify gate, diff check | Runbook che sembra autorizzare publish automatico o saltare Phase C |
| 0730 | End-to-End MVP Closure Pack | L0/L1 docs operative | docs/motor, README, changelog, roadmap, decision log, workflow index, health check | MVP Motore chiuso formalmente con criteri GO/WARNING/NO-GO e warning residui | workflow health, pytest, verify gate, diff check | Closure pack che dichiara successo pieno ignorando smoke sintetico, hook manuali o pilot reale assente |
| 0740 | MVP Real Step Pilot | L1/L2 docs/tooling locale | docs/motor, README, changelog, roadmap, decision log, workflow index, health check, tests | Baseline MVP usata su modifica reale piccola con evidence e decisione prudente | workflow health, pytest, verify gate, diff check | Pilot trattato come prova produttiva, Phase B/C eseguite da Codex, warning manuali ignorati |
| 0750 | State Machine Publish Runner Event Hooks | L2/L3 runner integration human-gated | `scripts/asf_publish_step.ps1`, state machine, docs, tests, examples | Runner emette eventi state machine opzionali durante Phase B/C senza ridurre gate | pytest runner/state machine/generator/selector, workflow health, verify gate, diff check | Hook che pubblicano senza approval, shell execution, config legacy rotte, Dropbox/GitHub reali nei test |
| 0760 | MVP Real Step Pilot 2 with State Hooks | L1/L2 docs/tooling locale | docs/motor, README, changelog, roadmap, decision log, workflow index, health check, tests, tmp evidence | Secondo pilot reale prepara state file `READY_TO_PUBLISH` e config hook-aware validata in `Phase Plan` | workflow health, pytest, verify gate, diff check, Phase Plan hook-aware | Pilot trattato come validazione finale degli hook, Phase B/C eseguite da Codex, warning manuali ignorati |

---

## 4. Sequenza operativa prevista

```text
0570 docs -> 0580 dry-run loop -> 0590 stable publish runner -> 0600 risk gate -> 0610 risk integration -> 0620 gate decision packet -> 0630 verification profiles -> 0640 selector integration with publish runner -> 0650 publish config generator -> 0660 bridge output integration -> 0670 state machine -> 0680 state bridge -> 0690 generator integration -> 0700 end-to-end smoke -> 0710 run manifest -> 0720 usage runbook -> 0730 closure pack -> 0740 real step pilot -> 0750 publish runner state hooks -> 0760 real pilot with state hooks
```

Il criterio di maturita' minima non e' "il runner esiste". Il criterio e': un loop completo produce evidence leggibile, classifica rischio, esegue test disponibili, passa review indipendente e ferma correttamente il flusso quando un gate non passa.

---

## 5. Ambiti ancora congelati dopo 0730

- Retry live OpenAI, salvo step separato e autorizzato da Alberto.
- Nuove integrazioni MCP operative.
- Automazione commit, push, PR, merge o deploy.
- Validatori strict non necessari al loop.
- Nuovi package o dipendenze runtime.
- Refactor dei documenti storici non necessari.

---

## 6. Stato dopo STEP 0630

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

Lo STEP 0620 aggiunge:

```text
scripts/asf_gate_decision_report.py
docs/motor/0620_GATE_DECISION_REPORT_HUMAN_APPROVAL_PACKET.md
docs/motor/0620_VERIFICATION_BALANCE_NOTES.md
examples/gate_decision/
```

Il Gate Decision Report produce Approval Packet JSON/Markdown/testo, mantiene il sistema fail-closed e non esegue azioni operative.

Lo STEP 0630 aggiunge:

```text
scripts/asf_verification_profile_selector.py
docs/motor/0630_VERIFICATION_PROFILE_SELECTOR_TEST_COST_POLICY.md
examples/verification_profiles/
```

Il selector raccomanda profili `docs-only`, `code-unit`, `motor-core`, `publish`, `final-main` e `high-risk`, stima il costo dei check e fallisce chiuso su input ambiguo o high-risk.

Il prossimo step consigliato e':

```text
0640) Verification Profile Integration with Publish Runner
```

## 7. Stato dopo STEP 0640

Lo STEP 0640 collega il selector 0630 al publish runner 0590:

```text
scripts/asf_publish_step.ps1
docs/motor/0640_VERIFICATION_PROFILE_INTEGRATION_PUBLISH_RUNNER.md
examples/publish_step/0640_publish_config_*.example.json
```

Il runner valida profili dichiarati, blocca mismatch piu' leggeri, fallisce chiuso se il selector fallisce chiuso e mantiene Phase B/Phase C con approval espliciti.

Il prossimo step consigliato e':

```text
0650) Verification Profile Driven Publish Config Generator
```

## 8. Stato dopo STEP 0650

Lo STEP 0650 aggiunge un generator locale per bozze config publish:

```text
scripts/asf_publish_config_generator.py
docs/motor/0650_VERIFICATION_PROFILE_DRIVEN_PUBLISH_CONFIG_GENERATOR.md
examples/publish_config_generator/
tests/unit/test_asf_publish_config_generator.py
```

Il generator usa il selector 0630, produce JSON/Markdown, deduce test mirati e blocca input mancanti, L4, high-risk, final-main e selector fail-closed. Non esegue il publish runner e non autorizza commit, push, PR, merge o deploy.

Il prossimo step consigliato e':

```text
0660) Publish Config Generator Bridge Output Integration
```

## 9. Stato dopo STEP 0660

Lo STEP 0660 aggiunge output Bridge dedicato al generator:

```text
docs/motor/0660_PUBLISH_CONFIG_GENERATOR_BRIDGE_OUTPUT_INTEGRATION.md
examples/publish_config_generator/sample_bridge_output_input.json
```

Il generator puo' produrre artifact progressivi e `LAST-*` sotto `publish_config`, incluso `LAST-Publish_Config.json`.

La validazione `--validate-plan` invoca solo `scripts/asf_publish_step.ps1 -Phase Plan`; Phase B e Phase C restano manuali e human-gated.

Il prossimo step consigliato e':

```text
0670) Step Execution State Machine
```

## 10. Stato dopo STEP 0670

Lo STEP 0670 aggiunge la macchina a stati locale:

```text
scripts/asf_step_state_machine.py
docs/motor/0670_STEP_EXECUTION_STATE_MACHINE.md
examples/state_machine/
tests/unit/test_asf_step_state_machine.py
```

La state machine modella stati, eventi, transizioni, recovery e output JSON/Markdown/testo. Persiste lo stato sotto `tmp/`, fallisce chiuso su transizioni incoerenti o state file corrotto e rappresenta recovery combinate come `0650-0660` con warning espliciti.

Non esegue Phase B, Phase C, commit, push, PR, merge o deploy.

Il prossimo step consigliato e':

```text
0680) State Machine Bridge Integration
```

## 11. Stato dopo STEP 0680

Lo STEP 0680 aggiunge output Bridge opzionale alla state machine:

```text
docs/motor/0680_STATE_MACHINE_BRIDGE_INTEGRATION.md
```

La state machine puo' produrre `LAST-State.json`, `LAST-Event.json`, `LAST-Output_Compatto.md`, `LAST-Output_Completo.txt` e file progressivi sotto `state_machine`.

Se `--write-bridge` e' attivo e `--state-file` non viene passato, usa `<bridge-root>\LAST-State.json` come state file. I test restano su directory temporanee e non dipendono da Dropbox reale.

Non esegue Phase B, Phase C, commit, push, PR, merge o deploy.

Il prossimo step consigliato e':

```text
0690) State Machine Integration with Publish Config Generator
```

## 12. Stato dopo STEP 0690

Lo STEP 0690 collega il Publish Config Generator alla state machine:

```text
docs/motor/0690_STATE_MACHINE_INTEGRATION_WITH_PUBLISH_CONFIG_GENERATOR.md
```

Il generator puo' leggere uno state file esistente, verificare `LOCAL_VERIFIED` o `READY_TO_PUBLISH`, applicare `publish_config_generated` con `--update-state` e scrivere riferimenti incrociati tra `LAST-Publish_Config.json` e `LAST-State.json`.

Recovery e step combinati richiedono `--state-allow-recovery`; altrimenti il generator fallisce chiuso.

Non esegue Phase B, Phase C, commit, push, PR, merge o deploy.

Il prossimo step consigliato e':

```text
0700) End-to-End MVP Smoke Scenario
```

## 13. Stato dopo STEP 0700

Lo STEP 0700 aggiunge uno smoke end-to-end locale:

```text
docs/motor/0700_END_TO_END_MVP_SMOKE_SCENARIO.md
scripts/asf_e2e_mvp_smoke.py
tests/unit/test_asf_e2e_mvp_smoke.py
```

Il percorso positivo attraversa classifier, dry-run runner, gate decision report, verification profile selector, publish config generator e state machine fino a `READY_TO_PUBLISH`.

Il percorso negativo parte da `IMPLEMENTED`, richiede una config pronta con state integration e fallisce chiuso senza produrre `publish_config.json`.

Restano manuali e human-gated:

- review della config;
- Phase B;
- Phase C;
- commit, push, PR, merge e verifica finale su `main`.

Prossimo step consigliato:

```text
0710) Motor Run Manifest and Evidence Pack
```

## 14. Stato dopo STEP 0710

Lo STEP 0710 aggiunge un manifest unico per le run del Motore:

```text
docs/motor/0710_MOTOR_RUN_MANIFEST_AND_EVIDENCE_PACK.md
scripts/asf_motor_run_manifest.py
tests/unit/test_asf_motor_run_manifest.py
examples/motor_run_manifest/
```

Il manifest legge evidence 0700 o input JSON, calcola checksum sugli artifact fisici, normalizza check, warning, blocker e decisione, e produce `motor_run_manifest.json` e `motor_run_summary.md`.

Il Bridge `motor_run` resta opzionale con `--write-bridge`; i test usano solo directory temporanee.

Restano manuali e human-gated:

- review del manifest;
- Phase B;
- Phase C;
- commit, push, PR, merge e verifica finale su `main`.

Prossimo step consigliato:

```text
0730) End-to-End MVP Closure Pack
```

## 15. Stato dopo STEP 0720

Lo STEP 0720 aggiunge il runbook operativo del Motore MVP:

```text
docs/motor/0720_MVP_USAGE_RUNBOOK.md
```

Il runbook collega in una procedura unica prompt Codex, state machine, smoke
0700, manifest 0710, review umana, publish config generator, runner Phase B,
runner Phase C e recovery.

Restano human-gated:

- review del report Codex;
- review di manifest e config;
- Phase B con `-ApprovePublish`;
- Phase C con `-ApproveMerge`;
- chiusura finale su `main`.

Restano non automatici:

- hook runner -> state machine;
- pilota reale su step applicativo non sintetico;
- dichiarazione formale di chiusura MVP.

Prossimo step consigliato:

```text
0730) End-to-End MVP Closure Pack
```

## 16. Stato dopo STEP 0730

Lo STEP 0730 aggiunge il closure pack formale del Motore MVP:

```text
docs/motor/0730_END_TO_END_MVP_CLOSURE_PACK.md
```

Il closure pack dichiara perimetro, componenti inclusi/esclusi, evidenze,
criteri GO/WARNING/NO-GO, stato di gate/test/Bridge/state machine/manifest,
limiti noti, rischi residui e decisione:

```text
MVP STATUS: GO WITH WARNINGS
```

Restano fuori dal MVP:

- esecuzione autonoma fire-and-forget;
- publish/merge/deploy automatici;
- GitHub come fonte automatica di stato;
- hook completi runner -> state machine;
- pilot reale non sintetico;
- UI grafica e orchestrazione multi-modello.

Prossimo step eseguito:

```text
0740) MVP Real Step Pilot
```

## 17. Stato dopo STEP 0740

Lo STEP 0740 aggiunge il primo pilot reale post-MVP:

```text
docs/motor/0740_MVP_REAL_STEP_PILOT.md
```

Il pilot applica la baseline MVP a una modifica reale piccola e versionabile,
usa state machine, publish config generator e manifest come evidence locali, e
mantiene fuori scope Phase B, Phase C, commit, push, PR, merge e deploy.

Decisione prudente:

```text
PILOT STATUS: GO WITH WARNINGS
```

Warning principali:

- lo step resta documentale/strumentale;
- state machine e generator richiedono ancora comandi manuali;
- il manifest e' utile ma non sostituisce review semantica;
- `READY_TO_PUBLISH` non equivale ad approval.

Prossimo step consigliato:

```text
0750) State Machine Publish Runner Event Hooks
```

## 18. Stato dopo STEP 0750

Lo STEP 0750 aggiunge hook opzionali tra publish runner e state machine:

```text
docs/motor/0750_STATE_MACHINE_PUBLISH_RUNNER_EVENT_HOOKS.md
```

Il runner puo' emettere eventi `phase_b_started`, `phase_b_passed`,
`pr_created`, `phase_c_started`, `phase_c_passed`, `main_verified` e failure
events quando `state_machine_enabled=true`.

Restano invariati:

- Phase B richiede `-ApprovePublish`;
- Phase C richiede `-ApproveMerge`;
- config legacy senza hook restano valide;
- i test non usano GitHub reale o Dropbox reale.

Prossimo step consigliato:

```text
0760) MVP Real Step Pilot 2 with State Hooks
```

## 19. Stato dopo STEP 0760

Lo STEP 0760 aggiunge il secondo pilot reale post-MVP:

```text
docs/motor/0760_MVP_REAL_STEP_PILOT_2_WITH_STATE_HOOKS.md
```

Il pilot prepara uno state file locale in `READY_TO_PUBLISH`, una config
hook-aware con `state_machine_enabled=true` e una validazione `Phase Plan`
senza eseguire Phase B, Phase C, commit, push, PR, merge o deploy.

Decisione prudente:

```text
PILOT STATUS: GO WITH WARNINGS
```

Restano da validare durante la pubblicazione reale:

- eventi Phase B `phase_b_started`, `phase_b_passed`, `pr_created`;
- eventi Phase C `phase_c_started`, `phase_c_passed`, `main_verified`;
- output Bridge `LAST-State.json` e `LAST-Event.json`;
- collegamento tra hook e manifest/evidence pack.

Prossimo step consigliato:

```text
0770) Runner Hook Evidence Manifest Integration
```
