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

---

## DEC-041 - Prompt Packet Generator Developer Onboarding

**Data:** 2026-05-29
**Stato:** Accettata

### Contesto

Dopo generator, packaging, smoke workflow e lifecycle checklist serve una guida rapida per chi deve usare il Prompt Packet Generator senza conoscere tutta la storia del progetto.

### Decisione

Introdurre `docs/33_PROMPT_PACKET_GENERATOR_DEVELOPER_ONBOARDING.md` come guida onboarding per sviluppatori e utilizzatori interni.

La guida raccoglie:

- contesto minimo di AI Software Factory e Codex Alchemy Method;
- mappa degli strumenti del generatore;
- Quickstart PowerShell;
- Lite Mode, Strict Mode, Verification Gate e Release Smoke Workflow;
- Prompt Packet Lifecycle Checklist;
- ruoli di ChatGPT, Codex e Alberto;
- errori comuni e troubleshooting rapido.

Non vengono introdotti script per automatizzare commit, push, PR o merge.

### Motivazione

Il workflow e' ormai utile, ma distribuito tra piu' documenti. Una guida onboarding riduce il costo di ingresso e previene errori operativi come partire dallo step successivo prima che il precedente sia su `main`.

### Conseguenze

I documenti del generatore possono rimandare alla guida come entry point pratico. Lo STEP 220 consigliato e' Project Workflow Index, per costruire un indice operativo piu' ampio del metodo.

---

## DEC-042 - Project Workflow Index

**Data:** 2026-05-29
**Stato:** Accettata

### Contesto

Dopo onboarding, lifecycle checklist, smoke workflow, validation e Documentation Sync, il metodo ha molti documenti operativi utili ma distribuiti.

### Decisione

Introdurre `docs/34_PROJECT_WORKFLOW_INDEX.md` come indice operativo centrale del workflow AI Software Factory.

L'indice collega:

- Prompt Packet Generator;
- Lite Mode e Strict Mode;
- Verification Gate;
- Documentation Sync;
- Soft Protection Guardrails;
- Release Smoke Workflow;
- Lifecycle Checklist;
- Developer Onboarding;
- script e template principali;
- troubleshooting Git, PR e merge.

L'indice non duplica integralmente i documenti specifici e non introduce automazioni Git.

### Motivazione

Serve un punto di ingresso unico per capire quale documento leggere e quale comando usare senza rileggere tutta la storia degli step.

### Conseguenze

I futuri cambiamenti a workflow, script, template o checklist devono valutare se aggiornare l'indice. Lo STEP 230 consigliato e' Workflow Health Check, per controllare che documenti operativi e riferimenti restino coerenti.

---

## DEC-043 - Workflow Health Check locale read-only

**Data:** 2026-05-29
**Stato:** Accettata

### Contesto

Dopo Project Workflow Index serve un controllo leggero per verificare che documenti, script, template e riferimenti principali del workflow restino presenti e navigabili.

### Decisione

Introdurre `scripts/check_workflow_health.py` come controllo locale read-only del workflow.

Il check verifica:

- file principali presenti;
- riferimenti critici in `docs/34_PROJECT_WORKFLOW_INDEX.md`;
- riferimenti critici in `docs/33_PROMPT_PACKET_GENERATOR_DEVELOPER_ONBOARDING.md`;
- passaggi critici in `docs/32_PROMPT_PACKET_LIFECYCLE_CHECKLIST.md`;
- assenza di pattern Git/GitHub pericolosi negli script workflow operativi.

Il runbook e' `docs/35_WORKFLOW_HEALTH_CHECK.md`.

Nello STEP 230 il check non viene integrato in CI e non viene aggiunto a `scripts/verify.ps1`.

### Motivazione

Il workflow cresce per documenti e strumenti. Un controllo locale read-only riduce regressioni di navigabilita' senza introdurre nuove automazioni Git o dipendenze.

### Conseguenze

Quando cambiano documenti operativi, script workflow o riferimenti centrali, il Workflow Health Check deve essere eseguito insieme al Verification Gate. Lo STEP 240 consigliato e' Workflow Quick Reference.

---

## DEC-044 - Workflow Quick Reference

**Data:** 2026-05-29
**Stato:** Accettata

### Contesto

Dopo Project Workflow Index e Workflow Health Check serve una scheda compatta per i comandi quotidiani, senza rileggere ogni volta lifecycle, onboarding e documenti lunghi.

### Decisione

Introdurre `docs/36_WORKFLOW_QUICK_REFERENCE.md` come quick reference operativa del workflow AI Software Factory.

La scheda raccoglie:

- generazione task packet strict-ready;
- validazione Lite Mode e Strict Mode;
- Release Smoke Workflow;
- Workflow Health Check;
- Verification Gate;
- Soft Protection Guardrails check;
- pre-commit manuale;
- PR checks e merge presidiato;
- verifica finale su `main`.

I comandi di commit, push, PR e merge sono documentati come riferimento presidiato per Alberto, non come automazione per Codex.

### Motivazione

Il workflow e' ormai navigabile, ma l'operatore ha bisogno di una pagina breve per l'uso quotidiano. Una quick reference riduce errori senza duplicare integralmente Project Workflow Index, Lifecycle Checklist o Developer Onboarding.

### Conseguenze

Il Project Workflow Index e il Workflow Health Check includono la quick reference come documento operativo centrale. Lo STEP 250 consigliato e' Step Closure Report, per standardizzare il riepilogo post-merge e la chiusura dello step prima del successivo.

---

## DEC-045 - Step Closure Report

**Data:** 2026-05-29
**Stato:** Accettata

### Contesto

Dopo Workflow Quick Reference serve uno standard per dichiarare quando uno step e' davvero chiuso. Il report Codex locale non basta: uno step puo' essere completato sul branch ma non ancora pushato, senza PR, senza merge o senza verifica finale su `main`.

### Decisione

Introdurre `docs/37_STEP_CLOSURE_REPORT.md` e `templates/codex_tasks/step_closure_report_template.md`.

Lo Step Closure Report distingue:

- completamento locale Codex;
- commit sul branch;
- push;
- PR;
- check PR;
- merge;
- pull di `main`;
- test finali;
- Verification Gate;
- Workflow Health Check;
- working tree pulita;
- prossimo step.

Il report documenta anche il caso in cui `gh pr checks --watch` restituisce `no checks reported on the branch`: va registrato come attenzione da verificare, non come prova automatica di fallimento del codice.

### Motivazione

Il metodo deve impedire che un report locale venga scambiato per step chiuso su `main`. Separare stati e prove riduce errori operativi prima dello step successivo.

### Conseguenze

Lifecycle Checklist, Project Workflow Index, Workflow Quick Reference e Workflow Health Check includono il nuovo riferimento di chiusura. Lo STEP 260 consigliato e' Workflow Command Cookbook, per raccogliere scenari e comandi manuali ricorrenti senza introdurre automazioni Git rischiose.

---

## DEC-046 - Workflow Command Cookbook

**Data:** 2026-05-29
**Stato:** Accettata

### Contesto

Dopo Quick Reference e Step Closure Report serve un riferimento pratico per scenari operativi specifici, non solo una lista breve di comandi.

### Decisione

Introdurre `docs/38_WORKFLOW_COMMAND_COOKBOOK.md` come ricettario operativo del workflow AI Software Factory.

Il Cookbook raccoglie ricette per:

- stato iniziale prima di uno step;
- verifica prerequisito su `main`;
- generazione e validazione task packet;
- controlli dopo report Codex;
- commit, push e PR presidiati da Alberto;
- PR checks non disponibili;
- merge e verifica finale su `main`;
- branch remoto assente;
- modifiche sul branch sbagliato;
- working tree sporca su `main`;
- health check e Verification Gate falliti;
- pulizia riferimenti remoti vecchi;
- warning CRLF/LF;
- preparazione dello Step Closure Report.

Il Cookbook documenta comandi manuali, non script. Non introduce automazioni Git, non modifica CI e non cambia GitHub.

### Motivazione

Gli errori operativi piu' probabili avvengono in scenari concreti: branch locale senza remoto, check PR assenti, main non aggiornato, working tree sporca o confusione tra report Codex e merge su `main`. Un ricettario riduce ambiguita' senza aumentare i permessi degli agenti.

### Conseguenze

Project Workflow Index, Workflow Quick Reference, Step Closure Report e Workflow Health Check includono il Cookbook come riferimento operativo centrale. Lo STEP 270 consigliato e' Workflow Status Dashboard, per rendere visibile lo stato degli step usando fonti manuali o read-only.

---

## DEC-047 - Workflow Status Dashboard

**Data:** 2026-05-29
**Stato:** Accettata

### Contesto

Dopo Workflow Command Cookbook serve una vista rapida dello stato locale del workflow senza aprire tutti i documenti operativi.

### Decisione

Introdurre `scripts/show_workflow_status.py` e `docs/39_WORKFLOW_STATUS_DASHBOARD.md`.

La dashboard e' locale, read-only e basata su Python standard library. Mostra:

- branch corrente;
- stato working tree CLEAN/DIRTY;
- ultimi commit;
- documenti centrali presenti;
- script principali presenti;
- controlli locali suggeriti.

La dashboard non usa GitHub API, non richiede rete, non modifica file o configurazioni, non fa commit, push, PR o merge e non sostituisce Verification Gate, Workflow Health Check o PR checks.

### Motivazione

Serve uno snapshot operativo rapido per ridurre il costo di orientamento e riconoscere subito se si e' sul branch corretto, con working tree pulita o sporca, e se i riferimenti workflow principali sono presenti.

### Conseguenze

Project Workflow Index, Workflow Health Check, Workflow Quick Reference e Workflow Command Cookbook includono la dashboard. Lo STEP 280 consigliato e' Release Readiness.

---

## DEC-048 - Release Readiness

**Data:** 2026-05-29
**Stato:** Accettata

### Contesto

Dopo Workflow Status Dashboard il framework ha abbastanza elementi operativi per valutare un primo pilot interno su un progetto reale. Serve pero' distinguere readiness per pilot local-first da release pubblica, SaaS, packaging esterno o automazione remota.

### Decisione

Introdurre `docs/40_RELEASE_READINESS.md` e `templates/codex_tasks/release_readiness_checklist.md`.

La readiness definisce:

- livelli di maturita' da Experimental a Public/SaaS ready;
- stato corrente come Beta operativa local-first / Pilot ready da valutare;
- componenti gia' pronti;
- componenti beta da usare con attenzione;
- componenti non ancora disponibili;
- criteri GO, WARNING e NO-GO per un pilot;
- criteri per progetti esistenti gia' a meta' sviluppo;
- primo step pilota consigliato piccolo e reversibile.

La decisione non dichiara AI Software Factory pronta come prodotto pubblico o SaaS.

### Motivazione

Il metodo deve poter essere provato su un progetto reale senza confondere pilot interno con release esterna. La checklist rende espliciti rischi, requisiti minimi, dati sensibili, test, branch dedicato, owner umano e criteri di chiusura.

### Conseguenze

Project Workflow Index, Workflow Health Check, Workflow Quick Reference, Workflow Command Cookbook e Workflow Status Dashboard includono Release Readiness. Lo STEP 290 consigliato e' Existing Project Pilot Onboarding.

---

## DEC-049 - Existing Project Pilot Onboarding

**Data:** 2026-05-29
**Stato:** Accettata

### Contesto

Dopo Release Readiness serve una procedura pratica per applicare AI Software Factory a un progetto reale gia' avviato senza trattarlo come un progetto nuovo e senza modificare subito repository esterne.

Un progetto esistente puo' avere branch, working tree, test, documentazione, dati sensibili, secret, debito tecnico, CI e decisioni pregresse gia' presenti.

### Decisione

Introdurre `docs/41_EXISTING_PROJECT_PILOT_ONBOARDING.md` come protocollo di Existing Project Pilot Onboarding.

Il protocollo definisce:

- Project Intake;
- fotografia dello stato Git;
- lettura della documentazione;
- mappa file/cartelle;
- stato test;
- rischi;
- decisione GO/WARNING/NO-GO;
- scelta del primo step pilota piccolo e reversibile;
- produzione del primo task packet pilot.

Vengono introdotti anche:

- `templates/codex_tasks/existing_project_intake_template.md`;
- `templates/codex_tasks/first_pilot_step_packet_template.md`.

Lo step non applica ancora il metodo a repository esterne e non crea automazioni cross-repository.

### Motivazione

Il primo pilot reale deve aumentare controllo e comprensione, non entrare subito con refactor massivo, migrazioni, modifiche CI o modifiche a dati sensibili.

Un onboarding esplicito riduce il rischio di partire dal task sbagliato e rende verificabile la scelta GO, WARNING o NO-GO prima di Codex.

### Conseguenze

Project Workflow Index, Workflow Health Check, Workflow Quick Reference, Workflow Command Cookbook, Workflow Status Dashboard e Release Readiness includono Existing Project Pilot Onboarding.

