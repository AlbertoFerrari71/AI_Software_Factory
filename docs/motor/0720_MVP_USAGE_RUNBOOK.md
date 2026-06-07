# 0720 - MVP Usage Runbook

## 1. Scopo

Questo runbook spiega come usare oggi il Motore ASF MVP in modo locale,
ripetibile, verificabile e human-gated.

Il Motore ASF MVP non e' un autopilota. Coordina componenti che aiutano a:

- preparare uno step Codex;
- registrare stato e decisioni;
- produrre evidence locali;
- normalizzare un manifest di run;
- generare una config per il publish runner;
- pubblicare solo dopo review umana esplicita.

La regola operativa e': prima evidence, poi review, poi Phase B, poi Phase C.

## 2. Prerequisiti

Prima di usare il flusso:

- lavorare su `main` aggiornato o su uno stato concordato;
- verificare che la working tree non contenga file sporchi fuori scope;
- avere Python disponibile come `python`;
- avere PowerShell Core disponibile come `pwsh`;
- non usare GitHub, Dropbox reale o API esterne nei test locali;
- conservare prompt, output Bridge e file versionati separati;
- trattare Git e file versionati come fonte autorevole.

Comandi di controllo iniziale:

```powershell
git --no-pager status --short --branch --untracked-files=all
git --no-pager log --oneline --decorate -n 12
```

## 3. Directory Bridge

Il Bridge e' storage operativo condiviso tra Alberto, ChatGPT, Codex e
PowerShell. Non sostituisce Git e non e' la fonte autorevole dello stato.

Radice operativa tipica:

```text
D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory
```

Directory usate dal Motore MVP:

| Directory | Uso | Artifact tipici |
|---|---|---|
| `codex_command` | Prompt Codex e handoff pulito | `LAST-Prompt_Codex.md` |
| `pwsh_command` | Output del publish runner | `LAST-Comando_Eseguito.ps1`, `LAST-Output_Compatto.md`, `LAST-Output_Completo.txt` |
| `publish_config` | Audit del Publish Config Generator | `LAST-Publish_Config.json`, `LAST-Output_Compatto.md`, `LAST-Output_Completo.txt` |
| `state_machine` | Stato/eventi dello step | `LAST-State.json`, `LAST-Event.json`, `LAST-Output_Compatto.md` |
| `e2e_smoke` | Evidence dello smoke 0700 | `LAST-Evidence_Summary.md`, `LAST-Evidence_Pack.json` |
| `motor_run` | Manifest normalizzato della run | `LAST-Run_Manifest.json`, `LAST-Run_Summary.md`, `LAST-Output_Completo.txt` |

Gli alias `LAST-*` sono comodi per l'operativita'. Per audit robusto, usare
anche gli artifact progressivi prodotti dagli strumenti e i file versionati in
repo.

## 4. Componenti principali

| Componente | Ruolo | Cosa non fa |
|---|---|---|
| `scripts/asf_risk_classifier.py` | Classifica rischio L0-L4 e gate richiesto | Non esegue step, test o publish |
| `scripts/asf_dry_run_loop_runner.py` | Simula il loop ASF da una request locale | Non modifica target repo e non pubblica |
| `scripts/asf_gate_decision_report.py` | Produce Approval Packet umano da risk/evidence | Non approva automaticamente |
| `scripts/asf_verification_profile_selector.py` | Suggerisce profilo di verifica e costi test | Non esegue i check |
| `scripts/asf_step_state_machine.py` | Valida stato/eventi dello step | Non esegue Phase B/C o GitHub |
| `scripts/asf_publish_config_generator.py` | Genera config JSON/Markdown per il runner | Non committa, pusha, crea PR o mergea |
| `scripts/asf_e2e_mvp_smoke.py` | Esegue smoke locale fino a `READY_TO_PUBLISH` | Non pubblica e resta sintetico |
| `scripts/asf_motor_run_manifest.py` | Normalizza evidence in manifest e summary | Non promuove evidence mancanti |
| `scripts/asf_publish_step.ps1` | Pubblica con Phase B e Phase C human-gated | Non parte senza flag di approvazione |

