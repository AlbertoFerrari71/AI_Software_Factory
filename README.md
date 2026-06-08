# AI Software Factory

**Metodo interno:** Codex Alchemy Method
**Stato:** STEP 0790 - Post-MVP Roadmap and Hardening Plan
**Data bootstrap:** 2026-05-25
**Strategia:** local-first personale, progettato per evoluzione SaaS

---

## 1. Scopo del progetto

AI Software Factory è un framework operativo per trasformare idee espresse in linguaggio naturale in software:

- funzionante;
- documentato;
- testato;
- mantenibile;
- sicuro;
- tracciabile;
- reversibile;
- riutilizzabile su più progetti.

Il progetto non nasce per generare codice in modo incontrollato. Nasce per creare una pipeline guidata in cui ChatGPT, Codex, GitHub, test automatici, documentazione viva, API OpenAI, MCP e regole di sicurezza lavorano insieme sotto controllo umano.

Il metodo interno si chiama **Codex Alchemy Method**: l'idea grezza viene trasformata progressivamente in requisiti, architettura, task, codice, test, documentazione e rilascio.

---

## 2. Stato repository

Questo repository e' nello stato **STEP 0790 - Post-MVP Roadmap and Hardening Plan**.

Sono presenti:

- documentazione iniziale;
- roadmap 010-150;
- decision log;
- `AGENTS.md` con regole operative per agenti AI;
- struttura `src/` senza logica applicativa;
- struttura `tests/` con smoke test minimale;
- template GitHub issue/PR;
- workflow GitHub Actions minimale;
- template per prompt, task Codex, test plan e ADR;
- modello di sicurezza operativo L0-L4;
- policy machine-readable in `policies/`;
- template approval, dry-run, risk assessment e rollback;
- test automatici sulle regole critiche di sicurezza;
- adapter OpenAI API dry-run/mock senza chiamate live;
- live boundary e credential gate deterministici;
- primo percorso live smoke OpenAI API controllato, human-gated e con output redatto sotto `tmp/`;
- schema risultato live smoke stabile, classificazioni fail-closed e artifact JSON/Markdown sicuri.
- regola clean-first per prompt Codex, con separazione tra prompt pulito, Bridge, intake gate e publication command pack.
- standard Safe Bootstrap PowerShell Command Pack con bootstrap corto, parse-check, script `.ps1` completo, artefatti progressivi `NNNN-II-Tipo_Nome.ext`, DOCX non bloccante e pubblicazione PR-first.
- pacchetto canonico PowerShell Command Pack con README template, skill draft esportabile, parser Git robusto e `ArgList`.
- export installabile della skill `as-common-pwsh-command-pack` dentro ASF, con installer dry-run/apply e guardrail anti-scrittura esterna non autorizzata.
- deprecazione degli artefatti `LAST-*`, regola `max(II)` per trovare l'ultimo artefatto e utility prudente di migrazione dry-run/apply.
- controlled live execution pack OpenAI dry-run-default con doppio consenso futuro, artifact safe sotto `tmp/` e template operatore PowerShell.
- wrapper STEP 0560 per primo live run autorizzato via adapter, con report versionato `docs/0560-01-Report_OpenAI_API_Adapter_First_Authorized_Live_Run.md`.
- diagnostic pack STEP 0560 provider-side, con `docs/0560-03-Diagnostic_OpenAI_Provider_HTTP_Error_And_Rate_Limit.md`, stato `BLOCKED_BY_RATE_LIMIT_OR_QUOTA` e nessuna evidence positiva inventata.
- ADR e roadmap per autonomia supervisionata a gate, MVP Motore, loop a gate e nodo revisione indipendente.
- Dry-run Loop Runner locale che legge richiesta simulata, genera o legge piano dry-run, produce artifact strutturati e ferma il ciclo su gate supervisionato.
- Stable PowerShell Publish Runner versionato per sostituire i mega-blocchi PowerShell copiati in chat con comando corto, config JSON, gate espliciti e output Bridge.
- Risk Classifier + Gate Policy deterministico, rule-based e fail-closed per assegnare livelli L0-L4 e gate richiesti.
- integrazione del Risk Classifier nel checkpoint `RISK_CLASSIFY` del Dry-run Loop Runner, con risk report strutturato e nessuna autorizzazione write/publish/live.
- Gate Decision Report che trasforma risk report e check evidence in un Approval Packet umano JSON/Markdown/testo, fail-closed e senza azioni operative.
- Verification Profile Selector che suggerisce profili `docs-only`, `code-unit`, `motor-core`, `publish`, `final-main` e `high-risk` per bilanciare risultato, velocita', costo e rischio.
- integrazione del Verification Profile Selector nel Publish Runner, con validazione opzionale delle config profilo, fail-closed su mismatch e Phase B/Phase C ancora human-gated.
- Publish Config Generator guidato dal Verification Profile Selector, che produce bozze JSON/Markdown per il runner senza eseguire publish, merge o altre azioni operative.
- output Bridge dedicato del Publish Config Generator in `publish_config`, con artifact progressivi, `LAST-Publish_Config.json`, riepilogo compatto, output completo e validazione `-Phase Plan` opt-in.
- Step Execution State Machine locale, con stati/eventi ASF, transizioni fail-closed, persistenza JSON sotto `tmp/` e output JSON/Markdown/testo senza eseguire Phase B/C o Git/GitHub.
- State Machine Bridge Integration in `state_machine`, con `LAST-State.json`, `LAST-Event.json`, output compatto/completo e file progressivi senza usare Dropbox reale nei test.
- integrazione opzionale tra Publish Config Generator e State Machine: il generator puo' leggere uno stato esistente, applicare `publish_config_generated`, aggiornare `LAST-State.json` e collegare `LAST-Publish_Config.json` senza pubblicare.
- End-to-End MVP Smoke Scenario locale, con scenario positivo fino a `READY_TO_PUBLISH`, scenario negativo fail-closed, evidence pack sotto `tmp/e2e_mvp_smoke` e Bridge opzionale solo su richiesta.
- Motor Run Manifest and Evidence Pack, con manifest unico `motor_run_manifest.json`, summary Markdown, checksum artifact, decisione prudente e Bridge opzionale sotto `motor_run`.
- MVP Usage Runbook, con procedura operativa smoke -> manifest -> review -> publish config -> Phase B -> Phase C, directory Bridge, checklist Alberto, recovery e limiti MVP.
- End-to-End MVP Closure Pack, con perimetro MVP, evidenze, criteri GO/WARNING/NO-GO, stato gate/test/Bridge/state machine/manifest e decisione prudente `MVP STATUS: GO WITH WARNINGS`.
- MVP Real Step Pilot, con modifica reale piccola, state machine locale, evidence temporanee, manifest documentale e decisione `PILOT STATUS: GO WITH WARNINGS`.
- State Machine Publish Runner Event Hooks, con hook opzionali del publish runner verso la state machine per Phase B/Phase C, fail-closed su mismatch e gate `-ApprovePublish`/`-ApproveMerge` invariati.
- MVP Real Step Pilot 2 with State Hooks, con stato iniziale `READY_TO_PUBLISH`, config hook-aware validata in `Phase Plan`, evidence temporanee sotto `tmp/` e decisione `PILOT STATUS: GO WITH WARNINGS`.
- Runner Hook Evidence Manifest Integration, con sezione `runner_hooks` nel manifest, lettura read-only dello state file prodotto dal runner, validazione eventi/final state e Bridge output temporaneo nei test.
- MVP Real Step Pilot 3 with Manifest Hooks, con modifica reale documentale, state file iniziale, config hook-aware, `Phase Plan` locale e manifest sintetico per preparare la validazione post-publish runner -> state machine -> manifest.
- Post-MVP Roadmap and Hardening Plan, con decisione `HARDENING FIRST`, warning residui consolidati, priorita' PowerShell/recovery/evidence/Bridge e roadmap 0800-0860.

