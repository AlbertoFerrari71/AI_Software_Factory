# STEP 0820 - Bridge Output Retry, Fallback and LAST Validation

## 1. Context

STEP 0800 hardened PowerShell native command guardrails in the publish runner.
STEP 0805 aligned the PowerShell command-pack skill with the proven ASF runner
flow. STEP 0810 added scope discovery, `PrepareConfig`, recovery UX and
no-false-`COMPLETATO` rules.

During STEP 0810 publication, Phase B had already completed correctly, but a
Bridge output file remained locked:

```text
D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\pwsh_command\0810-Output_Completo_Publish_Runner_Scope_Discovery_Recovery_UX_And_No_False_Completed_Guard.txt
```

The observed error was:

```text
The process cannot access the file because it is being used by another process.
```

Likely causes include an open editor/preview, Dropbox sync, antivirus/indexing,
an external transcript, or two writers targeting the same Bridge file.

## 2. Blocking Gates vs Accessory Outputs

The runner remains fail-closed for real gates:

- failed Git command, PR command, tests, Workflow Health Check, Verification
  Gate or diff-check means `BLOCCATO`;
- out-of-scope files remain blocking;
- missing approval flags remain blocking;
- a missing or invalid PR number before Phase C remains blocking.

Bridge output files are important audit artifacts, but they are not the same as
publication gates once the gates already passed.

## 3. Retry Policy

Bridge and LAST file writes use controlled retry:

- default retry count is small and finite;
- delay is short and fixed;
- retry is used only around write, copy and move operations;
- failed attempts are logged as concise operational lines;
- no infinite loop is allowed.

The intent is to absorb temporary file locks caused by sync, preview or
indexing without weakening any publish gate.

## 4. Fallback Policy

When a primary Bridge path remains blocked after retry, the runner writes a
timestamped fallback in the same Bridge directory.

Example:

```text
0810-Output_Completo_Name_fallback_20260608_141436.txt
```

Fallback rules:

- the primary expected path is still reported;
- the fallback path is reported explicitly;
- fallback is used only after retry failed;
- fallback does not silently replace the primary path;
- compact Markdown must exist either at the primary path or fallback path.

If compact Markdown cannot be written anywhere, the step is `BLOCCATO` because
the minimum traceability artifact is missing.

## 5. Markdown Mandatory, DOCX Best-Effort

TXT and compact Markdown are primary runner outputs. Compact Markdown is the
minimum audit artifact for human handoff and clipboard copy.

Compact Markdown is mandatory in the primary path or in a timestamped fallback.

DOCX remains best-effort:

- Word COM is not required;
- DOCX generation failure is a warning;
- a `.docx.failed.txt` marker may be written;
- DOCX failure must not make a verified publish look failed.

## 6. LAST Validation

The runner updates the compatibility `LAST-*` files with retry and fallback.
Typical files are:

```text
LAST-Richiesta_Generazione.txt
LAST-Comando_Eseguito.ps1
LAST-Output_Completo.txt
LAST-Output_Compatto.md
LAST-Output_Compatto.docx
```

`LAST-Output_Compatto.md` is copied to the clipboard with:

```powershell
Get-Content -Path <file> -Raw | Set-Clipboard
```

Do not use:

```powershell
Set-Clipboard -Path
```

When a LAST primary path remains locked, the runner retries, writes a
timestamped LAST fallback if possible and reports a strong warning. This does
not hide a real gate failure and does not invalidate a publish already verified
by gates.

## 7. Single Writer Ownership

This is the single writer ownership rule for runner Bridge output.

The publish runner owns its standard Bridge outputs:

```text
NNNN-Output_Completo_<name>.txt
NNNN-Output_Compatto_<name>.md
LAST-Output_Completo.txt
LAST-Output_Compatto.md
```

External wrappers must not open `Start-Transcript` on those same paths. If an
external transcript is needed, use a different name, for example:

```text
NNNN-Wrapper_Log_<name>.txt
```

Wildcard form:

```text
NNNN-Wrapper_Log_*.txt
```

This prevents the wrapper from locking the file that the runner must write.

## 8. Status Policy

Use these states consistently:

```text
BLOCCATO
COMPLETATO
COMPLETATO CON WARNING NON BLOCCANTE
```

Rules:

- gate failed = `BLOCCATO`;
- Git/PR/test/verify/diff-check failed = `BLOCCATO`;
- Bridge primary output locked after gates passed = retry, fallback, warning;
- DOCX failed = warning;
- LAST primary locked = retry, fallback or warning;
- compact Markdown missing both primary and fallback = `BLOCCATO`.

## 9. Operational Examples

Primary output temporarily locked:

```text
retry -> primary write succeeds -> COMPLETATO
```

Primary output still locked after retry, fallback succeeds:

```text
retry -> fallback_YYYYMMDD_HHMMSS -> COMPLETATO CON WARNING NON BLOCCANTE
```

Verification Gate fails:

```text
BLOCCATO
```

DOCX fails after Markdown was written:

```text
warning + optional .docx.failed.txt -> non-blocking
```

## 10. Out of Scope

This step does not:

- make publication automatic;
- weaken approval flags;
- make direct push to `main` acceptable;
- require Word COM;
- add new runtime dependencies;
- change external target repositories;
- replace Git/versioned files as the authoritative source.

The Bridge remains operational storage. Git and versioned files remain
authoritative.
