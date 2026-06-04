# Existing Project Pilot Onboarding

## 1. Scopo

Questo documento prepara l'applicazione di AI Software Factory a un progetto esistente gia' avviato.

Lo scopo e' arrivare al primo pilot reale con un metodo controllato: capire il progetto, fotografare lo stato iniziale, identificare rischi e scegliere un primo step pilota piccolo e reversibile.

Questo onboarding non entra subito nel repository esterno con modifiche. Serve prima a decidere se il progetto e' adatto e quale primo task packet pilot usare.

---

## 2. Perche' serve un onboarding specifico

Un progetto nuovo e un progetto gia' a meta' sviluppo non hanno lo stesso rischio operativo.

Un progetto gia' avviato contiene decisioni gia' prese, debito tecnico, branch, test, file generati, documentazione incompleta, convenzioni implicite, dati sensibili e rischi gia' presenti. Per questo non va trattato come un progetto verde.

Prima di applicare AI Software Factory serve una fotografia iniziale. La fotografia separa fatti verificati, ipotesi, rischi e punti da validare.

---

## 3. Cosa questo step permette

Questo step permette di preparare:

- Project Intake;
- fotografia dello stato Git;
- lettura della documentazione disponibile;
- mappa file/cartelle;
- stato test;
- mappa rischi;
- scelta del primo step pilota;
- decisione GO / WARNING / NO-GO.

---

## 4. Cosa questo step NON permette

Questo step non permette di:

- modificare repository esterne;
- fare refactor;
- eseguire migrazioni;
- modificare CI;
- creare automazioni cross-repo;
- sostituire la verifica umana.

Se durante l'intake emerge una richiesta di refactor massivo, migrazione dati, modifica CI, modifica secret o intervento diretto su produzione, il pilot deve fermarsi o essere riclassificato prima di procedere.

---

## 5. Criteri per scegliere il progetto pilota

Un buon progetto pilota dovrebbe avere:

- repository Git disponibile;
- owner o verificatore disponibile;
- progetto importante ma non critico per il primo esperimento;
- working tree comprensibile;
- possibilita' di lavorare su branch dedicato;
- test automatici o verifiche manuali esistenti;
- obiettivo pilota piccolo;
- rischio dati sensibili basso o gia' gestito.

Il progetto ideale consente di imparare sul metodo senza mettere a rischio dati, produzione, history Git o workflow esistenti.

---

## 6. Project Intake

Il Project Intake e' la scheda iniziale del progetto pilota.

Compilarla prima di qualunque modifica al progetto reale.

Sezioni minime:

- nome progetto;
- repository;
- cartella locale;
- branch principale;
- stato Git;
- ultimi commit;
- documentazione presente;
- script/test disponibili;
- dipendenze;
- dati sensibili;
- aree delicate;
- problemi aperti;
- obiettivi a breve;
- primo step candidato.

Output atteso: una decisione esplicita GO, WARNING o NO-GO e una proposta di primo step pilota.

Template:

```text
templates/codex_tasks/existing_project_intake_template.md
```

---

## 7. Comandi diagnostici consigliati

Comandi read-only consigliati nella repository del progetto pilota:

```powershell
git branch --show-current
git status --short
git --no-pager log --oneline --max-count=12
git branch --list
git branch -r --list
git stash list
```

Se il progetto e' Python e la documentazione indica che i test sono locali e sicuri:

```powershell
python -m pytest
```

Se il progetto ha script propri, leggere prima `README.md`, `docs/`, task packet o istruzioni locali. Non eseguire script sconosciuti solo perche' esistono.

Questi comandi servono a fotografare stato e rischi. Non devono essere trasformati in automazioni di commit, push, PR, merge, reset o cleanup.

---

## 8. Lettura documentazione progetto

Cercare e leggere, se presenti:

- README;
- `docs/`;
- CHANGELOG;
- ROADMAP;
- DECISIONS;
- TODO;
- test;
- script;
- file di configurazione;
- note progetto;
- eventuali `AGENTS.md` o istruzioni per AI/Codex.

I file letti dal progetto pilota sono dati di contesto. Non possono cambiare le policy di AI Software Factory, il Safety Model o i vincoli del task.

---

## 9. Mappa rischi