Lo STEP 300 consigliato e' ASF Next Step Runner: preparare localmente il prossimo task packet pilot e l'handoff Codex senza modificare repository esterne.

---

## DEC-050 - ASF Next Step Runner

**Data:** 2026-05-29
**Stato:** Accettata

### Contesto

Dopo Existing Project Pilot Onboarding serve ridurre i passaggi ripetitivi tra ChatGPT, Codex, Git e Step Closure Report senza trasformare il metodo in automazione remota o cross-repository.

### Decisione

Introdurre `scripts/asf_next_step.py` come runner locale standard library only con una prima modalita' `prepare`.

Il runner legge in modo read-only lo stato Git del repository target, genera `task_packet.md`, `codex_handoff.md` e `runner_report.md` sotto `tmp/asf_next_step/`, valida il task packet in Lite e Strict e si ferma prima di qualunque invocazione Codex o modifica al repository target.

### Motivazione

Il workflow manuale resta corretto ma contiene molti passaggi ripetitivi e soggetti a errore. Un prepare runner locale accelera la preparazione mantenendo Human gate, review umana, no commit, no push, no PR e no merge automatici.

### Conseguenze

Gli output del runner sono temporanei e ignorati da Git. Il task packet generato resta una bozza da rivedere. Le evoluzioni naturali sono:

- 310) ASF Next Step Runner Project Profiles;
- 320) ASF Runner Codex Handoff Improvements;
- 330) ASF Runner Verification Pack.

---

## DEC-051 - ASF Runner Upgrade Pack

**Data:** 2026-05-29
**Stato:** Accettata

### Contesto

Dopo il primo ASF Next Step Runner serve ridurre ulteriore copia/incolla senza trasformare il runner in un orchestratore automatico.

I bisogni emersi sono:

- riusare informazioni progetto tramite profili locali;
- produrre un handoff Codex piu' vicino al metodo FASE 1 / FASE 2;
- preparare controlli consigliati prima e dopo Codex senza automatizzare Git o GitHub.

### Decisione

Introdurre l'ASF Runner Upgrade Pack:

- `config/asf_project_profiles.json` per profili progetto locali;
- supporto `--profile` in `scripts/asf_next_step.py` con override manuali;
- handoff Codex migliorato con stato Git target, FASE 1, FASE 2, note safety e Step Closure Report;
- generazione di `verification_pack.md`;
- documenti `docs/43_ASF_RUNNER_PROJECT_PROFILES.md`, `docs/44_ASF_RUNNER_CODEX_HANDOFF_IMPROVEMENTS.md` e `docs/45_ASF_RUNNER_VERIFICATION_PACK.md`;
- template `templates/codex_tasks/asf_runner_verification_pack_template.md`.

Il runner resta standard library only, local-first e read-only verso repository target. Non invoca Codex, non usa GitHub API, non modifica repository target e non automatizza commit, push, PR o merge.

### Motivazione

I profili riducono errori ripetitivi su repo path, branch principale, test command e note safety. L'handoff migliorato rende piu' chiaro cosa Codex deve fare e cosa resta gate umano. Il Verification Pack separa le verifiche consigliate dal ciclo Git presidiato.

### Conseguenze

Il runner genera quattro output temporanei sotto `tmp/asf_next_step/`: `task_packet.md`, `codex_handoff.md`, `runner_report.md` e `verification_pack.md`.

Gli output restano bozze da rivedere da Alberto/ChatGPT. Lo STEP 340 consigliato e' ASF Runner Verification Pack Hardening.

---

## DEC-052 - ASF Runner Automation Readiness Pack

**Data:** 2026-05-29
**Stato:** Accettata

### Contesto

Dopo profili, handoff migliorato e Verification Pack serve avvicinare il runner all'automazione completa senza saltare gate umani.

Il flusso desiderato e':

- ASF Runner prepara task packet, handoff e verification pack;
- Alberto incolla l'handoff in Codex;
- Codex lavora localmente e produce report;
- Alberto salva il report Codex in Markdown;
- ASF legge il report e produce un intake;
- ASF genera un closure pack;
- Alberto verifica ed esegue manualmente i comandi finali.

### Decisione

Introdurre l'ASF Runner Automation Readiness Pack:

- hardening del `verification_pack.md` generato da `scripts/asf_next_step.py`;
- script read-only `scripts/asf_codex_report_intake.py`;
- script `scripts/asf_generate_closure_pack.py` che genera solo Markdown;
- documenti `docs/46_ASF_RUNNER_VERIFICATION_PACK_HARDENING.md`, `docs/47_ASF_CODEX_REPORT_INTAKE.md` e `docs/48_ASF_HUMAN_GATED_CLOSURE_PACK.md`;
- template `templates/codex_tasks/asf_codex_report_intake_template.md` e `templates/codex_tasks/asf_human_gated_closure_pack_template.md`.

Gli script operativi non invocano Codex, non usano GitHub API, non modificano repository target esterni e non eseguono commit, push, PR o merge.

I comandi Git/GitHub di chiusura possono comparire solo nel closure pack Markdown come istruzioni manuali human-gated.

### Motivazione

Separare intake e closure pack riduce passaggi ripetitivi e rende verificabile la qualita' del report Codex prima della pubblicazione manuale.

Il closure pack prepara comandi e checklist, ma lascia ad Alberto l'approvazione esplicita di commit, push, PR e merge.

### Conseguenze

Gli output restano sotto `tmp/` e sono ignorati da Git.

Il prossimo step consigliato e' 370) ASF Runner Human Approval Gate, per rendere ancora piu' esplicite le approvazioni tra report intake, closure pack e pubblicazione manuale.

---

## DEC-053 - ASF Automation Bridge Pack

**Data:** 2026-06-03
**Stato:** Accettata

### Contesto

Dopo l'Automation Readiness Pack serve costruire il ponte verso una futura invocazione Codex controllata, senza saltare Human gate, review, verifiche e branch dedicato.

Il flusso desiderato diventa:

- ASF Runner prepara task packet, handoff e Verification Pack;
- Codex report intake e closure pack restano human-gated;
- Human Approval Gate produce una decisione `GO`, `WARNING`, `HOLD` o `NO-GO`;
- ASF puo' generare una preview dry-run di futura invocazione Codex;
- l'esecuzione reale resta fuori scope finche' non esiste un prototipo read-only approvato.

### Decisione

Introdurre l'ASF Automation Bridge Pack:

- `scripts/asf_human_approval_gate.py`;
- `scripts/asf_codex_invocation_dry_run.py`;
- `docs/49_ASF_HUMAN_APPROVAL_GATE.md`;
- `docs/50_ASF_CODEX_INVOCATION_DESIGN.md`;
- `docs/51_ASF_CODEX_INVOCATION_DRY_RUN_PACK.md`;
- template per approval gate e dry-run invocation pack.

`codex exec` puo' comparire solo come testo di preview. Lo script Python non invoca Codex e il `.ps1` generato stampa la preview senza eseguirla.

### Motivazione

Il passaggio da handoff manuale a invocazione controllata e' rischioso se fatto in un salto unico. Serve prima rendere verificabili:

- stato Git target;
- decisione umana;
- sandbox proposta;
- stop condition;
- comando preview;
- blocchi `HOLD` e `NO-GO`.

### Conseguenze

Il livello attivo diventa Level 1: dry-run command preview.

Il prossimo step consigliato e':

```text
400) ASF Codex Invocation Read-Only Prototype
```

Solo dopo un prototipo read-only verificato si potra' valutare una futura esecuzione `workspace-write`, sempre su branch dedicato e con approval esplicita.

---

## DEC-054 - ASF Codex Read-Only Invocation Prototype Pack

**Data:** 2026-06-03
**Stato:** Accettata

### Contesto

Dopo l'Automation Bridge Pack esiste una preview dry-run di futura invocazione Codex, ma manca ancora un passaggio controllato per provare la sola analisi read-only e salvare output verificabili.

Il rischio principale e' trasformare troppo presto il runner in un esecutore che modifica repository target o automatizza Git/GitHub.

### Decisione

Introdurre il pack 400-420:

- `scripts/asf_codex_readonly_invoke.py` con default `preview` e `execute-readonly` solo dietro conferma esplicita, Human Approval Gate `GO`, working tree target `CLEAN` e sandbox read-only;
- `scripts/asf_codex_result_capture.py` per normalizzare stdout, stderr, exit code e report in `PASS`, `WARNING` o `FAIL`;
- `scripts/asf_codex_readonly_safety_gate.py` per decidere `GO_TO_WORKSPACE_WRITE_DESIGN`, `WARNING_REVIEW_REQUIRED`, `HOLD` o `NO_GO`;
- documenti e template dedicati per invocation, capture e safety gate.

Il pack non autorizza workspace-write. `GO_TO_WORKSPACE_WRITE_DESIGN` autorizza solo la progettazione di uno step futuro separato.

### Motivazione

Il passaggio da preview a execution deve restare incrementale. Una invocation read-only controllata permette di verificare:

- disponibilita' del comando Codex;
- comportamento della sandbox read-only;
- raccolta di stdout/stderr/exit code;
- working tree target prima e dopo;
- qualita' delle evidenze prima di qualunque livello successivo.

### Conseguenze

Il livello attivo diventa Level 2 read-only analysis, con default preview.

Il prossimo step consigliato e':

```text
430) ASF Codex Read-Only Invocation First Manual Trial
```

Qualunque futura esecuzione workspace-write richiedera' un nuovo step, un nuovo gate umano, scope esplicito, branch dedicato e verifiche dedicate.

---

## DEC-055 - ASF Codex Read-Only First Manual Trial

**Data:** 2026-06-04
**Stato:** Accettata

### Contesto

Dopo il pack 400-420 serve provare il flusso reale del runner fino al safety gate, ma senza trasformare il prototipo in una automazione che modifica repository target.

Il target scelto per il primo trial e' `AI_Software_Factory`, perche' e' locale, controllato e contiene gli script del runner.

### Decisione

Il primo trial manuale resta valido anche in modalita' preview-only quando una condizione di esecuzione non e' soddisfatta.

Nel trial 430 il Human Approval Gate ha prodotto `HOLD` per branch atteso non coerente con il branch corrente. Di conseguenza `execute-readonly` non e' stato tentato.

Il result capture e' stato validato con output simulati sotto `tmp/`. Il Safety Gate ha bloccato il target ASF quando la working tree e' diventata `DIRTY` durante lo sviluppo dello step, e ha prodotto `GO_TO_WORKSPACE_WRITE_DESIGN` solo su un controllo pulito temporaneo.

### Motivazione

Questo mantiene la pipeline local-first, read-only e human-gated. Un gate `HOLD` deve bloccare Codex, non essere aggirato.

Validare il flusso con output simulati e target temporaneo pulito e' sufficiente per chiudere il first manual trial, ma non sostituisce una futura invocazione reale read-only.

### Conseguenze

Il prossimo step consigliato e':

```text
440) ASF Codex Read-Only Invocation Clean Target Trial
```

Prima di OpenAI API Adapter, MCP o workspace-write serve un trial su target pulito con branch atteso coerente, approval gate `GO`, eventuale disponibilita' del comando `codex`, conferma esplicita e sandbox read-only.

---

## DEC-056 - ASF Codex Read-Only Clean Target Trial

**Data:** 2026-06-04
**Stato:** Accettata

### Contesto

Dopo lo STEP 430 il prototipo read-only era stato validato solo in modalita' preview-only. Serviva una prova con target pulito, gate `GO` ed eventuale `execute-readonly` reale.

### Decisione

Usare una repo Git temporanea sotto `tmp/asf_clean_target_trial/step_440/clean_repo`, con soli file sintetici, branch locale temporaneo e Human Approval Gate `GO`.

Il trial ha tentato ed eseguito `execute-readonly` con sandbox read-only. L'exit code e' stato `0` e la working tree target e' rimasta `CLEAN`.

Il Safety Gate finale e' `WARNING_REVIEW_REQUIRED`, non `GO_TO_WORKSPACE_WRITE_DESIGN`, perche' Codex ha prodotto stderr non vuoto e non ha completato l'ispezione della repo a causa di un errore sandbox interno.

### Motivazione

Un exit code `0` e una working tree pulita non bastano per promuovere il risultato a GO se l'output Codex e' incompleto.

Il gate deve restare conservativo: stderr non vuoto o output incompleto richiedono review manuale e un trial ripetibile prima di qualsiasi design piu' ampio.

### Conseguenze

Il prossimo step consigliato e':

```text
450) ASF Codex Read-Only Invocation Repeatable Trial Pack
```

Workspace-write resta non autorizzato. Anche in presenza di target pulito e gate iniziale `GO`, la progressione deve fermarsi se il safety gate finale e' `WARNING_REVIEW_REQUIRED`.

---

## DEC-057 - ASF Codex Read-Only Repeatable Trial Pack

**Data:** 2026-06-04
**Stato:** Accettata

### Contesto

