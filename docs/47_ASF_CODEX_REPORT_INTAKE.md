# ASF Codex Report Intake

## 1. Scopo

`scripts/asf_codex_report_intake.py` legge un report finale Codex salvato in Markdown e produce un intake report locale.

Serve a capire se il report contiene le sezioni minime attese prima di preparare un closure pack.

---

## 2. Input report Codex

Input principale:

```powershell
python scripts/asf_codex_report_intake.py --report-path tmp/asf_codex_reports/step_580_codex_report.md --project-name Family_Photo_Organizer --repo-path "C:\Users\alberto.ferrari\source\repos\Family_Photo_Organizer" --step 580
```

Il report puo' essere copiato o salvato manualmente da Alberto. Lo script non invoca Codex.

---

## 3. Output intake

Output predefinito:

```text
tmp/asf_codex_intake/<project-name>/step_<step>/codex_report_intake.md
```

Il file contiene:

- project-name;
- repo-path;
- step;
- report-path;
- sezioni trovate;
- sezioni mancanti;
- stato Git target;
- working tree CLEAN/DIRTY;
- warning;
- prossime verifiche consigliate.

---

## 4. PASS / WARNING / FAIL

- `PASS`: le sezioni attese sono presenti.
- `WARNING`: alcune sezioni mancano, ma lo step e' identificabile.
- `FAIL`: manca la sezione `STEP ESEGUITO`.

Lo script esce con codice diverso da zero solo per errori forti: report mancante, repo target non valida o step non valido.

---

## 5. Cosa non fa

Lo script non:

- modifica repository target;
- esegue test;
- invoca Codex;
- chiama GitHub API;
- prepara commit automatici;
- apre PR;
- fa merge.

Legge solo file e stato Git locale con comandi read-only.

---

## 6. Non equivale ad approval

L'intake non approva lo step. Segnala solo se il report Codex ha struttura sufficiente per continuare con review umana.

Alberto/ChatGPT devono ancora verificare diff, scope, test, vincoli, rischi e gate umani.
