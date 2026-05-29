# AI Software Factory

**Metodo interno:** Codex Alchemy Method  
**Stato:** STEP 030 — Safety Model  
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

Questo repository è nello stato **STEP 030 — Safety Model**.

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
- test automatici sulle regole critiche di sicurezza.

Non sono ancora presenti:

- orchestratore locale;
- API FastAPI;
- database;
- integrazioni OpenAI API;
- integrazioni MCP;
- automazioni Codex operative;
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
040) Prompt Packet Generator
```

Obiettivo: standardizzare prompt packet e task packet usando le policy di sicurezza definite nello STEP 030.