Lo STEP 440 ha tentato `execute-readonly` reale su repo sintetica pulita. Il target e' rimasto `CLEAN` e l'exit code e' stato `0`, ma il Safety Gate e' rimasto `WARNING_REVIEW_REQUIRED` per stderr non vuoto e output incompleto.

### Decisione

Introdurre uno STEP 450 dedicato al Repeatable Trial Pack:

- `scripts/asf_codex_readonly_repeatable_trial.py`;
- `scripts/asf_codex_readonly_trial_compare.py`;
- documenti `docs/59_ASF_CODEX_READONLY_REPEATABLE_TRIAL_PACK.md` e `docs/60_ASF_CODEX_READONLY_REPEATABLE_TRIAL_RESULTS.md`;
- template per trial e compare;
- repo sintetica temporanea sotto `tmp/`;
- classificazioni esplicite, inclusa `CODEX_NOT_AVAILABLE`.

Il pack resta read-only e non autorizza workspace-write.

### Motivazione

Prima di progettare qualunque esecuzione piu' ampia serve distinguere meglio:

- limite ambientale;
- Codex non disponibile;
- stderr non vuoto;
- output incompleto;
- target dirty;
- approval gate non GO.

Un trial ripetibile e confrontabile riduce ambiguita' e impedisce di scambiare un exit code `0` per autorizzazione operativa.

### Conseguenze

Il prossimo step consigliato diventa:

```text
460) ASF Codex Read-Only Invocation Diagnostics Hardening
```

OpenAI API Adapter, MCP e qualunque futuro workspace-write restano posticipati finche' la diagnostica read-only non e' piu' robusta.

---

## DEC-058 - ASF PowerShell Command Pack Skill Hardening

**Data:** 2026-06-05
**Stato:** Accettata

### Contesto

Alberto usa una skill comune personale per preparare command pack PowerShell robusti e copiabili. Prima dello STEP 490 la skill conteneva molte regole direttamente in `SKILL.md` e non aveva ancora una struttura esplicita con riferimenti lunghi, template `.ps1` e demo progressive.

### Decisione

Rafforzare la skill esistente `as-common-pwsh-command-pack`, senza rinominarla e senza creare una seconda skill.

La skill deve:

- mantenere `SKILL.md` compatto con frontmatter YAML `name` e `description`;
- spostare standard e fonti tecniche in `references/pwsh-command-pack-standard.md`;
- fornire un template robusto in `references/pwsh-command-pack-template.ps1`;
- includere esempi progressivi in `examples/demo-prompts.md`;
- generare command pack `.ps1` con output numerati e, nello stato storico STEP 490, `LAST-*`, Markdown/DOCX compatto, clipboard e guardrail Git/Codex/ASF. Questa parte e' superseded da DEC-069: i nuovi command pack usano solo `NNNN-II-Tipo_Nome.ext`.

### Motivazione

I command pack lunghi sono fragili se incollati inline in PowerShell. Uno script `.ps1` completo riduce limiti di lunghezza, errori di incolla, perdita di log, ambiguita' tra verifica e pubblicazione e rischio di procedere dopo gate falliti.

Separare `SKILL.md`, riferimenti, template ed esempi segue il modello di progressive disclosure delle skill e rende piu' semplice mantenere la skill senza appesantire ogni attivazione.

### Conseguenze

La skill esterna diventa il riferimento operativo per generare command pack PowerShell robusti per ASF e per altri progetti locali di Alberto.

Lo step non autorizza commit, push, PR, merge, release, deploy, modifiche a PATH, installazione moduli o modifiche a repository target esterni.

---

## DEC-059 - OpenAI API Adapter dry-run/mock foundation

**Data:** 2026-06-06
**Stato:** Accettata

### Contesto

ASF deve preparare una futura integrazione OpenAI API senza introdurre subito SDK, credenziali, rete o chiamate live.

Il task packet dello STEP 500 corregge la numerazione dell'OpenAI API Adapter e impone che il lavoro corrente resti deterministico, standard-library-only e verificabile localmente.

### Decisione

Introdurre `scripts/asf_openai_api_adapter.py` come adapter foundation per:

- costruire payload Responses-style;
- validare modello, reasoning effort e text verbosity;
- controllare solo la presenza di `OPENAI_API_KEY`;
- produrre JSON evidence per `check-env`, `dry-run` e `mock`;
- redigere stringhe che assomigliano a chiavi OpenAI;
- mantenere `live` fail-closed con `LIVE_MODE_NOT_IMPLEMENTED_IN_STEP_500`.

Lo step non esegue chiamate live OpenAI API, non richiede `OPENAI_API_KEY`, non aggiunge SDK e non usa network.

### Motivazione

Separare payload building, mock e dry-run dalla futura chiamata live permette di testare il contratto locale senza rischiare leak di secret o dipendenze non necessarie.

Il fail-closed live boundary rende esplicito che il successo del mock non equivale a readiness produttiva.

### Conseguenze

Il prossimo step consigliato e':

```text
510) OpenAI API Adapter Live Boundary and Credential Gate
```

Qualunque chiamata live futura richiedera' un nuovo gate umano, regole credenziali esplicite, stop conditions, redazione verificata e test che non dipendono da credenziali reali di default.

---

## DEC-060 - OpenAI API Adapter live boundary and credential gate

**Data:** 2026-06-06
**Stato:** Accettata

### Contesto

STEP 500 ha introdotto l'adapter OpenAI API dry-run/mock, ma il mode `live` era ancora un placeholder fail-closed.

Prima di qualunque smoke test reale serve un gate deterministico che distingua credenziale presente, consenso locale, conferma CLI e assenza di chiamate network.

### Decisione

Estendere `scripts/asf_openai_api_adapter.py` con un live boundary report per il mode `live`.

Il gate richiede, in ordine:

- presenza boolean di `OPENAI_API_KEY`;
- `ASF_OPENAI_LIVE_ENABLED=1`;
- flag CLI `--allow-live`;
- conferma `--live-confirm I_UNDERSTAND_THIS_CALLS_OPENAI_API`.

Quando tutti i gate sono presenti, la decisione e' `LIVE_READY_FOR_SEPARATE_SMOKE_STEP`, ma il report mantiene `LIVE_CALLS_NOT_IMPLEMENTED_IN_STEP_510`, `network_performed: false` e `network_call_performed: false`.

### Motivazione

Separare credential gate, live boundary e live smoke test evita che la sola presenza di una API key abiliti chiamate OpenAI non presidiate.

Il report JSON rende verificabile la readiness futura senza stampare secret, hash, fingerprint, prefissi, suffissi o lunghezze della chiave.

### Conseguenze

Il prossimo step consigliato e':

```text
520) OpenAI API Adapter First Controlled Live Smoke Test
```

Lo STEP 520 dovra' essere un task separato, human-gated, con stop conditions, redazione verificata e nessun requisito di credenziali reali nei test di default.

---

## DEC-061 - OpenAI API Adapter first controlled live smoke test

**Data:** 2026-06-06
**Stato:** Accettata

### Contesto

STEP 510 ha introdotto gate e boundary live senza chiamate network.

Alberto ha autorizzato una prima smoke live controllata solo se tutti i gate locali sono presenti e dopo il passaggio dei test deterministici.

### Decisione

Estendere `scripts/asf_openai_api_adapter.py` con una live smoke limitata a una sola richiesta `POST https://api.openai.com/v1/responses`.

La live smoke richiede:

- presenza boolean di `OPENAI_API_KEY`;
- `ASF_OPENAI_LIVE_ENABLED=1`;
- flag `--allow-live`;
- conferma `--live-confirm I_UNDERSTAND_THIS_CALLS_OPENAI_API`;
- prompt tiny `Return exactly ASF_OPENAI_LIVE_SMOKE_OK.`;
- `store: false`;
- artifact solo sotto `tmp/`.

Il comando `--gate-only` permette di verificare localmente se la chiamata sarebbe consentita senza usare network.

### Motivazione

Il primo smoke test deve dimostrare che il boundary live puo' essere attraversato in modo controllato, verificabile e reversibile, senza introdurre SDK, retry automatici o produzione implicita.

La API key resta una credenziale locale: il report mostra solo se e' presente e non stampa valore, lunghezza, hash, prefissi, suffissi o fingerprint.

### Conseguenze

I test di default restano mockati e non richiedono rete o credenziali reali.

Le classificazioni principali sono:

```text
LIVE_SMOKE_EXECUTED_AND_PASSED
LIVE_SMOKE_EXECUTED_BUT_FAILED
LIVE_SMOKE_NOT_RUN_MISSING_GATE
LIVE_SMOKE_NOT_RUN_NETWORK_BLOCKED
LIVE_SMOKE_UNEXPECTED_MODEL_OUTPUT
```

Il prossimo step consigliato e':

```text
530) OpenAI API Adapter Live Smoke Result Hardening
```

---

## DEC-062 - OpenAI API Adapter live smoke result hardening

**Data:** 2026-06-06
**Stato:** Accettata

### Contesto

STEP 520 ha introdotto una prima smoke live controllata, ma prima di qualunque ulteriore prova live serve rendere piu' stabile e leggibile il risultato.

Il rischio e' confondere HTTP status, rete, schema risposta, gate mancanti e autorizzazione live in un unico errore generico, oppure produrre artifact difficili da confrontare.

### Decisione

Estendere `scripts/asf_openai_api_adapter.py` con un contratto live result stabile:

- `status` in `success`, `failed` o `skipped`;
- `classification` in `not_configured`, `disabled`, `credential_missing`, `live_not_allowed`, `success`, `provider_error`, `network_error`, `rate_limited`, `auth_error`, `schema_error` o `unknown_error`;
- `safe_details` redatto;
- `credential_present` solo booleano;
- artifact JSON machine-readable e Markdown opzionale per operatore.

Lo step usa solo test mockati. Non autorizza una nuova chiamata live.

### Motivazione

Una classificazione centrale rende i risultati confrontabili e impedisce di promuovere errori ambientali o provider a readiness operativa.

Il contratto stabile aiuta i futuri gate umani e mantiene la regola fail-closed prima di ogni prova live successiva.

### Conseguenze

Qualunque futura esecuzione live dovra' usare questo schema, mantenere artifact sotto `tmp/`, non emettere segreti o derivati e richiedere autorizzazione separata.

Il prossimo step consigliato e':

```text
540) OpenAI API Adapter Controlled Live Execution Pack
```

---

## DEC-063 - Codex prompt clean-first workflow

**Data:** 2026-06-06
**Stato:** Accettata

### Contesto

Il workflow ASF usa sia prompt Codex direttamente copiabili sia command pack PowerShell per salvataggio, audit trail e pubblicazione controllata.

Il rischio operativo e' mischiare nello stesso blocco prompt Codex, script PowerShell, salvataggio Bridge, comandi Git, pubblicazione e verifiche finali, rendendo i prompt piu' sporchi, meno leggibili e piu' fragili.

### Decisione

Stabilire la regola:

```text
Clean Codex prompt first by default.
PowerShell only when archiving, auditing, or publishing.
```

Per i prompt destinati a Codex, il default e' un prompt pulito, autosufficiente e direttamente copiabile, senza wrapper PowerShell.

Il Codex command pack PowerShell si usa solo quando Alberto chiede esplicitamente salvataggio nel Bridge Dropbox / ChatGPT Bridge, file numerati, file `LAST` o audit trail formale.

Il pwsh/publication command pack si usa dopo il report Codex e l'intake gate, per commit, push, PR/merge e verifica finale presidiata. La pubblicazione resta bloccata se test, health check, Verification Gate o guardrail falliscono.

### Motivazione

Separare i livelli riduce ambiguita' tra istruzioni a Codex, archiviazione del prompt e pubblicazione Git.

Il Bridge Dropbox resta utile per audit trail, ripartenze, output tracciati e report finali, ma non deve diventare il wrapper obbligatorio per ogni prompt veloce.

### Conseguenze

I documenti operativi principali devono distinguere:

- prompt Codex pulito;
- eventuale salvataggio Bridge;
- intake gate dopo report Codex;
- publication command pack per chiusura Git controllata.

Codex lascia il working tree modificato per review manuale e non fa commit, push, PR, merge o deploy salvo richiesta esplicita.

Il prossimo step consigliato resta:

```text
540) OpenAI API Adapter Controlled Live Execution Pack
```

## DEC-064 - PowerShell command pack safe bootstrap

**Data:** 2026-06-06
**Stato:** Accettata

### Contesto

Durante la pubblicazione degli step 530 e 535 sono emersi problemi strutturali nei command pack PowerShell lunghi incollati direttamente nel terminale.

I sintomi includevano funzioni non disponibili, blocchi `else` interpretati fuori contesto, parser error su graffe isolate, here-string annidate che chiudevano il testo esterno, DOCX rumoroso e tentativi di push diretto a `main` bloccati dai soft guardrails.

### Decisione

Adottare lo standard Safe Bootstrap PowerShell Command Pack:

