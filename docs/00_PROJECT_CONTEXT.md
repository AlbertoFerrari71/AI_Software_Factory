# 00 — Project Context

## 1. Origine

AI Software Factory nasce dall'esperienza pratica di sviluppo assistito da AI su progetti reali, in particolare Family Photo Organizer.

Il problema osservato è ricorrente:

1. una persona ha una buona idea;
2. l'idea viene descritta in linguaggio naturale;
3. ChatGPT aiuta a chiarirla;
4. Codex può modificare codice;
5. GitHub registra il lavoro;
6. i test verificano;
7. la documentazione dovrebbe restare aggiornata.

Senza metodo, però, il processo può diventare caotico:

- chat troppo lunghe;
- prompt non riutilizzabili;
- task troppo grandi;
- codice generato senza test;
- documentazione che resta indietro;
- branch confusi;
- automazioni rischiose;
- difficoltà a riprendere il lavoro dopo giorni.

AI Software Factory nasce per risolvere questo problema.

---

## 2. Definizione sintetica

AI Software Factory è un framework operativo che trasforma idee in software tramite una pipeline controllata:

```text
Idea → Requisiti → Architettura → Task → Codice → Test → Documentazione → Release → Apprendimento
```

Il metodo interno, Codex Alchemy Method, serve a trasformare materiale grezzo in output tecnico affidabile.

La visione operativa di Alberto sull'AI come collaboratrice verificabile e' documentata in `docs/project_context/VISIONE_OPERATIVA_AI.md`.

---

## 3. Utente principale

L'utente principale iniziale è Alberto Ferrari:

- imprenditore tecnico;
- esperienza pratica in VBA, C++, Excel, Access, un po' Python;
- uso di GitHub Desktop;
- interesse per sviluppo rapido ma controllato;
- molti progetti industriali, software e R&D;
- preferenza per codice semplice, robusto, leggibile, testato e documentato.

Obiettivo personale:

```text
Ridurre drasticamente i tempi di sviluppo senza perdere controllo tecnico, sicurezza e manutenibilità.
```

---

## 4. Target esteso futuro

Il framework deve poter servire anche:

### Persona non tecnica

- ha idee valide;
- non sa programmare;
- deve essere guidata con domande semplici;
- deve essere protetta da errori tecnici;
- non deve vedere complessità inutile.

### Persona tecnica

- vuole accelerare;
- vuole controllare branch, diff, test e PR;
- vuole usare strumenti AI in modo più strutturato;
- vuole ridurre lavoro ripetitivo senza perdere qualità.

---

## 5. Caso pilota

Family Photo Organizer è il primo laboratorio.

Caratteristiche rilevanti:

- archivio familiare di foto e video;
- import da cartelle, smartphone, cloud, WhatsApp, Telegram e fonti miste;
- inventario read-only iniziale;
- protezione da cancellazioni accidentali;
- quarantena per foto candidate alla cancellazione;
- futuro workflow collaborativo;
- GitHub, Codex, test e documentazione già usati nel processo.

Motivo della scelta:

```text
È un progetto reale, comprensibile, con rischi concreti e sufficiente complessità per testare il metodo.
```

---

## 6. Cosa il progetto NON è

AI Software Factory non è:

- un generatore di codice full-auto senza controllo;
- un sostituto del programmatore;
- un IDE;
- un semplice prompt lungo;
- una raccolta disordinata di template;
- un SaaS da costruire subito;
- un sistema che tocca file, dati o repo senza policy.

---

## 7. Problemi che deve risolvere

| Problema | Risposta del framework |
|---|---|
| Idea confusa | FASE 1, domande guidate, Project Charter |
| Prompt non riutilizzabili | Prompt template versionati |
| Task troppo grandi | Step 010/020/030 e Work Package Generator |
| Codice fragile | Verification Gate e acceptance criteria |
| Automazioni rischiose | Safety Model L0-L4 |
| Documentazione che si perde | Documentation Sync |
| Repo caotici | GitHub Workflow standard |
| Utente non tecnico confuso | Guided Mode |
| Utente tecnico rallentato | Expert Mode |

---

## 8. Prima misura di successo

Il progetto avrà successo nella prima fase se permette di:

1. aprire un nuovo progetto software;
2. chiarire idea e vincoli;
3. generare roadmap;
4. generare documentazione iniziale;
5. generare task Codex sicuri;
6. lavorare su branch;
7. verificare con test/checklist;
8. aggiornare documentazione;
9. ripetere il metodo su un altro progetto.

