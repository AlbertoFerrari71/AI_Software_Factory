# ASF Human Approval Gate

## 1. Scopo

`scripts/asf_human_approval_gate.py` produce un report locale read-only prima di passare dalla fase di intake/verification alla fase di preview o chiusura human-gated.

Il gate non approva automaticamente lo step. Raccoglie evidenze e propone una decisione operativa:

- `GO`;
- `WARNING`;
- `HOLD`;
- `NO-GO`.

La decisione finale resta di Alberto.

---

## 2. Input

Input principali:

```powershell
python scripts/asf_human_approval_gate.py --project-name Family_Photo_Organizer --repo-path "C:\Users\alberto.ferrari\source\repos\Family_Photo_Organizer" --step 590 --branch 590-sandbox-import-static-simulation-prototype --codex-report-intake "tmp/asf_codex_intake/Family_Photo_Organizer/step_590/codex_report_intake.md" --verification-pack "tmp/asf_next_step/Family_Photo_Organizer/step_590/verification_pack.md" --output-dir tmp/asf_approval_gate
```

Argomenti supportati:

- `--project-name`;
- `--repo-path`;
- `--step`;
- `--branch`;
- `--main-branch`, default `main`;
- `--codex-report-intake`, opzionale;
- `--verification-pack`, opzionale;
- `--closure-pack`, opzionale;
- `--output-dir`, default `tmp/asf_approval_gate`;
- `--allow-dirty`, default disattivo;
- `--require-tests`, default disattivo.

`--require-tests` e' disattivo di default per non bloccare gate documentali o diagnostici. Quando e' attivo, i file forniti devono contenere evidenze test o Verification Gate.

---

## 3. Output

Output predefinito:

```text
tmp/asf_approval_gate/<project-name>/step_<step>/human_approval_gate.md
```

Il report contiene:

- project-name;
- repo-path;
- step;
- branch atteso;
- branch corrente;
- working tree `CLEAN` o `DIRTY`;
- decisione;
- motivazione;
- evidenze Git;
- evidenze file;
- prossime azioni consigliate;
- nota che la decisione finale resta di Alberto.

---

## 4. Decisioni

### GO

Usare solo quando:

- il repo e' valido;
- il branch corrente e' quello atteso;
- la working tree e' pulita oppure una dirty tree e' stata accettata in modo esplicito;
- non sono presenti segnali `HOLD` o `NO-GO`;
- i file richiesti sono presenti.

### WARNING

Usare quando esistono attenzioni non bloccanti:

- report intake non fornito;
- verification pack non fornito;
- closure pack non fornito;
- working tree dirty con `--allow-dirty`;
- branch diverso ma spiegabile;
- PR checks non disponibili registrati nei report;
- warning LF/CRLF documentati.

### HOLD

Usare quando serve fermarsi e completare evidenze:

- report intake richiesto ma mancante;
- verification pack richiesto ma mancante;
- closure pack richiesto ma mancante;
- branch ambiguo;
- test richiesti ma non documentati.

### NO-GO

Usare quando compare un blocco forte:

- repo non Git;
- step non valido;
- branch con spazi;
- branch atteso uguale a `main`;
- working tree dirty senza `--allow-dirty`;
- intake/report con segnale `FAIL` o `NO-GO`;
- file sensibili o secret citati come modificati;
- scope vietato rilevato nei report;
- richiesta di lavoro diretto su `main`.

---

## 5. Relazione con Codex Report Intake

Il Codex Report Intake controlla la struttura del report finale Codex e classifica `PASS`, `WARNING` o `FAIL`.

Il Human Approval Gate usa l'intake come evidenza, ma non lo sostituisce. Un intake `PASS` non equivale ad approval finale.

---

## 6. Relazione con Closure Pack

Il Closure Pack prepara comandi e checklist manuali per commit, push, PR e merge presidiati da Alberto.

Il Human Approval Gate puo' leggere il closure pack come evidenza, ma non esegue i comandi contenuti e non autorizza la chiusura automatica.

---

## 7. Cosa non fa

Lo script non:

- modifica repository target;
- esegue test;
- invoca Codex;
- chiama GitHub API;
- crea branch nel repository target;
- fa commit, push, PR o merge;
- modifica CI, hook, `core.hooksPath`, PATH o profili PowerShell.

---

## 8. Responsabilita' Alberto

Alberto legge il report, valuta warnings, hold e no-go, e decide se:

- procedere;
- correggere evidenze mancanti;
- fermare lo step;
- richiedere un nuovo gate.

Il gate e' un supporto decisionale, non una sostituzione del controllo umano.