1. ChatGPT genera un bootstrap PowerShell corto.
2. Il bootstrap scrive uno script `.ps1` completo sotto `pwsh_command`.
3. Il bootstrap valida il parsing con `[scriptblock]::Create(...)`.
4. Solo se il parsing passa, esegue il file con `pwsh -NoProfile -ExecutionPolicy Bypass -File`.
5. Tutta la logica complessa vive nello script `.ps1`, non nel blocco incollato.
6. Il bootstrap non contiene logica Git complessa, here-string annidate, DOCX XML, `else` esterni o `finally` fragile.

Per pubblicare verso `main`, il default diventa branch + PR. `git push origin main` non e' un default accettabile; resta solo un bypass eccezionale, manuale ed esplicito.

Se `main` locale e' avanti rispetto a `origin/main`, creare un branch publish dal `main` locale, pushare quel branch, aprire PR, mergiare, riallineare `main` locale e verificare.

### Motivazione

Il bootstrap corto riduce il rischio che PowerShell esegua pezzi interni come comandi separati.

Il parse-check fail-closed impedisce pubblicazioni parziali quando lo script generato non e' valido.

PR-first e' coerente con soft guardrails ASF, branch protection futura e regola clean-first dello STEP 535.

DOCX best-effort evita che un artifact accessorio blocchi una pubblicazione gia' verificata con TXT/MD validi.

### Conseguenze

I futuri command pack devono mantenere output numerati e `LAST`, generare compact Markdown non vuoto, usare `git --no-pager`, trattare warning LF/CRLF come non bloccanti solo se diff-check/test/health/verify passano e fermarsi su errori reali.

Il prossimo step consigliato resta:

```text
540) OpenAI API Adapter Controlled Live Execution Pack
```

---

## DEC-065 - OpenAI API Adapter controlled live execution pack

**Data:** 2026-06-06
**Stato:** Accettata

### Contesto

STEP 530 ha reso stabile lo schema risultato live smoke, ma una nuova live reale non deve essere eseguita direttamente da Codex o da un comando ambiguo.

Serve un pack operativo separato che prepari artifact, preflight, cost guard e template operatore, mantenendo dry-run come default e richiedendo consenso esplicito prima di qualunque live futura.

### Decisione

Introdurre `scripts/asf_openai_controlled_live_execution_pack.py` come layer operativo sopra l'adapter OpenAI:

- `--execution-mode dry-run` e' il default;
- `--execution-mode mock` usa provider finto e nessuna rete;
- `--execution-mode live` e' previsto solo per un futuro step autorizzato;
- la live reale richiede `ASF_OPENAI_LIVE_ENABLED=1` e `--confirm-live-openai`;
- la sola presenza di `OPENAI_API_KEY` non autorizza la chiamata;
- artifact JSON/Markdown restano sotto `tmp/`;
- la credenziale puo' comparire solo come boolean `credential_present`;
- cost guard minimale: prompt tiny, `store: false`, max output basso, timeout basso, una sola chiamata prevista, nessun retry aggressivo, nessun loop e nessuna chiamata parallela.

Aggiungere il runbook `docs/69_ASF_OPENAI_API_ADAPTER_CONTROLLED_LIVE_EXECUTION_PACK.md` e il template PowerShell `templates/pwsh_command_pack/step_540_openai_controlled_live_execution_pack_template.ps1` coerente con lo standard Safe Bootstrap STEP 536.

### Motivazione

Separare pack operativo e live reale riduce il rischio che credenziali presenti nell'ambiente o comandi copiati fuori contesto producano chiamate OpenAI non presidiate.

Il dry-run default consente a operatore e test di verificare schema, artifact e stop conditions senza rete e senza chiavi reali.

### Conseguenze

Ogni futura live OpenAI deve passare dal controlled live execution pack, produrre artifact redatti e dichiarare esplicitamente i gate usati.

Codex non deve eseguire live call, chiedere API key o leggere/stampare valori di credenziali.

Il prossimo step consigliato e':

```text
560) OpenAI API Adapter First Authorized Live Run
```

---

## DEC-066 - PowerShell command pack skill finalization

**Data:** 2026-06-06
**Stato:** Accettata

### Contesto

STEP 536 ha introdotto il Safe Bootstrap PowerShell Command Pack per evitare incolla fragile, esecuzioni parziali, here-string annidate, DOCX bloccante e push diretto a `main`.

STEP 540 ha validato lo standard in una pubblicazione reale riuscita con safe bootstrap, branch e PR.

Serve ora trasformare lo standard in un pacchetto canonico riusabile dentro la repository, senza modificare direttamente la skill esterna sotto `%USERPROFILE%\.agents\skills`.

### Decisione

Creare il pacchetto canonico in `templates/pwsh_command_pack/`:

- `README.md`;
- `as-common-pwsh-command-pack-SKILL.md`;
- `safe_bootstrap_template.ps1`;
- `safe_command_pack_script_template.ps1`.

Lo standard finalizzato richiede:

- bootstrap corto con `& { ... }`;
- parse-check con `[scriptblock]::Create($ScriptText) | Out-Null`;
- esecuzione con `pwsh -NoProfile -ExecutionPolicy Bypass -File $CommandFile`;
- logica complessa solo nel `.ps1` generato;
- parametro `ArgList`, non `$Args`;
- parser Git `git status --porcelain=v1 --untracked-files=all`;
- PR-first publishing;
- artefatti progressivi `NNNN-II-Tipo_Nome.ext`;
- nessuna generazione o lettura di `LAST-*`;
- DOCX best-effort;
- warning LF/CRLF non bloccanti quando diff-check, test, health check e verify gate passano.

### Motivazione

Un draft esportabile dentro la repository rende lo standard verificabile, versionato e riusabile senza editare cartelle esterne al progetto durante gli step ASF.

Il parser Git porcelain riduce errori di scope guard, specialmente con directory untracked e path il cui primo carattere potrebbe essere perso da slicing fragile.

### Conseguenze

I futuri command pack ASF devono usare il pacchetto canonico come riferimento.

Il command pack non diventa il default per i prompt Codex: la regola clean-first dello STEP 535 resta valida.

Il prossimo step consigliato resta:

```text
560) OpenAI API Adapter First Authorized Live Run
```

---

## DEC-070 - OpenAI API Adapter first authorized live run evidence gate

**Data:** 2026-06-06
**Stato:** Accettata

### Contesto

STEP 0560 autorizza un primo tentativo live reale dell'OpenAI API Adapter, ma deve restare fail-closed se mancano credenziali locali, autorizzazione esplicita, rete, quota o condizioni esterne.

La fonte ufficiale resta Git con file versionati. Il Bridge e qualunque artifact temporaneo non sono autorevoli.

### Decisione

Introdurre `scripts/asf_openai_first_authorized_live_run.py` come wrapper STEP 0560 sopra `scripts/asf_openai_api_adapter.py`.

Il wrapper:

- richiede `--live` oppure `ASF_OPENAI_LIVE_RUN=1`;
- richiede `OPENAI_API_KEY` presente solo nell'ambiente;
- usa `ASF_OPENAI_MODEL` se presente, altrimenti il default adapter;
- usa il prompt tiny `Return exactly ASF_OPENAI_LIVE_SMOKE_OK.`;
- limita l'output massimo;
- delega la chiamata reale a `adapter.run_live`;
- scrive sempre il report versionato `docs/0560-01-Report_OpenAI_API_Adapter_First_Authorized_Live_Run.md`;
- scrive `docs/0560-02-Evidence_OpenAI_API_Live_Run_Sanitized.json` solo se il risultato e' success;
- non esegue retry automatici.

Il primo tentativo STEP 0560 e' risultato `BLOCKED` per `OPENAI_API_KEY` assente, con `request_count=0`.

I tentativi live locali autorizzati successivi hanno raggiunto il provider con `request_count=1`, ma non hanno prodotto evidence positiva. Lo stato consolidato STEP 0560-E e' `BLOCKED_BY_RATE_LIMIT_OR_QUOTA`, con diagnostica sanitizzata coerente con HTTP 429 `insufficient_quota`.

Il diagnostic pack versionato `docs/0560-03-Diagnostic_OpenAI_Provider_HTTP_Error_And_Rate_Limit.md` documenta il blocco provider-side senza creare `docs/0560-02-Evidence_OpenAI_API_Live_Run_Sanitized.json`.

### Motivazione

Separare wrapper autorizzato, adapter e report versionato evita chiamate raw esterne, mantiene i test offline/mockati e impedisce che una run bloccata produca evidenza positiva.

### Conseguenze

Un eventuale nuovo tentativo live richiede uno step separato e autorizzato, dopo verifica manuale di quota, billing, organization/project e accesso modello nella dashboard OpenAI. Gli errori live futuri devono restare classificati con retry policy esplicita prima di qualunque ulteriore automazione.

Il prossimo step consigliato e':

```text
0560-F) Publish Provider-Blocked Live Run Diagnostic Pack
```

---

## DEC-069 - LAST deprecation and 4-digit artifact naming standard

**Data:** 2026-06-06
**Stato:** Accettata

### Contesto

Gli step precedenti usavano file `LAST-*` nel ChatGPT Bridge per ispezionare rapidamente l'ultimo output. Questo crea stato ambiguo: il Bridge e' operativo, mentre la fonte autorevole deve restare Git con file versionati e nomi progressivi.

### Decisione

Deprecare l'uso operativo di `LAST-*` e adottare lo standard:

```text
NNNN-II-Tipo_Nome.ext
```

Per trovare l'ultimo artefatto di un tipo per uno step si usa:

```text
max(II) per (step, tipo)
```

La repository mantiene gli artefatti storici `LAST-*` se esistono, ma i nuovi template, runbook e skill export non devono generarli o leggerli come input.

La futura live OpenAI gia' pianificata viene spostata da STEP 550 a STEP 560, per evitare due significati autorevoli dello stesso numero step.

### Conseguenze

`docs/73_LAST_DEPRECATION_4_DIGIT_ARTIFACT_NAMING_STANDARD.md` diventa il riferimento operativo dello standard.

`scripts/migrate_artifact_names_4digit.py` fornisce una migrazione prudente: dry-run di default, `--apply` esplicito, nessun overwrite, skip dei file `LAST-*`, skip dei documenti `NN_...`, skip dei file gia' `NNNN-II-...` e blocco su collisioni.

Il prossimo step consigliato e':

```text
560) OpenAI API Adapter First Authorized Live Run
```

---

## DEC-068 - Git line endings warning cleanup

**Data:** 2026-06-06
**Stato:** Accettata

### Contesto

Durante step recenti Git ha segnalato warning LF/CRLF non bloccanti, incluso:

```text
warning: in the working copy of 'templates/test_plans/test_plan_template.md', LF will be replaced by CRLF the next time Git touches it
```

La repository aveva `.gitattributes` tracciato, ma con sola regola `* text=auto`. Questa regola normalizza i contenuti testuali nell'index, ma non rende esplicita la EOL policy del working tree per documentazione, sorgenti e template.

### Decisione

Gestire la policy fine riga a livello repository tramite `.gitattributes`, non tramite configurazione globale utente.

La policy:

- mantiene `* text=auto`;
- forza LF per Markdown, Python, YAML, JSON, TOML, TXT e file testuali di progetto;
- forza LF per `templates/test_plans/test_plan_template.md`;
- mantiene CRLF per script Windows `.bat`, `.cmd` e `.ps1`;
- vieta normalizzazione massiva non misurata.

### Motivazione

Una policy repository-level e' versionata, verificabile e coerente tra operatori Windows e Git, mentre modificare `core.autocrlf` globale cambierebbe il comportamento di altre repository dell'utente.

La correzione e' mirata: riduce warning futuri sul file noto e sui tipi testuali principali senza riscrivere centinaia di file gia' tracciati.

### Conseguenze

I futuri step devono distinguere warning LF/CRLF da errori reali: restano non bloccanti solo se `git --no-pager diff --check`, test, health check e verify gate passano.

Qualunque rinormalizzazione ampia deve essere preceduta da dry-run e revisione manuale se supera 10 file.

Il prossimo step consigliato resta:

```text
560) OpenAI API Adapter First Authorized Live Run
```

---

## DEC-067 - PowerShell command pack skill export install

**Data:** 2026-06-06
**Stato:** Accettata

### Contesto

STEP 545 ha creato una skill draft esportabile per `as-common-pwsh-command-pack`, ma il file draft non era ancora nella forma canonica installabile `skill-folder/SKILL.md`.

Serve un passaggio controllato che prepari l'export e un installer verificabile senza scrivere direttamente in `%USERPROFILE%\.agents\skills` o in repository esterne come `Codex_Skills`.

### Decisione

Creare la forma installabile:

```text
templates/pwsh_command_pack/export/as-common-pwsh-command-pack/SKILL.md
```

Introdurre:

- `scripts/install_pwsh_command_pack_skill.py`;
- dry-run default;
- `--apply` obbligatorio per scrivere;
- target esplicito con `--target-user-skills` o `--target-dir`;
- backup timestamped prima di overwrite confermato;
- blocco su target sospetti, sorgente mancante, skill name errato o concetti standard mancanti;
- test automatici senza scritture fuori repository.

