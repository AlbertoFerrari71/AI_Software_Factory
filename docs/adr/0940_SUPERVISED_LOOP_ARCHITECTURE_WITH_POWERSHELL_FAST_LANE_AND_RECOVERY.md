# ADR 0940 - Supervised loop architecture with PowerShell Fast Lane and Recovery

**Data:** 2026-06-10
**Stato:** Accepted by Alberto, implementation deferred

---

## Contesto

ASF V1 ha gia' runner locali, state machine, Bridge output, manifest, human gates e un publish runner PowerShell con Phase A/B/C.

Il passo finale di architettura non e' costruire ASF V2. Serve invece chiudere ASF V1 come ciclo supervisionato end-to-end: pianificazione, esecuzione locale controllata, verifica, review, recovery e pubblicazione solo con approvazione esplicita.

---

## Problema

Un supervisor che invoca sempre modelli AI sarebbe lento, costoso e meno deterministico del necessario. Allo stesso tempo, un runner solo PowerShell non puo' decidere bene su scope, diagnosi ambigue, prompt Codex o review qualitativa.

ASF deve quindi scegliere la lane di esecuzione piu' adatta per ogni attivita', conservando evidence e stato in modo riprendibile.

---

## Decisione

ASF Supervisor non invoca sempre modelli AI.

Per ogni attivita' sceglie una execution lane:

1. Deterministic lane: PowerShell Fast Lane per comandi noti, veloci, ripetibili, verificabili e a basso costo.
2. Reasoning lane: GPT API / ChatGPT API per pianificazione, review, diagnosi errori, scelta del prossimo step e generazione prompt.
3. Code-editing lane: Codex CLI / `codex exec` per modifiche locali a codice, test e documentazione.

Il passaggio tra lane avviene tramite Bridge, `state.json`, report deterministici e semafori.

Regole vincolanti:

- GPT API non esegue direttamente PowerShell.
- GPT API puo' proporre o richiedere l'esecuzione di un tool.
- ASF Supervisor locale decide se il tool e' consentito.
- PowerShell runner esegue solo comandi o script autorizzati.
- Il risultato torna al ciclo tramite Bridge, report JSON e log.
- Alberto mantiene approval gate su publish, merge, deploy e milestone strategiche.

---

## Conseguenze

- Le attivita' meccaniche non consumano AI quando un comando deterministico basta.
- I passaggi di ragionamento restano separati dall'esecuzione locale.
- Codex resta executor locale per modifiche, non publisher automatico.
- Bridge diventa il piano di scambio tra planner, executor, reviewer e runner.
- `state.json` e' la verita' strutturata; i flag sono solo segnali semplici.
- Phase B richiede ancora `-ApprovePublish`.
- Phase C richiede ancora `-ApproveMerge`.

---

## Fuori scope

Questo ADR non implementa:

- loop automatico completo;
- chiamate API live;
- esecuzioni annidate di `codex exec`;
- nuova automazione publish/merge/deploy;
- refactoring pesante del publish runner;
- persistenza database;
- orchestratore SaaS.

---

## Guardrail

Il supervised loop resta fail-closed.

Stop immediato quando:

- rischio stimato passa a L3 o superiore senza approval;
- il comando e' distruttivo o fuori scope;
- serve credenziale o input umano;
- il diff esce dai file attesi;
- falliscono test, verify gate, workflow health o diff check;
- serve publish, merge o deploy;
- GPT reviewer non puo' motivare in modo chiaro un retry sicuro.