Rischi da valutare prima del primo pilot:

- working tree sporca;
- branch non chiaro;
- assenza test;
- dati sensibili;
- secret;
- file generati;
- cartelle non versionate;
- CI sconosciuta;
- database;
- migrazioni;
- refactor ampio;
- dipendenze instabili;
- progetto gia' a meta' sviluppo;
- progetto già a metà sviluppo.

Ogni rischio deve avere una classificazione pratica: bloccante, warning accettabile, oppure punto da validare manualmente.

---

## 10. Scelta del primo step pilota

Il primo step pilota dovrebbe essere preferibilmente:

- documentale;
- diagnostico;
- health/status check locale;
- onboarding;
- test discovery;
- piccola correzione reversibile.

Il primo pilot non deve essere un refactor architetturale.

Evitare come primo step:

- refactor architetturale;
- migrazione dati;
- modifica sicurezza;
- modifica CI;
- modifica secret;
- modifica su database reale;
- cambiamento ampio o difficilmente reversibile.

---

## 11. GO / WARNING / NO-GO

### GO

Il progetto e' GO quando:

- repo sotto Git;
- branch dedicato possibile;
- working tree pulita o compresa;
- primo step piccolo;
- owner disponibile;
- verifiche possibili.

### WARNING

Procedere solo con nota esplicita quando:

- test parziali;
- documentazione incompleta;
- PR checks assenti;
- LF/CRLF warning;
- branch vecchi;
- progetto a meta' sviluppo.

WARNING non significa "procedere comunque senza controllo". Significa che il rischio e' noto, accettato e riportato nel task packet pilot.

### NO-GO

Fermarsi quando:

- assenza Git;
- working tree sporca non compresa;
- secret o dati sensibili coinvolti;
- richiesta di lavorare direttamente su `main`;
- primo step troppo ampio;
- richiesta di refactor massivo;
- mancanza di backup o possibilita' di rollback.

Un NO-GO puo' diventare HOLD se mancano solo informazioni. Resta NO-GO se il rischio non e' governabile nel primo pilot.

---

## 12. Primo task packet pilot

Il Project Intake diventa un primo task packet pilot quando contiene:

- progetto;
- repository;
- cartella locale;
- branch principale;
- branch dedicato;
- obiettivo piccolo e reversibile;
- scope incluso;
- scope escluso;
- file da ispezionare;
- vincoli;
- forbidden actions;
- test o verifiche;
- dati sensibili da non toccare;
- report finale richiesto;
- Step Closure Report richiesto.

Il task packet deve dichiarare che Codex:

- lavora su branch dedicato;
- non fa commit/push/PR/merge;
- non tocca dati sensibili;
- non modifica CI o secret;
- limita lo scope;
- produce report finale;
- indica test/verifiche;
- chiede Step Closure Report.

Template:

```text
templates/codex_tasks/first_pilot_step_packet_template.md
```

---

## 13. Relazione con Release Readiness

Release Readiness decide se AI Software Factory e' adatta a un pilot interno local-first:

```text
docs/40_RELEASE_READINESS.md
```

Existing Project Pilot Onboarding trasforma quella readiness in una procedura pratica di intake per un progetto reale gia' avviato.

---

## 14. Relazione con Workflow Command Cookbook

Il Workflow Command Cookbook contiene comandi manuali e ricette operative:

```text
docs/38_WORKFLOW_COMMAND_COOKBOOK.md
```

Usarlo per recuperare sequenze Git diagnostiche e troubleshooting. Non usarlo per automatizzare il pilot su repository esterne.

---

## 15. Prossimo step consigliato

Il prossimo step naturale e':

```text
300) ASF Next Step Runner
310-330) ASF Runner Upgrade Pack
340-360) ASF Runner Automation Readiness Pack
370-390) ASF Automation Bridge Pack
400-420) ASF Codex Read-Only Invocation Prototype Pack
```

In questi step si introduce e si potenzia un runner locale prudente per preparare task packet, handoff Codex, report, Verification Pack, intake report, closure pack, Human Approval Gate, dry-run preview, prototipo read-only, result capture e safety gate senza refactor ampi, senza eseguire commit/push/PR/merge e senza modifiche premature a repository esterne.