### Motivazione

L'export installabile rende la skill comune versionabile e verificabile dentro ASF, mentre l'installer separa preparazione, dry-run e installazione reale.

Mantenere l'installazione reale come operazione manuale dopo intake riduce il rischio di modifiche cross-repo o di aggiornamenti non presidiati a skill personali.

### Conseguenze

Gli aggiornamenti futuri della skill devono passare da ASF export, dry-run, intake manuale e solo poi installazione o pubblicazione separata in eventuale repository skill.

Il prossimo step consigliato resta:

```text
560) OpenAI API Adapter First Authorized Live Run
```

---

## DEC-087 - MVP Real Step Pilot con GO WITH WARNINGS

**Data:** 2026-06-07
**Stato:** Accettata

### Contesto

Dopo STEP 0730 il Motore ASF MVP era chiuso come baseline `GO WITH WARNINGS`,
ma restava da provarlo su una modifica reale piccola invece che solo su smoke
sintetici o documenti di closure.

### Decisione

Lo STEP 0740 introduce `docs/motor/0740_MVP_REAL_STEP_PILOT.md`.

Il pilot:

- usa il runbook 0720 come riferimento operativo;
- registra lo stato con `scripts/asf_step_state_machine.py`;
- produce evidence temporanee sotto `tmp/0740_mvp_real_step_pilot/`;
- usa il Publish Config Generator senza eseguire pubblicazione;
- normalizza la run con un manifest documentale;
- aggiorna indici e workflow health in modo minimale;
- conclude con decisione prudente `PILOT STATUS: GO WITH WARNINGS`.

### Motivazione

Un pilot reale piccolo valida l'usabilita' della baseline MVP senza introdurre
automazioni pericolose. La scelta resta volutamente bassa nel rischio: il focus
e' capire frizioni operative, non dimostrare produzione o autonomia completa.

### Conseguenze

- Il Motore ASF MVP e' stato provato su una modifica reale e versionabile.
- Il pilot conferma che runbook, state machine, generator, manifest e verifiche
  locali sono usabili, ma ancora manuali.
- Phase B, Phase C, commit, push, PR, merge e deploy restano fuori dallo step.
- Il prossimo step consigliato e':

```text
0750) State Machine Publish Runner Event Hooks
```

---

## DEC-088 - State Machine Publish Runner Event Hooks human-gated

**Data:** 2026-06-07
**Stato:** Accettata

### Contesto

Dopo STEP 0740 state machine, publish config generator, manifest e publish
runner sono risultati utili, ma il passaggio da Phase B/Phase C agli eventi
state machine restava manuale.

### Decisione

Lo STEP 0750 introduce hook opzionali nel publish runner.

Quando `state_machine_enabled=true`, `scripts/asf_publish_step.ps1` puo'
emettere eventi come:

- `phase_b_started`;
- `phase_b_passed`;
- `pr_created`;
- `phase_b_failed`;
- `phase_c_started`;
- `phase_c_passed`;
- `phase_c_failed`;
- `main_verified`;
- `close_step` solo se configurato.

Gli hook invocano `scripts/asf_step_state_machine.py` via argv e non duplicano
le transizioni nel PowerShell.

### Motivazione

Il valore operativo e' ridurre la gestione manuale dello stato senza ridurre i
gate umani. La state machine resta il componente autorevole per coerenza,
transizioni e recovery.

### Conseguenze

- Le config legacy senza hook restano compatibili.
- Phase B richiede ancora `-ApprovePublish`.
- Phase C richiede ancora `-ApproveMerge`.
- Stato incoerente o hook falliti con hook abilitati bloccano il runner.
- I test usano fake `git`/`gh` e directory temporanee, senza GitHub o Dropbox reali.
- Il prossimo step consigliato e':

```text
0760) MVP Real Step Pilot 2 with State Hooks
```

---

## DEC-089 - MVP Real Step Pilot 2 con State Hooks

**Data:** 2026-06-07
**Stato:** Accettata

### Contesto

Dopo STEP 0750 il publish runner puo' emettere eventi state machine durante
Phase B e Phase C, ma il collegamento doveva essere preparato su un secondo
step reale piccolo prima di usarlo come pratica ordinaria.

### Decisione

Lo STEP 0760 introduce
`docs/motor/0760_MVP_REAL_STEP_PILOT_2_WITH_STATE_HOOKS.md`.

Il pilot:

- prepara uno state file locale in `READY_TO_PUBLISH`;
- genera una config publish e una variante hook-aware sotto `tmp/`;
- valida la config hook-aware solo con `scripts/asf_publish_step.ps1 -Phase Plan`;
- documenta gli eventi attesi `phase_b_started`, `phase_b_passed`,
  `pr_created`, `phase_c_started`, `phase_c_passed` e `main_verified`;
- conclude con decisione prudente `PILOT STATUS: GO WITH WARNINGS`.

### Motivazione

La prova mantiene basso il rischio e rende verificabile l'handoff verso la
pubblicazione reale. Gli hook vengono preparati e validati a livello config, ma
la pubblicazione resta human-gated e fuori da Codex.

### Conseguenze

- Gli hook sembrano pronti per uso ordinario controllato su step piccoli.
- La validazione completa resta da fare durante Phase B/C reale.
- `READY_TO_PUBLISH` non sostituisce approval umana.
- Il prossimo step consigliato e':

```text
0770) Runner Hook Evidence Manifest Integration
```

---

## DEC-092 - Post-MVP Hardening prima di nuova automazione

**Data:** 2026-06-08
**Stato:** Accettata

### Contesto

Dopo STEP 0730 il Motore ASF MVP e' stato chiuso come `GO WITH WARNINGS`.
Dopo gli STEP 0740, 0760 e 0780 sono stati eseguiti tre pilot reali piccoli,
con runner, state machine, generator, manifest e Bridge collegati in modo piu'
significativo.

I recovery recenti hanno pero' evidenziato frizioni operative: PowerShell non
ferma automaticamente i comandi nativi con `$ErrorActionPreference = "Stop"`,
gli exit code devono essere controllati, gli argomenti vuoti nei wrapper sono
pericolosi e `COMPLETATO` non deve essere stampato prima dei gate finali.

### Decisione

Lo STEP 0790 introduce
`docs/motor/0790_POST_MVP_ROADMAP_AND_HARDENING_PLAN.md`.

La fase post-MVP viene orientata a:

- hardening PowerShell e command safety;
- recovery UX del publish runner;
- consistenza Bridge e validazione `LAST-*`;
- integrazione post-publish tra state machine, runner hooks e manifest;
- tuning dei verification profile;
- pilot reali piu' operativi solo dopo i guardrail principali.

La decisione sintetica e':

```text
POST-MVP DECISION: HARDENING FIRST
```

### Motivazione

Il Motore ASF e' utilizzabile come baseline locale human-gated, ma non e'
ancora pronto per un modello "fire-and-forget". Prima di aumentare autonomia o
ampiezza dei pilot, serve rendere fail-closed la parte piu' fragile emersa nei
recovery: wrapper PowerShell, comandi nativi, exit code, output Bridge e
riconciliazione delle evidence.

### Conseguenze

- Il MVP resta `GO WITH WARNINGS`.
- Publish, merge e deploy restano human-gated.
- Gli hook e il manifest migliorano audit trail, ma non sostituiscono review.
- La roadmap proposta e' 0800-0860, con primo passo:

```text
0800) PowerShell Native Command Guardrail Hardening
```

---

## DEC-093 - Guardrail PowerShell per comandi nativi

**Data:** 2026-06-08
**Stato:** Accettata

### Contesto

Lo STEP 0790 ha indicato l'hardening PowerShell come primo passo post-MVP. Il
rischio pratico era che wrapper e command pack potessero proseguire dopo errori
di `git`, `gh`, `python` o `pwsh`, oppure dichiarare successo prima dei gate
finali.

### Decisione

Lo STEP 0800 introduce
`docs/motor/0800_POWERSHELL_NATIVE_COMMAND_GUARDRAIL_HARDENING.md`.

Il publish runner e lo standard command-pack vengono rafforzati con:

- wrapper `Invoke-NativeChecked` per comandi nativi critici;
- validazione fail-closed di comando, label, argomenti e `AllowedExitCodes`;
- rifiuto di argomenti nulli, vuoti o solo whitespace;
- lettura immediata di `$LASTEXITCODE`;
- blocco di Phase C senza `-PrNumber` o config `pr_number`;
- validazione di `expected_files` e file fuori scope;
- classificazione basata su exit code esplicitamente ammessi;
- stderr registrato come evidence da interpretare con contesto;
- successo dichiarato solo dopo i gate finali realmente passati.

### Motivazione

La sicurezza dei comandi nativi e' prerequisito per recovery piu' chiari e per
pilot futuri piu' operativi. Prima di migliorare UX o aumentare automazione,
serve che i wrapper falliscano chiusi sugli input ambigui e non trasformino
warning o exit code non ammessi in successo.

### Conseguenze

- `scripts/asf_publish_step.ps1` recepisce il wrapper nativo, la validazione
  PR number e gli scope guardrail.
- I template PowerShell e la skill export repository-local recepiscono lo
  stesso standard.
- Le skill esterne installate non vengono modificate dallo step.
- Il prossimo step consigliato e':

```text
0810) Publish Runner Recovery UX and No-False-Completed Guard
```

---

## DEC-094 - PowerShell publish skill sincronizzata al runner ASF provato

**Data:** 2026-06-08
**Stato:** Accettata

### Contesto

La pubblicazione dello STEP 0800 ha confermato che il flusso robusto non e' un
mega-wrapper adattivo, ma il modello gia' provato nello STEP 0790:

```text
config JSON esplicito + scripts/asf_publish_step.ps1 + Phase B -> recupero PR -> Phase C
```

### Decisione

Lo STEP 0805 introduce
`docs/motor/0805_POWERSHELL_PUBLISH_SKILL_SYNC_WITH_PROVEN_RUNNER_FLOW.md`.

La skill/template PowerShell repository-local deve raccomandare di default, per
pubblicazioni ASF, un config JSON esplicito con `expected_files` e
`changed_files`, chiamata a `scripts/asf_publish_step.ps1`, Phase B con
`-ApprovePublish`, recupero PR tramite `gh pr list --head`, validazione PR
number non vuoto e numerico, Phase C con `-PrNumber` e `-ApproveMerge`, e
verifiche finali prima di qualunque `COMPLETATO`.

### Motivazione

Duplicare logica di publish dentro wrapper PowerShell aumenta fragilita',
specialmente quando warning LF/CRLF, output Git e recovery si mescolano. Il
runner versionato deve restare la fonte operativa; il command pack deve
preparare config esplicita e orchestrare pochi passaggi verificabili.

### Conseguenze

- I template PowerShell e la skill export repository-local documentano il flusso
  config JSON + runner.
- Gli anti-pattern emersi nello STEP 0800 sono documentati.
- La skill installata esterna non viene modificata.
- Il prossimo step consigliato resta:

```text
0810) Publish Runner Recovery UX and No-False-Completed Guard
```

---

## DEC-091 - MVP Real Step Pilot 3 con Manifest Hooks

**Data:** 2026-06-07
**Stato:** Accettata

### Contesto

Dopo STEP 0770 il manifest puo' leggere gli output state machine prodotti dagli
hook del publish runner. Mancava un pilot reale piccolo che predisponesse una
modifica versionabile e una traccia evidence pronta per verificare runner ->
state machine -> manifest dopo pubblicazione human-gated.

### Decisione

Lo STEP 0780 introduce
`docs/motor/0780_MVP_REAL_STEP_PILOT_3_WITH_MANIFEST_HOOKS.md`.

Il pilot:

- resta documentale e a basso rischio;
- prepara stato iniziale `READY_TO_PUBLISH`;
- descrive la config publish con `state_machine_enabled: true`;
- richiede eventi `phase_b_started`, `phase_b_passed`, `pr_created`,
  `phase_c_started`, `phase_c_passed`, `main_verified` e `close_step`;
- definisce il manifest post-publish con `--include-runner-hooks`,
  `--state-file`, `--expected-step`, `--expected-final-state CLOSED` e
  `--expected-events`;
- mantiene Phase B, Phase C, commit, push, PR, merge e deploy fuori dallo
  scope Codex.

### Motivazione

Il valore operativo e' provare il collegamento hook/manifest su uno step reale
piccolo prima di renderlo prassi ordinaria. Il pilot non deve accelerare la
pubblicazione: deve rendere piu' chiara l'audit trail successiva.

### Conseguenze

- Decisione prudente del pilot: `PILOT STATUS: GO WITH WARNINGS`.
- La validazione completa resta da fare durante pubblicazione reale e manifest
  post-publish.
- Lo state file iniziale e la config hook-aware sono evidence locali, non
  approval.
- Il prossimo step consigliato e':

