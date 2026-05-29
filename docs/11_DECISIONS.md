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

Uno step futuro dovra' implementare un registry tool coerente con questa policy.

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

---

## DEC-028 - Documentation Sync come regola di completamento

**Data:** 2026-05-27
**Stato:** Accettata

### Contesto

Dopo l'introduzione del Verification Gate serve una regola stabile per evitare che roadmap, changelog, decision log e documenti centrali restino indietro rispetto alle modifiche mergiate.

### Decisione

Introdurre `docs/21_DOCUMENTATION_SYNC.md` come riferimento centrale e classificare i documenti in:

- always check;
- update when relevant;
- do not touch unless needed.

Documentation Sync entra nel Verification Gate e nel PR template. Nello STEP 080 non vengono introdotti script dedicati, nuove dipendenze, lint o scan: i controlli minimi restano pytest e review manuale.

### Motivazione

Il metodo deve prevenire disallineamenti senza trasformare ogni step in burocrazia o generare churn documentale inutile.

### Conseguenze

Ogni step futuro deve dichiarare nel report finale le verifiche documentali svolte, distinguere documenti aggiornati da documenti solo controllati e non modificare documenti per zelo.

---

## DEC-029 - Branch Protection Policy per main

**Data:** 2026-05-27
**Stato:** Accettata

### Contesto

Dopo Verification Gate e Documentation Sync serve una policy chiara per proteggere `main` da push diretti, merge senza CI, force push, deletion e modifiche non verificate.

### Decisione

Introdurre `docs/22_BRANCH_PROTECTION_POLICY.md` come riferimento centrale.

La policy documenta sia branch protection rules sia GitHub rulesets. Il livello minimo raccomandato per `main` richiede:

- pull request obbligatoria;
- CI verde prima del merge;
- force push bloccato;
- deletion bloccata;
- admin bypass solo per emergenza o recovery.

Nello STEP 090 non viene applicata nessuna regola reale su GitHub. L'implementazione concreta e' rimandata allo STEP 100.

### Motivazione

Il progetto deve proteggere `main` senza introdurre automatismi rischiosi o configurazioni remote prima che la policy sia chiara.

### Conseguenze

Gli step futuri devono trattare modifiche a branch protection e rulesets come azioni GitHub separate, da approvare esplicitamente e verificare dopo applicazione.

---

## DEC-030 - Branch protection scripts safe-by-default

**Data:** 2026-05-27
**Stato:** Accettata

### Contesto

Dopo la Branch Protection Policy serve preparare strumenti operativi per applicare e verificare la protezione di `main`, senza lasciare a Codex il potere di modificare GitHub durante lo step.

### Decisione

Introdurre script locali in `scripts/github/`:

- `detect_required_checks.ps1` per rilevare candidati read-only;
- `apply_branch_protection.ps1` per generare payload e applicare solo con `-Apply`;
- `verify_branch_protection.ps1` per leggere la configurazione corrente.

La branch protection classica viene scelta per semplicità operativa nello STEP 100. GitHub rulesets restano hardening futuro.

`apply_branch_protection.ps1` e' DryRun di default, richiede `-RequiredCheckName`, e l'applicazione reale richiede `-Apply` piu' conferma esplicita.

### Motivazione

Gli script rendono l'applicazione ripetibile e revisionabile, ma mantengono separata la preparazione locale dalla modifica remota effettiva.

### Conseguenze

Codex puo' creare e testare documentalmente gli script, ma non deve eseguirli in modalita' applicativa. Alberto dovra' scegliere o confermare il nome reale del required check CI prima dell'applicazione.

---

## DEC-031 - Branch protection plan limit and soft protection fallback

**Data:** 2026-05-28
**Stato:** Accettata

### Contesto

Durante STEP 110-A gli script STEP 100 hanno rilevato il nome reale del check CI, ma la lettura della branch protection ha restituito HTTP 403 sul repository privato con il piano GitHub attuale.

### Decisione

Il required check CI reale per questo repository e':

```text
Verification Gate
```

La branch protection reale non viene applicata nello stato corrente perche' GitHub richiede GitHub Pro/Team oppure repository pubblico per questa funzionalita' sul repo privato.

