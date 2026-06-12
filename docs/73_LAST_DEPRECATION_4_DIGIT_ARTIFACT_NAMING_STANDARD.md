# LAST Deprecation and 4-Digit Artifact Naming Standard

## 1. Purpose

STEP 0550 deprecates operational `LAST-*` artifacts and introduces a single
progressive artifact naming standard:

```text
NNNN-II-Tipo_Nome.ext
```

This removes ambiguous "latest file" state from the ChatGPT Bridge and keeps
the official source of truth in Git plus versioned files.

## 2. Final Rule

```text
No LAST.
No ambiguous state.
Only progressive artifacts.
Explicit iterations.
Official source = Git + versioned file.
Bridge = operational, not authoritative.
```

STEP 1050 clarification: `LAST-*` remains deprecated as a general repository
artifact pattern. The only accepted exception is operational Bridge
compatibility output under Bridge/codex_command, Bridge/pwsh_command, or
standard Bridge mirrors already produced by the publish runner/state machine.
Those `LAST-*` files are convenience mirrors, not authoritative durable
artifacts, and must not be introduced as permanent repository files.

## 3. Naming Standard

Use:

```text
NNNN-II-Tipo_Nome.ext
```

Where:

- `NNNN` is the four-digit step number, for example `0550`.
- `II` is the two-digit intra-step iteration, for example `01` or `02`.
- `Tipo` is the artifact type, for example `Prompt_Codex` or `Output_Compatto`.
- `Nome` is a descriptive slug.

Correct examples:

```text
0550-01-Richiesta_Generazione_last_deprecation_4_digit_artifact_naming_standard.txt
0550-01-Prompt_Codex_last_deprecation_4_digit_artifact_naming_standard.md
0550-01-Comando_Eseguito_last_deprecation_4_digit_artifact_naming_standard.ps1
0550-01-Output_Completo_last_deprecation_4_digit_artifact_naming_standard.txt
0550-01-Output_Compatto_last_deprecation_4_digit_artifact_naming_standard.md
0550-01-Output_Compatto_last_deprecation_4_digit_artifact_naming_standard.docx
0550-02-Prompt_Codex_last_deprecation_4_digit_artifact_naming_standard.md
```

Deprecated examples:

```text
LAST-Prompt_Codex.md
LAST-Comando_Eseguito.ps1
LAST-Output_Completo.txt
LAST-Output_Compatto.md
LAST-Output_Compatto.docx
LAST-Richiesta_Generazione.txt
LAST-HANDOFF.md
```

## 4. Finding the Latest Artifact

Do not read `LAST-*` as input.

To find the latest artifact of one type for one step:

```text
latest artifact = max(II) for (step, type)
```

Example: for step `0550` and type `Prompt_Codex`, compare only files matching:

```text
0550-II-Prompt_Codex_*.md
```

The latest prompt is the file with the greatest two-digit `II`.

## 5. Bridge vs Official Source

The ChatGPT Bridge is an operational staging area. It can hold generated
artifacts for convenience, but it is not authoritative.

The official source is:

1. Git history.
2. Versioned files in the repository.
3. Explicit artifact names using `NNNN-II-Tipo_Nome.ext`.

No workflow should depend on `LAST-*` as the source of truth.

## 6. Migration Rules

Use `scripts/migrate_artifact_names_4digit.py` for safe local migration checks.

Required behavior:

- dry-run by default;
- writes only with `--apply`;
- target directory is explicit;
- no overwrite;
- collision and ambiguous cases are reported;
- `LAST-*` files are not touched;
- `NN_...` structural documents are not touched;
- files already matching `NNNN-II-...` are not touched;
- safe legacy names are converted to iteration `01`;
- move/rename is used, not copy/delete.

Safe conversions:

```text
010-Prompt_Codex_x.md -> 0010-01-Prompt_Codex_x.md
530-Output_Compatto_x.md -> 0530-01-Output_Compatto_x.md
0550-Prompt_Codex_x.md -> 0550-01-Prompt_Codex_x.md
```

## 7. Historical Compatibility

Historical `LAST-*` files must not be deleted or rewritten by this step. They
remain historical evidence only.

Historical docs, changelog entries and decision records can mention `LAST-*`
when they describe what an older step did. New operational instructions,
templates and skill exports must not ask agents or command packs to generate or
read `LAST-*` as durable repository artifacts. The Bridge exception in section
2 is limited to standard operational mirrors.

PowerShell `$LASTEXITCODE` is unrelated to `LAST-*` artifact files and remains
valid where native command exit-code handling is required.

## 8. Skill and Template Impact

Repository-local command-pack templates and exported skill drafts must use only
progressive artifacts:

```text
NNNN-II-Richiesta_Generazione_<name>.txt
NNNN-II-Comando_Eseguito_<name>.ps1
NNNN-II-Output_Completo_<name>.txt
NNNN-II-Output_Compatto_<name>.md
NNNN-II-Output_Compatto_<name>.docx
```

External installed skills under `%USERPROFILE%\.agents\skills` are not modified
by this repository step. After review and publication, update external skills
from the repository-local export if Alberto explicitly authorizes that external
write.
