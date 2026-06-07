# 10 — Roadmap

## 1. Regola di numerazione

La roadmap usa step progressivi con intervallo 10.

Motivo:

- facilita inserimenti intermedi;
- mantiene ordine;
- evita numerazioni casuali;
- rende semplice collegare issue, branch e PR.

Esempio:

```text
010) Visione e contesto
020) Repository Genesis
030) Safety Model
```

---

## 2. Roadmap macro

| Step | Nome | Obiettivo | Deliverable | Tipo | Stato |
|---:|---|---|---|---|---|
| 010 | Visione e contesto | Definire identità, target, principi, roadmap e decisioni iniziali | README, contesto, visione, strategia, roadmap, decision log | MVP personale | Completato |
| 020 | Repository Genesis | Creare struttura repository completa | Cartelle, template, placeholder, CI base | MVP personale | Completato |
| 030 | Safety Model | Formalizzare L0-L4 e approval gate | Security model, policy, rollback strategy | MVP + SaaS-ready | Completato |
| 040 | Prompt Packet Generator | Standardizzare prompt e task packet | Template ChatGPT/Codex/review/repair | MVP personale | Completato |
| 050 | GitHub Workflow | Standardizzare issue, branch, PR e CI | Issue/PR template, branch policy | MVP personale | Completato |
| 060 | Codex Workflow | Definire uso Codex CLI e Cloud | Codex Task Packet, modalità ask/edit | MVP personale | Completato |
| 070 | Verification Gate | Definire test, lint, build, smoke, security | Test strategy, checklist, CI | MVP personale | Completato |
| 080 | Documentation Sync | Mantenere docs allineate | Changelog, decision log, roadmap update | MVP personale | Completato |
| 090 | Branch Protection Policy | Definire protezioni branch e status check richiesti | Policy branch protection, required checks, rollout manuale | MVP personale | Completato |
| 100 | Branch Protection Implementation | Preparare script e runbook per protezioni main | Script DryRun, verify script, runbook | MVP personale | Completato |
| 110 | Branch Protection Verification and Hardening | Verificare protezione reale e definire fallback soft protection | Required check reale, limite GitHub plan, script hardening | MVP personale | Completato |
| 120 | Soft Protection Guardrails | Ridurre il rischio di push accidentale su main finche' manca hard protection | Hook locali opt-in, install/check script, runbook | MVP personale | Completato |
| 130 | Prompt Packet Hardening | Rafforzare task packet e prompt contro errori operativi ricorrenti | Documento hardening, template aggiornati, test documentali | MVP personale | Completato |
| 140 | Prompt Packet Validation Lite | Validare sezioni minime dei task packet senza schema rigido | Validator leggero, documento operativo, test | MVP personale | Completato |
| 150 | Prompt Packet Examples and Golden Samples | Creare esempi validi e casi negativi per il validatore | Golden samples, esempi, test | MVP personale | Completato |
| 160 | Prompt Packet Validation Strict Mode | Rafforzare il validatore con controlli opzionali piu' granulari | Strict mode, controlli mirati, test | MVP personale | Completato |
| 170 | Prompt Packet Generator CLI Hardening | Rafforzare il generatore CLI di task packet | CLI hardening, validazione, test | MVP personale | Completato |
| 180 | Prompt Packet Generator Packaging | Rendere il generatore piu' riusabile e verificabile | Wrapper PowerShell, packaging locale, sample generato, test | MVP personale | Completato |
| 190 | Prompt Packet Generator Release Smoke Workflow | Verificare il flusso locale completo del generatore | Smoke workflow locale, documento, test | MVP personale | Completato |
| 200 | Prompt Packet Lifecycle Checklist | Formalizzare il ciclo completo da task packet a step mergiato su main | Checklist lifecycle, template spuntabile, test | MVP personale | Completato |
| 210 | Prompt Packet Generator Developer Onboarding | Rendere il generatore e la checklist facili da adottare da un operatore locale | Guida onboarding, mappa strumenti, quickstart, troubleshooting | MVP personale | Completato |
| 220 | Project Workflow Index | Rendere navigabile il metodo operativo completo | Indice workflow, mappa documenti, entry point operativi | MVP personale | Completato |
| 230 | Workflow Health Check | Controllare coerenza minima dei documenti operativi centrali | Health check documentale, test su link/keyword, runbook leggero | MVP personale | Completato |
| 240 | Workflow Quick Reference | Offrire una pagina breve di comandi e sequenze operative | Quick reference, comandi essenziali, checklist breve | MVP personale | Completato |
| 250 | Step Closure Report | Standardizzare il report post-merge e la chiusura operativa dello step | Template/report di chiusura, handoff prossimo step | MVP personale | Completato |
| 260 | Workflow Command Cookbook | Raccogliere comandi operativi per scenari ricorrenti senza automatizzare Git | Cookbook manuale, esempi sicuri, troubleshooting comandi | MVP personale | Completato |
| 270 | Workflow Status Dashboard | Rendere visibile lo stato degli step senza automatizzare Git/GitHub | Documento e script dashboard locale read-only | MVP personale | Completato |
| 280 | Release Readiness | Definire readiness per pilot interno local-first su progetto reale | Checklist GO/WARNING/NO-GO, template readiness, limiti no-release pubblica | MVP personale | Completato |
| 290 | Existing Project Pilot Onboarding | Preparare l'applicazione del metodo a un progetto reale gia' avviato | Intake progetto, fotografia repo, rischi, primo step pilota | MVP personale | Completato |
| 300 | ASF Next Step Runner | Preparare localmente il prossimo step senza saltare i gate umani | Runner prepare mode, handoff Codex, report, validazione Lite/Strict | MVP personale | Completato |
| 310 | ASF Next Step Runner Project Profiles | Aggiungere profili progetto riusabili per il runner | Config profili, override manuali, note safety, test | MVP personale | Completato |
| 320 | ASF Runner Codex Handoff Improvements | Migliorare handoff e task packet generati dal runner | Handoff FASE 1/FASE 2, stato Git, note safety, template evoluto | MVP personale | Completato |
| 330 | ASF Runner Verification Pack | Rafforzare verifiche e report del runner senza CI automatica | Verification pack locale, controlli consigliati, runbook | MVP personale | Completato |
| 340 | ASF Runner Verification Pack Hardening | Rafforzare output e controlli del Verification Pack dopo uso reale | Pre/Post Codex checks, report checks, PR/LF handling, human gates | MVP personale | Completato |
| 350 | ASF Codex Report Intake | Leggere report Codex salvati e produrre intake report read-only | Script intake, template, PASS/WARNING/FAIL, test | MVP personale | Completato |
| 360 | ASF Human-Gated Closure Pack | Generare pacchetto chiusura manuale senza eseguire comandi Git/GitHub | Closure pack Markdown, template human-gated, test | MVP personale | Completato |
| 370 | ASF Runner Human Approval Gate | Rafforzare gate umano prima di preview, closure e pubblicazione manuale | Approval gate GO/WARNING/HOLD/NO-GO, evidenze Git, report Markdown | MVP personale | Completato |
| 380 | ASF Runner Codex Invocation Design | Documentare livelli e limiti della futura invocazione Codex controllata | Design livelli 0-5, sandbox, input/output e stop condition | MVP personale | Completato |
| 390 | ASF Runner Codex Invocation Dry Run Pack | Generare preview dry-run di futura invocazione Codex senza eseguirla | Dry-run Markdown, preview PowerShell inertizzata, test | MVP personale | Completato |
| 400 | ASF Codex Invocation Read-Only Prototype | Primo prototipo di invocazione Codex solo read-only e human-approved | Preview default, execute-readonly controllato, stdout/stderr, exit code, report | MVP personale | Completato |
| 410 | ASF Codex Invocation Result Capture | Normalizzare output di una invocazione Codex read-only | Capture PASS/WARNING/FAIL, stdout/stderr summary, stato Git target | MVP personale | Completato |
| 420 | ASF Codex Read-Only Safety Gate | Valutare se le evidenze read-only permettono solo design futuro | Safety gate GO_TO_WORKSPACE_WRITE_DESIGN/WARNING/HOLD/NO_GO | MVP personale | Completato |
| 430 | ASF Codex Read-Only Invocation First Manual Trial | Eseguire una prima prova manuale read-only controllata | Trial locale preview-only, capture simulato e safety gate su controllo pulito | MVP personale | Completato |
| 440 | ASF Codex Read-Only Invocation Clean Target Trial | Ripetere il trial su target pulito con branch/gate coerenti | Trial read-only reale su repo tmp, exit 0, target CLEAN, safety gate WARNING | MVP personale | Completato |
| 450 | ASF Codex Read-Only Invocation Repeatable Trial Pack | Rendere ripetibile il trial e gestire meglio errori ambientali | Pack ripetibile, compare trial, CODEX_NOT_AVAILABLE, report e test | MVP personale | Completato |
| 460 | ASF Codex Read-Only Invocation Diagnostics Hardening | Consolidare diagnostica stderr/output incompleto prima di step piu' ampi | Hardening diagnostico, criteri run comparabili, retry/stop piu' chiari | MVP personale | Da fare |
| 470 | Reserved | Numero non assegnato nello stato corrente | Nessun deliverable attivo | N/A | Superato |
| 480 | MCP Tool Registry | Registro tool e permessi | Tool registry L0-L4 | SaaS-ready | Da fare |
| 490 | ASF PowerShell Command Pack Skill Hardening | Rafforzare la skill comune per command pack PowerShell robusti | Skill esterna aggiornata, template `.ps1`, esempi, documento STEP 490 | MVP personale | Completato |
| 500 | OpenAI API Adapter | Creare adapter dry-run/mock per payload Responses-style senza chiamate live | Script adapter, doc, template, test, JSON evidence | SaaS-ready | Completato |
| 510 | OpenAI API Adapter Live Boundary and Credential Gate | Definire confine live e gate credenziali senza esporre secret | Credential gate, stop conditions, live boundary documentato | SaaS-ready | Completato |
| 520 | OpenAI API Adapter First Controlled Live Smoke Test | Eseguire una prima prova live controllata solo dopo gate umano esplicito | Live smoke test controllato, evidenza redatta, stop conditions | SaaS-ready | Completato |
| 530 | OpenAI API Adapter Live Smoke Result Hardening | Rafforzare parsing, classificazioni e report della smoke live dopo il primo test controllato | Schema risultato live, classificazioni, artifact sicuri, test mockati | SaaS-ready | Completato |
| 535 | Codex Prompt Clean-First Workflow Update | Chiarire il default ChatGPT -> Codex con prompt pulito separato da Bridge, intake gate e pubblicazione | Regola operativa, richiami workflow, test documentale | MVP personale | Completato |
| 536 | PowerShell Command Pack Safe Bootstrap Hardening | Rafforzare command pack e publication pack contro incolla fragile, here-string annidate, DOCX rumoroso e push diretto a main | Safe bootstrap, template, PR-first, test documentale | MVP personale | Completato |
| 540 | OpenAI API Adapter Controlled Live Execution Pack | Preparare un pack separato per eventuale futura esecuzione live controllata | Dry-run default, doppio consenso, artifact safe, runbook, template operatore | SaaS-ready | Completato |
| 545 | PowerShell Command Pack Skill Finalization | Finalizzare lo standard command pack come skill/istruzione canonica riusabile | README template, skill draft, parser Git robusto, ArgList, test guardrail | MVP personale | Completato |
| 546 | Export/Install as-common-pwsh-command-pack Skill | Trasformare il draft in export installabile con installer dry-run/apply e guardrail | Export folder, installer, runbook, test guardrail | MVP personale | Completato |
| 548 | Git Line Endings Warning Cleanup | Diagnosticare e mitigare warning LF/CRLF con policy repository-level controllata | `.gitattributes`, documento STEP 548, test guardrail | MVP personale | Completato |
| 550 | LAST Deprecation and 4-Digit Artifact Naming Standard | Deprecare `LAST-*` e standardizzare artefatti progressivi `NNNN-II-Tipo_Nome.ext` | Documento standard, utility migrazione dry-run/apply, template e test aggiornati | MVP personale | Completato |
| 560 | OpenAI API Adapter First Authorized Live Run | Eseguire una prima live reale futura solo con autorizzazione esplicita di Alberto | Wrapper autorizzato, report provider-side `BLOCKED_BY_RATE_LIMIT_OR_QUOTA`, diagnostic pack 0560-03, nessuna evidence positiva | SaaS-ready | Bloccato da provider |
| 570 | ASF Supervised Gate Autonomy ADR and MVP Motor Roadmap | Formalizzare autonomia supervisionata a gate, roadmap MVP Motore, loop spec e nodo review indipendente | ADR, roadmap motore, loop spec, independent review node | MVP Motore | Completato |
| 580 | Dry-run Loop Runner | Creare il primo runner che attraversa il loop senza modificare target repository | Runner dry-run, state log, gate summary sotto `tmp/` | MVP Motore | Completato |
| 590 | Stable PowerShell Publish Runner | Stabilizzare pubblicazione step con runner PowerShell versionato e gate espliciti | Runner publish FASE A/B/C, config JSON, output Bridge | MVP Motore | Completato |
| 600 | Risk Classifier + Gate Policy | Rendere deterministica la classificazione L0-L4 e la decisione fail-closed | Risk classifier, gate policy, test L0-L4, esempi JSON | MVP Motore | Completato |
| 610 | Risk Classifier Integration with Dry-run Loop Runner | Collegare il classifier al checkpoint RISK_CLASSIFY del runner 0580 | Integrazione leggera, risk report stabile, test regressione runner | MVP Motore | Completato |
| 620 | Gate Decision Report and Human Approval Packet | Rendere esplicito il pacchetto di decisione umana usando risk report e review dry-run | Report gate, schema human approval, fixture PASS/FAIL/NEEDS_HUMAN | MVP Motore | Completato |
| 630 | Verification Profile Selector + Test Cost Policy | Definire profili di verifica per ridurre ridondanze senza ridurre sicurezza | Selector CLI, matrice profili, policy costi test, esempi JSON e test | MVP Motore | Completato |
| 640 | Verification Profile Integration with Publish Runner | Integrare il selector nel runner 0590 senza ridurre gate o safety | Uso profili in Phase B/C, dedup check prudente, fail-closed | MVP Motore | Completato |
| 650 | Verification Profile Driven Publish Config Generator | Generare bozze config publish coerenti con profilo, rischio e file modificati | Config generator dry-run, esempi e test | MVP Motore | Completato |
| 660 | Publish Config Generator Bridge Output Integration | Salvare output generator e riepiloghi in un flusso Bridge/audit dedicato senza pubblicare | Bridge output per config generator, audit trail, LAST config e test | MVP Motore | Completato |
| 670 | Step Execution State Machine | Modellare stati, transizioni, stop condition e ripresa controllata del ciclo step | State machine locale, stati auditabili, nessuna pubblicazione automatica | MVP Motore | Da fare |