Il repository non viene reso pubblico solo per ottenere branch protection. Finche' il piano non supporta protected branches o non viene scelto GitHub Pro/Team, il progetto usa una soft protection temporanea:

- branch dedicato;
- PR verso `main`;
- Verification Gate locale;
- CI verde;
- controllo manuale Alberto;
- nessun direct push volontario su `main`.

`apply_branch_protection.ps1 -Apply` non deve essere eseguito finche' il limite di piano non e' risolto e la decisione non e' approvata esplicitamente.

### Motivazione

La sicurezza operativa non deve dipendere da una configurazione GitHub non disponibile. Rendere pubblico il repository solo per aggirare il limite introdurrebbe un rischio e una scelta di visibilita' non motivata dal progetto.

### Conseguenze

Lo STEP 120 consigliato e' Soft Protection Guardrails, per ridurre il rischio di push accidentale su `main` finche' manca hard protection GitHub.

---

## DEC-032 - Soft protection guardrails opt-in

**Data:** 2026-05-28
**Stato:** Accettata

### Contesto

Dopo STEP 110, GitHub branch protection reale resta non disponibile sul repository privato con il piano attuale. Serve ridurre il rischio pratico di commit o push accidentali su `main` senza modificare GitHub e senza installare automazioni locali in modo invisibile.

### Decisione

Introdurre soft guardrails locali opt-in:

- hook versionati in `.githooks/`;
- `pre-commit` che blocca commit su `main`;
- `pre-push` che blocca push verso `main`;
- installazione manuale tramite `scripts/git/install_soft_guardrails.ps1`;
- verifica read-only tramite `scripts/git/check_soft_guardrails.ps1`;
- bypass solo tramite variabile esplicita `ASF_ALLOW_MAIN_BYPASS=1`;
- nessuna installazione automatica degli hook da parte di Codex.

### Motivazione

I guardrail locali riducono gli errori comuni sul computer operativo senza fingere che esista hard protection GitHub. L'installazione opt-in mantiene il controllo umano su `git config core.hooksPath`.

### Conseguenze

Soft protection non sostituisce hard protection GitHub. Quando GitHub Pro/Team o rulesets saranno disponibili, la protezione reale dovra' essere preferita. Lo STEP 130 consigliato e' Prompt Packet Hardening, per portare questi vincoli nei task packet e nei prompt operativi.

---

## DEC-033 - Prompt Packet Hardening

**Data:** 2026-05-28
**Stato:** Accettata

### Contesto

Dopo Verification Gate, Documentation Sync e Soft Protection Guardrails, i futuri task packet devono rendere questi vincoli espliciti prima dell'esecuzione Codex.

### Decisione

Introdurre `docs/25_PROMPT_PACKET_HARDENING.md` come riferimento centrale.

I task packet futuri devono includere:

- sezioni minime operative;
- forbidden actions standard;
- allowed scope esplicito;
- forbidden scope esplicito;
- Verification Gate;
- Documentation Sync;
- Soft Protection awareness;
- report finale Codex standard con step, tempo, stato e prossimo step.

Nello STEP 130 non viene introdotto uno schema rigido o un parser dedicato. La validazione leggera e' rimandata allo STEP 140.

### Motivazione

Prompt e task packet troppo liberi aumentano il rischio di modifiche fuori scope, refactor non richiesti, report incompleti e controlli non eseguiti.

### Conseguenze

I template Codex vengono rafforzati, ma restano leggibili e modificabili da Alberto. Lo STEP 140 consigliato e' Prompt Packet Validation Lite.

---

## DEC-034 - Prompt Packet Validation Lite

**Data:** 2026-05-28
**Stato:** Accettata

### Contesto

Dopo Prompt Packet Hardening serve un controllo leggero per intercettare task packet incompleti prima dell'esecuzione Codex, senza introdurre ancora uno schema rigido.

### Decisione

Introdurre `scripts/validate_task_packet.py` come validatore Python basato solo su standard library.

Il validatore controlla sezioni e concetti minimi:

- project context;
- branch instructions;
- allowed scope;
- forbidden scope;
- forbidden actions;
- Verification Gate;
- Documentation Sync;
- Soft Protection awareness;
- report finale Codex.

