# Workflow Status Dashboard

## 1. Scopo

La Workflow Status Dashboard e' una vista locale e read-only dello stato operativo del workflow AI Software Factory.

Serve a vedere rapidamente branch corrente, working tree, ultimi commit, documenti centrali, script principali e prossimi controlli locali consigliati.

---

## 2. Perche' e' locale e read-only

La dashboard e' local-first: legge lo stato disponibile nella working copy locale.

E' read-only: non modifica file, Git, GitHub, hook, `core.hooksPath`, CI, PATH, profili PowerShell, dipendenze o stato remoto.

Non usa GitHub API, non richiede connessione internet e non esegue azioni di commit, push, PR o merge.

---

## 3. Cosa mostra

Lo script `scripts/show_workflow_status.py` mostra:

- repository: AI Software Factory;
- branch corrente;
- working tree `CLEAN` o `DIRTY`;
- ultimi commit locali;
- presenza dei documenti centrali:
  - `docs/34_PROJECT_WORKFLOW_INDEX.md`;
  - `docs/35_WORKFLOW_HEALTH_CHECK.md`;
  - `docs/36_WORKFLOW_QUICK_REFERENCE.md`;
  - `docs/37_STEP_CLOSURE_REPORT.md`;
  - `docs/38_WORKFLOW_COMMAND_COOKBOOK.md`;
  - `docs/39_WORKFLOW_STATUS_DASHBOARD.md`;
  - `docs/40_RELEASE_READINESS.md`;
  - `docs/41_EXISTING_PROJECT_PILOT_ONBOARDING.md`;
  - `docs/42_ASF_NEXT_STEP_RUNNER.md`;
  - `docs/43_ASF_RUNNER_PROJECT_PROFILES.md`;
  - `docs/44_ASF_RUNNER_CODEX_HANDOFF_IMPROVEMENTS.md`;
  - `docs/45_ASF_RUNNER_VERIFICATION_PACK.md`;
  - `docs/46_ASF_RUNNER_VERIFICATION_PACK_HARDENING.md`;
  - `docs/47_ASF_CODEX_REPORT_INTAKE.md`;
  - `docs/48_ASF_HUMAN_GATED_CLOSURE_PACK.md`;
  - `docs/49_ASF_HUMAN_APPROVAL_GATE.md`;
  - `docs/50_ASF_CODEX_INVOCATION_DESIGN.md`;
  - `docs/51_ASF_CODEX_INVOCATION_DRY_RUN_PACK.md`;
  - `docs/52_ASF_CODEX_READONLY_INVOCATION_PROTOTYPE.md`;
  - `docs/53_ASF_CODEX_INVOCATION_RESULT_CAPTURE.md`;
  - `docs/54_ASF_CODEX_READONLY_SAFETY_GATE.md`;
  - `docs/55_ASF_CODEX_READONLY_FIRST_MANUAL_TRIAL.md`;
  - `docs/56_ASF_CODEX_READONLY_FIRST_TRIAL_RESULTS.md`;
- presenza degli script principali:
  - `scripts/asf_next_step.py`;
  - `scripts/asf_codex_report_intake.py`;
  - `scripts/asf_generate_closure_pack.py`;
  - `scripts/asf_human_approval_gate.py`;
  - `scripts/asf_codex_invocation_dry_run.py`;
  - `scripts/asf_codex_readonly_invoke.py`;
  - `scripts/asf_codex_result_capture.py`;
  - `scripts/asf_codex_readonly_safety_gate.py`;
  - `scripts/check_workflow_health.py`;
  - `scripts/show_workflow_status.py`;
  - `scripts/generate_task_packet.py`;
  - `scripts/validate_task_packet.py`;
  - `scripts/verify.ps1`;
  - `scripts/git/check_soft_guardrails.ps1`;
- Next suggested local checks.

---

## 4. Cosa non fa

La dashboard non:

- chiama GitHub API;
- controlla CI remota;
- crea commit;
- esegue push;
- crea PR;
- fa merge;
- installa hook;
- modifica `core.hooksPath`;
- esegue validazione completa;
- sostituisce test, Verification Gate o review umana.

---

## 5. Differenze dagli altri strumenti

### Workflow Health Check

Il Workflow Health Check verifica che documenti, riferimenti e script centrali siano coerenti.

La dashboard mostra uno snapshot operativo rapido: branch, working tree, commit recenti e presenza dei file chiave.

### Verification Gate

Il Verification Gate esegue i controlli di readiness, inclusi test, diff whitespace e stato Git.

La dashboard non sostituisce il Verification Gate e non decide se una modifica e' pronta per PR o merge.

### Workflow Quick Reference

La Workflow Quick Reference e' una scheda breve di comandi.