---

## 3. STEP 010 — Visione e contesto

### Obiettivo

Rendere il progetto comprensibile senza dover rileggere tutta la chat.

### Stato

Completato.

---

## 4. STEP 020 — Repository Genesis

### Obiettivo

Creare lo scheletro completo del repository.

### Stato

Completato.

---

## 5. STEP 030 — Safety Model

### Obiettivo

Formalizzare sicurezza e approval policy.

### Stato

Completato.

---

## 6. STEP 040 — Prompt Packet Generator

### Obiettivo

Rendere standard e riutilizzabili i prompt.

### Stato

Completato.

---

## 7. STEP 050 — GitHub Workflow

### Obiettivo

Rendere operativo il flusso GitHub completo.

### Output realizzati

- issue policy;
- branch naming policy;
- commit policy;
- PR policy;
- merge policy;
- branch protection checklist;
- release/tag policy;
- checklist STEP 050;
- test automatici leggeri sulla struttura GitHub.

### Criterio di completamento

Completato quando il workflow GitHub è documentato, i template GitHub sono verificati dai test, la roadmap e il changelog sono aggiornati e la PR è aperta senza merge automatico.

### Stato

Completato nello STEP 050.

---

## 8. STEP 060 — Codex Workflow

### Obiettivo

Rendere operativo il flusso Codex CLI/Codex Cloud.

### Output realizzati

- differenza tra Codex CLI locale e Codex Web/Cloud;
- modalita' Ask/Suggest, Auto Edit controllato, Review e Repair;
- divieto di Full Auto salvo sandbox esplicita;
- regole no commit/no push/no merge;
- output finale obbligatorio di Codex;
- procedura locale standard collegata al GitHub Workflow STEP 050;
- checklist STEP 060;
- esempio task packet STEP 060;
- test automatici leggeri sul workflow Codex.

### Criterio di completamento

Completato quando il workflow Codex e' documentato, i prompt includono i guardrail minimi, checklist ed esempio STEP 060 sono presenti, i test verificano le sezioni chiave e roadmap, changelog e TREE sono aggiornati.