```text
0790) Post-MVP Roadmap and Hardening Plan
```

---

## DEC-090 - Runner Hook Evidence Manifest Integration

**Data:** 2026-06-07
**Stato:** Accettata

### Contesto

Dopo STEP 0760 gli hook del publish runner possono aggiornare la state machine,
ma il manifest 0710 non espone ancora in modo standard eventi runner, final
state e riferimenti Bridge dello state output.

### Decisione

Lo STEP 0770 estende `scripts/asf_motor_run_manifest.py` con `runner_hooks`.

La nuova sezione legge uno state file gia' prodotto dalla state machine e
normalizza:

- `final_state`;
- `last_event`;
- eventi osservati;
- eventi richiesti mancanti;
- state file;
- state Bridge root;
- publish runner output;
- publish config.

La CLI resta read-only verso Git/GitHub e aggiunge `--include-runner-hooks`,
`--state-file`, `--state-bridge-root`, `--publish-runner-output`,
`--publish-config`, `--require-closed-state`, `--expected-step`,
`--expected-final-state` e `--expected-events`.

### Motivazione

Il valore operativo e' rendere auditabile non solo lo smoke o il pilot, ma
anche la traccia reale Phase B/Phase C raccolta dalla state machine durante una
pubblicazione human-gated.

### Conseguenze

- State file mancante produce `INCOMPLETE`.
- State file corrotto, step mismatch o final state mismatch producono
  `FAIL_CLOSED`.
- Eventi richiesti mancanti producono `INCOMPLETE`.
- State file `CLOSED` con eventi richiesti presenti puo' produrre decisione
  `CLOSED`.
- Il manifest osserva gli eventi, ma non esegue Phase B, Phase C, publish,
  merge o deploy.
- Il prossimo step consigliato e':

```text
0780) MVP Real Step Pilot 3 with Manifest Hooks
```

---

## DEC-086 - End-to-End MVP Closure Pack con GO WITH WARNINGS

**Data:** 2026-06-07
**Stato:** Accettata

### Contesto

Dopo STEP 0720 il Motore ASF MVP ha componenti, smoke, manifest, state
machine, generator, publish runner e runbook operativo. Mancava una chiusura
formale che distinguesse baseline completata, warning noti, aree simulate e
lavoro post-MVP.

### Decisione

Lo STEP 0730 introduce `docs/motor/0730_END_TO_END_MVP_CLOSURE_PACK.md`.

Il closure pack:

- dichiara il perimetro MVP;
- elenca componenti inclusi ed esclusi;
- riepiloga evidenze principali e storia PR #51-#64 verificata da log locale;
- definisce criteri GO, WARNING e NO-GO;
- descrive stato gate, test, Bridge, state machine e manifest;
- chiude il MVP con decisione prudente `MVP STATUS: GO WITH WARNINGS`;
- raccomanda `0740) MVP Real Step Pilot` come passo post-MVP.

### Motivazione

Prima di aggiungere hook automatici o nuove integrazioni, il Motore deve avere
una baseline auditabile e condivisa. La chiusura con warning evita di
confondere uno smoke sintetico con un pilot reale e mantiene espliciti i gate
umani.

### Conseguenze

- Il MVP Motore e' usabile come baseline locale, human-gated e verificabile.
- Smoke sintetico, recovery manuale, `LAST-*` da controllare, GitHub non
  automatico e hook runner/state machine incompleti restano warning noti.
- Nessuna Phase B, Phase C, commit, push, PR, merge o deploy viene introdotto
  dal closure pack.
- Il prossimo step consigliato e':

```text
0740) MVP Real Step Pilot
```

---

## DEC-085 - MVP Usage Runbook come procedura operativa human-gated

**Data:** 2026-06-07
**Stato:** Accettata

### Contesto

Dopo STEP 0710 il Motore ASF dispone di smoke locale, manifest di run,
state machine, generator di config e publish runner, ma l'uso end-to-end
richiedeva ancora di ricostruire la sequenza da piu' documenti.

### Decisione

Lo STEP 0720 introduce `docs/motor/0720_MVP_USAGE_RUNBOOK.md`.

Il runbook documenta:

- scopo e limiti del Motore ASF MVP;
- directory Bridge operative;
- ruolo dei componenti principali;
- flusso prompt Codex -> implementazione -> smoke -> manifest -> review -> config -> Phase B -> Phase C;
- comandi esempio realistici e sicuri;
- lettura di `LAST-*`;
- fail-closed e recovery;
- checklist decisionale per Alberto.

### Motivazione

Prima di chiudere formalmente il MVP o aggiungere hook automatici al runner,
serve una procedura unica che renda il sistema usabile senza perdere i gate
umani.

### Conseguenze

- Workflow Health Check riconosce il runbook 0720 senza eseguire smoke,
  manifest, Bridge reale o fasi publish.
- Phase B e Phase C restano esplicite e human-gated.
- Il prossimo step consigliato e':

```text
0730) End-to-End MVP Closure Pack
```

---

## DEC-084 - Motor Run Manifest and Evidence Pack

**Data:** 2026-06-07
**Stato:** Accettata

### Contesto

Lo STEP 0700 produce evidence locali dello smoke MVP, ma gli artifact restavano distribuiti tra JSON e Markdown senza un record unico della run.

### Decisione

Lo STEP 0710 introduce `scripts/asf_motor_run_manifest.py`.

Il manifest:

- legge directory evidence 0700 o input manifest JSON;
- calcola checksum sugli artifact fisici;
- normalizza risk, gate, verification profile, state, publish config, artifact, check, warning e blocker;
- produce `motor_run_manifest.json` e `motor_run_summary.md`;
- scrive Bridge output solo con `--write-bridge`;
- decide in modo prudente tra `READY_TO_PUBLISH`, `BLOCKED`, `FAIL_CLOSED`, `INCOMPLETE` e `REVIEW_REQUIRED`.

### Motivazione

Prima di aggiungere hook automatici al runner serve una evidence unit stabile, leggibile e auditabile.

### Conseguenze

- Workflow Health Check riconosce script, test, runbook ed esempi 0710 senza eseguire il manifest.
- I test Bridge usano directory temporanee e non Dropbox reale.
- Il prossimo step consigliato e':

```text
0720) MVP Usage Runbook
```

---

## DEC-083 - End-to-End MVP Smoke Scenario locale e non operativo

**Data:** 2026-06-07
**Stato:** Accettata

### Contesto

Dopo STEP 0690, il Motore ASF aveva componenti collegati ma mancava una prova locale end-to-end che attraversasse classifier, dry-run, gate report, selector, generator e state machine.

### Decisione

Lo STEP 0700 introduce `scripts/asf_e2e_mvp_smoke.py` come smoke locale controllato.

Lo smoke:

- usa uno scenario positivo fino a `READY_TO_PUBLISH`;
- usa uno scenario negativo fail-closed da `IMPLEMENTED`;
- produce evidence pack JSON/Markdown;
- puo' scrivere Bridge solo con `--write-bridge`;
- non esegue Phase B, Phase C, commit, push, PR, merge, deploy, GitHub operativo o API esterne.

### Motivazione

Il MVP Motore deve dimostrare integrazione reale tra componenti prima di aggiungere hook automatici al runner.

### Conseguenze

- Workflow Health Check riconosce script, test e runbook 0700 senza eseguire lo smoke.
- I test usano directory temporanee e non Dropbox reale.
- Il prossimo step consigliato e':

```text
0710) Motor Run Manifest and Evidence Pack
```

---

## DEC-082 - State Machine Integration with Publish Config Generator fail-closed

**Data:** 2026-06-07
**Stato:** Accettata

### Contesto

Lo STEP 0650/0660 ha introdotto il Publish Config Generator e lo STEP 0670/0680 ha introdotto la state machine con Bridge.

Senza collegamento tra i due componenti, `LAST-Publish_Config.json` poteva nascere senza evidenza diretta dello stato corrente dello step.

### Decisione

Il generator resta legacy-compatible, ma quando l'integrazione state machine e' attivata deve:

- leggere uno state file esistente o `LAST-State.json`;
- accettare solo stati coerenti per config pronte (`LOCAL_VERIFIED`, `READY_TO_PUBLISH`, recovery solo esplicita);
- applicare `publish_config_generated` solo tramite `scripts/asf_step_state_machine.py`;
- fallire chiuso se stato, step, evento o target dopo evento sono incoerenti;
- scrivere riferimenti incrociati tra `LAST-Publish_Config.json` e `LAST-State.json` quando Bridge e' attivo.

### Motivazione

La config publish e' un artefatto operativo ad alto impatto: non deve sembrare pronta se lo step non ha superato i gate locali o se si trova in recovery non dichiarata.

### Conseguenze

- Il comportamento senza opzioni state machine resta invariato.
- `--update-state` porta lo stato standard da `LOCAL_VERIFIED` a `READY_TO_PUBLISH`.
- `--write-state-bridge` mantiene il formato Bridge 0680.
- La pubblicazione resta manuale e richiede il runner `scripts/asf_publish_step.ps1`.

### Prossimo step consigliato

0700) End-to-End MVP Smoke Scenario

---

## DEC-081 - State Machine Bridge Integration non operativa

**Data:** 2026-06-07
**Stato:** Accettata

### Contesto

Lo STEP 0670 ha introdotto una state machine locale, ma lo stato sotto `tmp/` non basta per riprendere il workflow tra ChatGPT, Codex e PowerShell.

Serve una persistenza consultabile nel Bridge ASF, separata da prompt Codex, publish config e output del publish runner.

### Decisione

Estendere `scripts/asf_step_state_machine.py` con output Bridge opt-in tramite `--write-bridge`.

Il Bridge dedicato e':

```text
D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\state_machine
```

Con `--write-bridge` la state machine produce:

- `LAST-State.json`;
- `LAST-Event.json`;
- `LAST-Output_Compatto.md`;
- `LAST-Output_Completo.txt`;
- file progressivi dello step per state, event, output compatto e output completo.

Se `--state-file` non viene passato insieme a `--write-bridge`, viene usato `<bridge-root>\LAST-State.json`.

### Motivazione

`LAST-State.json` rende recuperabile lo stato corrente dello step. `LAST-Output_Compatto.md` rende leggibile dove siamo e quale azione e' consigliata. L'output completo conserva input normalizzato, history, warning, blocker e file scritti.

Separare `state_machine` da `codex_command`, `publish_config` e `pwsh_command` riduce il rischio di ripartenze ambigue o di confondere report di stato con autorizzazioni di pubblicazione.

### Conseguenze

La state machine resta non operativa: non esegue Phase B, Phase C, commit, push, PR, merge o deploy.

I test usano solo root temporanee e non richiedono Dropbox reale.

Il prossimo step consigliato e':

```text
0690) State Machine Integration with Publish Config Generator
```

---

## DEC-080 - Step Execution State Machine locale e non operativa

**Data:** 2026-06-07
**Stato:** Accettata

### Contesto

Gli step 0650/0660 hanno mostrato un problema reale di sequenza: sviluppo sopra stato non ancora pubblicato, config Phase C non aggiornata, diagnostica manuale e rischio di messaggi di chiusura positivi dopo un errore.

Il problema non e' solo di comando PowerShell. Manca uno stato esplicito e persistente dello step.

### Decisione

Introdurre `scripts/asf_step_state_machine.py` come macchina a stati locale.

La state machine:

- modella stati ed eventi dello step ASF;
- valida transizioni ammesse;
- fallisce chiuso su stato ambiguo, state file corrotto o transizione incoerente;
- produce JSON, Markdown e testo compatto;
- persiste stato JSON sotto `tmp/`;
- rappresenta recovery e step combinati come `0650-0660` con warning espliciti;
- non esegue Phase B, Phase C, commit, push, PR, merge o deploy.

### Motivazione

Lo stato dello step deve essere osservabile e riprendibile prima di integrare generator, runner e futuri componenti del motore.

Separare il modello di stato dalle azioni operative evita che una transizione dichiarata diventi autorizzazione implicita alla pubblicazione.

### Conseguenze

Il nuovo script entra nel profilo `motor-core` e viene riconosciuto da Workflow Health Check, Verification Profile Selector e Publish Config Generator.

Il prossimo step consigliato e':

```text
0680) State Machine Bridge Integration
```

---

## DEC-079 - Publish Config Generator Bridge Output separato dal Publish Runner

**Data:** 2026-06-07
**Stato:** Accettata

### Contesto

Lo STEP 0650 ha introdotto un generator locale di config publish, ma l'output era limitato a `tmp/` o a una directory `--out-dir`.

Per l'uso operativo di Alberto/ChatGPT serve un pacchetto recuperabile dal Bridge senza confonderlo con gli output del runner di pubblicazione.

### Decisione

Estendere `scripts/asf_publish_config_generator.py` con output Bridge opt-in tramite `--write-bridge`.

Il Bridge dedicato del generator e':

```text
D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\publish_config
```

Il Bridge operativo del publish runner resta:

```text
D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\pwsh_command
```

