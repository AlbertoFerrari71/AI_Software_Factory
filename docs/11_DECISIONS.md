# 11 — Decisions

Decision log del progetto AI Software Factory.

Formato:

```text
DEC-XXX — Titolo
Data:
Stato:
Contesto:
Decisione:
Motivazione:
Conseguenze:
```

---

## DEC-001 — Nome pubblico del progetto

**Data:** 2026-05-25
**Stato:** Accettata

### Contesto

Serviva un nome chiaro per il framework.

### Decisione

Il nome pubblico iniziale è:

```text
AI Software Factory
```

### Motivazione

Il nome comunica un processo ripetibile, controllato e orientato alla produzione di software.

### Conseguenze

Il repository, i documenti e la comunicazione useranno AI Software Factory come nome principale.

---

## DEC-002 — Nome interno del metodo

**Data:** 2026-05-25
**Stato:** Accettata

### Decisione

Il metodo interno si chiama:

```text
Codex Alchemy Method
```

### Motivazione

Rappresenta la trasformazione progressiva di un'idea grezza in software affidabile.

### Conseguenze

Codex Alchemy Method viene usato nei documenti come nome della metodologia, non necessariamente come brand pubblico principale.

---

## DEC-003 — Strategia local-first, SaaS-ready

**Data:** 2026-05-25
**Stato:** Accettata

### Decisione

Il progetto nasce local-first/personale, ma viene progettato con compatibilità SaaS futura.

### Motivazione

Permette di ottenere valore subito senza appesantire l'MVP con multiutente, billing, OAuth e infrastruttura cloud.

### Conseguenze

I documenti devono distinguere sempre tra:

- MVP personale;
- funzionalità SaaS-ready;
- SaaS futuro.

---

## DEC-004 — Stack iniziale candidato

**Data:** 2026-05-25  
**Stato:** Accettata provvisoria

### Decisione

Stack candidato iniziale:

- Python;
- FastAPI;
- SQLite;
- Pydantic;
- pytest;
- Markdown;
- YAML;
- JSON;
- GitHub Actions.

### Motivazione

Stack semplice, adatto a orchestratore locale, API leggere, output strutturati e test.

### Conseguenze

Lo stack può essere confermato o corretto negli step successivi. Nessun codice applicativo viene ancora scritto nello step 010.

---

## DEC-005 — GitHub come centro operativo

**Data:** 2026-05-25  
**Stato:** Accettata

### Decisione

GitHub sarà usato come centro per:

- repository;
- issue;
- branch;
- pull request;
- history;
- release;
- GitHub Actions.

### Motivazione

Permette versioning, controllo, PR, test automatici e tracciabilità.

### Conseguenze

Il metodo standard sarà issue → branch → PR → test → review → merge.

---

## DEC-006 — Codex CLI e Codex Cloud entrambi previsti

**Data:** 2026-05-25  
**Stato:** Accettata

### Decisione

Usare:

- Codex CLI per lavoro locale, audit, patch, test e refactoring;
- Codex Cloud/Web per task paralleli, PR e lavoro su repository GitHub.

### Motivazione

Le due modalità hanno punti di forza diversi.

### Conseguenze

I task dovranno dichiarare quale modalità Codex è ammessa.

---

## DEC-007 — Safety Model L0-L4 obbligatorio

**Data:** 2026-05-25  
**Stato:** Accettata

### Decisione

Ogni tool o azione deve essere classificato da L0 a L4.

### Motivazione

Serve per evitare automazioni incontrollate.

### Conseguenze

Gli step successivi dovranno implementare approval gate, dry-run e rollback.

---

## DEC-008 — Family Photo Organizer come caso pilota

**Data:** 2026-05-25  
**Stato:** Accettata

### Decisione

Family Photo Organizer sarà il primo caso pilota.

### Motivazione

È un progetto reale, già impostato con sicurezza read-only, GitHub, Codex, test e documentazione.

### Conseguenze

Il framework sarà testato su Family Photo Organizer ma non vincolato a quel dominio.

---

## DEC-009 — No automazioni distruttive senza controllo

**Data:** 2026-05-25  
**Stato:** Accettata

### Decisione

Le azioni L4 richiedono:

- approvazione esplicita;
- dry-run;
- backup o rollback;
- conferma doppia.

