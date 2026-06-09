# 0590 - Stable PowerShell Publish Runner

## 1. Scopo

Lo STEP 0590 introduce un runner PowerShell stabile, versionato e testabile per pubblicare gli step ASF senza generare mega-blocchi PowerShell in chat.

Il runner e':

```text
scripts/asf_publish_step.ps1
```

La configurazione di esempio e':

```text
examples/publish_step/0590_publish_config.example.json
```

Questo step implementa il runner e i test, ma non esegue pubblicazione reale. Commit, push, PR, merge e deploy restano vietati durante l'implementazione Codex.

---

## 2. Perche' abbandonare i mega-blocchi

I blocchi PowerShell lunghi copiati in chat sono fragili:

- possono rompersi con here-string aperte;
- soffrono quoting e nesting;
- mischiano generazione file, logica Git, pubblicazione e report;
- diventano difficili da correggere se l'incolla si interrompe;
- rendono il workflow meno verificabile.

La nuova filosofia e': codice operativo versionato nel repository, comando corto in chat, configurazione JSON per lo step.

---

## 3. Comandi corti

FASE A - verifica locale:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\asf_publish_step.ps1 -Config examples\publish_step\0590_publish_config.example.json -Phase A
```

FASE B - pubblicazione branch/commit/push/PR, solo con consenso esplicito:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\asf_publish_step.ps1 -Config path\to\publish.config.json -Phase B -ApprovePublish
```

FASE C - merge e verifica finale, solo con consenso esplicito:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\asf_publish_step.ps1 -Config path\to\publish.config.json -Phase C -PrNumber 52 -ApproveMerge
```

Modalita' piano, senza GitHub o publish:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\asf_publish_step.ps1 -Config examples\publish_step\0590_publish_config.example.json -Phase Plan
```

