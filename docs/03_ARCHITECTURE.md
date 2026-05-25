# 03 — Architecture

## 1. Stato architetturale

Questo documento definisce l'architettura candidata del framework.

Nello STEP 030 non esiste ancora logica applicativa. Esiste lo scheletro del repository più il Safety Model operativo, progettati per evitare monoliti e permettere sviluppo incrementale sicuro.

---

## 2. Principi architetturali

- Local-first nel primo MVP.
- SaaS-ready senza costruire SaaS prematuro.
- Moduli piccoli e separati.
- Sicurezza e approval policy integrate nel flusso.
- Adapter separati per strumenti esterni.
- Documentazione viva come parte del prodotto.
- Nessuna dipendenza inutile nelle prime fasi.

---

## 3. Moduli candidati

```text
src/ai_software_factory/
  core/          Project model, workflow engine, state machine, policy engine
  intake/        Idea parser, requirement extractor, question generator
  prompts/       Prompt templates, packet builder, prompt validation
  codex/         Codex CLI/Cloud adapters, task packet generation
  github/        Issue, branch, PR, workflow status adapters
  openai_api/    Responses API adapter, structured output schemas, tool calling
  mcp/           MCP registry, permission model, connector metadata
  safety/        L0-L4 policy, dry-run, rollback, secret checks
  verification/  Test runner, lint runner, smoke checks, quality gate
  docs_sync/     README, changelog, decisions, roadmap updates
  audit/         Event log, tool call log, approval log, cost/token log
  ui/            CLI and future web dashboard
```

---

## 4. Regola di dipendenza

I moduli di dominio interno non devono dipendere direttamente da servizi esterni.

Regola desiderata:

```text
core
  ↑
intake / prompts / safety / verification / docs_sync / audit
  ↑
codex / github / openai_api / mcp
  ↑
ui
```

Gli adapter verso sistemi esterni devono essere isolati.

---

## 5. Architettura MVP personale

Nel primo MVP reale:

- CLI o FastAPI locale;
- SQLite opzionale;
- file Markdown/YAML/JSON come fonte primaria;
- niente multiutente;
- niente deploy;
- niente tool distruttivi.

---

## 6. Architettura SaaS futura

In evoluzione futura:

- PostgreSQL;
- workspace;
- ruoli e permessi;
- OAuth;
- billing;
- audit log persistente;
- secrets vault;
- sandbox code execution;
- marketplace template;
- connettori GitHub/GitLab/MCP.

---

## 7. Cosa non fare ora

- Non creare microservizi.
- Non creare code execution sandbox nello STEP 030.
- Non creare multi-tenancy prematura.
- Non vincolare tutto a un singolo vendor.
- Non introdurre queue, worker o orchestratori complessi prima di un reale bisogno.