Gli exit code sono:

- `0` per validazione passata;
- `1` per validazione fallita;
- `2` per errore di uso o input.

Nello STEP 140 il validatore non viene integrato automaticamente in CI o nel Verification Gate. Lo schema rigido resta rimandato.

### Motivazione

Un controllo leggero riduce task packet vaghi o incompleti, ma mantiene i prompt modificabili e leggibili. La qualita' semantica resta responsabilita' della revisione umana.

### Conseguenze

I task packet centrali possono essere validati manualmente prima dell'uso. Lo STEP 150 consigliato e' Prompt Packet Examples and Golden Samples, per aggiungere esempi positivi e negativi stabili.

---

## DEC-035 - Prompt Packet golden samples

**Data:** 2026-05-28
**Stato:** Accettata

### Contesto

Dopo il validatore Lite serve un set di esempi stabili per documentare il formato minimo e proteggere il comportamento atteso del validatore.

### Decisione

Introdurre golden samples in `examples/task_packets/`:

- `examples/task_packets/valid/step_valid_minimal_task_packet.md` deve passare la validazione;
- `examples/task_packets/invalid/missing_forbidden_actions.md` deve fallire;
- `examples/task_packets/invalid/missing_scope.md` deve fallire;
- `examples/task_packets/invalid/missing_final_report.md` deve fallire.

Nello STEP 150 non viene introdotta modalita' strict e non viene irrigidito il validatore oltre il comportamento Lite necessario per i campioni.

### Motivazione

I golden samples rendono il validatore piu' mantenibile: un cambiamento futuro puo' essere verificato contro esempi validi e invalidi senza interpretare ogni volta il comportamento desiderato.

### Conseguenze

Le modifiche future al validatore devono preservare il passaggio del sample valido e il fallimento degli invalidi. Lo STEP 160 consigliato e' Prompt Packet Validation Strict Mode.

---

## DEC-036 - Prompt Packet Validation Strict Mode

**Data:** 2026-05-28
**Stato:** Accettata

### Contesto

Dopo Lite validator e golden samples serve una modalita' opzionale piu' severa per controllare task packet importanti senza rendere rigido il formato di default.

### Decisione

Introdurre il flag `--strict` in `scripts/validate_task_packet.py`.

Lite resta il comportamento di default:

```powershell
python scripts/validate_task_packet.py <file>
```

Strict e' esplicito:

```powershell
python scripts/validate_task_packet.py --strict <file>
```

Strict usa controlli granulari ma ancora keyword-based su:

- branch e working tree;
- allowed scope;
- forbidden scope;
- forbidden actions complete;
- Verification Gate;
- Documentation Sync;
- Soft Protection;
- report finale Codex.

Nello STEP 160 non viene introdotto uno schema formale JSON/YAML e Strict non viene integrato automaticamente in CI o nel Verification Gate.

### Motivazione

La modalita' Strict aumenta il controllo sui task packet piu' importanti senza rompere compatibilita' con Lite e senza anticipare un parser formale.

### Conseguenze

I golden samples Strict diventano riferimento per evoluzioni future. Lo STEP 170 consigliato e' Prompt Packet Generator CLI Hardening.

---

## DEC-037 - Prompt Packet Generator CLI Hardening

**Data:** 2026-05-28
**Stato:** Accettata

### Contesto

Dopo Lite, golden samples e Strict Mode, il Prompt Packet Generator deve poter produrre bozze di task packet da parametri espliciti senza dipendere da copia manuale del template.

### Decisione

Introdurre `scripts/generate_task_packet.py` come CLI locale basata solo su standard library.

La CLI supporta:

- `--step`;
- `--title`;
- `--branch`;
- `--objective`;
- `--output`;
- `--print`;
- `--force`;
- `--strict-ready`.

La CLI valida input essenziali, crea la cartella di output se necessario, non chiama GitHub API, non esegue comandi Git e genera Markdown compatibile con Lite e Strict.

### Motivazione

Un generatore minimale riduce errori ricorrenti nei task packet senza introdurre schema formale, dipendenze esterne o automazione eccessiva.

### Conseguenze