Modalita' self-test, utile per testare output Bridge e DOCX:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\asf_publish_step.ps1 -SelfTest -BridgeRoot tmp\publish_selftest
```

---

## 4. FASE A

La FASE A verifica lo stato locale:

- legge la configurazione JSON;
- controlla che il repository esista;
- mostra branch corrente;
- mostra `git status --porcelain=v1 --untracked-files=all`;
- verifica che le modifiche siano solo nei file attesi;
- esegue i comandi `phase_a_checks`;
- esegue `git --no-pager diff --check`;
- blocca su file fuori scope o check falliti.
- tratta i soli warning Git LF/CRLF su stderr come warning non bloccanti
  quando il comando Git termina con exit code `0`.

Non fa commit, push, PR, merge o deploy.

---

## 5. FASE B

La FASE B richiede sempre:

```powershell
-ApprovePublish
```

Operazioni previste:

- riesegue la FASE A;
- crea o riusa il branch configurato;
- esegue `git add` solo dei file previsti da `expected_files`;
- esegue `git --no-pager diff --cached --check`;
- crea commit;
- esegue push del branch;
- crea PR oppure riusa una PR esistente;
- salva il numero PR negli output Bridge se disponibile.

Non fa merge.

---

## 6. FASE C

La FASE C richiede sempre:

```powershell
-ApproveMerge
```

Richiede anche `-PrNumber` oppure una PR ricavabile in modo sicuro dal branch configurato.

Operazioni previste:

- `gh pr view`;
- `gh pr checks --watch`;
- merge PR con `--squash` solo se i gate passano;
- checkout `main`;
- `git pull --ff-only origin main`;
- verifiche finali `phase_c_checks`;
- `git --no-pager diff --check`;
- working tree clean;
- log finale con `git --no-pager log --oneline --max-count=N`.

---

## 7. Gestione no checks reported

`gh pr checks` puo' restituire exit code 1 quando GitHub non riporta check.

Il runner:

- salva e ripristina `$PSNativeCommandUseErrorActionPreference`;
- legge `$LASTEXITCODE`;
- registra warning per `no checks reported`;
- prosegue solo se `allow_no_github_checks_reported` e' `true` e il fallback
  `gh run list --commit <headSha>` trova almeno un workflow run
  `completed/success` sul commit head della PR.

Se l'output indica veri fallimenti, se GitHub API fallisce o se manca evidenza
alternativa success, il runner blocca la FASE C.

---

## 8. Gestione warning Git LF/CRLF su stderr

Git puo' scrivere warning di conversione line ending su stderr anche quando il
comando e' riuscito, per esempio durante `git --no-pager diff --check` o path
discovery.

Il runner accetta come warning non bloccanti solo le forme:

- `CRLF will be replaced by LF the next time Git touches it`;
- `LF will be replaced by CRLF the next time Git touches it`.

La policy vale solo con exit code `0`. Exit code diverso da `0`, stderr Git non
whitelisted o veri errori whitespace restano bloccanti.

---

## 9. Configurazione JSON

Campi principali:

- `step`;
- `name`;
- `repo_path`;
- `bridge_root`;
- `branch`;
- `commit_message`;
- `pr_title`;
- `pr_body`;
- `next_step`;
- `expected_files`;
- `phase_a_checks`;
- `phase_c_checks`;
- `allow_no_github_checks_reported`;
- `log_max_count`.

I comandi usano `argv`, non stringhe shell:

```json
{
  "name": "Verification Gate",
  "argv": ["pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts\\verify.ps1"]
}
```

La modalita' shell e' disabilitata. Se un comando dichiara `"shell": true`, il runner fallisce.

---

## 10. Output Bridge

Il Bridge default e':

```text
D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\pwsh_command
```

Il runner genera:

```text
NNNN-Richiesta_Generazione_<nome>.txt
NNNN-Comando_Eseguito_<nome>.ps1
NNNN-Output_Completo_<nome>.txt
NNNN-Output_Compatto_<nome>.md
NNNN-Output_Compatto_<nome>.docx
LAST-Richiesta_Generazione.txt
LAST-Comando_Eseguito.ps1
LAST-Output_Completo.txt
LAST-Output_Compatto.md
LAST-Output_Compatto.docx
```

Nota di compatibilita': questi `LAST-*` sono alias operativi richiesti per questo runner di pubblicazione. La fonte autorevole resta Git con file versionati e report step. Non usare `LAST-*` come input autorevole quando serve tracciabilita' storica.

Il file DOCX e' un archivio OpenXML minimale valido, con:

- `[Content_Types].xml`;
- `_rels/.rels`;
- `word/document.xml`.

Il runner lascia il compatto disponibile su file Bridge e `LAST-*`; non esegue
copie automatiche negli appunti.

---

## 11. Sicurezza

Default fail-closed:

- nessun commit;
- nessun push;
- nessuna PR;
- nessun merge;
- nessun deploy;
- nessuna chiamata provider live;
- nessun secret o API key;
- nessun comando distruttivo.

FASE B e FASE C richiedono flag espliciti. FASE A e Plan sono le modalita' ordinarie per verifica e preparazione.

Il runner evita `Invoke-Expression` e usa comandi `argv`.

---

## 12. Relazione con autonomia supervisionata a gate

Il runner non e' autonomia cieca. E' uno strumento di esecuzione supervisionata:

- la config dichiara scope e gate;
- la FASE A verifica;
- la FASE B pubblica solo con consenso;
- la FASE C mergia solo con consenso e check;
- ogni fase produce output Bridge leggibili.

Il controllo umano resta parte del workflow.

---

## 13. Limiti residui

- Il runner non sostituisce review umana del diff.
- La robustezza GitHub dipende da `gh` installato e autenticato.
- `LAST-*` e' supportato come alias operativo per richiesta dello STEP 0590, ma non deve diventare fonte storica autorevole.
- Non include ancora un Risk Classifier stabile L0-L4; quello resta lo step successivo.

---

## 14. Verifiche

Test mirati:

```powershell
python -m pytest tests\unit\test_asf_publish_step_runner.py
```

Gate completi:

```powershell
python -m pytest
python scripts\check_workflow_health.py
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify.ps1
git --no-pager diff --check
git status --short
```

---

## 15. Prossimo step

```text
0600) Risk Classifier + Gate Policy
```
