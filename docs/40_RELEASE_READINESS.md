# Release Readiness

## 1. Scopo

Questo documento definisce quando AI Software Factory puo' essere usata come beta operativa local-first su un progetto reale.

La readiness qui descritta riguarda un pilot interno, controllato e manual-gated. Non dichiara il framework pronto come prodotto pubblico, SaaS, release esterna o servizio general purpose.

L'obiettivo e' decidere se avviare un primo progetto pilota con rischi compresi, scope piccolo e verifiche locali ripetibili.

---

## 2. Stato di maturita' attuale

Livelli usati dal progetto:

- **Experimental**: metodo ancora esplorativo, con molte parti non stabilizzate.
- **Beta operativa local-first**: workflow usabile localmente con branch dedicati, documentazione viva, test e controllo umano.
- **Pilot ready**: adatto a un progetto reale selezionato, con scope iniziale piccolo, reversibile e verificato.
- **Stable internal release**: utilizzabile internamente su piu' progetti con procedure consolidate.
- **Public/SaaS ready**: adatto a distribuzione esterna, multiutente, packaging pubblico, sicurezza e governance piu' mature.

Stato attuale: AI Software Factory punta a essere valutata come **Beta operativa local-first / Pilot ready** per un pilot interno. Non e' classificata come **Public/SaaS ready**.

---

## 3. Cosa e' gia' pronto

Componenti maturi per un pilot controllato:

- Prompt Packet Generator;
- validazione Lite;
- validazione Strict;
- Release Smoke Workflow;
- Prompt Packet Lifecycle Checklist;
- Developer Onboarding;
- Project Workflow Index;
- Workflow Health Check;
- Workflow Quick Reference;
- Step Closure Report;
- Workflow Command Cookbook;
- Workflow Status Dashboard;
- ASF Next Step Runner;
- ASF Codex Report Intake;
- ASF Human-Gated Closure Pack;
- ASF Human Approval Gate;
- ASF Codex Invocation Dry Run Pack;
- Verification Gate;
- Documentation Sync;
- soft guardrails locali.

Questi elementi non eliminano il controllo umano. Rendono pero' piu' ripetibile il ciclo: preparazione step, task packet, validazione, Codex, report, verifiche, PR, merge, chiusura e scelta step successivo.

---

## 4. Cosa e' beta / da usare con attenzione

Parti da usare con attenzione durante un pilot:

- adattamento a progetti esistenti;
- health check non ancora specifico per repo esterni;
- assenza di dashboard grafica;
- assenza di schema formale task packet;
- assenza di integrazione CI per tutti i controlli;
- gestione manuale di PR/check/merge;
- branch protection reale non disponibile sul repository privato con piano attuale.

Questi punti non bloccano un pilot, ma devono essere registrati come WARNING quando impattano il progetto candidato.

---

## 5. Cosa non e' ancora pronto

Non sono ancora disponibili:

- SaaS;
- installer;
- PyPI package;
- GitHub Release pubblica;
- project skeleton generator completo;
- integrazione automatica cross-repository;
- UI web;
- gestione multi-progetto centralizzata.

Un pilot non deve dipendere da questi elementi.

---

## 6. Criteri go/no-go per un pilot

### GO

Un progetto candidato e' GO quando:

- il repository pilota e' sotto controllo Git;
- esiste o puo' essere creato un branch dedicato;
- la working tree pulita e' verificata prima dello step;
- test minimi sono presenti oppure esistono verifiche manuali chiare;
- l'owner del progetto e' disponibile a verificare diff, test e stato Git;
- il primo step pilota e' piccolo e reversibile;
- nessun dato sensibile deve essere modificato automaticamente;
- Verification Gate e Workflow Health Check sono eseguibili nel contesto del repository o adattabili manualmente.

### WARNING

Continuare solo con nota esplicita quando:

- il repository ha test parziali;
- la documentazione e' incompleta;
- sono presenti branch remoti vecchi;
- compaiono warning LF/CRLF non bloccanti;
- PR checks non disponibili richiedono verifica manuale;
- il progetto e' gia' a meta' sviluppo;
- il progetto è un progetto già a metà sviluppo e richiede prima una fotografia dello stato reale.

### NO-GO

Fermarsi quando:

- la working tree e' sporca e non compresa;
- non esiste backup o controllo Git;
- viene richiesta una modifica direttamente su `main`;
- il primo step pilota e' troppo ampio;
- lo step richiede di toccare secret o dati sensibili;
- il primo step richiede refactor massivo;
- il rollback non e' chiaro;
- l'owner non puo' verificare l'esito.

---

## 7. Progetto pilota ideale

Un progetto adatto al pilot:

- e' gia' versionato;
- e' abbastanza importante da essere realistico, ma non critico per il primo esperimento;
- ha un obiettivo chiaro;
- ha repository leggibile;
- ha una porzione piccola su cui intervenire;
- permette branch dedicato;
- ha test automatici o verifiche manuali ripetibili;
- non richiede modifiche iniziali a segreti, produzione, dati reali o CI.

