# STEP 0860 - Codex_Skills External Workflow Dry-Run Pilot

## 1. Scopo dello step

Lo STEP 0860 esegue il primo dry-run esterno controllato di AI Software
Factory su `Codex_Skills`, senza modificare la repository esterna.

Il risultato e' un pacchetto locale ASF con readiness report, dry-run plan,
changed-files preview ipotetica, risk assessment, human approval gate ed
evidence manifest. Il pilot dimostra che ASF puo' preparare un workflow su una
repo esterna in modo tracciabile, prudente e human-gated.

## 2. Prerequisito 0850

Prima di procedere e' stato verificato che `main` contiene:

```text
09ff164 0850 add first real external workflow pilot pack (#78)
```

Lo STEP 0850 ha raccomandato `Codex_Skills` come primo target esterno perche'
la repo e' reale, vicina a skill/template, non produttiva e meno rischiosa di
progetti applicativi operativi.

## 3. Perche' Codex_Skills

`Codex_Skills` e' la candidata corretta per il primo pilot esterno perche':

- contiene skill e template direttamente collegati al metodo ASF;
- e' una repo reale ma non un sistema produttivo applicativo;
- ha scope leggibile e rischio inferiore rispetto a
  `Family_Photo_Organizer`;
- permette un dry-run utile senza richiedere deploy, servizi o dati sensibili;
- `Mansionario_Vivo` resta escluso come primo pilot per rischio operativo alto.

## 4. Vincoli read-only

Questo step e' read-only / dry-run verso `Codex_Skills`.

Azioni vietate sulla repo esterna:

- scrivere o modificare file;
- installare, disinstallare o sincronizzare skill;
- eseguire commit, push, PR, merge, deploy o tag;
- eseguire checkout, switch, pull, fetch, merge, rebase o cleanup;
- cancellare file o directory;
- alterare stato locale o remoto.

Azioni consentite e svolte solo in lettura:

- verifica esistenza path;
- lettura branch corrente;
- lettura `git status --short`;
- lettura remote;
- lettura ultimi commit;
- elenco sintetico di file/cartelle;
- lettura del README;
- rilevazione di cartelle `as-common-*`, `SKILL.md`, validator e test.

## 5. Cosa e' stato ispezionato

Path candidato:

```text
C:\Users\alberto.ferrari\.agents\skills
```

Esito read-only:

- path esistente: si;
- branch corrente: `main`;
- git status short: clean;
- remote: `https://github.com/AlbertoFerrari71/Codex_Skills.git`;
- ultimi commit leggibili, con HEAD `36b065d 150) Add installed skills sync checker`;
- cartelle `as-common-*` presenti;
- file `SKILL.md` presenti nelle skill;
- `README.md`, `SKILLS_INDEX.md`, `SKILL_SCORE.md` e `validators/` presenti;
- test/validator presenti sotto `validators/`.

## 6. Cosa non e' stato modificato

Non e' stato modificato nulla fuori da `AI_Software_Factory`.

In particolare:

- nessun file sotto `C:\Users\alberto.ferrari\.agents\skills` e' stato scritto;
- nessuna skill installata e' stata modificata;
- nessuna azione Git operativa e' stata eseguita sulla repo esterna;
- nessun remote e' stato letto tramite fetch/pull;
- nessuna pubblicazione reale e' stata eseguita.

## 7. Readiness assessment

Readiness sintetica: `GO_FOR_READ_ONLY_DRY_RUN`.

Motivazione:

- repo accessibile localmente;
- branch e status leggibili;
- working tree esterno pulito;
- remote coerente con `AlbertoFerrari71/Codex_Skills`;
- struttura skill e validator presenti;
- README contiene workflow locale di verifica;
- non sono richieste credenziali, rete o scritture.

Questa readiness non autorizza modifiche. Autorizza solo un futuro step
human-gated se Alberto decide di passare da dry-run a proposta di write
controllata.

## 8. Risk assessment

Rischio del dry-run 0860: `L1`.

