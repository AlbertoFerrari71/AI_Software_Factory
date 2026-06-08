# STEP 0830 - MVP Real Step Pilot 4 - Slightly More Operational

## 1. Scopo

Lo STEP 0830 esegue un pilot reale piccolo del Motore ASF dopo gli hardening
0800-0820.

Lo scopo e' validare che il flusso aggiornato sia piu' operativo e recuperabile
senza introdurre nuova automazione di pubblicazione. Codex prepara documenti,
manifest di esempio, test ed evidence locali; non esegue Phase B, Phase C,
commit, push, PR, merge o deploy.

## 2. Prerequisiti

Prerequisiti richiesti su `main`:

- 0800 - PowerShell Native Command Guardrail Hardening;
- 0805 - PowerShell Publish Skill Sync With Proven ASF Runner Flow;
- 0810 - Publish Runner Scope Discovery, Recovery UX and No-False-Completed
  Guard;
- 0820 - Bridge Output Retry, Fallback and LAST Validation.

Prima del pilot bisogna verificare branch, log e working tree:

```powershell
git branch --show-current
git --no-pager log --oneline --max-count=20
git --no-pager status --short
```

Se lo STEP 0820 non compare su `main`, il pilot deve fermarsi con stato
`BLOCCATO`.

## 3. Cosa viene validato

Il pilot valida o documenta:

- `PrepareConfig` e scope discovery;
- review umana dello scope prima di Phase B;
- interpretazione di suggested config e recovery report;
- decisione manuale sui file fuori scope;
- passaggio da `PrepareConfig` a Phase B solo con config revisionata;
- recupero PR tramite numero PR non vuoto e numerico;
- passaggio a Phase C solo con `PrNumber` valido e `-ApproveMerge`;
- Bridge/LAST validation dopo output primari o fallback;
- warning LF/CRLF come warning non bloccanti quando i gate passano;
- DOCX/output accessori come best-effort;
- no-false-`COMPLETATO`.

## 4. Flusso operativo consigliato

### 4.1 PrepareConfig / scope discovery

Usare `PrepareConfig` solo per generare una bozza scope:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\asf_publish_step.ps1 `
  -Phase PrepareConfig `
  -StepNumber 0830 `
  -StepName "MVP_Real_Step_Pilot_4_Slightly_More_Operational" `
  -BranchName "step-0830-mvp-real-step-pilot-4-slightly-more-operational" `
  -CommitMessage "0830 add MVP real step pilot 4" `
  -PrTitle "0830 add MVP real step pilot 4" `
  -NextStep "0840) Runner Hook Evidence Manifest Post-Publish Pack" `
  -BridgeRoot "tmp/0830_mvp_real_step_pilot_4_prepare_config_bridge"