### Motivazione

Il framework deve evitare cancellazioni, force push, deploy o modifiche dati non volute.

### Conseguenze

Nessun agente potrà eseguire azioni distruttive in automatico.

---

## DEC-010 — Primo MVP centrato su metodo e template

**Data:** 2026-05-25  
**Stato:** Accettata

### Decisione

Il primo MVP non sarà una grande piattaforma, ma un insieme robusto di:

- documenti;
- template;
- prompt;
- task packet;
- checklist;
- workflow GitHub/Codex.

### Motivazione

Prima si valida il metodo, poi si automatizza.

### Conseguenze

Gli step 010–100 sono prioritari rispetto a dashboard, API e SaaS.

---

## DEC-011 — Repository Genesis come scheletro senza logica applicativa

**Data:** 2026-05-25  
**Stato:** Accettata

### Contesto

Lo STEP 020 deve rendere il repository ordinato e pronto per Codex/GitHub, senza anticipare l'implementazione del prodotto.

### Decisione

Creare struttura `src/`, `tests/`, `.github/`, `templates/` e documentazione, ma non introdurre logica applicativa reale.

### Motivazione

Separare il lavoro di fondazione dal lavoro di sviluppo evita codice fragile e consente di stabilire regole prima degli automatismi.

### Conseguenze

Il package Python contiene solo skeleton e metadata minimi.

---

## DEC-012 — CI minima con smoke test

**Data:** 2026-05-25  
**Stato:** Accettata

### Decisione

Introdurre una GitHub Actions CI minimale che installa il package e lancia `pytest`.

### Motivazione

Anche un repository iniziale deve avere un controllo automatico minimo per evitare regressioni strutturali.

### Conseguenze

La CI non fa ancora lint, security scan o build complessa. Questi controlli saranno ampliati negli step 050 e 070.

---

## DEC-013 — Template GitHub presenti da subito

**Data:** 2026-05-25  
**Stato:** Accettata

### Decisione

Aggiungere issue template, PR template e template documentali nel repository già nello STEP 020.

### Motivazione

Il metodo dipende dalla qualità del lavoro tracciato. Issue e PR devono imporre obiettivo, scope, test, rischi e rollback.

### Conseguenze

Ogni step futuro avrà una struttura standard.

---

## DEC-014 — Branch principale previsto come main

**Data:** 2026-05-25  
**Stato:** Accettata provvisoria

### Decisione

Per il nuovo repository AI Software Factory il branch principale consigliato è `main`.

### Motivazione

È il default moderno di GitHub per nuovi repository.

### Conseguenze

Se il repository viene creato diversamente, aggiornare documentazione e workflow. Non applicare automaticamente questa decisione ad altri repository esistenti.

---

## DEC-015 — Nessuna branch protection automatica nello STEP 020

**Data:** 2026-05-25  
**Stato:** Accettata

### Decisione

Documentare branch protection e required status checks, ma non automatizzare configurazioni GitHub nello STEP 020.

### Motivazione

Le protezioni richiedono un repository remoto reale, permessi amministrativi e una CI già stabile.

### Conseguenze

La branch protection sarà attivata manualmente o tramite tool controllato in step successivi, con approvazione esplicita.


---

## DEC-016 — Safety Model operativo L0-L4

**Data:** 2026-05-25  
**Stato:** Accettata

### Contesto

Lo STEP 030 deve rendere la sicurezza applicabile, non solo descrittiva.

### Decisione

Adottare cinque livelli di rischio: L0 read-only, L1 write safe, L2 write controlled, L3 risky, L4 destructive.

### Motivazione

La classificazione consente di decidere quali azioni possono essere automatiche e quali richiedono approvazione umana.

### Conseguenze

Ogni task futuro deve indicare il livello massimo consentito e rispettare la policy.

---

## DEC-017 — Fail closed come default

**Data:** 2026-05-25  
**Stato:** Accettata

### Decisione

Se un'azione, un tool o un path non è classificabile, il sistema deve bloccare o elevare l'azione almeno a L3.

### Motivazione

Nel contesto agentico, l'ambiguità è un rischio operativo. È meglio fermarsi che eseguire un'azione non compresa.

### Conseguenze