Il generator produce file progressivi `step-II` e `LAST-*`, inclusi `LAST-Publish_Config.json`, riepilogo compatto e output completo.

### Motivazione

La separazione mantiene chiara la differenza tra config draft, audit della generazione e pubblicazione effettiva.

`LAST-Publish_Config.json` riduce il copia/incolla manuale, ma non autorizza Phase B o Phase C.

### Conseguenze

Phase B resta manuale e richiede `-ApprovePublish`.

Phase C resta manuale e richiede `-ApproveMerge` e numero PR.

La validazione `--validate-plan` puo' invocare solo `-Phase Plan`; fallimenti Plan bloccano il generator con errore non-zero.

Il prossimo step consigliato e':

```text
0670) Step Execution State Machine
```

---

## DEC-078 - Verification Profile Integration with Publish Runner

**Data:** 2026-06-07
**Stato:** Accettata

### Contesto

Lo STEP 0630 ha introdotto un selector locale dei verification profile, ma il Publish Runner 0590 non lo usava ancora.

La pubblicazione degli step deve restare human-gated, ma le config publish devono poter dichiarare e validare un profilo di verifica senza duplicare regole nel PowerShell.

### Decisione

Integrare il selector nel publish runner come validazione opzionale di config.

Il runner:

- invoca `scripts/asf_verification_profile_selector.py` solo se la config contiene campi profilo;
- mantiene compatibili le config legacy senza profilo;
- richiede un profilo dichiarato quando sono presenti campi di integrazione profilo;
- blocca se il selector fallisce chiuso;
- blocca se il profilo dichiarato e' piu' leggero del profilo raccomandato;
- mantiene `allow_profile_check_reduction` con default `false`;
- non riduce Phase C nello STEP 0640.

### Motivazione

La logica dei profili deve restare in un componente Python testabile e deterministico. Il runner PowerShell deve solo validare il contratto operativo e fermarsi prima di azioni Git/GitHub se il profilo non e' coerente.

### Conseguenze

Phase B richiede ancora `-ApprovePublish` e Phase C richiede ancora `-ApproveMerge`.

Gli output Bridge del runner includono profilo dichiarato, profilo raccomandato, stato validazione, warning e riduzione abilitata o no.

Il prossimo step consigliato e':

```text
0650) Verification Profile Driven Publish Config Generator
```

---

## DEC-077 - Verification Profile Selector and Test Cost Policy

**Data:** 2026-06-07
**Stato:** Accettata

### Contesto

Gli step 0580-0620 hanno reso il motore ASF piu' osservabile: dry-run loop, risk classifier, integrazione del rischio e Gate Decision Report.

Le verifiche locali sono pero' volutamente ridondanti: test mirati, full pytest, workflow health, verify gate, Phase A, Phase B e Phase C possono ripetersi. La ridondanza e' utile prima di publish o merge, ma puo' diventare costosa durante iterazioni locali a scope chiaro.

### Decisione

Introdurre `scripts/asf_verification_profile_selector.py` come selettore locale dei profili di verifica.

Il selector:

- supporta `docs-only`, `code-unit`, `motor-core`, `publish`, `final-main` e `high-risk`;
- restituisce JSON, Markdown o testo compatto;
- include `recommended_checks`, `required_checks`, `optional_checks`, `skipped_checks`, `estimated_cost` e note safety;
- fallisce chiuso su input vuoto, ambiguo, non riconosciuto o high-risk senza approval elevato;
- tratta `scripts/asf_publish_step.ps1` come file `motor-core` quando viene modificato;
- tratta `publish` come intento operativo, non come semplice presenza della parola in un path.

Lo STEP 0630 non modifica direttamente `scripts/asf_publish_step.ps1` e non integra ancora il selector nel Gate Decision Report.

### Motivazione

La scelta dei test deve diventare esplicita e verificabile, non una scorciatoia implicita.

Separare il selector consente di testare la policy di costo prima di collegarla a runner o packet decisionali. La sicurezza resta fail-closed: se non e' chiaro che un profilo ridotto sia appropriato, il sistema raccomanda full verification o review manuale.

### Conseguenze

`docs-only` e `code-unit` possono ridurre tempi locali quando scope e rischio sono chiari.

`motor-core`, `publish`, `final-main` e `high-risk` restano conservativi e preservano full pytest, workflow health, verify gate, approval o verifica finale quando serve.

Il prossimo step consigliato e':

```text
0640) Verification Profile Integration with Publish Runner
```

---

## DEC-076 - Gate Decision Report and Human Approval Packet

**Data:** 2026-06-07
**Stato:** Accettata

### Contesto

Lo STEP 0610 produce un `risk_report.json` strutturato con livello L0-L4, gate richiesto, `allowed`, stato dry-run e blocker del piano.

Questa evidence e' utile tecnicamente, ma non basta come pacchetto decisionale per Alberto: serve un report che spieghi cosa si sta approvando, quali file e check sono coinvolti, quali blocker restano e quale azione successiva e' consigliata.

### Decisione

Introdurre `scripts/asf_gate_decision_report.py` come generatore locale di Approval Packet umano.

Il report:

- legge JSON prodotto o compatibile con il dry-run/risk output 0610;
- non duplica le regole L0-L4 del Risk Classifier;
- produce output JSON, Markdown e testo compatto;
- gestisce `APPROVE_LOCAL_ONLY`, `NEEDS_HUMAN`, `APPROVE_PUBLISH`, `BLOCKED` e `FAIL_CLOSED`;
- richiede check locali coerenti per L2;
- richiede `explicit_publish_approval` per L3;
- blocca L4 di default o fallisce chiuso;
- non esegue publish, write target, provider live, commit, push, PR, merge o deploy.

### Motivazione

Il motore ASF deve rendere le decisioni supervisionate comprensibili prima di aumentare l'autonomia operativa.

Separare il Gate Decision Report dal Dry-run Loop Runner mantiene semplice il runner 0580/0610 e permette di evolvere la decisione umana come componente testabile.

### Conseguenze

Il publish runner 0590 resta lo strumento standard per pubblicare dopo review umana.

Lo STEP 0620 introduce anche una prima matrice dei verification profile. Il prossimo step consigliato diventa:

```text
0630) Verification Profile Selector + Test Cost Policy
```

---

## DEC-073 - Stable PowerShell Publish Runner

**Data:** 2026-06-07
**Stato:** Accettata

### Contesto

La pubblicazione degli step ASF tramite mega-blocchi PowerShell copiati da chat si e' dimostrata fragile: quoting, nesting, here-string aperte e incolla interrotto possono rompere un flusso critico.

Serve un runner versionato e testabile che separi comando corto, configurazione dello step, gate locali, pubblicazione e report Bridge.

### Decisione

Introdurre `scripts/asf_publish_step.ps1` come runner stabile per la pubblicazione degli step ASF.

Il runner usa:

- config JSON per step, branch, messaggi, PR, scope e check;
- comandi in forma `argv`;
- FASE A per verifica locale;
- FASE B con `-ApprovePublish` per branch, commit, push e PR;
- FASE C con `-ApproveMerge` per checks, merge e verifica finale;
- output Bridge con file numerati e alias `LAST-*`;
- DOCX OpenXML minimale senza dipendenze esterne.

La modalita' shell resta disabilitata. `Invoke-Expression` non viene usato.

### Motivazione

Il workflow deve essere ripetibile e correggibile. Un file `.ps1` versionato riduce la fragilita' dell'incolla, permette test automatici e rende il comando effettivamente eseguito breve e riproducibile.

Gli alias `LAST-*` sono accettati in questo runner come compatibilita' operativa richiesta per il Bridge, ma non sostituiscono Git, report step e file versionati come fonte autorevole.

### Conseguenze