---

## 8. Progetti esistenti gia' a meta' sviluppo

Un progetto gia' avviato puo' essere adatto al pilot. Prima serve pero':

- Project Intake;
- lettura di README e documentazione disponibile;
- analisi branch e stato Git;
- fotografia dei test disponibili;
- identificazione dei rischi;
- scelta di un primo step piccolo;
- divieto di refactor ampio iniziale.

Il primo intervento deve aumentare chiarezza e controllo, non cambiare architettura in modo esteso.

---

## 9. Primo step pilota consigliato

Il primo step su un progetto reale dovrebbe essere preferibilmente:

- documentale;
- diagnostico;
- di onboarding;
- di health/status check locale;
- oppure una modifica piccola e reversibile.

Evitare come primo step:

- refactor architetturali;
- migrazioni dati;
- modifiche CI;
- modifiche sicurezza;
- modifiche distruttive.

---

## 10. Readiness checklist

### Repository readiness

- [ ] Repository sotto Git.
- [ ] Branch principale identificato.
- [ ] Branch dedicato possibile.
- [ ] Working tree pulita prima dello step.
- [ ] Nessuna modifica locale non compresa.

### Workflow readiness

- [ ] Prompt Packet Generator disponibile.
- [ ] Validazione Lite disponibile.
- [ ] Validazione Strict disponibile quando utile.
- [ ] Workflow Status Dashboard eseguibile o sostituibile con comandi equivalenti.
- [ ] Workflow Health Check eseguibile o adattabile.
- [ ] Workflow Command Cookbook disponibile come riferimento.

### Documentation readiness

- [ ] README o documento equivalente presente.
- [ ] Obiettivo del pilot documentato.
- [ ] Rischi iniziali documentati.
- [ ] Documentation Sync applicabile.

### Test readiness

- [ ] Test automatici presenti oppure verifiche manuali ripetibili.
- [ ] Comando test documentato.
- [ ] Verification Gate eseguibile o equivalente manuale definito.
- [ ] PR checks disponibili oppure assenza documentata come WARNING.

### Safety readiness

- [ ] Nessun secret da modificare.
- [ ] Nessun dato sensibile da toccare automaticamente.
- [ ] Nessuna modifica diretta su `main`.
- [ ] Nessuna automazione commit/push/PR/merge.
- [ ] Rollback o revert chiaro.

### Pilot scope readiness

- [ ] Primo step piccolo.
- [ ] Primo step reversibile.
- [ ] Nessun refactor massivo iniziale.
- [ ] Owner disponibile per review.

### Closure/report readiness

- [ ] Step Closure Report disponibile.
- [ ] Stato finale da registrare.
- [ ] Test finali da registrare.
- [ ] Workflow Health Check da registrare.
- [ ] Prossimo step da decidere.

---

## 11. Decisione finale

Esiti ammessi:

- **GO pilot**: tutti i criteri essenziali sono soddisfatti.
- **GO pilot with warnings**: il pilot puo' partire, ma i WARNING sono registrati e accettati.
- **HOLD**: mancano informazioni o serve preparazione prima di decidere.
- **NO-GO**: uno o piu' rischi bloccanti rendono il pilot non accettabile.

La decisione deve indicare motivazione, rischi residui, primo step pilota e prossimo controllo.

---

## 12. Relazione con i documenti esistenti

Riferimenti principali:

- `docs/34_PROJECT_WORKFLOW_INDEX.md`
- `docs/35_WORKFLOW_HEALTH_CHECK.md`
- `docs/36_WORKFLOW_QUICK_REFERENCE.md`
- `docs/37_STEP_CLOSURE_REPORT.md`
- `docs/38_WORKFLOW_COMMAND_COOKBOOK.md`
- `docs/39_WORKFLOW_STATUS_DASHBOARD.md`
- `docs/42_ASF_NEXT_STEP_RUNNER.md`

La readiness non sostituisce questi documenti. Li usa come evidenze operative per decidere se iniziare un pilot.

---

## 13. Prossimo step dopo readiness

Lo step successivo alla readiness e' il protocollo di onboarding per progetti esistenti:

```text
docs/41_EXISTING_PROJECT_PILOT_ONBOARDING.md
```

Scopo: preparare l'applicazione del metodo a un progetto reale gia' avviato, partendo da intake, fotografia del repository, rischi e primo step pilota sicuro.

Il prossimo step operativo naturale dopo l'onboarding e':

```text
300) ASF Next Step Runner
310-330) ASF Runner Upgrade Pack
340-360) ASF Runner Automation Readiness Pack
370-390) ASF Automation Bridge Pack
```

Scopo: preparare localmente task packet, handoff Codex, report, Verification Pack, report intake, closure pack, Human Approval Gate e dry-run preview senza modificare repository esterne, senza invocare Codex e senza eseguire automaticamente commit/push/PR/merge.
