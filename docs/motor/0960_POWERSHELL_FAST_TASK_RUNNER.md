# 0960 - PowerShell Fast Task Runner

## Scopo

Lo STEP 0960 introduce una foundation locale per validare ed eseguire, solo quando esplicitamente richiesto, task deterministici della PowerShell Fast Lane.

Lo script non e' un orchestratore completo. Non pubblica, non apre PR, non fa merge, non fa deploy e non invoca Codex.

## Script

```text
scripts/asf_powershell_task_runner.py
```

## Modalita'

- default: dry-run di validazione;
- `--execute`: esecuzione limitata a comandi read-only whitelisted;
- output JSON sempre prodotto su stdout;
- output su file solo durante esecuzione reale validata.

## Envelope JSON

Campi minimi:

- `task_id`;
- `working_directory`;
- `allowed_paths`;
- `forbidden_patterns`;
- `timeout_seconds`;
- `idle_timeout_seconds`;
- `script_path` o `arguments`;
- `stdout_path`;
- `stderr_path`;
- `full_output_path`;
- `compact_output_path`.

## Validazioni fail-closed

Il runner blocca:

- campi obbligatori mancanti;
- `working_directory` fuori dagli `allowed_paths`;
- `script_path` o output path fuori scope;
- pattern vietati nel comando;
- timeout non validi;
- esecuzione di comandi non whitelisted, classificata come `COMMAND_NOT_WHITELISTED`.

## Output

L'output JSON contiene almeno:

- `status`;
- `dry_run`;
- `command`;
- `timeout_seconds`;
- `idle_timeout_seconds`;
- `output_paths`;
- `exit_code`;
- `classification`;
- `validation_errors`;
- `warnings`.

In `--execute`, la classificazione usa `scripts/asf_powershell_recovery_classifier.py`.

## Limiti intenzionali

- Nessuna API live.
- Nessun Codex exec.
- Nessun publish.
- Nessun merge.
- Nessun deploy.
- Nessun comando interattivo.
- Nessuna gestione completa del loop automatico.