Non sono ancora presenti:

- orchestratore locale;
- API FastAPI;
- database;
- integrazioni OpenAI API live produttive;
- integrazioni MCP;
- automazioni Codex operative;
- Controlled Codex Executor;
- first controlled write pilot;
- logica applicativa reale.

---

## 3. Principio guida

> L'AI non sostituisce il controllo umano.
> L'AI accelera il passaggio da idea confusa a software affidabile attraverso un processo controllato, tracciabile, testabile e reversibile.

---

## 4. Caso pilota

Il caso pilota iniziale è **Family Photo Organizer**.

Family Photo Organizer viene usato come laboratorio reale perché contiene già molti elementi tipici del metodo:

- idea nata in linguaggio naturale;
- sviluppo incrementale;
- approccio read-only iniziale;
- protezione da cancellazioni accidentali;
- quarantena per foto candidate alla cancellazione;
- GitHub come centro operativo;
- Codex come assistente di sviluppo;
- test automatici;
- documentazione viva;
- step numerati;
- branch e PR;
- attenzione a sicurezza e reversibilità.

Family Photo Organizer non limita il framework: serve a estrarre una metodologia generale.

---

## 5. Target utenti

### 5.1 Guided Mode

Per persone con buone idee ma poca programmazione.

Obiettivo:

- domande semplici;
- scelte guidate;
- default sicuri;
- protezione da errori tecnici;
- trasformazione progressiva dell'idea in software.

### 5.2 Expert Mode

Per utenti tecnici o semi-tecnici.

Obiettivo:

- accelerare progettazione e sviluppo;
- mantenere controllo su branch, commit, PR e test;
- vedere diff, log, rischi e rollback;
- usare Codex CLI, Codex Cloud, API e GitHub senza perdere sicurezza.

---

## 6. Pipeline base

```text
Idea naturale
  ↓
FASE 1 — Allineamento
  ↓
Project Charter
  ↓
Requirement Alchemy
  ↓
Architecture Forge
  ↓
Work Package Generator
  ↓
Codex Task Packet
  ↓
Branch dedicato
  ↓
Codex CLI / Codex Cloud
  ↓
Diff Review
  ↓
Verification Gate
  ↓
Documentation Sync
  ↓
Human Approval Gate
  ↓
PR / Merge / Release
  ↓
Learning Loop
```

---

## 7. Struttura principale

```text
docs/                         Documentazione viva
templates/                    Template prompt, Codex, issue, PR, test, ADR
src/ai_software_factory/       Scheletro moduli futuri
tests/                         Smoke/unit/integration tests
.github/                       Workflow CI e template GitHub
```

Indice operativo centrale:

```text
docs/34_PROJECT_WORKFLOW_INDEX.md
```

Usarlo per orientarsi tra Prompt Packet Generator, Verification Gate, Documentation Sync, Soft Protection Guardrails, lifecycle checklist, onboarding e script locali.

Controllo locale read-only del workflow:

```text
docs/35_WORKFLOW_HEALTH_CHECK.md
```

Scheda rapida dei comandi operativi:

```text
docs/36_WORKFLOW_QUICK_REFERENCE.md
```

Report standard di chiusura step:

```text
docs/37_STEP_CLOSURE_REPORT.md
```

Ricettario operativo dei comandi workflow:

```text
docs/38_WORKFLOW_COMMAND_COOKBOOK.md
```

Dashboard locale read-only dello stato workflow:

```text
docs/39_WORKFLOW_STATUS_DASHBOARD.md
```

Checklist di readiness per pilot interno local-first:

```text
docs/40_RELEASE_READINESS.md
```

Protocollo di onboarding per pilot su progetto esistente:

```text
docs/41_EXISTING_PROJECT_PILOT_ONBOARDING.md
```

Runner locale per preparare il prossimo step senza invocare Codex o modificare il repo target:

```text
docs/42_ASF_NEXT_STEP_RUNNER.md
```

Upgrade del runner con profili progetto, handoff Codex migliorato e Verification Pack:

```text
docs/43_ASF_RUNNER_PROJECT_PROFILES.md
docs/44_ASF_RUNNER_CODEX_HANDOFF_IMPROVEMENTS.md
docs/45_ASF_RUNNER_VERIFICATION_PACK.md
```

Automation readiness pack con hardening verifiche, intake report Codex e closure pack human-gated:

```text
docs/46_ASF_RUNNER_VERIFICATION_PACK_HARDENING.md
docs/47_ASF_CODEX_REPORT_INTAKE.md
docs/48_ASF_HUMAN_GATED_CLOSURE_PACK.md
```

Automation bridge pack verso futura invocazione Codex controllata, ancora senza esecuzione automatica:

```text
docs/49_ASF_HUMAN_APPROVAL_GATE.md
docs/50_ASF_CODEX_INVOCATION_DESIGN.md
docs/51_ASF_CODEX_INVOCATION_DRY_RUN_PACK.md
```

Prototipo read-only human-approved per invocazione Codex, result capture e safety gate:

```text
docs/52_ASF_CODEX_READONLY_INVOCATION_PROTOTYPE.md
docs/53_ASF_CODEX_INVOCATION_RESULT_CAPTURE.md
docs/54_ASF_CODEX_READONLY_SAFETY_GATE.md
```

Primo trial manuale controllato della pipeline Codex read-only:

```text
docs/55_ASF_CODEX_READONLY_FIRST_MANUAL_TRIAL.md
docs/56_ASF_CODEX_READONLY_FIRST_TRIAL_RESULTS.md
docs/57_ASF_CODEX_READONLY_CLEAN_TARGET_TRIAL.md
docs/58_ASF_CODEX_READONLY_CLEAN_TARGET_TRIAL_RESULTS.md
docs/59_ASF_CODEX_READONLY_REPEATABLE_TRIAL_PACK.md
docs/60_ASF_CODEX_READONLY_REPEATABLE_TRIAL_RESULTS.md
```

Hardening della skill comune per PowerShell Command Pack robusti:

```text
docs/64_ASF_PWSH_COMMAND_PACK_SKILL_HARDENING.md
docs/70_ASF_PWSH_COMMAND_PACK_SKILL_FINALIZATION.md
docs/71_ASF_PWSH_COMMAND_PACK_SKILL_EXPORT_INSTALL.md
docs/73_LAST_DEPRECATION_4_DIGIT_ARTIFACT_NAMING_STANDARD.md
templates/pwsh_command_pack/README.md
templates/pwsh_command_pack/as-common-pwsh-command-pack-SKILL.md
templates/pwsh_command_pack/export/as-common-pwsh-command-pack/SKILL.md
templates/pwsh_command_pack/safe_bootstrap_template.ps1
templates/pwsh_command_pack/safe_command_pack_script_template.ps1
scripts/install_pwsh_command_pack_skill.py
scripts/migrate_artifact_names_4digit.py
```

Regola prompt Codex clean-first e separazione da Bridge, intake gate e publication command pack:

```text
docs/08_CODEX_WORKFLOW.md
docs/34_PROJECT_WORKFLOW_INDEX.md
docs/36_WORKFLOW_QUICK_REFERENCE.md
docs/38_WORKFLOW_COMMAND_COOKBOOK.md
```

OpenAI API Adapter dry-run/mock, senza SDK e senza chiamate live:

```text
docs/65_ASF_OPENAI_API_ADAPTER.md
```

OpenAI API Adapter live boundary e credential gate dello STEP 510:

```text
docs/66_ASF_OPENAI_API_ADAPTER_LIVE_BOUNDARY_CREDENTIAL_GATE.md
```

OpenAI API Adapter first controlled live smoke test:

```text
docs/67_ASF_OPENAI_API_ADAPTER_FIRST_CONTROLLED_LIVE_SMOKE_TEST.md
```

OpenAI API Adapter live smoke result hardening:

```text
docs/68_ASF_OPENAI_API_ADAPTER_LIVE_SMOKE_RESULT_HARDENING.md
```

OpenAI API Adapter controlled live execution pack:

```text
docs/69_ASF_OPENAI_API_ADAPTER_CONTROLLED_LIVE_EXECUTION_PACK.md
```

Autonomia supervisionata a gate e MVP Motore:

```text
docs/adr/0570_SUPERVISED_GATE_AUTONOMY.md
docs/motor/0570_MVP_MOTOR_ROADMAP.md
docs/motor/0570_GATE_LOOP_SPEC.md
docs/motor/0570_INDEPENDENT_REVIEW_NODE.md
docs/motor/0580_DRY_RUN_LOOP_RUNNER.md
docs/motor/0590_STABLE_POWERSHELL_PUBLISH_RUNNER.md
docs/motor/0600_RISK_CLASSIFIER_GATE_POLICY.md
docs/motor/0610_RISK_CLASSIFIER_DRY_RUN_INTEGRATION.md
docs/motor/0620_GATE_DECISION_REPORT_HUMAN_APPROVAL_PACKET.md
docs/motor/0620_VERIFICATION_BALANCE_NOTES.md
docs/motor/0630_VERIFICATION_PROFILE_SELECTOR_TEST_COST_POLICY.md
docs/motor/0640_VERIFICATION_PROFILE_INTEGRATION_PUBLISH_RUNNER.md
docs/motor/0650_VERIFICATION_PROFILE_DRIVEN_PUBLISH_CONFIG_GENERATOR.md
docs/motor/0660_PUBLISH_CONFIG_GENERATOR_BRIDGE_OUTPUT_INTEGRATION.md
docs/motor/0670_STEP_EXECUTION_STATE_MACHINE.md
docs/motor/0680_STATE_MACHINE_BRIDGE_INTEGRATION.md
docs/motor/0690_STATE_MACHINE_INTEGRATION_WITH_PUBLISH_CONFIG_GENERATOR.md
docs/motor/0700_END_TO_END_MVP_SMOKE_SCENARIO.md
docs/motor/0710_MOTOR_RUN_MANIFEST_AND_EVIDENCE_PACK.md
docs/motor/0720_MVP_USAGE_RUNBOOK.md
docs/motor/0730_END_TO_END_MVP_CLOSURE_PACK.md
docs/motor/0740_MVP_REAL_STEP_PILOT.md
docs/motor/0750_STATE_MACHINE_PUBLISH_RUNNER_EVENT_HOOKS.md
docs/motor/0760_MVP_REAL_STEP_PILOT_2_WITH_STATE_HOOKS.md
docs/motor/0770_RUNNER_HOOK_EVIDENCE_MANIFEST_INTEGRATION.md
docs/motor/0780_MVP_REAL_STEP_PILOT_3_WITH_MANIFEST_HOOKS.md
docs/motor/0790_POST_MVP_ROADMAP_AND_HARDENING_PLAN.md
```

---

## 8. Setup locale minimo

Per verificare il repository:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pytest -q

```

I test presenti verificano che il package sia importabile, che i file fondamentali del repository esistano e che la policy di sicurezza L0-L4 rispetti i controlli minimi.

---

## 9. Regole operative iniziali

1. Non generare codice applicativo prima di aver chiarito obiettivi, vincoli, rischi e struttura minima.
2. Non proporre automazioni distruttive senza dry-run, approvazione esplicita e rollback.
3. Ogni modifica deve essere piccola, isolata, testabile e documentata.
4. Ogni step deve avere numero, nome, obiettivo e criterio di completamento.
5. Ogni sviluppo deve prevedere test automatici o checklist manuale esplicita.
6. Ogni decisione architetturale importante deve essere registrata.
7. La semplicità prevale su soluzioni sofisticate non necessarie.
8. Ogni azione deve distinguere fatti verificati, ipotesi, stime, rischi, decisioni e punti da validare.

---

## 10. Safety Model operativo

Lo STEP 030 introduce:

- livelli L0-L4;
- approval gate;
- dry-run policy;
- backup/rollback policy;
- path allowlist/denylist;
- secret policy;
- classificazione tool;
- regole specifiche per Codex, GitHub, OpenAI API e MCP.

Policy principali:

```text
policies/safety_policy.v0.json
policies/safety_policy.v0.yaml
policies/path_policy.v0.json
```

## 11. Prossimo step

```text
0800) PowerShell Native Command Guardrail Hardening
```

Obiettivo: standardizzare i guardrail PowerShell per comandi nativi, exit code, argomenti vuoti e falsi `COMPLETATO` prima di aumentare l'automazione post-MVP.