Le future pubblicazioni ASF possono usare:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\asf_publish_step.ps1 -Config path\to\publish.config.json -Phase A
```

La pubblicazione e il merge richiedono ancora consenso esplicito e gate superati.

Il prossimo step consigliato e':

```text
0600) Risk Classifier + Gate Policy
```

---

## DEC-075 - Risk classifier integrated into dry-run loop

**Data:** 2026-06-07
**Stato:** Accettata

### Contesto

Lo STEP 0600 ha introdotto un classifier L0-L4 locale, deterministico e fail-closed, ma il Dry-run Loop Runner 0580 usava ancora una classificazione minima interna.

Per trasformare il classifier nel primo nodo operativo del motore ASF serve collegarlo al checkpoint `RISK_CLASSIFY`, senza trasformare il runner dry-run in un executor di write, publish o live run.

### Decisione

Integrare `scripts/asf_risk_classifier.py` dentro `scripts/asf_dry_run_loop_runner.py`.

Il runner:

- costruisce un `ClassifierInput` da title, objective, allowed scope, checks e azioni/comandi del piano;
- non considera `forbidden_actions` come intento operativo;
- importa il classifier reale e non copia le regole L0-L4;
- scrive `risk_report.json` con blocchi `risk`, `gate`, `dry_run` e `plan_blockers`;
- fallisce chiuso se il classifier manca, restituisce schema non valido, l'input e' ambiguo, il piano non e' dry-run o L4 non ha gate elevato dichiarato;
- resta inertizzato e non esegue gate reali.

### Motivazione

Il risk classifier deve essere riusabile e testabile come fonte unica della policy. Il Dry-run Loop Runner deve consumarne l'output come evidence, non reinterpretare le regole o promuovere autorizzazioni operative.

Separare `risk.allowed` da autorizzazione operativa evita un errore pericoloso: un gate dichiarato nel JSON non equivale a commit, push, PR, merge, deploy o write permessi dal runner.

### Conseguenze

Il checkpoint `RISK_CLASSIFY` diventa il primo nodo operativo del motore ASF.

Il prossimo step consigliato e':

```text
0620) Gate Decision Report and Human Approval Packet
```

---

## DEC-074 - Risk Classifier and Gate Policy fail-closed

**Data:** 2026-06-07
**Stato:** Accettata

### Contesto

Il Dry-run Loop Runner 0580 contiene una classificazione minima interna, sufficiente per dimostrare il loop, ma non abbastanza stabile come componente riusabile del motore ASF.

Dopo lo STEP 0590, la pubblicazione degli step usa un runner PowerShell versionato e human-gated. Serve quindi separare la classificazione del rischio dalla pubblicazione, mantenendo il comportamento fail-closed e senza abilitare write automatici.

### Decisione

Introdurre `scripts/asf_risk_classifier.py` come classificatore locale, deterministico e standard-library-only.

Il classificatore:

- accetta testo libero o JSON leggero;
- assegna il livello massimo L0-L4;
- restituisce output strutturato con `risk_level`, `allowed`, `required_gate`, `reasons`, `matched_rules`, `fail_closed` e `recommended_next_action`;
- fallisce chiuso su input vuoto, incompleto o non riconosciuto;
- tratta commit, push e PR come L3;
- tratta merge, deploy, cancellazioni, secret, live provider, rete e side effect esterni come L4.

La gate policy iniziale e':

- L0: `none`;
- L1: `implicit_or_local_approval`;
- L2: `local_verification`;
- L3: `explicit_publish_approval`;
- L4: `elevated_manual_approval`.

Lo STEP 0600 non modifica direttamente il runner 0580 e non modifica `scripts/asf_publish_step.ps1`.

### Motivazione

Separare il classifier consente test mirati, esempi golden minimi e integrazione futura nel checkpoint `RISK_CLASSIFY` senza cambiare nello stesso step il comportamento del loop dry-run.

La scelta fail-closed mantiene ASF coerente con il principio che l'ambiguita' non deve diventare autorizzazione implicita.

### Conseguenze

Il prossimo step dovrebbe collegare il nuovo classifier al Dry-run Loop Runner, sostituendo la classificazione minima interna o affiancandola con compatibilita' controllata.

Il prossimo step consigliato e':

```text
0610) Risk Classifier Integration with Dry-run Loop Runner
```

---

## DEC-075 - Publish config generator come configuratore non operativo

**Data:** 2026-06-07
**Stato:** Accettata

### Contesto

Lo STEP 0640 ha permesso al Publish Runner di validare profili di verifica dichiarati usando il selector 0630.

Rimaneva pero' una superficie manuale fragile: la scrittura delle config JSON per `scripts/asf_publish_step.ps1`, inclusi check Phase A/Phase C, scope file, profilo dichiarato e campi selector.

### Decisione

Introdurre `scripts/asf_publish_config_generator.py` come generatore locale di bozze config publish.

Il generatore:

- usa il selector 0630 come fonte della raccomandazione;
- produce config JSON e riepilogo Markdown;
- tratta il nuovo generator come superficie `motor-core`;
- blocca input mancanti, L4, `high-risk`, `final-main` e selector fail-closed;
- mantiene Phase C robusta;
- non esegue il publish runner;
- non autorizza azioni GitHub o deploy.

### Motivazione

La config publish deve essere ripetibile e validabile, ma la pubblicazione resta un atto operativo separato e human-gated.

Separare generator, review e runner evita di trasformare una bozza config in una autorizzazione implicita.

### Conseguenze

Lo STEP 0650 riduce errori manuali e ridondanze nella preparazione della config, ma non chiude il tema dell'audit trail Bridge dedicato al generator.

Il prossimo step consigliato e':

```text
0660) Publish Config Generator Bridge Output Integration
```

---

## DEC-072 - Dry-run Loop Runner locale

**Data:** 2026-06-07
**Stato:** Accettata

### Contesto

Lo STEP 0570 ha fissato la rotta verso autonomia supervisionata a gate e ha congelato nuovi raffinamenti di meta-processo finche' il motore non dimostra almeno un giro end-to-end dry-run.

Serve quindi un runner minimo che colleghi richiesta simulata, piano, checkpoint, evidence, review e decisione finale senza introdurre live run, write automatico o pubblicazione Git.

### Decisione

Introdurre `scripts/asf_dry_run_loop_runner.py` come primo runner locale del MVP Motore.

Il runner:

- legge una richiesta JSON simulata;
- legge un piano dry-run fornito oppure ne genera uno deterministico;
- attraversa gli stati dello spec 0570;
- produce artifact JSON/Markdown e `state_log.jsonl`;
- classifica il rischio in modo minimo e fail-closed;
- produce review deterministica locale;
- termina con `NEEDS_HUMAN` oppure `FAIL`;
- non chiama provider esterni;
- non legge secret/API key;
- non modifica il repository target;
- non esegue commit, push, PR, merge, deploy o release.

### Motivazione

Il primo valore del motore non e' eseguire Codex o scrivere codice nei target, ma dimostrare che la sequenza e' osservabile, ripetibile e bloccabile da gate.

Mantenere risk classifier e review nello stesso script e' accettabile per STEP 0580, ma solo come MVP. Gli step successivi devono separarli e renderli piu' espliciti.

### Conseguenze

Gli artifact runtime vivono sotto:

```text
tmp/asf_dry_run_loop/<project>/step_<step>/
```

Lo STEP 0590 ha inserito prima il runner PowerShell stabile per rendere meno fragile la pubblicazione degli step. Il Risk Classifier + Gate Policy viene quindi spostato allo STEP 0600.

Il prossimo step consigliato e':

```text
0600) Risk Classifier + Gate Policy
```

---

## DEC-071 - Supervised gate autonomy and MVP motor roadmap

**Data:** 2026-06-07
**Stato:** Accettata

### Contesto

Dopo STEP 0560 il progetto deve evitare due derive: retry/live work non prioritario e accumulo di nuovo meta-processo senza un loop operativo verificabile.

ASF ha gia' prompt packet, verification gate, report intake, human gate, closure pack e design di invocation. Manca pero' un motore minimo che attraversi questi pezzi in sequenza, produca evidence e si fermi ai gate.

### Decisione

Adottare autonomia supervisionata a gate come rotta strategica.

Il motore futuro deve attraversare stati espliciti:

```text
PLAN_NEXT_STEP -> BUILD_TASK_PACKET -> RISK_CLASSIFY -> EXECUTE_DRY_OR_WRITE -> RUN_TESTS -> INDEPENDENT_REVIEW -> GATE_DECISION -> COMMIT_OR_HOLD
```

La roadmap prioritaria diventa:

```text
0570 ADR + MVP Motor Roadmap
0580 Dry-run Loop Runner
0590 Stable PowerShell Publish Runner
0600 Risk Classifier + Gate Policy
0610 Risk Classifier Integration with Dry-run Loop Runner
0620 Gate Decision Report and Human Approval Packet
0630 Verification Profile Selector + Test Cost Policy
0640 Verification Profile Integration with Publish Runner
0650 Verification Profile Driven Publish Config Generator
0660 Publish Config Generator Bridge Output Integration
```

Nuovi step di meta-processo, naming, packaging, validazioni strict o guardrail isolati restano congelati finche' il motore non completa almeno un giro end-to-end dry-run.

### Motivazione

Il valore di ASF non e' autonomia cieca, ma automazione locale, diagnosabile e supervisionata. Il gate condizionale consente avanzamento quando rischio, scope, test, review e confidence sono favorevoli, e impone hold o revisione umana quando l'evidence non basta.

### Conseguenze

I futuri step devono privilegiare MVP Motore rispetto a raffinamenti laterali.

L3 e L4 restano human-gated. Commit, push, PR, merge, deploy, cancellazioni e costi API live non diventano azioni automatiche.

Il prossimo step consigliato e':

```text
0580) Dry-run Loop Runner
```

---

## DEC-095 - Scope discovery assistivo e output accessori non bloccanti

**Data:** 2026-06-08
**Stato:** Accettata

### Contesto

Dopo gli STEP 0800 e 0805 il publish runner ASF blocca correttamente file fuori
scope, ma la preparazione manuale di `expected_files` e `changed_files` puo'
dimenticare file reali. Inoltre un DOCX/accessorio puo' fallire dopo gate finali
gia' passati, creando un falso segnale di pubblicazione fallita.

### Decisione

Il runner deve offrire scope discovery e `PrepareConfig`, ma solo come supporto
alla review umana. La lista file viene scoperta da stdout Git dedicato
(`diff --name-only`, `diff --cached --name-only`, `ls-files --others`) e non da
parsing fragile di `git status --short` o output `2>&1`.

Out-of-scope resta bloccante. Il recovery report e la suggested config aiutano
a correggere lo scope, ma non pubblicano automaticamente.

TXT e Markdown restano output primari. DOCX e accessori sono best-effort: dopo
gate finali passati, un errore DOCX produce `COMPLETATO CON WARNING NON
BLOCCANTE`, non `BLOCCATO`.

### Conseguenze

La skill/template PowerShell deve raccomandare:

- `PrepareConfig` o scope discovery;
- review umana dello scope;
- Phase B/C solo con config JSON revisionato;
- recovery report/suggested config in caso di out-of-scope;
- nessun `COMPLETATO` prima dei gate finali;
- DOCX/accessori non bloccanti dopo pubblicazione verificata.

Il prossimo step consigliato e':

```text
0820) Bridge Output Retry, Fallback and LAST Validation
```

---

## DEC-096 - Retry/fallback Bridge e LAST senza falsi fallimenti

**Data:** 2026-06-08
**Stato:** Accettata

### Contesto

Durante la pubblicazione dello STEP 0810, Phase B era completata ma il runner
ha fallito nella scrittura di un file Bridge `Output_Completo` perche' il file
era bloccato da un altro processo. Le cause probabili includono Dropbox sync,
preview/editor, antivirus/indexing o un wrapper esterno con transcript sullo
stesso file.

### Decisione

Il publish runner deve trattare i gate veri e gli output accessori come superfici
diverse:

- gate Git, PR, test, Workflow Health Check, Verification Gate e diff-check
  falliti restano `BLOCCATO`;
- output Bridge/LAST primario bloccato dopo gate passati usa retry controllato;
- se il primario resta bloccato, viene scritto un fallback timestampato nella
  stessa cartella Bridge;
- il compatto Markdown e' obbligatorio nel path primario o fallback;
- DOCX resta best-effort;
- i `LAST-*` sono aggiornati con retry/fallback e warning esplicito;
- il runner e' single writer owner dei propri output standard.

### Conseguenze

Wrapper esterni non devono usare `Start-Transcript` sullo stesso
`Output_Completo` del runner. Se serve un log wrapper, usare un nome separato
come `NNNN-Wrapper_Log_*.txt`.

Un Bridge/LAST lock dopo gate passati produce `COMPLETATO CON WARNING NON
BLOCCANTE`, non falso fallimento. Un gate vero fallito resta sempre
`BLOCCATO`.

Il prossimo step consigliato e':

```text
0830) MVP Real Step Pilot 4 - Slightly More Operational
```

---

## DEC-097 - Pilot operativo post-0820 senza pubblicazione automatica

**Data:** 2026-06-08
**Stato:** Accettata

### Contesto

Dopo gli hardening 0800-0820 il Motore ASF dispone di guardrail nativi
PowerShell, flusso runner allineato, scope discovery, recovery out-of-scope,
retry/fallback Bridge e LAST validation. Serve un pilot reale piu' operativo
dei precedenti, ma ancora piccolo e non pubblicante da Codex.

### Decisione

Lo STEP 0830 introduce un operational pilot pack con:

- documento operativo 0830;
- manifest JSON di esempio non operativo;
- test automatico dedicato;
- aggiornamento degli indici minimi;
- prova `PrepareConfig` non pubblicante quando ci sono changed files
  intenzionali.

Il pilot deve dimostrare `PrepareConfig`, review umana dello scope, suggested
config/recovery report, Phase B, recupero PR, Phase C, Bridge/LAST validation,
LF/CRLF come warning controllati e DOCX/output accessori best-effort.

### Conseguenze

Il pilot non autorizza Phase B, Phase C, commit, push, PR, merge, deploy o tag
da Codex. La pubblicazione resta human-gated e separata.

Il prossimo step consigliato e':

```text
0840) Runner Hook Evidence Manifest Post-Publish Pack
```

---

## DEC-098 - Post-publish evidence pack leggibile e non automatico

**Data:** 2026-06-08
**Stato:** Accettata

### Contesto

Dopo gli step 0800-0830 il publish runner ASF e' piu' robusto su comandi
nativi, scope discovery, recovery UX, Bridge retry/fallback, LAST validation e
pilot operativo. Dopo una pubblicazione riuscita restano pero' evidenze sparse:
PR, merge commit, checks finali, output Bridge, `LAST-*`, warning accettati e
manifest/evidence.

### Decisione

Lo STEP 0840 introduce un post-publish evidence pack documentale:

- documento operativo 0840;
- manifest JSON esempio non live;
- test automatico dedicato;
- riferimenti minimi in README, changelog, roadmap, index, health, quick
  reference, cookbook e template/skill PowerShell repository-local.

Il pack deve indicare PR, merge commit, checks finali, Bridge outputs, `LAST-*`,
warning accettati, manifest/evidence disponibili e prossimo step consigliato.

### Conseguenze

Il pack non autorizza commit, push, PR, merge, deploy o tag. Non introduce una
nuova fase runner obbligatoria e non modifica la skill installata fuori
repository. Git, PR mergiata, commit finale e file versionati restano le fonti
autorevoli; Bridge e `LAST-*` restano supporti operativi.

Il prossimo step consigliato e':

```text
0850) First Real External Workflow Pilot
```

---

## DEC-099 - First Real External Workflow Pilot planning-only

**Data:** 2026-06-08
**Stato:** Accettata

### Contesto

Dopo gli step 0800-0840 il runner ASF ha guardrail, recovery, Bridge/LAST
validation, pilot operativo interno e pack post-publish. Il passo successivo e'
preparare un primo pilot esterno senza anticipare modifiche reali fuori da ASF.

### Decisione

Lo STEP 0850 introduce un External Workflow Pilot Pack preparatorio:

- documento operativo 0850;
- matrice di scelta repo;
- raccomandazione `Codex_Skills` come primo target esterno;
- `Family_Photo_Organizer` come candidata futura;
- esclusione di `Mansionario_Vivo` come primo pilot per rischio alto;
- manifest JSON esempio `planning_only`;
- test automatico dedicato;
- safety boundaries e human gate espliciti.

### Conseguenze

Il pack non accede operativamente a repository esterne, non modifica
`Codex_Skills` o altri target e non autorizza commit, push, PR, merge, deploy o
tag. Il futuro pilot dovra' partire da controlli read-only/dry-run e fermarsi al
gate umano.

Il prossimo step consigliato e':

```text
0860) Codex_Skills External Workflow Dry-Run Pilot
```

---

## DEC-100 - Codex_Skills external dry-run read-only

**Data:** 2026-06-08
**Stato:** Accettata

### Contesto

Dopo lo STEP 0850, `Codex_Skills` e' la candidata principale per il primo pilot
esterno ASF perche' reale, vicina a skill/template e meno rischiosa di un
progetto applicativo operativo. Lo step successivo deve dimostrare readiness,
dry-run, preview, risk assessment ed evidence senza modificare la repo esterna.

### Decisione

Lo STEP 0860 introduce un dry-run pack esterno controllato:

- documento operativo 0860;
- readiness report su `Codex_Skills`;
- dry-run plan JSON non pubblicante;
- changed-files preview ipotetica;
- human approval gate per il futuro 0870;
- evidence manifest di dry-run;
- test automatico dedicato.

L'accesso alla repo esterna resta read-only. Il pack non autorizza scritture,
sincronizzazioni skill, installazioni skill, commit, push, PR, merge, deploy o
tag su repository esterne.

### Conseguenze

ASF puo' preparare un workflow esterno tracciabile e human-gated senza toccare
il target. Il futuro 0870 potra' proporre una prima modifica minima solo dopo
review umana del readiness report, del dry-run plan e della changed-files
preview.

Il prossimo step consigliato e':

```text
0870) Codex_Skills First Controlled Write Pilot
```
