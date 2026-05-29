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
| 210 | Prompt Packet Generator Developer Onboarding | Rendere il generatore e la checklist facili da adottare da un operatore locale | Onboarding, esempi operativi, workflow guidato | MVP personale | Da fare |
| 220 | OpenAI API Adapter | Output strutturati e tool calling | Adapter Responses API, JSON Schema | SaaS-ready | Da fare |
| 230 | MCP Tool Registry | Registro tool e permessi | Tool registry L0-L4 | SaaS-ready | Da fare |
| 240 | Guided Mode | Percorso per non tecnici | Wizard A/B/C/D | SaaS-ready | Da fare |
| 250 | SaaS Evolution Plan | Preparare SaaS futuro | Multiutente, ruoli, billing, audit, vault | SaaS futuro | Da fare |

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

### Output previsti

- guida onboarding del generatore;
- checklist operativa per creare, validare e consegnare task packet;
- ciclo di vita di un prompt packet;
- esempi di uso quotidiano;
- nessuna pubblicazione esterna.

---

## 24. STEP 220 — OpenAI API Adapter

### Obiettivo

Collegare Responses API e Structured Outputs.

### Output previsti

- adapter;
- JSON Schema;
- tool calling layer;
- test mockati;
- no azioni rischiose senza policy.

---

## 25. STEP 230 — MCP Tool Registry

### Obiettivo

Gestire tool esterni in modo sicuro.

### Output previsti

- registry tool;
- permessi L0-L4;
- approval policy;
- read-only first.

---

## 26. STEP 240 — Guided Mode

### Obiettivo

Rendere il framework utilizzabile da utenti non tecnici.

### Output previsti

- wizard;
- domande A/B/C/D;
- default sicuri;
- spiegazioni brevi.

---

## 27. STEP 250 — SaaS Evolution Plan

### Obiettivo

Preparare il passaggio futuro a SaaS.

### Output previsti

- workspace;
- utenti;
- ruoli;
- audit log;
- billing;
- secrets vault;
- marketplace template.
