# ASF Codex Invocation Result Capture

## 1. Scopo

`scripts/asf_codex_result_capture.py` normalizza i risultati di una invocazione Codex read-only.

Lo script non invoca Codex. Legge una directory di invocation, fotografa lo stato Git target in read-only e produce un report `codex_result_capture.md`.

---

## 2. Input

Esempio:

```powershell
python scripts/asf_codex_result_capture.py --project-name Family_Photo_Organizer --repo-path "C:\Users\alberto.ferrari\source\repos\Family_Photo_Organizer" --step 590 --invocation-dir tmp/asf_codex_readonly_invocation/Family_Photo_Organizer/step_590 --output-dir tmp/asf_codex_result_capture
```

Argomenti:

- `--project-name`;
- `--repo-path`;
- `--step`;
- `--invocation-dir`;
- `--output-dir`, default `tmp/asf_codex_result_capture`.

---

## 3. File letti

Lo script cerca:

- `stdout.txt`;
- `stderr.txt`;
- `exit_code.txt`;
- `codex_readonly_invocation_result.md`.

Se trova solo output preview, produce una classificazione `WARNING` invece di fingere che Codex sia stato eseguito.

---

## 4. Output

Output predefinito:

```text
tmp/asf_codex_result_capture/<project-name>/step_<step>/codex_result_capture.md
```

Il report contiene:

- project-name;
- repo-path;
- step;
- invocation-dir;
- output presenti e mancanti;
- exit code;
- sintesi stdout/stderr;
- stato Git target;
- classificazione;
- prossime azioni consigliate.

---

## 5. Classificazioni

`PASS`:

- exit code `0`;
- output richiesti presenti;
- working tree target `CLEAN`.

`WARNING`:

- output incompleti;
- solo preview presente;
- nessun fail signal rilevato.

`FAIL`:

- exit code non zero;
- working tree target `DIRTY` dopo una esecuzione read-only.

---

## 6. Limiti

Lo script non:

- invoca Codex;
- modifica il repository target;
- crea branch;
- fa commit, push, PR o merge;
- chiama GitHub API.

Il capture non e' approval. Serve come input per il Safety Gate read-only.

---

## 7. Relazione con il first manual trial

Il trial manuale in `docs/55_ASF_CODEX_READONLY_FIRST_MANUAL_TRIAL.md` usa questo capture anche con output simulati sotto `tmp/` quando `execute-readonly` non e' sicuro o non e' consentito.

Il risultato del trial e' registrato in `docs/56_ASF_CODEX_READONLY_FIRST_TRIAL_RESULTS.md`. Un capture simulato puo' validare il flusso, ma non sostituisce una futura invocation read-only reale su target pulito e gate `GO`.
