# 0730 - End-to-End MVP Closure Pack

## 1. Scopo

Questo closure pack chiude formalmente il Motore ASF MVP come baseline locale,
human-gated, auditabile e verificabile.

Il documento non introduce nuove automazioni operative. Serve a dichiarare:

- cosa include il MVP Motore;
- cosa resta escluso dal MVP;
- quali evidenze sono disponibili;
- quali criteri distinguono GO, WARNING e NO-GO;
- cosa significa considerare il MVP completato;
- quale fase post-MVP e' consigliata.

## 2. Stato repo verificato

Verifica iniziale eseguita nello STEP 0730:

- branch corrente: `main`;
- working tree iniziale: pulita;
- commit HEAD verificato: `ac6a5ce 0720 add MVP usage runbook (#64)`;
- `main` contiene lo STEP 0720;
- la documentazione motor 0580-0720 e gli script principali risultano presenti.

Storia MVP Motore verificata tramite log locale:

| Step | Evidenza log |
|---:|---|
| 0580 | `0580 add dry-run loop runner (#51)` |
| 0590 | `0590 add stable PowerShell publish runner (#52)` |
| 0600 | `0600 add risk classifier and gate policy (#53)` |
| 0610 | `0610 integrate risk classifier with dry-run loop runner (#54)` |
| 0620 | `0620 add gate decision approval packet (#55)` |
| 0630 | `0630 add verification profile selector (#56)` |
| 0640 | `0640 integrate verification profiles with publish runner (#57)` |
| 0650-0660 | `0650-0660 add publish config generator and bridge outputs (#58)` |
| 0670 | `0670 add step execution state machine (#59)` |
| 0680 | `0680 add state machine bridge integration (#60)` |
| 0690 | `0690 integrate state machine with publish config generator (#61)` |
| 0700 | `0700 add end-to-end MVP smoke scenario (#62)` |
| 0710 | `0710 add motor run manifest and evidence pack (#63)` |
| 0720 | `0720 add MVP usage runbook (#64)` |

Commit hash e dettagli PR diversi da quelli mostrati dal log locale non sono
verificati in questo step.

## 3. Perimetro MVP

Il Motore ASF MVP include:

- Risk Classifier;
- Gate Policy;
- Dry-run Loop Runner;
- Gate Decision Report / Human Approval Packet;
- Verification Profile Selector;
- Publish Runner stabile;
- Publish Config Generator;
- Step Execution State Machine;
- State Machine Bridge integration;
- integrazione State Machine con Publish Config Generator;
- End-to-End MVP Smoke Scenario;
- Motor Run Manifest and Evidence Pack;
- MVP Usage Runbook;
- questo End-to-End MVP Closure Pack.

Il MVP non include ancora:

- esecuzione autonoma fire-and-forget;
- merge automatico senza approval;
- deploy automatico;
- chiamate live AI obbligatorie;
- integrazione completa con GitHub come fonte automatica di stato;
- hook automatici completi del publish runner verso state machine;
- pilot reale su modifica funzionale non simulata;
- UI grafica;
- orchestrazione multi-modello completa;
- orchestratore unico che sostituisce la review umana.

## 4. Componenti inclusi

| Componente | Stato MVP | Evidenza principale |
|---|---|---|
| Risk Classifier | Incluso | `scripts/asf_risk_classifier.py`, `docs/motor/0600_RISK_CLASSIFIER_GATE_POLICY.md` |
| Gate Policy | Incluso | policy fail-closed documentata nello STEP 0600 |
| Dry-run Loop Runner | Incluso | `scripts/asf_dry_run_loop_runner.py`, `docs/motor/0580_DRY_RUN_LOOP_RUNNER.md` |
| Gate Decision Report | Incluso | `scripts/asf_gate_decision_report.py`, `docs/motor/0620_GATE_DECISION_REPORT_HUMAN_APPROVAL_PACKET.md` |
| Verification Profile Selector | Incluso | `scripts/asf_verification_profile_selector.py`, `docs/motor/0630_VERIFICATION_PROFILE_SELECTOR_TEST_COST_POLICY.md` |
| Publish Runner stabile | Incluso | `scripts/asf_publish_step.ps1`, `docs/motor/0590_STABLE_POWERSHELL_PUBLISH_RUNNER.md` |
| Publish Config Generator | Incluso | `scripts/asf_publish_config_generator.py`, `docs/motor/0650_VERIFICATION_PROFILE_DRIVEN_PUBLISH_CONFIG_GENERATOR.md` |
| State Machine | Incluso | `scripts/asf_step_state_machine.py`, `docs/motor/0670_STEP_EXECUTION_STATE_MACHINE.md` |
| State Machine Bridge | Incluso | `docs/motor/0680_STATE_MACHINE_BRIDGE_INTEGRATION.md` |
| Generator/state integration | Incluso | `docs/motor/0690_STATE_MACHINE_INTEGRATION_WITH_PUBLISH_CONFIG_GENERATOR.md` |
| E2E smoke | Incluso | `scripts/asf_e2e_mvp_smoke.py`, `docs/motor/0700_END_TO_END_MVP_SMOKE_SCENARIO.md` |
| Manifest/evidence pack | Incluso | `scripts/asf_motor_run_manifest.py`, `docs/motor/0710_MOTOR_RUN_MANIFEST_AND_EVIDENCE_PACK.md` |
| Usage runbook | Incluso | `docs/motor/0720_MVP_USAGE_RUNBOOK.md` |