### Stato

Completato nello STEP 060.

---

## 9. STEP 070 — Verification Gate

### Obiettivo

Definire cosa significa "verificato".

### Output realizzati

- test automatici;
- `git diff --check`;
- controllo `git status --short`;
- verifica template e policy principali;
- checklist manuale;
- CI GitHub allineata al gate;
- output standard di verifica;
- script locale `scripts/verify.ps1`;
- documento `docs/20_VERIFICATION_GATE.md`.

### Criterio di completamento

Completato quando il gate locale e quello CI eseguono i controlli minimi, la PR template include la checklist di verifica, i documenti di workflow rimandano al gate e i test automatici proteggono la struttura.

### Stato

Completato nello STEP 070.

---

## 10. STEP 080 — Documentation Sync

### Obiettivo

Evitare disallineamento tra codice e documentazione.

### Output realizzati

- regole aggiornamento docs;
- changelog policy;
- decision log policy;
- roadmap update checklist;
- classi documentali always check / update when relevant / do not touch unless needed;
- integrazione nel Verification Gate;
- test automatici leggeri sul Documentation Sync.

### Future evolutions

- lint/format gate;
- security scan gate;
- prompt packet hardening.

### Criterio di completamento

Completato quando la regola Documentation Sync e' documentata, i workflow principali la richiamano, il PR template la include e i test verificano i riferimenti minimi.

### Stato

Completato nello STEP 080.

---

## 11. STEP 090 — Branch Protection Policy

### Obiettivo

Definire quando e come attivare branch protection e required status checks senza automatismi rischiosi.

### Output realizzati

- policy branch protection;
- required status checks;
- regole per force push e delete branch;
- rollout manuale;
- rollback e safe stop;
- criteri per non configurare automaticamente protezioni nello step sbagliato.
- distinzione tra branch protection rules e rulesets;
- livello minimo raccomandato per `main`;
- test automatici leggeri sulla policy.

### Future evolutions

- Lint and Formatting Gate;
- Security Scan Gate;
- Prompt Packet Hardening;
- Ruleset Hardening.

### Criterio di completamento

Completato quando la policy e' documentata, i workflow principali rimandano al documento, il changelog e il decision log sono aggiornati e i test verificano i riferimenti minimi.

### Stato

Completato nello STEP 090.

---

## 12. STEP 100 — Branch Protection Implementation

### Obiettivo

Preparare strumenti locali e runbook per applicare la Branch Protection Policy dopo approvazione esplicita.

### Output realizzati

- scelta tra ruleset e branch protection classica;
- verifica permessi GitHub;
- identificazione del nome esatto del check CI;
- script DryRun per applicazione branch protection classica;
- script read-only per rilevare check candidati;
- script read-only per verifica branch protection;
- runbook `docs/23_BRANCH_PROTECTION_IMPLEMENTATION.md`;
- test automatici leggeri su script e documentazione.

### Future evolutions

- rulesets;
- lint/format gate;
- security scan gate;
- prompt packet hardening.

### Criterio di completamento

Completato quando script e runbook sono presenti, safe-by-default, verificati dai test e collegati a workflow, Verification Gate, Documentation Sync e decision log.

### Stato

Completato nello STEP 100.

---

## 13. STEP 110 — Branch Protection Verification and Hardening

### Obiettivo

Verificare la disponibilita' reale della branch protection e definire il fallback operativo quando GitHub non puo' imporla.

### Output realizzati

- required check CI reale confermato: `Verification Gate`;
- limite GitHub plan documentato per repository privato con HTTP 403;
- soft protection policy introdotta come fallback;
- script `verify_branch_protection.ps1` migliorato per gestire HTTP 403 con exit code `2`;
- script `apply_branch_protection.ps1` rafforzato con warning prima di `-Apply`;
- workflow, Verification Gate, Codex Workflow, decision log e changelog aggiornati.

---

## 14. STEP 120 — Soft Protection Guardrails

### Obiettivo

Ridurre il rischio operativo mentre la hard protection GitHub non e' disponibile sul repository privato.

### Output realizzati

- guardrail locali contro push accidentale su `main`;
- hook versionati in `.githooks/`;
- script `scripts/git/install_soft_guardrails.ps1` con `-DryRun`;
- script read-only `scripts/git/check_soft_guardrails.ps1`;
- documento `docs/24_SOFT_PROTECTION_GUARDRAILS.md`;
- bypass esplicito solo con `ASF_ALLOW_MAIN_BYPASS=1`;
- test automatici leggeri sui guardrail.

### Future evolutions

- GitHub Pro/Team upgrade;
- real branch protection activation;
- rulesets;
- lint/format gate;
- security scan gate.

---

## 15. STEP 130 — Prompt Packet Hardening

### Obiettivo

Rafforzare prompt e task packet affinche' i vincoli operativi recenti siano presenti prima dell'esecuzione Codex.

### Output realizzati

- task packet con richiami espliciti a soft guardrails, Documentation Sync e Verification Gate;
- prompt Codex allineati a no commit/no push/no merge e no hook install automatico;
- forbidden actions standard;
- allowed scope e forbidden scope espliciti;
- report finale Codex standard;
- documento `docs/25_PROMPT_PACKET_HARDENING.md`;
- test documentali leggeri.

### Future evolutions

- Prompt Packet Validation Lite;
- prompt packet schema;
- lint/format gate;
- security scan gate;
- GitHub Pro/Team decision;
- hard protection real activation;
- rulesets.

---

## 16. STEP 140 — Prompt Packet Validation Lite

### Obiettivo

Introdurre una validazione leggera dei task packet senza irrigidire ancora il formato con uno schema completo.

### Output realizzati

- controllo sezioni minime;
- verifica forbidden actions;
- verifica allowed/forbidden scope;
- verifica Verification Gate, Documentation Sync e Soft Protection awareness;
- verifica report finale Codex;
- script `scripts/validate_task_packet.py`;
- documento `docs/26_PROMPT_PACKET_VALIDATION_LITE.md`;
- test automatici leggeri;
- nessuna nuova dipendenza;
- nessuna integrazione automatica in CI o `scripts/verify.ps1`.

### Future evolutions

- modalita' strict;
- schema JSON/YAML;
- lint/format gate;
- security scan gate.

---

## 17. STEP 150 — Prompt Packet Examples and Golden Samples

### Obiettivo

Creare esempi validi e casi negativi controllati per rendere il validatore piu' utile senza irrigidire ancora il formato.

### Output realizzati

- task packet golden validi;
- esempi incompleti usati dai test;
- documentazione d'uso in `docs/27_PROMPT_PACKET_GOLDEN_SAMPLES.md`;
- test del validatore su campioni stabili;
- nessuna modalita' strict introdotta.

### Future evolutions

- report JSON;
- schema JSON/YAML;
- lint/format gate;
- security scan gate.

---

## 18. STEP 160 — Prompt Packet Validation Strict Mode

### Obiettivo

Introdurre una modalita' opzionale piu' severa per il validatore, senza rompere la validazione Lite.

### Output realizzati

- flag `--strict` nel validatore;
- controlli piu' granulari su branch, scope, forbidden actions, Verification Gate, Documentation Sync, Soft Protection e report finale;
- documento `docs/28_PROMPT_PACKET_VALIDATION_STRICT_MODE.md`;
- golden samples Strict valid/invalid;
- test automatici sul comportamento Strict;
- nessuna nuova dipendenza;
- nessuna integrazione automatica in CI o `scripts/verify.ps1`.

### Future evolutions

- report JSON;
- schema JSON/YAML;
- lint/format gate;
- security scan gate.

---

## 19. STEP 170 — Prompt Packet Generator CLI Hardening

### Obiettivo

Rafforzare il generatore CLI di prompt/task packet usando Lite, Strict e golden samples come riferimenti operativi.

### Output realizzati

- CLI piu' robusta;
- integrazione manuale con validatore;
- test su output generati;
- documento `docs/29_PROMPT_PACKET_GENERATOR_CLI_HARDENING.md`;
- nessuna nuova dipendenza;
- nessuna modifica a CI o `src/**`.

---

## 20. STEP 180 — Prompt Packet Generator Packaging

### Obiettivo

Rendere il generatore piu' riusabile mantenendo il modello local-first e senza introdurre complessita' prematura.

### Output realizzati

