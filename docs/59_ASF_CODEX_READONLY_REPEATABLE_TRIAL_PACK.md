# ASF Codex Read-Only Repeatable Trial Pack

## 1. Scopo

Questo documento definisce il Repeatable Trial Pack dello STEP 450 per le invocazioni Codex read-only.

Lo STEP 440 ha dimostrato che `execute-readonly` puo' essere tentato su una repo temporanea pulita, con exit code `0` e target rimasto `CLEAN`. Il risultato finale e' rimasto `WARNING_REVIEW_REQUIRED` per stderr non vuoto e output incompleto.

Lo STEP 450 rende quel trial:

- ripetibile;
- diagnostico;
- confrontabile tra run;
- robusto quando Codex non e' disponibile;
- ancora completamente read-only.

Il pack non autorizza workspace-write.

Formula operativa: workspace-write non autorizzato.

---

## 2. Script principali

Script repeatable trial:

```powershell
python scripts/asf_codex_readonly_repeatable_trial.py --mode prepare-only --trial-name step_450_baseline --step 450
```

Script trial comparison:

```powershell
python scripts/asf_codex_readonly_trial_compare.py --reports tmp/asf_codex_readonly_repeatable_trials/trial1/reports/repeatable_trial_report.md tmp/asf_codex_readonly_repeatable_trials/trial2/reports/repeatable_trial_report.md
```

Entrambi usano solo Python standard library.

---

## 3. Prepare-only

`prepare-only` e' la modalita' default.

In questa modalita' lo script:

- crea la struttura del trial sotto `tmp/asf_codex_readonly_repeatable_trials/<trial-name>/`;
- crea una repo Git sintetica in `target_repo`;
- genera `inputs/handoff.md`;
- genera evidenze sintetiche per il Human Approval Gate;
- chiama `scripts/asf_human_approval_gate.py`;
- chiama `scripts/asf_codex_readonly_invoke.py --mode preview`;
- genera `reports/repeatable_trial_report.md`;
- classifica il risultato come `PREPARED_ONLY`.

Codex non viene eseguito.

---

## 4. Run-readonly-if-safe

`run-readonly-if-safe` e' la modalita' controllata per tentare la sola invocazione read-only.

Richiede:

- conferma esplicita `YES_I_APPROVE_READONLY_CODEX_EXECUTION`;
- approval gate GO;
- target CLEAN;
- sandbox read-only;
- nessun workspace-write;
- nessun danger-full-access;
- nessuna modifica a repository target esterni.

Esempio:

```powershell
python scripts/asf_codex_readonly_repeatable_trial.py --mode run-readonly-if-safe --trial-name step_450_baseline --step 450 --confirm-readonly-execution YES_I_APPROVE_READONLY_CODEX_EXECUTION
```

Se le condizioni non sono soddisfatte, lo script blocca il trial con classificazione esplicita, ad esempio `BLOCKED_BY_APPROVAL` o `BLOCKED_BY_DIRTY_TARGET`.

---

## 5. Repo sintetica tmp

La repo target e' sempre sintetica e sotto:

```text
tmp/asf_codex_readonly_repeatable_trials/<trial-name>/target_repo
```

Contiene solo:

- `README.md`;
- `docs/NOTES.md`;
- `src/demo.txt`.

E' ammesso creare un commit iniziale solo dentro questa repo temporanea per ottenere una working tree Git `CLEAN`.

Non vengono modificati repository target esterni.

---

## 6. Output

Ogni trial crea:

```text
tmp/asf_codex_readonly_repeatable_trials/<trial-name>/
  target_repo/
  inputs/
  approval/
  invocation/
  capture/
  safety/
  reports/
```

Il report principale e':

```text
reports/repeatable_trial_report.md
```

Contiene:

- trial-name;
- step;
- mode;
- target repo path;
- approval status;
- invocation status;
- capture status;
- safety gate status;
- Codex availability;
- exit code;
- stdout/stderr paths;
- working tree finale target;
- classificazione finale;
- prossime azioni.

---

## 7. Classificazioni

Classificazioni finali:

- `PREPARED_ONLY`: trial preparato, Codex non eseguito.
- `READONLY_EXECUTED_CLEAN`: esecuzione read-only conclusa con target CLEAN e senza warning rilevanti.
- `READONLY_EXECUTED_WARNING`: esecuzione read-only con target CLEAN ma stderr, output incompleto o safety gate warning.
- `CODEX_NOT_AVAILABLE`: Codex non disponibile localmente; il risultato e' diagnostico e non modifica il target.
- `BLOCKED_BY_APPROVAL`: approval gate diverso da GO.
- `BLOCKED_BY_DIRTY_TARGET`: target non CLEAN prima dell'esecuzione.
- `FAILED`: exit code non zero, target dirty dopo il trial o errore non controllato.

`CODEX_NOT_AVAILABLE` non e' automaticamente fallimento dello step se il report viene prodotto e il target resta CLEAN.

---

## 8. Codex non disponibile

Se `--codex-command` non e' disponibile:

- Codex non viene eseguito;
- il report finale usa `CODEX_NOT_AVAILABLE`;
- result capture e safety gate possono registrare warning diagnostici;
- il target deve restare CLEAN;
- il prossimo passo e' ripetere il trial quando la CLI e' disponibile.

Questo permette di distinguere un limite ambientale da una regressione del target.

---

## 9. Output incompleto e stderr

Lo STEP 440 ha mostrato che exit code `0` e target `CLEAN` non bastano.

Il Repeatable Trial Pack mantiene separati:

- esito meccanico dell'invocazione;
- result capture;
- safety gate;
- classificazione finale del repeatable trial.

Se stderr e' non vuoto o l'output e' incompleto, la classificazione resta `READONLY_EXECUTED_WARNING` o `CODEX_NOT_AVAILABLE`, non `READONLY_EXECUTED_CLEAN`.

---

## 10. Cosa non autorizza

Questo pack non autorizza:

- workspace-write;
- danger-full-access;
- modifiche a repository target esterni;
- commit, push, PR o merge automatici;
- modifiche GitHub;
- modifiche CI;
- modifiche dipendenze;
- modifiche a secret o `.env`;
- modifiche a `src/**` del repository ASF;
- modifiche a `policies/**`.

Un trial read-only riuscito non e' autorizzazione automatica a workspace-write.

---

## 11. Relazione con futuro workspace-write

Il risultato migliore possibile dello STEP 450 permette solo una diagnosi migliore della pipeline read-only.

Qualunque passaggio futuro verso workspace-write richiede uno step separato, nuovo gate umano, branch dedicato, scope esplicito, test e rollback.

---

## 12. Trial comparison

Per confrontare due o piu' run usare:

```powershell
python scripts/asf_codex_readonly_trial_compare.py --reports <report1> <report2> --output-dir tmp/asf_codex_readonly_repeatable_trials/comparison
```

Il confronto evidenzia:

- differenze tra trial;
- trial riusciti;
- trial warning;
- trial bloccati;
- ricorrenza di stderr/output incompleto;
- raccomandazione prudente.

Il compare non esegue Codex, non modifica repo target e non usa Git/GitHub.

---

## 13. Prossimo step

Prossimo step consigliato:

```text
460) ASF Codex Read-Only Invocation Diagnostics Hardening
```

Motivo: prima di progettare workspace-write o adapter piu' ampi, serve consolidare la diagnostica su stderr, output incompleto e disponibilita' ambientale della CLI.