## 5. Componenti esclusi

| Esclusione | Motivo |
|---|---|
| Autopilota completo | Il controllo umano resta parte del modello operativo. |
| Publish automatico | Phase B richiede `-ApprovePublish`; Phase C richiede `-ApproveMerge`. |
| GitHub state source automatica | Lo stato reale resta da verificare con Git, PR e output runner. |
| Hook runner/state machine completi | La state machine esiste, ma Phase B/C non scrivono ancora eventi automaticamente. |
| Pilot reale non sintetico | Lo smoke 0700 usa file e risultati simulati. |
| AI live obbligatoria | Il MVP e' locale e non richiede chiamate OpenAI/API esterne. |
| UI grafica | Il MVP resta CLI/documentazione/runbook. |
| Orchestrazione multi-modello | Fuori perimetro MVP. |

## 6. Flusso end-to-end supportato

Il flusso MVP supportato e':

```text
prompt Codex -> implementazione locale Codex -> verifiche locali -> state machine
-> smoke/evidence -> manifest -> review umana -> publish config -> Phase B -> Phase C
```

Nel dettaglio:

1. Il prompt viene salvato nel Bridge `codex_command`.
2. Codex lavora localmente e lascia la working tree modificata.
3. Le verifiche locali vengono eseguite prima della pubblicazione.
4. La state machine rende esplicito il passaggio verso `LOCAL_VERIFIED` e `READY_TO_PUBLISH`.
5. Lo smoke 0700 dimostra il percorso positivo e il fail-closed negativo.
6. Il manifest 0710 normalizza evidence, artifact, checksum, warning, blocker e decisione.
7. Alberto rivede report, manifest, config e warning.
8. Il Publish Config Generator produce una config runner.
9. Phase B pubblica solo con `-ApprovePublish`.
10. Phase C mergea e verifica `main` solo con `-ApproveMerge`.

Questo flusso non elimina la review umana e non autorizza commit, push, PR,
merge o deploy automatici.

## 7. Evidenze disponibili

| Evidenza | Stato | Note |
|---|---|---|
| Smoke e2e 0700 | Disponibile | Scenario positivo fino a `READY_TO_PUBLISH`; scenario negativo fail-closed. |
| Manifest 0710 | Disponibile | Normalizza artifact, checksum, check, warning, blocker e decisione. |
| Runbook 0720 | Disponibile | Procedura operativa manuale/human-gated. |
| Test unitari e completi | Disponibili | Da eseguire con `python -m pytest -q`. |
| Workflow health | Disponibile | Da eseguire con `python scripts/check_workflow_health.py`. |
| Verify gate | Disponibile | Da eseguire con `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify.ps1`. |
| Bridge output | Disponibile come funzione dei tool | In STEP 0730 il prompt e' stato salvato nel Bridge `codex_command`; gli altri output Bridge non sono rigenerati automaticamente da questo documento. |
| PR #51-#64 | Verificati da log locale | Numeri presenti nei subject commit locali su `main`. |
| Recovery 0650-0660 | Documentata | Caso combinato pubblicato con PR #58 e richiamato nei runbook. |

## 8. Criteri GO

Il MVP puo' essere classificato GO se:

- `python scripts/check_workflow_health.py` passa;
- `python -m pytest -q` passa;
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify.ps1` passa;
- `git --no-pager diff --check` passa;
- lo smoke positivo arriva a `READY_TO_PUBLISH`;
- lo scenario negativo fail-closed passa;
- il manifest produce una decisione coerente e non promuove evidence mancanti;
- il runbook 0720 esiste e descrive il flusso operativo;
- il publish runner resta human-gated;
- nessun comando publish automatico viene eseguito senza approval;
- Bridge output per prompt, config, state, manifest e report resta disponibile come audit operativo;
- risk classifier e policy restano fail-closed.

## 9. Criteri WARNING

Il MVP deve essere classificato con warning se:

- lo smoke usa file, contenuto applicativo o check simulati;
- alcuni hook restano manuali;
- recovery complessa resta manuale;
- `LAST-*` sono alias operativi da validare contro step, branch e timestamp reali;
- la state machine non interroga GitHub automaticamente;
- il manifest non valida semanticamente ogni campo interno dei componenti;
- Phase B/C non scrivono automaticamente eventi state machine;
- il pilot reale su modifica funzionale non e' ancora stato eseguito.

Questi warning sono limiti noti e non bloccanti se i gate locali passano e se
la review umana resta esplicita.

## 10. Criteri NO-GO

Il MVP deve essere classificato NO-GO se:

- workflow health fallisce;
- `python -m pytest -q` fallisce;
- `verify.ps1` fallisce;
- `git --no-pager diff --check` fallisce;
- Phase B o Phase C vengono eseguite senza approval esplicita;
- il manifest `FAIL_CLOSED` o `INCOMPLETE` viene ignorato;
- la state machine produce stati incoerenti;
- file fuori scope entrano nella pubblicazione;
- il publish runner non resta human-gated;
- il risk classifier non fallisce chiuso su input ambiguo;
- Bridge, config o `LAST-*` vengono trattati come fonte autorevole al posto di Git e file versionati.

## 11. Stato dei gate

| Gate | Stato MVP |
|---|---|
| Prompt saved | Supportato tramite Bridge `codex_command`; in STEP 0730 eseguito per il prompt corrente. |
| Codex implementation | Manuale, locale, senza commit/push/PR/merge/deploy automatici. |
| Local verification | Supportata da workflow health, pytest, verify.ps1 e diff check. |
| Risk/gate classification | Supportata da classifier e gate policy fail-closed. |
| Human approval | Obbligatoria per avanzare a pubblicazione. |
| Phase B | Human-gated con `-ApprovePublish`. |
| Phase C | Human-gated con `-ApproveMerge` e verifica finale su `main`. |
| Recovery | Documentata, ma resta manuale. |

## 12. Stato dei test

Il closure pack richiede questi check locali prima dell'handoff:

```powershell
python scripts/check_workflow_health.py
python -m pytest -q
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify.ps1
git --no-pager diff --check
git status --short --untracked-files=all
```

Snapshot STEP 0730:

- `python scripts/check_workflow_health.py`: PASS;
- `python -m pytest -q`: PASS;
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify.ps1`: PASS, con `576 passed`;
- `git --no-pager diff --check`: PASS; warning LF/CRLF non bloccante su `tests/unit/test_workflow_health_check.py`;
- `git status --short --untracked-files=all`: mostra solo i file attesi dello STEP 0730;
- decisione finale mantenuta: `MVP STATUS: GO WITH WARNINGS`.

Se uno dei check obbligatori fallisce in una riesecuzione successiva, la
decisione finale deve diventare `MVP STATUS: NO-GO` fino a correzione.

## 13. Stato Bridge

Il Bridge resta storage operativo, non fonte autorevole.

Directory MVP rilevanti:

- `codex_command`;
- `publish_config`;
- `state_machine`;
- `e2e_smoke`;
- `motor_run`;
- `pwsh_command`.

In STEP 0730 il prompt e' stato salvato in:

- `0730-01-Prompt_Codex_End_To_End_MVP_Closure_Pack.md`;
- `LAST-Prompt_Codex.md`.

Gli altri output Bridge sono disponibili tramite gli strumenti dedicati, ma non
devono essere considerati approvazione automatica.

## 14. Stato state machine

La state machine MVP:

- modella stati ed eventi dello step;
- valida transizioni fail-closed;
- puo' persistere stato locale o Bridge;
- puo' essere integrata con il Publish Config Generator;
- non esegue Phase B, Phase C, GitHub, commit, push, PR, merge o deploy.

Limite noto: Phase B/C non emettono ancora automaticamente eventi verso la state
machine.

## 15. Stato manifest/evidence pack

Il manifest MVP:

- legge evidence directory o input JSON;
- produce `motor_run_manifest.json`;
- produce `motor_run_summary.md`;
- calcola checksum degli artifact presenti;
- classifica decisioni come `READY_TO_PUBLISH`, `BLOCKED`, `FAIL_CLOSED`,
  `INCOMPLETE` o `REVIEW_REQUIRED`;
- non promuove a `READY_TO_PUBLISH` se artifact richiesti o check richiesti mancano;
- non approva pubblicazione.

Limite noto: il manifest e' un consolidatore di evidence, non un revisore
semantico completo del contenuto di ogni componente.

## 16. Limiti noti e rischi residui

Limiti noti:

- lo smoke 0700 resta sintetico;
- `READY_TO_PUBLISH` non equivale ad approval;
- la recovery complessa richiede intervento umano;
- i file `LAST-*` semplificano l'operativita' ma possono essere stale;
- GitHub non e' ancora fonte automatica dello stato;
- il runner publish non aggiorna ancora automaticamente la state machine;
- non esiste un orchestratore unico.

Rischi residui:

- confondere config generata con approval;
- usare un `LAST-*` di uno step o branch diverso;
- saltare Phase C per velocita';
- trattare lo smoke come prova di pilot reale;
- ignorare `INCOMPLETE` o `FAIL_CLOSED` nel manifest;
- estendere il MVP verso automazioni non ancora testate.

## 17. Cosa resta human-gated

Restano human-gated:

- decisione di avviare Codex;
- review del report Codex;
- accettazione dei warning;
- classificazione finale GO/WARNING/NO-GO;
- review di manifest e publish config;
- scelta di procedere a Phase B;
- scelta di procedere a Phase C;
- merge e verifica finale su `main`;
- recovery.

## 18. Cosa resta simulato

Restano simulati o non dimostrati nel MVP:

- contenuto applicativo dello smoke 0700;
- alcuni esiti check dello scenario smoke;
- pilot reale su modifica funzionale non sintetica;
- review indipendente completa;
- hook automatici runner/state machine;
- orchestrazione multi-modello.

## 19. Decisione finale MVP

Decisione prudente:

```text
MVP STATUS: GO WITH WARNINGS
```

Motivazione:

- il Motore ASF MVP ha componenti core versionati;
- il flusso locale end-to-end e' documentato e dimostrato da smoke/manifest/runbook;
- i gate restano espliciti e human-gated;
- il runner publish non parte senza approval;
- le evidenze sono auditabili;
- restano limiti noti non bloccanti: smoke sintetico, hook manuali, recovery manuale e pilot reale non ancora eseguito.

La decisione deve essere degradata a `MVP STATUS: NO-GO` se le verifiche locali
dello step 0730 falliscono.

## 20. Prossima fase consigliata

Prossimo step consigliato:

```text
0740) MVP Real Step Pilot
```

Motivo: prima di aggiungere hook automatici tra publish runner e state machine,
conviene usare la baseline MVP su uno step reale piccolo, non sintetico,
documentare frizioni operative, verificare che manifest/config/gate reggano in
uso effettivo e solo dopo automatizzare ulteriormente.

## 20.1 Aggiornamento STEP 0740

Lo STEP 0740 ha eseguito il primo pilot reale post-MVP:

```text
docs/motor/0740_MVP_REAL_STEP_PILOT.md
```

Il pilot usa una modifica reale piccola, evidence temporanee locali, state
machine, publish config generator e manifest documentale. La decisione resta
prudente:

```text
PILOT STATUS: GO WITH WARNINGS
```

Il prossimo step consigliato dopo il pilot e':

```text
0750) State Machine Publish Runner Event Hooks
```

## 21. Sintesi di chiusura

Il Motore ASF MVP e' chiuso come baseline usabile, locale, human-gated e
verificabile.

La chiusura non autorizza automazione cieca. La fase post-MVP deve partire da un
pilot reale controllato, mantenendo fail-closed, review umana e pubblicazione
via `scripts/asf_publish_step.ps1`.