- wrapper PowerShell sottile `scripts/generate_task_packet.ps1`;
- documento `docs/30_PROMPT_PACKET_GENERATOR_PACKAGING.md`;
- sample generato e validabile in `examples/task_packets/generated/`;
- test automatici sul packaging locale;
- compatibilita' con Lite e Strict;
- nessuna pubblicazione PyPI/registry, nessuna nuova dipendenza, nessuna modifica a CI.

---

## 21. STEP 190 — Prompt Packet Generator Release Smoke Workflow

### Obiettivo

Rendere ripetibile la verifica end-to-end locale del generatore dopo modifiche a CLI, wrapper, sample e documentazione.

### Output realizzati

- script `scripts/smoke_prompt_packet_release.ps1`;
- documento `docs/31_PROMPT_PACKET_GENERATOR_RELEASE_SMOKE_WORKFLOW.md`;
- generazione temporanea sotto `tmp/`;
- validazione Lite e Strict del task packet generato;
- test automatici sullo smoke workflow;
- nessuna pubblicazione esterna, nessuna GitHub Release, nessuna modifica a CI.

---

## 22. STEP 200 — Prompt Packet Lifecycle Checklist

### Obiettivo

Formalizzare il ciclo operativo completo dal prompt packet allo step confermato su `main`.

### Output realizzati

- documento `docs/32_PROMPT_PACKET_LIFECYCLE_CHECKLIST.md`;
- template spuntabile `templates/codex_tasks/prompt_packet_lifecycle_checklist.md`;
- checklist per preparazione, validazione, esecuzione Codex, report, pre-commit, PR/merge, pull `main` e step successivo;
- troubleshooting per branch remoto assente, PR mancante, `main` non aggiornato e prerequisiti mancanti;
- anti-pattern operativi;
- test automatici leggeri.

---

## 23. STEP 210 — Prompt Packet Generator Developer Onboarding

### Obiettivo

Rendere il generatore piu' facile da adottare e usare in modo coerente da un operatore locale.

### Output realizzati

- guida onboarding `docs/33_PROMPT_PACKET_GENERATOR_DEVELOPER_ONBOARDING.md`;
- mappa degli strumenti del Prompt Packet Generator;
- quickstart PowerShell per generazione, Lite Mode, Strict Mode e smoke workflow;
- ruoli e responsabilita' di ChatGPT, Codex e Alberto;
- errori comuni e troubleshooting operativo;
- test automatici leggeri.

---

## 24. STEP 220 — Project Workflow Index

### Obiettivo

Rendere navigabile il metodo operativo completo senza dover conoscere tutta la storia degli step.

### Output realizzati

- indice centrale `docs/34_PROJECT_WORKFLOW_INDEX.md`;
- mappa rapida "devo fare X";
- elenco documenti, script e template principali;
- sequenze operative PowerShell non distruttive;
- troubleshooting rapido e anti-pattern;
- test automatici leggeri.

---

## 25. STEP 230 — Workflow Health Check

### Obiettivo

Controllare che i documenti operativi centrali restino navigabili e coerenti dopo l'espansione del workflow.

### Output realizzati

- script read-only `scripts/check_workflow_health.py`;
- documento `docs/35_WORKFLOW_HEALTH_CHECK.md`;
- controlli su documenti, script, template, riferimenti e safety scan degli script workflow;
- integrazione nell'indice `docs/34_PROJECT_WORKFLOW_INDEX.md`;
- test automatici leggeri;
- nessuna integrazione in CI o `scripts/verify.ps1`.

---

## 26. STEP 240 — Workflow Quick Reference

### Obiettivo

Creare una pagina breve con i comandi operativi essenziali per il workflow locale.

### Output realizzati

- documento `docs/36_WORKFLOW_QUICK_REFERENCE.md`;
- comandi rapidi per generazione task packet, validazione Lite/Strict, smoke workflow, Workflow Health Check, Verification Gate e soft guardrails;
- sequenze manuali per pre-commit, PR checks, merge presidiato e verifica finale su `main`;
- collegamento a Project Workflow Index, Workflow Health Check, Lifecycle Checklist e documenti di validazione;
- test automatici leggeri;
- nessuna automazione commit/push/PR/merge.

---

## 27. STEP 250 — Step Closure Report

### Obiettivo

Standardizzare il riepilogo post-merge e la conferma che uno step sia davvero chiuso su `main` prima di avviare il successivo.

### Output realizzati

- documento `docs/37_STEP_CLOSURE_REPORT.md`;
- template compilabile `templates/codex_tasks/step_closure_report_template.md`;
- stati ufficiali da "Completato localmente" a "Chiuso e verificato su main";
- gestione del caso `gh pr checks --watch` senza check disponibili;
- collegamento a Workflow Quick Reference, Lifecycle Checklist e Project Workflow Index;
- test automatici leggeri;
- nessuna automazione commit/push/PR/merge.

---

## 28. STEP 260 — Workflow Command Cookbook

### Obiettivo

Raccogliere comandi manuali e sicuri per scenari operativi ricorrenti del workflow senza creare script che automatizzano commit, push, PR o merge.

### Output realizzati

- documento `docs/38_WORKFLOW_COMMAND_COOKBOOK.md`;
- ricette PowerShell/Git/Python per preparazione step, validazione, post-report Codex, PR checks, merge e verifica finale;
- troubleshooting per branch remoto assente, branch sbagliato, working tree sporca, health check fallito, Verification Gate fallito, riferimenti remoti vecchi e warning CRLF/LF;
- collegamento a Workflow Quick Reference, Step Closure Report e Project Workflow Index;
- test automatici leggeri;
- nessuna automazione commit/push/PR/merge.

---

## 29. STEP 270 — Workflow Status Dashboard

### Obiettivo

Rendere visibile lo stato degli step e del workflow senza introdurre automazioni Git/GitHub rischiose.

### Output realizzati

- script read-only `scripts/show_workflow_status.py`;
- documento `docs/39_WORKFLOW_STATUS_DASHBOARD.md`;
- output locale con branch corrente, working tree CLEAN/DIRTY, ultimi commit, documenti centrali e script principali;
- suggerimento dei prossimi controlli locali;
- integrazione in Workflow Health Check, Project Workflow Index, Quick Reference e Command Cookbook;
- test automatici leggeri;
- nessuna GitHub API, nessuna rete, nessuna automazione commit/push/PR/merge.

---

## 30. STEP 280 — Release Readiness

### Obiettivo

Definire quando AI Software Factory e' pronta per un pilot interno local-first su un progetto reale, anche gia' avviato, senza dichiarare readiness pubblica o SaaS.

### Output realizzati

- documento `docs/40_RELEASE_READINESS.md`;
- template spuntabile `templates/codex_tasks/release_readiness_checklist.md`;
- livelli di maturita' da Experimental a Public/SaaS ready;
- checklist GO/WARNING/NO-GO per pilot interno;
- criteri per progetti esistenti gia' a meta' sviluppo;
- primo step pilota consigliato piccolo, reversibile e non distruttivo;
- integrazione in Project Workflow Index, Workflow Health Check, Quick Reference, Command Cookbook e Workflow Status Dashboard;
- test automatici leggeri;
- nessuna GitHub Release, nessun PyPI, nessuna CI nuova, nessuna dichiarazione di readiness pubblica o SaaS.

---

## 31. STEP 290 — Existing Project Pilot Onboarding

### Obiettivo

Preparare l'applicazione del metodo a un progetto reale gia' avviato.

### Output realizzati

- Project Intake;
- fotografia branch, stato Git, test e documentazione;
- identificazione rischi e dati sensibili;
- scelta del primo step pilota sicuro;
- criteri di stop se il progetto non e' pronto;
- documento `docs/41_EXISTING_PROJECT_PILOT_ONBOARDING.md`;
- template `templates/codex_tasks/existing_project_intake_template.md`;
- template `templates/codex_tasks/first_pilot_step_packet_template.md`;
- test automatici leggeri;
- nessuna modifica a repository esterne, nessuna automazione cross-repository e nessun refactor massivo.

---

## 32. STEP 300 - ASF Next Step Runner

### Obiettivo

Preparare localmente il prossimo step del workflow senza saltare i gate umani.

### Output realizzati

- script `scripts/asf_next_step.py`;
- documento `docs/42_ASF_NEXT_STEP_RUNNER.md`;
- template `templates/codex_tasks/asf_next_step_runner_handoff_template.md`;
- output temporanei sotto `tmp/asf_next_step/`;
- generazione `task_packet.md`, `codex_handoff.md` e `runner_report.md`;
- validazione Lite e Strict del task packet generato;
- test automatici leggeri;
- nessuna invocazione Codex, nessuna modifica a repository target, nessuna automazione commit/push/PR/merge.

