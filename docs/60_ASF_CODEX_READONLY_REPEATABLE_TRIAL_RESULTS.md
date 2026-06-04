# ASF Codex Read-Only Repeatable Trial Results

## 1. Data e step

- Data: 2026-06-04
- Step: 450) ASF Codex Read-Only Invocation Repeatable Trial Pack
- Branch ASF: `step-450-asf-codex-readonly-invocation-repeatable-trial-pack`

---

## 2. Prerequisito

Prima delle modifiche e' stato verificato `main` con:

```powershell
git switch main
git pull origin main
git --no-pager log --oneline --max-count=15
```

Il log conteneva:

```text
Merge pull request #35 from AlbertoFerrari71/step-440-asf-codex-readonly-invocation-clean-target-trial
440) add ASF codex readonly clean target trial
```

Il prerequisito STEP 440 era quindi soddisfatto.

---

## 3. Trial eseguiti

Trial prepare-only:

```powershell
python scripts/asf_codex_readonly_repeatable_trial.py --mode prepare-only --trial-name step_450_prepare_only --step 450
```

Classificazione attesa e verificata dal pack:

```text
PREPARED_ONLY
```

Trial Codex non disponibile:

```powershell
python scripts/asf_codex_readonly_repeatable_trial.py --mode run-readonly-if-safe --trial-name step_450_missing_codex --step 450 --codex-command codex-command-that-does-not-exist --confirm-readonly-execution YES_I_APPROVE_READONLY_CODEX_EXECUTION
```

Classificazione attesa e verificata dal pack:

```text
CODEX_NOT_AVAILABLE
```

---

## 4. Execute-readonly

Stato:

```text
Non tentato con Codex reale nello STEP 450.
```

Motivo:

- il trial obbligatorio di robustezza usa un comando Codex finto inesistente;
- lo scopo e' verificare che il pack documenti correttamente `CODEX_NOT_AVAILABLE`;
- il task non richiede un run Codex reale;
- lo STEP 440 aveva gia' tentato `execute-readonly` reale e aveva prodotto `WARNING_REVIEW_REQUIRED`.

Lo script resta capace di tentare `execute-readonly` solo con:

- conferma esplicita;
- approval gate GO;
- target CLEAN;
- sandbox read-only;
- Codex disponibile.

---

## 5. Output

Output principali:

```text
tmp/asf_codex_readonly_repeatable_trials/step_450_prepare_only/reports/repeatable_trial_report.md
tmp/asf_codex_readonly_repeatable_trials/step_450_missing_codex/reports/repeatable_trial_report.md
```

Nel caso `CODEX_NOT_AVAILABLE`, lo script produce comunque:

- preview;
- result capture diagnostico;
- safety gate diagnostico;
- report finale;
- target CLEAN.

---

## 6. Codex non disponibile

Il comando finto:

```text
codex-command-that-does-not-exist
```

ha prodotto una classificazione controllata:

```text
CODEX_NOT_AVAILABLE
```

Questo risultato e' accettabile per lo STEP 450 perche':

- Codex non viene eseguito;
- il target sintetico resta CLEAN;
- il report documenta il limite ambientale;
- non viene trasformato automaticamente in autorizzazione a workspace-write.

---

## 7. Stderr e output incompleto

Lo STEP 450 mantiene la diagnosi introdotta dallo STEP 440:

- stderr non vuoto richiede review;
- output incompleto richiede review;
- exit code `0` non basta da solo;
- target CLEAN non basta da solo;
- il safety gate resta separato dal result capture.

Nel trial con Codex non disponibile, stderr/output sono diagnostici e non rappresentano una modifica target.

---

## 8. Target CLEAN

Ogni trial usa una repo sintetica sotto:

```text
tmp/asf_codex_readonly_repeatable_trials/<trial-name>/target_repo
```

La working tree finale del target deve essere:

```text
CLEAN
```

Se il target diventa DIRTY, la classificazione finale diventa `FAILED` o `BLOCKED_BY_DIRTY_TARGET` a seconda del momento.

---

## 9. Safety gate

Il safety gate resta conservativo:

- `GO_TO_WORKSPACE_WRITE_DESIGN` non autorizza workspace-write;
- `WARNING_REVIEW_REQUIRED` richiede review;
- `HOLD` blocca per evidenze insufficienti;
- `NO_GO` blocca per failure o segnali vietati.

Nel trial `CODEX_NOT_AVAILABLE`, il safety gate puo' produrre warning diagnostico. La classificazione finale del repeatable trial resta `CODEX_NOT_AVAILABLE`.

---

## 10. Trial comparison

Il confronto tra run usa:

```powershell
python scripts/asf_codex_readonly_trial_compare.py --reports tmp/asf_codex_readonly_repeatable_trials/step_450_prepare_only/reports/repeatable_trial_report.md tmp/asf_codex_readonly_repeatable_trials/step_450_missing_codex/reports/repeatable_trial_report.md --output-dir tmp/asf_codex_readonly_repeatable_trials/comparison
```

Output:

```text
tmp/asf_codex_readonly_repeatable_trials/comparison/trial_comparison_report.md
```

Il compare non esegue Codex, non modifica repo target e non usa Git/GitHub.

---

## 11. Conclusione

Lo STEP 450 completa il Repeatable Trial Pack:

- prepara trial ripetibili in `prepare-only`;
- gestisce `run-readonly-if-safe` con conferma esplicita;
- usa repo sintetiche sotto `tmp/`;
- mantiene approval gate GO e target CLEAN come prerequisiti;
- documenta Codex non disponibile senza considerarlo automaticamente fallimento;
- mantiene stderr e output incompleto come warning/review;
- non autorizza workspace-write.

workspace-write non autorizzato.

---

## 12. Prossimo step consigliato

```text
460) ASF Codex Read-Only Invocation Diagnostics Hardening
```

Motivo: consolidare diagnostica, confronto run e classificazione di stderr/output incompleto prima di qualunque step futuro piu' ampio.