La dashboard mostra lo stato locale corrente e suggerisce i prossimi controlli.

### Workflow Command Cookbook

Il Workflow Command Cookbook contiene ricette operative e troubleshooting.

La dashboard non spiega scenari complessi: indica dove si e' e quali controlli locali lanciare dopo.

### Step Closure Report

Lo Step Closure Report formalizza la chiusura reale di uno step su `main`.

La dashboard puo' aiutare a raccogliere evidenze, ma non sostituisce il report di chiusura.

### ASF Next Step Runner

ASF Next Step Runner prepara task packet, handoff Codex, runner report e Verification Pack per lo step successivo.

La dashboard mostra se documenti, config e script del runner sono presenti, inclusi report intake, closure pack, Human Approval Gate, dry-run invocation pack, read-only invocation prototype, result capture, safety gate e first manual trial, ma non esegue il runner e non invoca Codex.

---

## 6. Uso

Eseguire dalla root del repository:

```powershell
python scripts/show_workflow_status.py
```

---

## 7. Come interpretare l'output

### Branch corrente

Indica dove si sta lavorando. Per uno step operativo deve essere il branch dedicato, salvo verifiche finali su `main`.

### Working tree

- `CLEAN`: `git status --short` non restituisce righe.
- `DIRTY`: esistono modifiche locali o file non tracciati.

`DIRTY` non e' automaticamente un errore durante uno step, ma deve essere coerente con il task packet.

### Ultimi commit

Mostrano il contesto locale recente. Prima di uno step nuovo, il log di `main` deve includere lo step prerequisito.

### Documenti e script presenti

`OK` indica che il file esiste. `MISSING` indica un problema critico da risolvere prima di considerare il workflow navigabile.

### Next suggested local checks

La dashboard propone:

```powershell
python scripts/check_workflow_health.py
python -m pytest
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\git\check_soft_guardrails.ps1
```

---

## 8. Limiti attuali

Limiti intenzionali:

- nessuna GitHub API;
- nessun controllo CI remoto;
- nessun merge;
- nessuna validazione completa;
- nessun JSON report;
- nessuna integrazione in CI;
- nessuna modifica a `scripts/verify.ps1`.
- nessuna invocazione di ASF Next Step Runner.
- nessuna validazione semantica dei profili progetto.
- nessuna generazione automatica di closure pack.
- nessuna generazione automatica di Human Approval Gate.
- nessuna generazione automatica di Codex invocation dry-run pack.
- nessuna generazione automatica di Codex read-only invocation prototype.
- nessuna generazione automatica di result capture.
- nessuna generazione automatica di read-only safety gate.
- nessuna esecuzione di `codex exec`.

La dashboard non sostituisce test, Verification Gate, Workflow Health Check, PR checks o Step Closure Report.

---

## 9. Link utili

- `docs/34_PROJECT_WORKFLOW_INDEX.md`
- `docs/35_WORKFLOW_HEALTH_CHECK.md`
- `docs/36_WORKFLOW_QUICK_REFERENCE.md`
- `docs/37_STEP_CLOSURE_REPORT.md`
- `docs/38_WORKFLOW_COMMAND_COOKBOOK.md`
- `docs/42_ASF_NEXT_STEP_RUNNER.md`
- `docs/43_ASF_RUNNER_PROJECT_PROFILES.md`
- `docs/44_ASF_RUNNER_CODEX_HANDOFF_IMPROVEMENTS.md`
- `docs/45_ASF_RUNNER_VERIFICATION_PACK.md`
- `docs/46_ASF_RUNNER_VERIFICATION_PACK_HARDENING.md`
- `docs/47_ASF_CODEX_REPORT_INTAKE.md`
- `docs/48_ASF_HUMAN_GATED_CLOSURE_PACK.md`
- `docs/49_ASF_HUMAN_APPROVAL_GATE.md`
- `docs/50_ASF_CODEX_INVOCATION_DESIGN.md`
- `docs/51_ASF_CODEX_INVOCATION_DRY_RUN_PACK.md`
- `docs/52_ASF_CODEX_READONLY_INVOCATION_PROTOTYPE.md`
- `docs/53_ASF_CODEX_INVOCATION_RESULT_CAPTURE.md`
- `docs/54_ASF_CODEX_READONLY_SAFETY_GATE.md`
- `docs/55_ASF_CODEX_READONLY_FIRST_MANUAL_TRIAL.md`
- `docs/56_ASF_CODEX_READONLY_FIRST_TRIAL_RESULTS.md`
- `docs/40_RELEASE_READINESS.md`
- `docs/41_EXISTING_PROJECT_PILOT_ONBOARDING.md`
- `docs/42_ASF_NEXT_STEP_RUNNER.md`