---

## 33. STEP 310 - ASF Next Step Runner Project Profiles

### Obiettivo

Aggiungere profili progetto locali per ridurre gli argomenti ripetitivi del runner.

### Output realizzati

- config `config/asf_project_profiles.json`;
- profili iniziali per `AI_Software_Factory` e `Family_Photo_Organizer`;
- supporto CLI `--profile` con override manuali;
- note safety, default forbidden notes e file consigliati da ispezionare;
- nessuna modifica automatica ai repository target;
- test su parsing, override, profilo mancante e JSON malformato.

---

## 34. STEP 320 - ASF Runner Codex Handoff Improvements

### Obiettivo

Migliorare il formato dell'handoff Codex prodotto dal runner.

### Output realizzati

- `codex_handoff.md` piu' completo;
- template handoff aggiornato;
- sezioni FASE 1 e FASE 2;
- stato Git target, prerequisito, scope incluso/escluso e note safety;
- richiesta esplicita di Step Closure Report;
- compatibilita' con Lite e Strict;
- nessuna invocazione automatica di Codex.

---

## 35. STEP 330 - ASF Runner Verification Pack

### Obiettivo

Rafforzare verifiche e report del runner senza integrare nuovi check in CI.

### Output realizzati

- generazione `verification_pack.md` sotto `tmp/asf_next_step/<project>/step_<step>/`;
- template `templates/codex_tasks/asf_runner_verification_pack_template.md`;
- controlli Pre-Codex e Post-Codex consigliati;
- riferimenti a Quick Reference, Command Cookbook e Step Closure Report;
- report runner aggiornato con path Verification Pack e stato handoff improvements;
- nessuna automazione commit/push/PR/merge.

---

## 36. STEP 340 - ASF Runner Verification Pack Hardening

### Obiettivo

Rafforzare Verification Pack e report del runner dopo uso reale su piu' profili.

### Output realizzati

- controlli Pre-Codex e Post-Codex rafforzati;
- scope checks e report checks;
- gestione PR checks non disponibili;
- gestione warning LF/CRLF;
- human gates per commit, push, PR e merge;
- nessuna integrazione CI;
- nessuna automazione commit/push/PR/merge.

---

## 37. STEP 350 - ASF Codex Report Intake

### Obiettivo

Leggere un report finale Codex salvato in Markdown e produrre un intake report locale.

### Output realizzati

- script `scripts/asf_codex_report_intake.py`;
- template `templates/codex_tasks/asf_codex_report_intake_template.md`;
- output `codex_report_intake.md` sotto `tmp/asf_codex_intake/`;
- classificazione PASS/WARNING/FAIL;
- lettura Git target read-only;
- nessuna approval automatica.

---

## 38. STEP 360 - ASF Human-Gated Closure Pack

### Obiettivo

Generare un pacchetto di chiusura step con comandi consigliati ma non eseguiti.

### Output realizzati

- script `scripts/asf_generate_closure_pack.py`;
- template `templates/codex_tasks/asf_human_gated_closure_pack_template.md`;
- output `closure_pack.md` sotto `tmp/asf_closure_pack/`;
- comandi manuali e human-gated;
- gestione `gh pr checks --watch`;
- Step Closure Report finale.

---

## 39. STEP 370 - ASF Runner Human Approval Gate

### Obiettivo

Rendere esplicita l'approvazione umana tra intake, verification pack, closure pack e futura preview Codex.

### Output realizzati

- script `scripts/asf_human_approval_gate.py`;
- documento `docs/49_ASF_HUMAN_APPROVAL_GATE.md`;
- template `templates/codex_tasks/asf_human_approval_gate_template.md`;
- decisione `GO`, `WARNING`, `HOLD` o `NO-GO`;
- lettura Git target read-only;
- output `human_approval_gate.md` sotto `tmp/asf_approval_gate/`;
- nessuna automazione commit/push/PR/merge.

---

## 40. STEP 380 - ASF Runner Codex Invocation Design

### Obiettivo

Documentare il design della futura invocazione Codex controllata.

### Output realizzati

- documento `docs/50_ASF_CODEX_INVOCATION_DESIGN.md`;
- livelli 0-5 di invocazione;
- regole sandbox read-only, workspace-write e divieto danger-full-access;
- input, output e stop condition;
- chiarimento che `codex exec` non viene eseguito in questo step.

---

## 41. STEP 390 - ASF Runner Codex Invocation Dry Run Pack

### Obiettivo

Generare un pacchetto dry-run per futura invocazione Codex controllata.

### Output realizzati

- script `scripts/asf_codex_invocation_dry_run.py`;
- documento `docs/51_ASF_CODEX_INVOCATION_DRY_RUN_PACK.md`;
- template `templates/codex_tasks/asf_codex_invocation_dry_run_template.md`;
- output `codex_invocation_dry_run.md` e `codex_exec_preview.ps1` sotto `tmp/asf_codex_invocation/`;
- preview `codex exec` solo come testo, marcata dry-run e manual review required.

---

## 42. STEP 400 - ASF Codex Invocation Read-Only Prototype

### Obiettivo

Verificare una prima invocazione Codex controllata in sola analisi read-only.

### Output realizzati

- script `scripts/asf_codex_readonly_invoke.py`;
- documento `docs/52_ASF_CODEX_READONLY_INVOCATION_PROTOTYPE.md`;
- template `templates/codex_tasks/asf_codex_readonly_invocation_template.md`;
- modalita' `preview` default senza invocazione Codex;
- modalita' `execute-readonly` solo con conferma esplicita, approval gate `GO`, working tree `CLEAN` e sandbox read-only;
- output sotto `tmp/asf_codex_readonly_invocation/`;
- nessuna esecuzione Codex nei test dello step.

---

## 43. STEP 410 - ASF Codex Invocation Result Capture

### Obiettivo

Normalizzare stdout, stderr, exit code e report di una invocazione Codex read-only.

### Output realizzati

- script `scripts/asf_codex_result_capture.py`;
- documento `docs/53_ASF_CODEX_INVOCATION_RESULT_CAPTURE.md`;
- template `templates/codex_tasks/asf_codex_invocation_result_capture_template.md`;
- output `codex_result_capture.md` sotto `tmp/asf_codex_result_capture/`;
- classificazione `PASS`, `WARNING` o `FAIL`;
- lettura Git target read-only.

---

## 44. STEP 420 - ASF Codex Read-Only Safety Gate

### Obiettivo

Valutare se un result capture read-only e' sufficiente per progettare uno step futuro piu' ampio.

### Output realizzati

- script `scripts/asf_codex_readonly_safety_gate.py`;
- documento `docs/54_ASF_CODEX_READONLY_SAFETY_GATE.md`;
- template `templates/codex_tasks/asf_codex_readonly_safety_gate_template.md`;
- output `readonly_safety_gate.md` sotto `tmp/asf_codex_readonly_safety_gate/`;
- decisioni `GO_TO_WORKSPACE_WRITE_DESIGN`, `WARNING_REVIEW_REQUIRED`, `HOLD` e `NO_GO`;
- chiarimento che il gate non autorizza direttamente workspace-write.

---

## 45. STEP 430 - ASF Codex Read-Only Invocation First Manual Trial

### Obiettivo

Eseguire una prima prova manuale read-only controllata usando il prototipo 400-420.

### Output realizzati

- documento procedura `docs/55_ASF_CODEX_READONLY_FIRST_MANUAL_TRIAL.md`;
- documento risultati `docs/56_ASF_CODEX_READONLY_FIRST_TRIAL_RESULTS.md`;
- runner prepare per step fittizio 440 sotto `tmp/`;
- Human Approval Gate con decisione `HOLD`, che blocca correttamente `execute-readonly`;
- preview read-only generata senza eseguire Codex;
- result capture su output simulati;
- safety gate validato anche su controllo pulito temporaneo;
- nessuna modifica automatica a repository target.

---

## 46. STEP 440 - ASF Codex Read-Only Invocation Clean Target Trial

### Obiettivo

Ripetere il trial read-only su target pulito, con branch atteso coerente e Human Approval Gate `GO` prima di valutare qualunque `execute-readonly`.

### Output realizzati

