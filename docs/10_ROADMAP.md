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
| 060 | Codex Workflow | Definire uso Codex CLI e Cloud | Codex Task Packet, modalità ask/edit | MVP personale | Da fare |
| 070 | Verification Gate | Definire test, lint, build, smoke, security | Test strategy, checklist, CI | MVP personale | Da fare |
| 080 | Documentation Sync | Mantenere docs allineate | Changelog, decision log, roadmap update | MVP personale | Da fare |
| 090 | Expert Mode | Workflow per utenti tecnici | Procedure con diff, log, test, rollback | MVP personale | Da fare |
| 100 | Family Photo Organizer Case Study | Applicare il metodo al caso pilota | Case study, retrospettiva, template migliorati | MVP personale | Da fare |
| 110 | Local Orchestrator MVP | Primo software locale | CLI/API locale per generare pacchetti | MVP software | Da fare |
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

### Output previsti

- modalità ASK;
- modalità CODE controllata;
- prompt task standard;
- checklist diff/test;
- regole no commit/no push/no merge.

---

## 9. STEP 070 — Verification Gate

### Obiettivo

Definire cosa significa "verificato".

### Output previsti

- test automatici;
- lint;
- build;
- smoke test;
- security check;
- manual checklist;
- blocchi PR.

---

## 10. STEP 080 — Documentation Sync

### Obiettivo

Evitare disallineamento tra codice e documentazione.

### Output previsti

- regole aggiornamento docs;
- changelog policy;
- decision log policy;
- roadmap update checklist.

---

## 11. STEP 090 — Expert Mode

### Obiettivo

Rendere il metodo comodo per Alberto e utenti tecnici.

### Output previsti

- comandi;
- diff review;
- test log;
- rollback;
- costi stimati;
- output JSON.

---

## 12. STEP 100 — Family Photo Organizer Case Study

### Obiettivo

Applicare il metodo al caso reale.

### Output previsti

- case study;
- retrospettiva;
- template corretti;
- lessons learned.

---

## 13. STEP 110 — Local Orchestrator MVP

### Obiettivo

Costruire il primo software locale.

### Output previsti

- CLI o FastAPI minimale;
- project starter;
- roadmap generator;
- Codex Task Packet generator;
- verification checklist.

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