Rischio di un futuro write pilot 0870: `L1/L2`, da rivalutare in base al file
specifico e alla modifica proposta.

Fattori che aumentano il rischio:

- modifica a skill installate attive;
- aggiornamento di validator o release workflow;
- alterazione di cataloghi generati;
- qualsiasi azione Git o sync esterna;
- ambiguita' su quali skill siano in uso da Codex.

## 9. Dry-run workflow proposto

Workflow proposto per un futuro 0870, senza eseguirlo ora:

1. ripetere verifica read-only path/branch/status/remote;
2. scegliere una modifica minima e reversibile;
3. produrre changed-files preview concreta;
4. classificare rischio;
5. preparare proposta locale senza write automatico;
6. attendere human approval gate;
7. solo dopo approvazione esplicita, consentire eventuale write controllato;
8. non fare commit, push, PR, merge, deploy o tag da Codex.

## 10. Changed-files preview ipotetica

La preview resta candidate-only. Nessun file esterno e' stato modificato.

Possibili file futuri da valutare in 0870:

- `README.md`;
- `SKILLS_INDEX.md`;
- `SKILL_SCORE.md`;
- `docs/release-workflow/...`;
- `validators/check_agent_skills.py`;
- `validators/test_*.py`;
- `as-common-pwsh-command-pack/SKILL.md`;
- singoli `as-common-*/SKILL.md`.

La scelta deve essere ridotta a uno scope minimo prima del gate umano.

## 11. Human approval gate

Decisione proposta per 0860: `GO_FOR_READ_ONLY_DRY_RUN_COMPLETED`.

Gate richiesto per 0870:

```text
HUMAN APPROVAL REQUIRED BEFORE ANY EXTERNAL WRITE
```

Il gate umano deve confermare:

- file esterno candidato;
- motivo della modifica;
- rischio L1/L2;
- rollback manuale;
- divieto di commit/push/PR/merge/deploy da Codex;
- verifiche locali da eseguire nella repo esterna, se autorizzate.

## 12. Evidence attesa

Evidence prodotta nello step 0860:

- `docs/motor/0860_CODEX_SKILLS_READINESS_REPORT.md`;
- `docs/motor/0860_CODEX_SKILLS_CHANGED_FILES_PREVIEW.md`;
- `docs/motor/0860_CODEX_SKILLS_HUMAN_APPROVAL_GATE.md`;
- `examples/publish_runner/0860_codex_skills_external_dry_run_plan.example.json`;
- `examples/publish_runner/0860_codex_skills_dry_run_evidence_manifest.example.json`;
- test automatico dedicato.

## 13. Criteri di successo

Lo step 0860 e' riuscito se:

- 0850 e' presente su `main`;
- la repo esterna non e' stata modificata;
- esistono documento 0860, readiness report e changed-files preview;
- esistono dry-run plan JSON ed evidence manifest;
- safety boundaries e human gate sono espliciti;
- i test automatici passano;
- Workflow Health Check, Verification Gate e diff check passano;
- non sono stati eseguiti commit, push, PR, merge, deploy o tag.

## 14. Criteri di stop

Fermare qualunque step successivo se:

- la repo esterna non e' clean;
- serve un comando non read-only;
- manca il consenso umano;
- la modifica proposta non e' minima;
- il rischio supera L2;
- compare un secret, dato privato o informazione non necessaria;
- una verifica locale fallisce senza diagnosi.

## 15. Prossimo step consigliato

```text
0870) Codex_Skills First Controlled Write Pilot
```

Il prossimo step deve restare piccolo, esplicito e human-gated. Non deve essere
anticipato dentro 0860.

## 16. Fuori scope

Restano fuori scope:

- scrivere nella repo esterna;
- modificare skill installate;
- sincronizzare release;
- rigenerare cataloghi reali;
- eseguire validator in modalita write;
- fare commit, push, PR, merge, deploy o tag;
- toccare `Family_Photo_Organizer` o `Mansionario_Vivo`;
- trasformare questo dry-run in un pilot operativo.