- documento procedura `docs/57_ASF_CODEX_READONLY_CLEAN_TARGET_TRIAL.md`;
- documento risultati `docs/58_ASF_CODEX_READONLY_CLEAN_TARGET_TRIAL_RESULTS.md`;
- repo Git temporanea sintetica sotto `tmp/asf_clean_target_trial/step_440/clean_repo`;
- Human Approval Gate `GO`;
- preview read-only generata;
- `execute-readonly` reale con sandbox read-only, exit code `0` e target rimasto `CLEAN`;
- result capture `PASS`;
- safety gate `WARNING_REVIEW_REQUIRED` per stderr non vuoto e output Codex incompleto;
- nessuna autorizzazione workspace-write.

---

## 47. STEP 450 - ASF Codex Read-Only Invocation Repeatable Trial Pack

### Obiettivo

Rendere ripetibile il clean target trial e distinguere in modo piu' chiaro limiti ambientali, stderr non vuoto e output incompleti.

### Output realizzati

- script `scripts/asf_codex_readonly_repeatable_trial.py`;
- script `scripts/asf_codex_readonly_trial_compare.py`;
- documenti `docs/59_ASF_CODEX_READONLY_REPEATABLE_TRIAL_PACK.md` e `docs/60_ASF_CODEX_READONLY_REPEATABLE_TRIAL_RESULTS.md`;
- template repeatable trial e trial compare;
- repo sintetica temporanea sotto `tmp/asf_codex_readonly_repeatable_trials/<trial-name>/target_repo`;
- modalita' `prepare-only` default;
- modalita' `run-readonly-if-safe` con conferma esplicita, approval gate GO e target CLEAN;
- gestione `CODEX_NOT_AVAILABLE` senza modificare il target;
- compare tra report trial;
- test automatici per script, documenti e riferimenti health check;
- nessuna autorizzazione workspace-write.

---

## 48. STEP 460 - ASF Codex Read-Only Invocation Diagnostics Hardening

### Obiettivo

Consolidare diagnostica, confronto run e criteri di retry/stop per stderr non vuoto, output incompleto e disponibilita' Codex prima di qualunque step piu' ampio.

### Output previsti

- diagnostica piu' granulare su stderr/output incompleto;
- criteri di ripetizione trial;
- separazione piu' chiara tra ambiente non disponibile, warning Codex e failure target;
- nessuna autorizzazione workspace-write.

---

## 49. STEP 470 - Reserved

### Obiettivo

Numero non assegnato nello stato corrente.

### Output

- nessun deliverable attivo;
- nessun branch operativo associato.

---

## 50. STEP 480 - MCP Tool Registry

### Obiettivo

Gestire tool esterni in modo sicuro.

### Output previsti

- registry tool;
- permessi L0-L4;
- approval policy;
- read-only first.

---

## 51. STEP 490 - ASF PowerShell Command Pack Skill Hardening

### Obiettivo

Rafforzare la skill comune `as-common-pwsh-command-pack` per generare command pack PowerShell robusti, loggati e verificabili.

### Output realizzati

- skill esterna aggiornata in `%USERPROFILE%\.agents\skills\as-common-pwsh-command-pack`;
- `SKILL.md` compatto con frontmatter YAML valido;
- riferimento operativo `references/pwsh-command-pack-standard.md`;
- template robusto `references/pwsh-command-pack-template.ps1`;
- esempi progressivi `examples/demo-prompts.md`;
- documento `docs/64_ASF_PWSH_COMMAND_PACK_SKILL_HARDENING.md`;
- nessuna pubblicazione automatica e nessuna modifica a repository target esterni.

---

## 52. STEP 500 - OpenAI API Adapter

### Obiettivo

Creare una base standard-library-only per costruire payload Responses-style, validare impostazioni, controllare readiness ambiente senza leak di secret e produrre evidenza JSON dry-run/mock.

### Output realizzati

- script `scripts/asf_openai_api_adapter.py`;
- documento `docs/65_ASF_OPENAI_API_ADAPTER.md`;
- template `templates/codex_tasks/asf_openai_api_adapter_template.md`;
- test unitari e documentali;
- modalita' `check-env`, `dry-run`, `mock`;
- placeholder `live` fail-closed;
- nessuna chiamata live OpenAI API;
- nessun SDK OpenAI o nuova dipendenza.

Prossimo step consigliato:

```text
510) OpenAI API Adapter Live Boundary and Credential Gate
```

---

## 53. STEP 510 - OpenAI API Adapter Live Boundary and Credential Gate

### Obiettivo

Definire il confine per una futura integrazione live e il gate credenziali senza esporre secret e senza trasformare il mock/dry-run in produzione.

### Output realizzati

- credential gate su presenza boolean di `OPENAI_API_KEY`;
- live boundary con `ASF_OPENAI_LIVE_ENABLED=1`, `--allow-live` e conferma esplicita;
- decisioni deterministiche per gate mancanti e readiness futura;
- live request plan no-network per `/v1/responses`;
- documento `docs/66_ASF_OPENAI_API_ADAPTER_LIVE_BOUNDARY_CREDENTIAL_GATE.md`;
- template `templates/codex_tasks/asf_openai_api_live_boundary_gate_template.md`;
- test unitari e documentali;
- nessuna chiamata live OpenAI API;
- nessun SDK OpenAI o nuova dipendenza.

Prossimo step consigliato:

```text
520) OpenAI API Adapter First Controlled Live Smoke Test
```

---

## 54. STEP 520 - OpenAI API Adapter First Controlled Live Smoke Test

### Obiettivo

Eseguire una prima prova live controllata dell'adapter OpenAI solo dopo gate umano esplicito, credenziali locali, stop conditions e redazione verificata.

### Output realizzati

- comando preflight `--gate-only`;
- comando smoke test live con massimo una richiesta Responses API;
- payload live con `store: false`, prompt tiny e output massimo 32 token;
- evidenza JSON redatta sotto `tmp/`;
- classificazione errori API/network/output;
- nessuna esposizione di secret;
- test default ancora senza credenziali reali o network.

Prossimo step consigliato:

```text
530) OpenAI API Adapter Live Smoke Result Hardening
```

---

## 55. STEP 530 - OpenAI API Adapter Live Smoke Result Hardening

### Obiettivo

Rafforzare parsing, classificazioni, report e casi limite della live smoke dopo il primo test controllato.

### Output realizzati

- schema risultato live stabile con `status`, `classification`, `safe_details`, `provider`, `model`, `live_enabled`, `credential_present`, `duration_ms` e `timestamp`;
- classificazioni granulari per gate, provider, rete, auth, rate limit, schema e unknown error;
- artifact JSON machine-readable e Markdown operatore opzionale, entrambi redatti;
- test mockati per tutti i casi minimi senza rete e senza credenziali reali;
- nessun allargamento verso integrazione produttiva e nessuna chiamata live reale.

---

## 56. STEP 535 - Codex Prompt Clean-First Workflow Update

### Obiettivo

Chiarire il flusso ChatGPT -> Codex stabilendo che il default e' un prompt Codex pulito, autosufficiente e direttamente copiabile, separato da PowerShell, Bridge, intake gate e pubblicazione.

### Output realizzati

- regola clean-first in `AGENTS.md` e `docs/08_CODEX_WORKFLOW.md`;
- tabella livelli per prompt Codex pulito, Codex command pack PowerShell, intake gate, pwsh/publication command pack e Codex;
- richiami brevi in Project Workflow Index, Workflow Quick Reference, Workflow Command Cookbook e documento PowerShell Command Pack;
- conferma la separazione da Bridge Dropbox / ChatGPT Bridge e audit trail, poi aggiornata dallo STEP 0550 con artefatti progressivi senza `LAST-*`;
- conferma che Codex lascia il working tree modificato e non fa commit, push, PR, merge o deploy salvo richiesta esplicita;
- test documentale a protezione della regola operativa.

---

## 57. STEP 536 - PowerShell Command Pack Safe Bootstrap Hardening

### Obiettivo

Rafforzare il PowerShell Command Pack / publication pack ASF per evitare blocchi interattivi, esecuzioni parziali, here-string annidate, DOCX fragile, output compatti vuoti e push diretto a `main`.

### Output realizzati

- standard Safe Bootstrap: bootstrap corto, script `.ps1` completo, parse-check con `[scriptblock]::Create(...)`, esecuzione via `pwsh -File`;
- divieto di here-string annidate, logica Git complessa, DOCX XML, `else` esterni e `finally` fragile nel bootstrap incollato;
- template ASF per bootstrap e script command pack;
- regola PR-first per pubblicare verso `main`, incluso il caso `main...origin/main [ahead N]`;
- DOCX best-effort non bloccante quando TXT/MD sono prodotti correttamente;
- output compatto costruito con array di righe o builder sicuro e fallback non vuoto;
- test documentale a protezione dello standard.