```

Questa fase non pubblica. Produce draft config e review report da leggere prima
di qualsiasi Phase B.

### 4.2 Review umana dello scope

La review umana dello scope deve confrontare:

- `expected_files`;
- `changed_files`;
- diff reale;
- file intenzionali del pilot;
- file fuori scope o generati accidentalmente.

Un file va accettato nello scope solo se e' coerente con il pilot e necessario
alla modifica. Un file nuovo sotto `tmp/` resta evidence locale ignorata e non
deve diventare automaticamente versionato.

### 4.3 Phase B

Phase B e' consentita solo dopo config JSON revisionata, branch corretto, check
locali passati e consenso esplicito con `-ApprovePublish`.

Codex non esegue Phase B nello STEP 0830.

### 4.4 Recupero PR validato

Dopo una Phase B reale autorizzata, il numero PR deve essere recuperato e
validato come valore non vuoto e numerico. Se manca, il flusso resta bloccato e
non passa a Phase C.

### 4.5 Phase C

Phase C richiede:

- config revisionata;
- `PrNumber` valido;
- consenso esplicito `-ApproveMerge`;
- check PR e check finali passati.

Codex non esegue Phase C nello STEP 0830.

### 4.6 Bridge/LAST validation

Dopo STEP 0820, il runner possiede i propri output Bridge standard. Se un file
primario e' bloccato, il runner usa retry e poi fallback timestampato. La
Bridge/LAST validation deve confermare che il compatto Markdown esista nel path
primario o fallback e che i `LAST-*` siano stati aggiornati oppure segnalati con
warning chiaro.

Wrapper esterni non devono usare `Start-Transcript` sullo stesso
`Output_Completo` del runner.

## 5. Gate bloccanti, warning non bloccanti e output accessori

Gate bloccanti:

- STEP 0820 assente su `main`;
- branch errato;
- working tree sporca non compresa;
- `expected_files` vuoto o non coerente;
- out-of-scope non revisionato;
- Phase B senza `-ApprovePublish`;
- PR number mancante o non numerico;
- Phase C senza `-ApproveMerge`;
- test, Workflow Health Check, Verification Gate o `git diff --check` falliti;
- compatto Markdown mancante sia nel path primario sia nel fallback.

Warning non bloccanti:

- warning LF/CRLF quando `git --no-pager diff --check`, test, health check e
  verify gate passano;
- output Bridge primario bloccato dopo gate passati, se fallback e Markdown
  sono validi;
- `LAST-*` primario bloccato ma fallback o warning esplicito presenti;
- DOCX/output accessori falliti dopo output TXT/Markdown validi.

Output accessori:

- DOCX;
- log wrapper separati;
- file di fallback timestampati;
- evidence locale sotto `tmp/`.

Gli output accessori non devono ribaltare un publish gia' verificato dai gate
veri.

## 6. Mini-checklist operativa

- Verificare `main`, log e working tree.
- Confermare 0820 su `main`.
- Preparare o leggere il manifest pilot 0830.
- Eseguire `PrepareConfig` solo se ci sono changed files intenzionali.
- Leggere draft config e review report.
- Accettare nello scope solo file attesi.
- Non eseguire Phase B/C da Codex.
- Controllare Bridge/LAST validation e fallback.
- Eseguire `python -m pytest`.
- Eseguire `python scripts/check_workflow_health.py`.
- Eseguire `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1`.
- Eseguire `git --no-pager diff --check`.
- Lasciare modifiche locali pronte per review umana.

## 7. Esempio di decisione su file fuori scope

Scenario: `PrepareConfig` o Phase A segnala anche
`docs/motor/9999_TEMP_NOTE.md`.

Decisione consigliata:

- se il file e' un appunto temporaneo non richiesto, non aggiungerlo allo scope
  e rimuoverlo solo se e' stato creato dal pilot e la rimozione e' esplicitamente
  parte della pulizia locale;
- se il file documenta davvero il pilot, aggiornare il manifest e la config solo
  dopo review umana;
- se l'origine non e' chiara, fermarsi e chiedere decisione prima di Phase B.

La suggested config e' una proposta di correzione, non un'approvazione.

## 8. Esempio di fallback Bridge

Scenario: il compatto primario e' bloccato da sync o preview.

Esito atteso dopo 0820:

```text
retry -> fallback timestampato -> warning non bloccante
```

Il report deve indicare il path fallback. Se il compatto Markdown manca sia nel
path primario sia nel fallback, lo stato resta `BLOCCATO`.

## 9. Rischi residui

- Il pilot non prova una pubblicazione reale fino al merge.
- La validazione PR completa resta demandata a una Phase B/C futura e
  human-gated.
- I file Bridge reali possono essere bloccati da Dropbox, editor, preview o
  antivirus.
- Warning LF/CRLF vanno sempre confermati con `git --no-pager diff --check`.
- DOCX resta best-effort e non deve diventare dipendenza del flusso.

## 10. Criteri di successo

Il pilot 0830 e' riuscito se:

- lo STEP 0820 e' su `main`;
- il documento operativo 0830 esiste;
- il manifest 0830 e' JSON valido e non operativo;
- un test automatico dedicato passa;
- `PrepareConfig` o scope discovery sono validati o documentati;
- Bridge/LAST retry, fallback e validation sono validati o documentati;
- test, Workflow Health Check, Verification Gate e diff check passano;
- nessuna pubblicazione Git viene eseguita da Codex.

## 11. Fuori scope

Restano fuori scope:

- modifiche al runner di publish;
- nuovi guardrail runtime;
- commit, push, apertura PR, merge, deploy o tag;
- automazione di approvazione;
- DOCX obbligatorio;
- normalizzazione LF/CRLF massiva;
- modifica di repository esterne;
- invocazione Codex automatica su target.

## 12. Decisione finale del pilot

```text
PILOT STATUS: GO WITH WARNINGS
```

Motivo: il pilot e' piu' operativo dei precedenti perche' usa un manifest
versionato, un test dedicato e una prova `PrepareConfig` non pubblicante, ma la
pubblicazione reale resta volutamente fuori scope e human-gated.

## 13. Prossimo step consigliato

```text
0840) Runner Hook Evidence Manifest Post-Publish Pack
```

Motivo: dopo il pilot 0830, il valore successivo e' consolidare il pack
post-publish che collega runner, state machine, manifest ed evidence dopo una
pubblicazione reale human-gated.