I prompt, i task packet e i futuri adapter devono dichiarare chiaramente scope e livello.

---

## DEC-018 — Policy machine-readable in JSON

**Data:** 2026-05-25  
**Stato:** Accettata

### Decisione

Creare `policies/safety_policy.v0.json` come versione canonica della policy, accompagnata da YAML leggibile da umani.

### Motivazione

JSON è validabile con la libreria standard Python, evitando dipendenze premature.

### Conseguenze

I test automatici possono verificare le proprietà critiche della policy senza introdurre nuove dipendenze.

---

## DEC-019 — L4 richiede doppia conferma

**Data:** 2026-05-25  
**Stato:** Accettata

### Decisione

Le azioni L4 richiedono approvazione esplicita, dry-run, backup/rollback e una seconda conferma scritta.

### Motivazione

Le azioni distruttive non devono essere eseguite per errore, per ambiguità o per prompt injection.

### Conseguenze

Il framework dovrà sempre presentare un approval request prima di qualunque L4.

---

## DEC-020 — MCP e tool remoti con approval default

**Data:** 2026-05-25  
**Stato:** Accettata

### Decisione

Per MCP e tool remoti, usare approval attiva per default, server fidati, allowed tools espliciti e log dei dati condivisi.

### Motivazione

I tool remoti possono ricevere dati sensibili o compiere azioni esterne al repository.

### Conseguenze

Lo STEP 130 dovrà implementare un registry tool coerente con questa policy.

---

## DEC-021 — Prompt Packet come contratto operativo

**Data:** 2026-05-25
**Stato:** Accettata

### Contesto

Lo STEP 040 deve evitare prompt liberi, ambigui o non verificabili.

### Decisione

Ogni prompt operativo deve dichiarare almeno obiettivo, contesto, livello rischio L0-L4, file da leggere, file modificabili, file vietati, vincoli, output atteso, criteri di accettazione, test/verifica, rollback o safe stop e cosa non fare.

### Motivazione

Queste sezioni trasformano una richiesta naturale in un incarico controllabile, coerente con il Safety Model.

### Conseguenze

I template ChatGPT, Codex e Codex Task Packet devono essere verificabili con test leggeri.

---

## DEC-022 — Template specializzati per modalita' AI

**Data:** 2026-05-25
**Stato:** Accettata

### Contesto

ChatGPT, Codex Ask, Codex Code, Codex Review e Codex Repair hanno rischi e output diversi.

### Decisione

Mantenere template separati per ciascuna modalita', con lo stesso schema minimo ma con vincoli specifici.

### Motivazione

Un unico prompt generico ridurrebbe chiarezza e controllo operativo.

### Conseguenze

Le modalita' read-only restano L0, mentre Code e Repair sono limitate a L2 salvo approval esplicita L3/L4.

---

## DEC-023 — Test leggeri sui template

**Data:** 2026-05-25
**Stato:** Accettata

### Contesto

I prompt sono documenti Markdown, ma regressioni strutturali possono renderli incompleti.

### Decisione

Aggiungere test unitari che verificano presenza dei template principali e delle sezioni minime.

### Motivazione

I controlli automatici proteggono il contratto operativo senza introdurre dipendenze o logica applicativa.

### Conseguenze

La CI potra' intercettare template mancanti o incompleti con `python -m pytest -q`.

---

## DEC-027 - Verification Gate local-first

**Data:** 2026-05-27
**Stato:** Accettata

### Contesto

Dopo STEP 060 serve un criterio ripetibile per decidere quando una modifica e' verificata prima di entrare su `main`.

### Decisione

Introdurre un Verification Gate local-first con:

- documento operativo `docs/20_VERIFICATION_GATE.md`;
- script locale `scripts/verify.ps1`;
- CI GitHub allineata ai controlli minimi;
- checklist nel PR template;
- branch protection raccomandata ma non configurata automaticamente nello STEP 070.

### Motivazione

Il metodo deve rendere esplicito il passaggio tra lavoro Codex locale, verifica umana, PR, CI e merge.

### Conseguenze

Ogni step futuro deve distinguere verifiche locali, CI GitHub, controlli manuali, verifiche non eseguite e rischi residui. L'applicazione automatica della branch protection resta un'azione futura e separata.