## 5. Flusso operativo consigliato

### 5.1 Preparazione step

1. Creare un prompt Codex pulito e self-contained.
2. Salvare il prompt in `codex_command`, incluso `LAST-Prompt_Codex.md`.
3. Far implementare a Codex senza commit, push, PR, merge o deploy.
4. Far eseguire a Codex test locali coerenti con lo scope.
5. Leggere il report finale Codex e verificare file modificati, test, warning e
   limiti.

Codex lascia la working tree modificata per review e pubblicazione successiva.

### 5.2 Stato macchina

La state machine rende esplicito dove si trova lo step. Il flusso base e':

```text
PLANNED -> PROMPT_PREPARED -> CODEX_RUNNING -> IMPLEMENTED -> LOCAL_VERIFIED -> READY_TO_PUBLISH
```

Eventi principali:

- `prompt_saved`: prompt salvato;
- `codex_started`: Codex avviato;
- `codex_completed`: Codex ha completato il lavoro;
- `local_checks_passed`: verifiche locali passate;
- `publish_config_generated`: config publish generata e coerente.

Esempio Bridge:

```powershell
python scripts/asf_step_state_machine.py --step 0720 --event prompt_saved --write-bridge --bridge-root "D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\state_machine" --markdown
```

Output da leggere:

- `LAST-State.json`: stato corrente;
- `LAST-Event.json`: ultimo evento applicato;
- `LAST-Output_Compatto.md`: riepilogo leggibile.

Se lo stato non e' `READY_TO_PUBLISH`, non procedere con Phase B.

### 5.3 Smoke end-to-end

Usare lo smoke quando serve verificare che il Motore MVP attraversi il percorso
locale positivo o che un caso incoerente fallisca chiuso.

Smoke positivo:

```powershell
python scripts/asf_e2e_mvp_smoke.py --scenario code-unit-to-ready-to-publish --out-dir tmp/e2e_mvp_smoke --json
```

Lo smoke dimostra:

- integrazione tra classifier, dry-run, gate packet, selector, generator e
  state machine;
- produzione di evidence sotto `tmp/e2e_mvp_smoke`;
- stato finale positivo fino a `READY_TO_PUBLISH`;
- scenario negativo fail-closed se richiesto.

Resta simulato:

- contenuto applicativo dello step;
- risultato dei check dello scenario sintetico;
- review umana finale;
- pubblicazione Git/GitHub.

### 5.4 Manifest ed evidence pack

Generare il manifest quando esiste una evidence directory da rendere auditabile
prima della review finale.

```powershell
python scripts/asf_motor_run_manifest.py --evidence-dir tmp/e2e_mvp_smoke --step 0700-smoke --scenario code-unit-to-ready-to-publish --out-dir tmp/motor_run_manifest --json
```

Output locali:

- `tmp/motor_run_manifest/motor_run_manifest.json`;
- `tmp/motor_run_manifest/motor_run_summary.md`.

Decisioni possibili:

- `READY_TO_PUBLISH`: evidence minima coerente, nessun blocker;
- `BLOCKED`: blocker dichiarati;
- `FAIL_CLOSED`: input o scenario indicano fail-closed;
- `INCOMPLETE`: artifact o check richiesti mancanti/non passati;
- `REVIEW_REQUIRED`: input valido ma non conclusivo.

Non usare `READY_TO_PUBLISH` come autorizzazione automatica: resta necessaria
la review umana.

### 5.5 Publish config generator

Usare il generator dopo:

- report Codex completato;
- check locali passati;
- state machine almeno in `LOCAL_VERIFIED`;
- manifest revisionato, se presente.

Esempio coerente con l'integrazione state machine 0690:

```powershell
python scripts/asf_publish_config_generator.py --step 0720 --name MVP_Usage_Runbook --branch step-0720-mvp-usage-runbook --commit-message "0720 add MVP usage runbook" --pr-title "0720 add MVP usage runbook" --pr-body "Implements STEP 0720. Adds the MVP Usage Runbook while publication remains manual and human-gated." --next-step "0730) End-to-End MVP Closure Pack" --repo-path "." --risk-level L0 --verification-phase local --expected-files docs/motor/0720_MVP_USAGE_RUNBOOK.md README.md CHANGELOG.md docs/10_ROADMAP.md docs/11_DECISIONS.md docs/34_PROJECT_WORKFLOW_INDEX.md docs/35_WORKFLOW_HEALTH_CHECK.md docs/motor/0570_MVP_MOTOR_ROADMAP.md docs/motor/0710_MOTOR_RUN_MANIFEST_AND_EVIDENCE_PACK.md scripts/check_workflow_health.py --changed-files docs/motor/0720_MVP_USAGE_RUNBOOK.md README.md CHANGELOG.md docs/10_ROADMAP.md docs/11_DECISIONS.md docs/34_PROJECT_WORKFLOW_INDEX.md docs/35_WORKFLOW_HEALTH_CHECK.md docs/motor/0570_MVP_MOTOR_ROADMAP.md docs/motor/0710_MOTOR_RUN_MANIFEST_AND_EVIDENCE_PACK.md scripts/check_workflow_health.py --intent "document MVP usage runbook" --checks-already-run "python scripts/check_workflow_health.py" "python -m pytest -q" "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify.ps1" --provided-gate local_verification --write-bridge --bridge-root "D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\publish_config" --runner-bridge-root "D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\pwsh_command" --require-state --state-bridge-root "D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\state_machine" --state-event publish_config_generated --update-state --state-expected-current LOCAL_VERIFIED --state-target-after READY_TO_PUBLISH --write-state-bridge --out-dir tmp/publish_config --json
```

Output da leggere:

- `LAST-Publish_Config.json`;
- `LAST-Output_Compatto.md`;
- eventuali riferimenti incrociati a `LAST-State.json`.

Il generator prepara una config. Non approva Phase B o Phase C.

### 5.6 Review umana

Checklist per Alberto prima di pubblicare:

- rischio coerente con scope e file;
- gate richiesto coerente;
- test locali passati;
- manifest `READY_TO_PUBLISH`, se usato;
- state machine in `READY_TO_PUBLISH`;
- config runner riferita allo step corretto;
- branch di pubblicazione corretto;
- expected files coerenti con la diff reale;
- Phase C non alleggerita;
- warning LF/CRLF accettabili solo se `git diff --check`, test e verify passano;
- nessun file fuori scope;
- nessun secret o dato privato negli artifact.

### 5.7 Pubblicazione con runner

Per step ordinari usare flusso ottimizzato B -> C.

Phase B:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\asf_publish_step.ps1 -Config "<path-config>" -Phase B -ApprovePublish
```

Phase B esegue le verifiche locali necessarie, crea branch/commit/push/PR e
richiede sempre `-ApprovePublish`.

Phase C:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\asf_publish_step.ps1 -Config "<path-config>" -Phase C -PrNumber <PR_NUMBER> -ApproveMerge
```

Phase C esegue merge e verifica finale su `main`, richiede sempre
`-ApproveMerge` e un PR corretto.

Non lanciare Phase A separata se si usa Phase B, perche' Phase B contiene gia'
la verifica locale. Phase C resta obbligatoria per chiudere su `main`.

## 6. Come leggere i LAST-*

Regola pratica:

- usare `LAST-*` per riprendere velocemente l'ultimo output operativo;
- verificare sempre che step, branch, timestamp e path siano coerenti;
- se lo step e' diverso, fermarsi;
- se serve audit, preferire file progressivi e Git;
- non considerare `LAST-Publish_Config.json` come approvazione automatica.

Check minimo su un file `LAST-*`:

1. step corretto;
2. scenario corretto;
3. branch corretto;
4. decisione coerente;
5. warning compresi;
6. path config e expected files coerenti con la diff.

## 7. Errori e fail-closed

Se qualcosa fallisce, non dichiarare lo step completato. Fermarsi e diagnosticare.

