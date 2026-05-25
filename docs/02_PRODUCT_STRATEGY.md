# 02 — Product Strategy

## 1. Strategia iniziale

La strategia è costruire prima un framework personale realmente utile, poi valutarne l'evoluzione a prodotto.

Ordine corretto:

```text
Metodo solido → Template riutilizzabili → Workflow GitHub/Codex → Orchestratore locale → Guided Mode → SaaS
```

Non invertire l'ordine.

---

## 2. Proposta di valore

### Per Alberto

Ridurre tempi di sviluppo mantenendo:

- controllo;
- qualità;
- sicurezza;
- documentazione;
- test;
- ordine nei repository.

### Per utente non tecnico

Permettere di trasformare un'idea in progetto software senza dover capire subito:

- architettura;
- Git;
- branch;
- PR;
- test;
- API;
- sicurezza;
- prompt engineering.

### Per utente tecnico

Ridurre attrito in:

- analisi;
- task breakdown;
- generazione prompt;
- review;
- test;
- aggiornamento documentazione;
- gestione Codex e GitHub.

---

## 3. Personas

### Persona A — Founder con idee

- sa descrivere il problema;
- non sa programmare;
- vuole vedere risultati;
- rischia di accettare codice fragile;
- ha bisogno di Guided Mode.

### Persona B — Tecnico pratico

- conosce un po' di programmazione;
- lavora su progetti concreti;
- vuole accelerare senza perdere controllo;
- usa GitHub Desktop o strumenti simili;
- ha bisogno di Expert Mode semplificata.

### Persona C — Sviluppatore esperto

- vuole integrare AI nel workflow;
- richiede controllo su diff, branch, PR, CI;
- vuole policy chiare;
- richiede log e audit;
- può usare API e CLI.

---

## 4. Modalità prodotto

| Modalità | Target | Caratteristiche |
|---|---|---|
| Guided Mode | Non tecnico | Domande A/B/C/D, default sicuri, pochi dettagli |
| Expert Mode | Tecnico | Branch, file, diff, test, log, prompt, rischi |
| Audit Mode | Review | Legge e valuta, non modifica |
| Codex Mode | Esecuzione | Produce task packet controllati |
| SaaS Mode | Futuro | Multiutente, workspace, ruoli, billing |

---

## 5. MVP personale

Il primo MVP deve risolvere questi casi:

1. creare una scheda progetto da idea naturale;
2. generare roadmap 010/020/030;
3. generare documenti base;
4. generare Codex Task Packet;
5. generare checklist di verifica;
6. guidare lavoro GitHub con issue/branch/PR;
7. aggiornare decision log e changelog.

Non deve ancora:

- modificare repository automaticamente;
- chiamare API in produzione;
- gestire utenti;
- fare billing;
- eseguire deploy;
- integrare tutti gli MCP;
- avere dashboard complessa.

---

## 6. Funzioni prioritarie

| Priorità | Funzione | Motivo |
|---:|---|---|
| 1 | Template documentali | Base del metodo |
| 2 | Codex Task Packet | Riduce rischio di task AI fuori controllo |
| 3 | Roadmap generator | Spezza il lavoro in step piccoli |
| 4 | Safety Model | Evita azioni rischiose |
| 5 | Verification Gate | Impedisce codice non testato |
| 6 | Documentation Sync | Mantiene memoria viva |
| 7 | Expert Mode | Utile subito per Alberto |
| 8 | Guided Mode | Serve al prodotto futuro |
| 9 | OpenAI API Adapter | Automatizza output strutturati |
| 10 | MCP Registry | Estende tool in sicurezza |

---

## 7. Differenziazione

AI Software Factory non compete solo con IDE o coding assistant.

Differenza principale:

```text
Non aiuta solo a scrivere codice.
Aiuta a governare l'intero ciclo idea → software affidabile.
```

Elementi distintivi:

- human-guided;
- safety-first;
- documentazione viva;
- task piccoli;
- Codex Task Packet;
- decision log;
- GitHub workflow;
- riuso del metodo;
- modalità per non tecnici e tecnici;
- local-first con SaaS-ready design.

---

## 8. Metriche di qualità

Metriche iniziali:

| Metrica | Significato |
|---|---|
| Tempo da idea a roadmap | Velocità di chiarimento |
| Percentuale step con acceptance criteria | Qualità del breakdown |
| Percentuale task con test | Qualità tecnica |
| Numero PR piccole vs grandi | Manutenibilità |
| Documenti aggiornati per step | Continuità |
| Numero azioni L3/L4 approvate correttamente | Sicurezza |
| Numero rollback riusciti | Reversibilità |
| Numero template riusati | Maturità del metodo |

---

## 9. Strategia SaaS futura

Il SaaS potrà nascere solo dopo aver validato il metodo local-first.

Componenti SaaS futuri:

- account;
- workspace;
- progetti multipli;
- ruoli e permessi;
- audit log centralizzato;
- billing;
- limiti consumo API;
- template marketplace;
- connettori GitHub/GitLab;
- connettori MCP;
- sandbox di esecuzione;
- secret vault;
- dashboard qualità;
- scoring affidabilità agenti.

Rischio principale:

```text
Costruire il SaaS troppo presto e appesantire il prodotto prima di aver validato il metodo.
```

Mitigazione:

```text
Prima usare il framework su 2-3 progetti reali.
Poi estrarre ciò che è ripetibile.
```

