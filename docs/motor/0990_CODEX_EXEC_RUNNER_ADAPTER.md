# 0990 - Codex Exec Runner Adapter

## Scopo

Questo step introduce un adapter per preparare envelope Codex CLI in modalita' dry-run.

Lo script non esegue Codex reale. Costruisce e valida il comando previsto, produce JSON e opzionalmente un report Markdown.

## Script

```text
scripts/asf_codex_exec_adapter.py
```

CLI minima:

```text
python scripts/asf_codex_exec_adapter.py --prompt path\to\prompt.md --working-directory C:\...\AI_Software_Factory --mode dry-run --json
```

## Validazioni

L'adapter valida:

- `prompt_path` esistente;
- `working_directory` dentro il repository ASF;
- `allowed_paths`;
- `forbidden_actions`;
- `execute=false` come default.

Se `--execute` viene richiesto senza `--allow-execute`, il risultato e' fail-closed.

Anche con `--allow-execute`, lo step 0980-1010 blocca l'esecuzione reale: il flag e' solo un segnaposto per un futuro pilot controllato.

## Stati

- `CODEX_DRY_RUN_DONE`: envelope dry-run valido e comando costruito;
- `CODEX_BLOCKED`: input non valido, path fuori scope o richiesta di esecuzione reale;
- `CODEX_READY`: stato logico precedente quando il prompt e' pronto per il dry-run.

## Output

Template:

```text
docs/templates/0990_CODEX_EXEC_ENVELOPE_TEMPLATE.json
```

Output JSON minimo:

- `step_id`;
- `mode`;
- `codex_command`;
- `prompt_path`;
- `working_directory`;
- `allowed_paths`;
- `forbidden_actions`;
- `execute_enabled`;
- `requires_alberto`;
- `status`;
- `next_action`;
- `validation_errors`.

## Guardrail

- dry-run default;
- nessuna esecuzione reale Codex;
- blocco path fuori scope;
- blocco working directory fuori repository;
- blocco azioni vietate;
- no pubblicazione Git;
- no merge;
- no deploy;
- no OS appunti.

## Test

```text
tests/unit/test_asf_codex_exec_adapter.py
```

Copertura minima:

- comando Codex preparato senza esecuzione;
- `execute` senza approvazione bloccato;
- prompt mancante bloccato;
- working directory fuori repo bloccata;
- prompt path fuori allowed paths bloccato;
- forbidden action bloccata;
- envelope JSON valido;
- assenza pattern OS appunti nel sorgente.
