# ASF Codex Invocation Dry Run Pack

## 1. Scopo

`scripts/asf_codex_invocation_dry_run.py` genera un pacchetto dry-run per una futura invocazione Codex controllata.

Il pack serve a revisionare comando, sandbox proposta, stato approval e stop condition prima di qualunque prototipo reale.

---

## 2. Dry-run

Il dry-run genera file di preview, ma non esegue Codex.

Output predefinito:

```text
tmp/asf_codex_invocation/<project-name>/step_<step>/
```

File generati:

- `codex_invocation_dry_run.md`;
- `codex_exec_preview.ps1`.

`tmp/` resta ignorato da Git.

---

## 3. Esempio

```powershell
python scripts/asf_codex_invocation_dry_run.py --project-name Family_Photo_Organizer --repo-path "C:\Users\alberto.ferrari\source\repos\Family_Photo_Organizer" --step 590 --branch 590-sandbox-import-static-simulation-prototype --handoff-path tmp/asf_next_step/Family_Photo_Organizer/step_590/codex_handoff.md --approval-gate tmp/asf_approval_gate/Family_Photo_Organizer/step_590/human_approval_gate.md --output-dir tmp/asf_codex_invocation
```

---

## 4. codex_invocation_dry_run.md

Il Markdown contiene:

- project-name;
- repo-path;
- step;
- branch;
- sandbox proposta;
- approval status;
- comando preview;
- rischi;
- stop conditions;
- istruzioni manuali;
- nota che non e' stato eseguito.

Se approval gate contiene `HOLD` o `NO-GO`, il pack viene comunque generato ma marcato `DO NOT RUN`.

---

## 5. codex_exec_preview.ps1

Il file PowerShell e' una preview inertizzata.

Contiene:

- `DRY RUN ONLY`;
- `MANUAL REVIEW REQUIRED`;
- `DO NOT RUN WITHOUT ALBERTO APPROVAL`;
- il comando `codex exec` come testo da rivedere;
- nessun comando che invochi Codex.

Se il file viene aperto o lanciato per errore, stampa la preview e non esegue `codex exec`.

---

## 6. Sandbox

Valori ammessi:

- `read-only`: default e unica modalita' raccomandata per il prossimo prototipo;
- `workspace-write-preview`: genera preview con sandbox futura `workspace-write`, ma resta non eseguita.

`danger-full-access` non e' supportato.

---

## 7. Perche' non esegue Codex

L'obiettivo dello step 390 e' preparare una revisione controllata del comando, non cambiare livello di automazione.

Eseguire Codex introdurrebbe nuovi rischi:

- condivisione del contesto con il processo Codex;
- possibili modifiche se sandbox o comando sono errati;
- ambiguita' su branch e working tree;
- assenza di prototipo read-only verificato;
- assenza di log strutturati approvati.

Per questo il comando resta testo di preview.

---

## 8. Approval HOLD / NO-GO

Se il Human Approval Gate e' `HOLD` o `NO-GO`:

- il dry-run pack viene creato per rendere il blocco leggibile;
- il Markdown e il `.ps1` sono marcati `DO NOT RUN`;
- nessuna esecuzione e' consentita;
- Alberto deve risolvere i blocchi e rigenerare il gate.

---

## 9. Prossimi sviluppi

Prossimo step prudente:

```text
400-420) ASF Codex Read-Only Invocation Prototype Pack
```

Il prototipo resta read-only, registra stdout/stderr, exit code e report, normalizza il risultato con result capture e blocca progressione futura tramite safety gate se il gate umano o le evidenze non sono favorevoli.