I task packet generati restano bozze da revisionare. Lo STEP 180 consigliato e' Prompt Packet Generator Packaging, per rendere il generatore piu' riusabile senza anticipare integrazioni OpenAI o MCP.

---

## DEC-038 - Prompt Packet Generator Packaging

**Data:** 2026-05-28
**Stato:** Accettata

### Contesto

Dopo l'hardening della CLI serve rendere il Prompt Packet Generator piu' comodo da usare localmente, senza introdurre pubblicazione esterna o packaging Python prematuro.

### Decisione

Introdurre packaging locale attorno alla CLI esistente:

- `scripts/generate_task_packet.py` resta la fonte della logica;
- `scripts/generate_task_packet.ps1` e' un wrapper PowerShell sottile;
- `docs/30_PROMPT_PACKET_GENERATOR_PACKAGING.md` documenta uso, limiti e validazione;
- `examples/task_packets/generated/step_180_generated_packaging_sample.md` e' il sample generato versionato;
- non viene pubblicato nulla su PyPI o registry;
- non vengono modificati PATH, profili PowerShell, hook Git o `core.hooksPath`.

### Motivazione

Un packaging locale riduce attrito d'uso e copia/incolla in PowerShell, ma mantiene il progetto local-first, revisionabile e senza nuove dipendenze.

### Conseguenze

Le evoluzioni future devono continuare a evitare duplicazione della logica del generatore. Lo STEP 190 consigliato e' Prompt Packet Generator Release Smoke Workflow, per rendere ripetibile la verifica end-to-end locale.

---

## DEC-039 - Prompt Packet Generator Release Smoke Workflow

**Data:** 2026-05-28
**Stato:** Accettata

### Contesto

Dopo il packaging locale del generatore serve una verifica rapida e ripetibile per confermare che il tool funzioni come strumento operativo interno.

### Decisione

Introdurre uno smoke workflow locale:

- script `scripts/smoke_prompt_packet_release.ps1`;
- generazione di un task packet temporaneo sotto `tmp/`;
- uso del wrapper `scripts/generate_task_packet.ps1`;
- validazione Lite con `scripts/validate_task_packet.py`;
- validazione Strict con `scripts/validate_task_packet.py --strict`;
- documento `docs/31_PROMPT_PACKET_GENERATOR_RELEASE_SMOKE_WORKFLOW.md`.

Lo smoke workflow non crea release pubbliche, non pubblica su PyPI o registry, non modifica CI, non modifica GitHub e non installa nulla.

### Motivazione

Il generatore deve essere controllabile localmente prima di essere considerato pronto dopo modifiche a CLI, wrapper, packaging o documentazione.

### Conseguenze

Lo smoke workflow affianca il Verification Gate ma non lo sostituisce. Lo STEP 200 consigliato e' Prompt Packet Generator Developer Onboarding, per trasformare CLI, packaging e smoke workflow in una procedura di uso quotidiano.

---

## DEC-040 - Prompt Packet Lifecycle Checklist

**Data:** 2026-05-29
**Stato:** Accettata

### Contesto

Dopo generator, packaging e smoke workflow serve una checklist unica che copra l'intero ciclo operativo dello step, non solo la produzione del task packet.

### Decisione

Introdurre la Prompt Packet Lifecycle Checklist:

- documento `docs/32_PROMPT_PACKET_LIFECYCLE_CHECKLIST.md`;
- template spuntabile `templates/codex_tasks/prompt_packet_lifecycle_checklist.md`;
- fasi da preparazione step a verifica che il merge sia su `main`;
- distinzione esplicita tra azioni Codex e azioni Alberto;
- troubleshooting per errori operativi comuni;
- anti-pattern, incluso trattare il report Codex come merge gia' avvenuto.

La checklist resta manuale: non vengono creati script per automatizzare commit, push, PR o merge.

### Motivazione

Il rischio principale emerso non e' solo tecnico, ma di handoff: uno step puo' essere completato localmente senza essere pushato, senza PR, senza merge o senza `main` aggiornato prima dello step successivo.

### Conseguenze

Ogni step futuro puo' usare la checklist per verificare prerequisiti, task packet, report Codex, pre-commit, PR/merge e avvio dello step successivo. Lo STEP 210 consigliato e' Prompt Packet Generator Developer Onboarding.