---

## 58. STEP 540 - OpenAI API Adapter Controlled Live Execution Pack

### Obiettivo

Preparare un pack separato per eventuale futura esecuzione live controllata, solo con autorizzazione esplicita.

### Output realizzati

- script `scripts/asf_openai_controlled_live_execution_pack.py`;
- runbook `docs/69_ASF_OPENAI_API_ADAPTER_CONTROLLED_LIVE_EXECUTION_PACK.md`;
- template PowerShell operatore `templates/pwsh_command_pack/step_540_openai_controlled_live_execution_pack_template.ps1`;
- dry-run default senza rete;
- doppio consenso per live futuro con `ASF_OPENAI_LIVE_ENABLED=1` e `--confirm-live-openai`;
- artifact JSON/Markdown sotto `tmp/`;
- stop conditions, no retry automatico, no loop e no chiamate parallele;
- test mockati senza rete e senza chiavi reali.

---

## 59. STEP 545 - PowerShell Command Pack Skill Finalization

### Obiettivo

Finalizzare lo standard PowerShell Command Pack come skill/istruzione canonica riusabile per i prossimi step ASF e per i progetti di Alberto.

### Output realizzati

- documento `docs/70_ASF_PWSH_COMMAND_PACK_SKILL_FINALIZATION.md`;
- README template `templates/pwsh_command_pack/README.md`;
- skill draft esportabile `templates/pwsh_command_pack/as-common-pwsh-command-pack-SKILL.md`;
- template canonici aggiornati con `ArgList`, file prefix a 4 cifre, parser Git robusto e clipboard best-effort;
- guardrail su PR-first, DOCX best-effort, warning LF/CRLF e divieto di `$Args` come parametro;
- test automatici per standard e parse-check.

---

## 60. STEP 546 - Export/Install as-common-pwsh-command-pack Skill

### Obiettivo

Trasformare la skill draft dello STEP 545 in una struttura realmente installabile, verificabile e riusabile senza scrivere in cartelle esterne durante lo step ASF.

### Output realizzati

- export installabile `templates/pwsh_command_pack/export/as-common-pwsh-command-pack/SKILL.md`;
- installer dry-run/apply `scripts/install_pwsh_command_pack_skill.py`;
- documento `docs/71_ASF_PWSH_COMMAND_PACK_SKILL_EXPORT_INSTALL.md`;
- guardrail su target esplicito, no write in dry-run, backup prima di overwrite, no cancellazioni e no cross-repo write;
- test automatici su export, contenuti standard, installer e documentazione.

---

## 61. STEP 548 - Git Line Endings Warning Cleanup

### Obiettivo

Diagnosticare e mitigare i warning Git LF/CRLF della repository senza modificare configurazione globale, senza normalizzazione massiva e senza azioni Git remote.

### Output realizzati

- policy `.gitattributes` repository-level per file sorgente, documentazione, configurazione, template e script Windows;
- documento `docs/72_ASF_GIT_LINE_ENDINGS_WARNING_CLEANUP.md`;
- riferimento esplicito a `templates/test_plans/test_plan_template.md` con `eol=lf`;
- guardrail contro `git add --renormalize .` non misurato;
- test automatico `tests/unit/test_git_line_endings_warning_cleanup.py`.

---

## 62. STEP 550 - LAST Deprecation and 4-Digit Artifact Naming Standard

### Obiettivo

Deprecare l'uso operativo dei file `LAST-*` e introdurre lo standard progressivo `NNNN-II-Tipo_Nome.ext`.

### Output realizzati

- documento `docs/73_LAST_DEPRECATION_4_DIGIT_ARTIFACT_NAMING_STANDARD.md`;
- utility `scripts/migrate_artifact_names_4digit.py` dry-run di default e apply solo con `--apply`;
- test `tests/unit/test_migrate_artifact_names_4digit.py` per conversioni, skip, collisioni, contenuto e timestamp;
- template PowerShell command pack aggiornati per non generare `LAST-*`;
- skill draft/export repository-local aggiornati, senza modificare skill esterne;
- regola `max(II)` per trovare l'ultimo artefatto di un tipo per uno step;
- distinzione esplicita: Bridge operativo, Git + file versionato autorevoli.

---

## 63. STEP 560 - OpenAI API Adapter First Authorized Live Run

### Obiettivo

Eseguire una prima live reale futura solo se Alberto autorizza esplicitamente lo step e fornisce l'ambiente locale necessario.

### Output realizzati

- wrapper `scripts/asf_openai_first_authorized_live_run.py`;
- report versionato `docs/0560-01-Report_OpenAI_API_Adapter_First_Authorized_Live_Run.md`;
- diagnostic pack versionato `docs/0560-03-Diagnostic_OpenAI_Provider_HTTP_Error_And_Rate_Limit.md`;
- live authorization via `--live` o `ASF_OPENAI_LIVE_RUN=1`;
- modello configurabile via `ASF_OPENAI_MODEL`;
- prompt tiny non sensibile `Return exactly ASF_OPENAI_LIVE_SMOKE_OK.`;
- `store: false`;
- output massimo basso;
- classificazione risultato e stop conditions;
- test mockati per key assente, flag live assente, redazione secret, successo, errori API/rete/quota e no-leak.

### Stato live

- status: `BLOCKED_BY_RATE_LIMIT_OR_QUOTA`;
- motivo consolidato: provider HTTP 429 `insufficient_quota`, coerente con quota/billing/project limit;
- request count ultimo tentativo autorizzato: `1`;
- evidence JSON non creato, perche' la live non e' stata eseguita con successo;
- nessun retry aggressivo o loop live.

### Prossimo step consigliato

0570) ASF Supervised Gate Autonomy ADR and MVP Motor Roadmap

---

## 64. STEP 570 - ASF Supervised Gate Autonomy ADR and MVP Motor Roadmap

### Obiettivo

Correggere la rotta strategica di ASF da autonomia fire-and-forget ad autonomia supervisionata a gate, congelando nuovi step di meta-processo finche' il motore non completa almeno un giro end-to-end dry-run.

### Output realizzati

- ADR `docs/adr/0570_SUPERVISED_GATE_AUTONOMY.md`;
- roadmap MVP Motore `docs/motor/0570_MVP_MOTOR_ROADMAP.md`;
- specifica loop a gate `docs/motor/0570_GATE_LOOP_SPEC.md`;
- nodo revisione indipendente `docs/motor/0570_INDEPENDENT_REVIEW_NODE.md`;
- aggiornamento README, changelog, roadmap, decision log e Project Workflow Index;
- nessun runner operativo, nessuna live run OpenAI e nessuna modifica alle evidence STEP 0560.

### Roadmap MVP Motore

- 0570 - ADR + MVP Motor Roadmap;
- 0580 - Dry-run Loop Runner;
- 0590 - Stable PowerShell Publish Runner;
- 0600 - Risk Classifier + Gate Policy;
- 0610 - Risk Classifier Integration with Dry-run Loop Runner;
- 0620 - Gate Decision Report and Human Approval Packet;
- 0630 - Verification Profile Selector + Test Cost Policy;
- 0640 - Verification Profile Integration with Publish Runner;
- 0650 - Verification Profile Driven Publish Config Generator;
- 0660 - Publish Config Generator Bridge Output Integration.

### Prossimo step consigliato

0580) Dry-run Loop Runner

---

## 65. STEP 580 - Dry-run Loop Runner

### Obiettivo

Creare il primo runner locale del MVP Motore che attraversa il loop supervisionato a gate in modalita' dry-run, senza chiamate live, senza secret, senza write sul repository target e senza pubblicazione Git.

### Output realizzati

- script `scripts/asf_dry_run_loop_runner.py`;
- runbook `docs/motor/0580_DRY_RUN_LOOP_RUNNER.md`;
- esempi JSON `examples/dry_run_loop/step_0580_simulated_request.json` e `examples/dry_run_loop/step_0580_execution_plan.json`;
- artifact runtime strutturati sotto `tmp/asf_dry_run_loop/<project>/step_<step>/`;
- attraversamento degli stati `PLAN_NEXT_STEP`, `BUILD_TASK_PACKET`, `RISK_CLASSIFY`, `EXECUTE_DRY_OR_WRITE`, `RUN_TESTS`, `INDEPENDENT_REVIEW`, `GATE_DECISION`, `COMMIT_OR_HOLD`;
- decisione finale `NEEDS_HUMAN` oppure `FAIL`;
- test automatici `tests/unit/test_asf_dry_run_loop_runner.py`.