| Caso | Azione |
|---|---|
| Phase C fallisce | Non scrivere `COMPLETATO`; registrare `phase_c_failed`, leggere output runner e aprire recovery |
| PR non trovata | Verificare branch, numero PR, config e output Phase B; non rilanciare merge alla cieca |
| Config vecchia usata per step nuovo | Rigenerare config con step/branch/files corretti |
| State machine non `READY_TO_PUBLISH` | Tornare agli eventi mancanti o a recovery esplicita |
| Manifest `INCOMPLETE` | Identificare artifact/check mancanti e ripetere evidence prima di review |
| Manifest `FAIL_CLOSED` | Bloccare publish e correggere causa primaria |
| File fuori scope | Fermare pubblicazione e decidere se escludere o creare step separato |
| Workflow health fallisce | Correggere riferimenti docs/script prima di publish |
| `verify.ps1` fallisce | Trattare come gate bloccante |
| Warning LF/CRLF con `diff --check` passato | Segnalare warning, non fallire automaticamente se test e verify passano |
| Step combinato di recovery | Dichiarare recovery, usare state machine con target esplicito e aggiornare docs/report |

## 8. Recovery scenario

Per recovery dopo errore:

1. leggere `LAST-Output_Compatto.md` e `LAST-Output_Completo.txt` del runner;
2. leggere `LAST-State.json`;
3. leggere `motor_run_manifest.json` o `LAST-Run_Manifest.json`, se presente;
4. identificare stato reale: `PUBLISHING`, `PR_CREATED`, `MERGING`,
   `RECOVERY_REQUIRED`, `FAILED` o `BLOCKED`;
5. applicare solo eventi supportati;
6. usare `recovery_completed` solo con target state e prove sufficienti;
7. rigenerare config se step, branch o expected files non coincidono;
8. ripetere Phase B o Phase C solo dopo nuova review umana.

Per step combinati come `0650-0660`, la recovery deve essere esplicita nel
report, nella state machine e nella config. Non usare uno step combinato per
nascondere errori di sequenza.

## 9. Cosa non e' automatico

Restano manuali o human-gated:

- decisione di avviare Codex;
- review del report Codex;
- accettazione dei warning;
- scelta di procedere da `LOCAL_VERIFIED` a `READY_TO_PUBLISH`;
- approvazione Phase B;
- approvazione Phase C;
- merge e chiusura finale dello step;
- gestione recovery.

Restano simulati o sintetici nel MVP:

- contenuto applicativo dello smoke 0700;
- alcuni check dello scenario smoke;
- review indipendente completa;
- integrazione diretta tra runner e state machine durante Phase B/C;
- pilota reale su step applicativo non sintetico.

## 10. Limiti MVP

Il MVP e' usabile per orchestrare un percorso locale controllato, ma non chiuso
come prodotto autonomo.

Limiti principali:

- non esiste ancora orchestratore unico;
- Phase B/C non scrivono eventi state machine in automatico;
- il manifest osserva evidence ma non produce approvazione;
- lo smoke non sostituisce uno step reale;
- `LAST-*` aiuta l'operativita' ma richiede controllo umano su step e branch;
- Dropbox reale non deve diventare dipendenza dei test.

## 11. Prossimo step consigliato

Prossimo step consigliato:

```text
0730) End-to-End MVP Closure Pack
```

Motivo: dopo questo runbook il Motore MVP ha componenti e procedura d'uso.
Prima di aggiungere hook automatici al runner, conviene creare un closure pack
che verifichi end-to-end documenti, evidence, manifest, state machine, config,
runner e criteri di chiusura formale del MVP.

## 12. Aggiornamento STEP 0730

Lo STEP 0730 ha creato il closure pack formale:

```text
docs/motor/0730_END_TO_END_MVP_CLOSURE_PACK.md
```

Il MVP Motore viene chiuso come baseline `GO WITH WARNINGS`: usabile,
human-gated e verificabile, ma ancora con smoke sintetico, hook manuali e pilot
reale non eseguito.

Prossimo step post-MVP consigliato:

```text
0740) MVP Real Step Pilot
```
