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
| 110 | Branch Protection Verification and Hardening | Verificare protezione reale e pianificare hardening | Verifica GitHub, required checks, hardening plan | MVP personale | Da fare |
| 120 | OpenAI API Adapter | Output strutturati e tool calling | Adapter Responses API, JSON Schema | SaaS-ready | Da fare |
| 130 | MCP Tool Registry | Registro tool e permessi | Tool registry L0-L4 | SaaS-ready | Da fare |
| 140 | Guided Mode | Percorso per non tecnici | Wizard A/B/C/D | SaaS-ready | Da fare |
| 150 | SaaS Evolution Plan | Preparare SaaS futuro | Multiutente, ruoli, billing, audit, vault | SaaS futuro | Da fare |

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

Verificare l'applicazione reale della branch protection e definire l'hardening successivo.

### Output previsti

- verifica GitHub della protezione di `main`;
- conferma nome required check CI;
- eventuale PR di prova;
- valutazione rulesets;
- piano per review obbligatorie, conversation resolution, linear history e security scan;
- rollback e safe stop.

---

## 14. STEP 120 — OpenAI API Adapter

### Obiettivo

Collegare Responses API e Structured Outputs.

### Output previsti

- adapter;
- JSON Schema;
- tool calling layer;
- test mockati;
- no azioni rischiose senza policy.

---

## 15. STEP 130 — MCP Tool Registry

### Obiettivo

Gestire tool esterni in modo sicuro.

### Output previsti

- registry tool;
- permessi L0-L4;
- approval policy;
- read-only first.

---

## 16. STEP 140 — Guided Mode

### Obiettivo

Rendere il framework utilizzabile da utenti non tecnici.

### Output previsti

- wizard;
- domande A/B/C/D;
- default sicuri;
- spiegazioni brevi.

---

## 17. STEP 150 — SaaS Evolution Plan

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