### Guardrail

- nessuna chiamata live OpenAI o provider esterni;
- nessun secret/API key;
- nessun write sul repository target;
- nessun commit, push, PR, merge, deploy o release;
- risk classifier e review restano minimi, locali e fail-closed.

### Prossimo step consigliato

0590) Stable PowerShell Publish Runner

---

## 66. STEP 590 - Stable PowerShell Publish Runner

### Obiettivo

Sostituire i mega-blocchi PowerShell copiati in chat con un runner stabile, versionato, testabile e configurabile per pubblicare gli step ASF tramite comando corto e config JSON.

### Output realizzati

- runner `scripts/asf_publish_step.ps1`;
- config esempio `examples/publish_step/0590_publish_config.example.json`;
- documento `docs/motor/0590_STABLE_POWERSHELL_PUBLISH_RUNNER.md`;
- test `tests/unit/test_asf_publish_step_runner.py`;
- supporto FASE A locale, FASE B publish con `-ApprovePublish`, FASE C merge con `-ApproveMerge`;
- output Bridge con file numerati e alias `LAST-*` richiesti dallo step;
- writer DOCX OpenXML minimale senza dipendenze esterne;
- gestione `gh pr checks` con warning controllato per `no checks reported`.

### Guardrail

- default fail-closed;
- nessuna publish action senza flag esplicito;
- comandi config in forma `argv`;
- nessun `Invoke-Expression`;
- nessun provider live, secret/API key o deploy;
- nessuna pubblicazione reale eseguita durante l'implementazione Codex dello step.

### Prossimo step consigliato

0600) Risk Classifier + Gate Policy

---

## 67. STEP 600 - Risk Classifier + Gate Policy

### Obiettivo

Rendere stabile, testabile e riusabile la classificazione L0-L4 e la gate policy fail-closed per il futuro motore ASF.

### Output realizzati

- script `scripts/asf_risk_classifier.py`;
- documento `docs/motor/0600_RISK_CLASSIFIER_GATE_POLICY.md`;
- esempi JSON in `examples/risk_classifier/`;
- test automatici `tests/unit/test_asf_risk_classifier.py`;
- aggiornamento README, changelog, roadmap, decision log e Project Workflow Index.

### Guardrail

- classificazione rule-based, standard library only;
- input vuoto o non riconosciuto fail-closed;
- L3/L4 non allowed senza gate espliciti;
- nessuna chiamata live, nessun secret, nessuna pubblicazione Git;
- nessuna modifica al runner 0580 o al publish runner 0590.

### Prossimo step consigliato

0610) Risk Classifier Integration with Dry-run Loop Runner

---

## 68. STEP 610 - Risk Classifier Integration with Dry-run Loop Runner

### Obiettivo

Collegare il Risk Classifier + Gate Policy dello STEP 0600 al checkpoint `RISK_CLASSIFY` del Dry-run Loop Runner dello STEP 0580.

### Output realizzati

- integrazione in `scripts/asf_dry_run_loop_runner.py`;
- risk report strutturato con blocchi `risk`, `gate`, `dry_run` e `plan_blockers`;
- esempi request dry-run 0610 in `examples/dry_run_loop/`;
- documento `docs/motor/0610_RISK_CLASSIFIER_DRY_RUN_INTEGRATION.md`;
- test automatici di integrazione e regressione.

### Guardrail

- classifier 0600 come fonte unica delle regole L0-L4;
- nessuna duplicazione delle regole nel runner;
- fail-closed su input ambiguo, classifier non valido, piano non dry-run o L4 senza gate elevato dichiarato;
- nessuna chiamata live, nessun secret, nessun write target, nessuna pubblicazione Git;
- nessuna modifica al publish runner 0590.

### Prossimo step consigliato

0620) Gate Decision Report and Human Approval Packet

---

## 69. STEP 620 - Gate Decision Report and Human Approval Packet

### Obiettivo

Trasformare l'output tecnico del Dry-run Loop Runner e del Risk Classifier in un Approval Packet leggibile, fail-closed e adatto a una decisione umana supervisionata.

### Output realizzati

- script `scripts/asf_gate_decision_report.py`;
- documento `docs/motor/0620_GATE_DECISION_REPORT_HUMAN_APPROVAL_PACKET.md`;
- nota `docs/motor/0620_VERIFICATION_BALANCE_NOTES.md`;
- esempi JSON in `examples/gate_decision/`;
- test automatici `tests/unit/test_asf_gate_decision_report.py`;
- integrazione leggera in workflow health e Project Workflow Index.

### Guardrail

- nessuna duplicazione delle regole L0-L4 del classifier;
- input ambiguo o non valido gestito in `FAIL_CLOSED`;
- L3 richiede `explicit_publish_approval` per produrre `APPROVE_PUBLISH`;
- L4 resta bloccato o fail-closed;
- nessuna chiamata live, nessun secret, nessun write target, nessuna pubblicazione Git;
- nessuna modifica al publish runner 0590.

### Prossimo step consigliato

0630) Verification Profile Selector + Test Cost Policy

---

## 70. STEP 630 - Verification Profile Selector + Test Cost Policy

### Obiettivo

Introdurre un selettore locale dei profili di verifica per bilanciare risultato, velocita', costo computazionale e rischio operativo.

### Output realizzati

- script `scripts/asf_verification_profile_selector.py`;
- documento `docs/motor/0630_VERIFICATION_PROFILE_SELECTOR_TEST_COST_POLICY.md`;
- esempi JSON in `examples/verification_profiles/`;
- test automatici `tests/unit/test_asf_verification_profile_selector.py`;
- integrazione leggera in workflow health e Project Workflow Index.

### Guardrail

- selector deterministico, locale e standard-library only;
- input vuoto, ambiguo o non riconosciuto fail-closed;
- profili `motor-core`, `publish`, `final-main` e `high-risk` conservativi;
- nessuna chiamata live, nessun secret, nessuna pubblicazione Git;
- nessuna modifica al publish runner 0590 in questo step.

### Prossimo step consigliato

0640) Verification Profile Integration with Publish Runner

---

## 71. STEP 640 - Verification Profile Integration with Publish Runner

### Obiettivo

Integrare il Verification Profile Selector dello STEP 0630 nel Publish Runner dello STEP 0590, mantenendo retrocompatibilita' config, fail-closed e gate umani.

### Output realizzati

- validazione opzionale in `scripts/asf_publish_step.ps1`;
- esempi config 0640 in `examples/publish_step/`;
- documento `docs/motor/0640_VERIFICATION_PROFILE_INTEGRATION_PUBLISH_RUNNER.md`;
- test automatici su profilo coerente, mismatch, L4, selector fail-closed, riduzione check, Phase B/C e divieto shell;
- integrazione in workflow health e Project Workflow Index.

### Guardrail

- config legacy senza profilo ancora compatibili;
- selector 0630 resta fonte della logica profili;
- profilo dichiarato piu' leggero della raccomandazione blocca;
- `allow_profile_check_reduction` default `false`;
- Phase B richiede ancora `-ApprovePublish`;
- Phase C richiede ancora `-ApproveMerge` e non viene ridotta nello STEP 0640;
- nessuna chiamata live, nessun secret, nessuna pubblicazione Git eseguita da Codex.

### Prossimo step consigliato

0650) Verification Profile Driven Publish Config Generator

---

## 72. STEP 650 - Verification Profile Driven Publish Config Generator

### Obiettivo

Generare bozze config JSON per `scripts/asf_publish_step.ps1` usando il Verification Profile Selector, riducendo errori manuali senza eseguire pubblicazione.

### Output realizzati

- script `scripts/asf_publish_config_generator.py`;
- documento `docs/motor/0650_VERIFICATION_PROFILE_DRIVEN_PUBLISH_CONFIG_GENERATOR.md`;
- esempi input in `examples/publish_config_generator/`;
- test automatici `tests/unit/test_asf_publish_config_generator.py`;
- classificazione del generator come `motor-core` nel selector 0630;
- integrazione in workflow health e Project Workflow Index.

### Guardrail

- generator locale, deterministico e standard-library only;
- input essenziale mancante, selector fail-closed, L4, `high-risk` e `final-main` bloccano la config ordinaria;
- Phase C resta completa con full pytest, workflow health e verify gate;
- il generator non esegue il publish runner;
- nessuna chiamata live, nessun secret, nessun commit, push, PR, merge o deploy.

### Prossimo step consigliato

0660) Publish Config Generator Bridge Output Integration
