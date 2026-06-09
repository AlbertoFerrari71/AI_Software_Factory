# 0805 - PowerShell Publish Skill Sync With Proven ASF Runner Flow

## 1. Contesto dello STEP 0800

Lo STEP 0800 ha pubblicato correttamente il hardening dei guardrail PowerShell
per comandi nativi.

Esito operativo noto:

- PR #72 mergiata su `main`;
- commit finale `4391b24`;
- Workflow Health Check PASS;
- Verification Gate PASS;
- `pytest` PASS;
- `git --no-pager diff --check` PASS;
- working tree finale pulita;
- warning `gh pr checks returned no checks reported` accettato solo con fallback
  `gh run list --commit <headSha>` e almeno un workflow run `completed/success`;
- DOCX via Word COM trattato come warning non bloccante.

La lezione principale e' che il flusso stabile non era un mega-wrapper
PowerShell adattivo. Il flusso stabile era:

```text
config JSON esplicito + scripts/asf_publish_step.ps1 + Phase B -> recupero PR -> Phase C
```

Lo stesso schema era gia' stato usato con successo nello STEP 0790.

## 2. Problema osservato nei tentativi fragili

I tentativi meno stabili tendevano a concentrare troppe decisioni nel wrapper
PowerShell:

- deduzione automatica dei file da pubblicare;
- parsing fragile di `git status --short`;
- cattura `2>&1` usata come lista file, con rischio di includere warning LF/CRLF;
- introspezione `Get-Command -Path` su script `.ps1`;
- AST parsing per dedurre parametri del runner;
- recovery adattivo con troppe diramazioni;
- stampa di `COMPLETATO` prima dei gate finali;
- dipendenza bloccante da Word COM/DOCX.

Questi pattern aumentano la superficie di errore proprio nella fase in cui lo
step deve essere piu' deterministico e human-gated.

## 3. Soluzione consolidata

Per pubblicazioni ASF future, la skill/template PowerShell deve proporre di
default un comando basato sul runner versionato:

1. creare config JSON esplicito nel Bridge;
2. eseguire `scripts/asf_publish_step.ps1 -Config <config>`;
3. lanciare Phase B solo con `-ApprovePublish`;
4. recuperare il numero PR con `gh pr list --head`;
5. validare PR number non vuoto e numerico;
6. lanciare Phase C solo con `-PrNumber <numero> -ApproveMerge`;
7. eseguire verifiche finali;
8. produrre output Bridge numerati e `LAST-*` di compatibilita';
9. copiare il compatto finale con `Get-Content -Path ... -Raw | Set-Clipboard`.

Il command pack deve restare un orchestratore leggero. La pubblicazione vive nel
runner versionato, non in logica PowerShell duplicata nel wrapper.

## 4. Struttura del comando consigliato

Il config JSON deve contenere almeno:

```text
step
name
repo_path
bridge_root
branch
commit_message
pr_title
pr_body
next_step
expected_files
changed_files
verification_profile
risk_level
verification_phase
profile_selector_expected_profile
intent
provided_gates
phase_a_checks
phase_c_checks
allow_no_github_checks_reported
log_max_count
```

Il wrapper generato deve usare un helper `Run` semplice:

- rifiuta comando, label o argomenti vuoti;
- esegue il comando nativo;
- legge subito `$LASTEXITCODE`;
- fallisce con `throw` se l'exit code non e' `0`.

Per il recupero PR serve output catturato dal comando `gh`, ma non deve essere
usato `2>&1` come lista file o come deduzione dello scope.

## 5. Esempio sintetico

```powershell
$ConfigPath = "D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\publish_config\0805_publish_config.json"
$BranchName = "step-0805-pwsh-publish-skill-sync"
$LastCompact = "D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\publish_step\LAST-Output_Compatto.md"

Run "pwsh" @(
    "-NoProfile",
    "-ExecutionPolicy",
    "Bypass",
    "-File",
    "scripts/asf_publish_step.ps1",
    "-Config",
    $ConfigPath,
    "-Phase",
    "B",
    "-ApprovePublish"
)

$PrNumber = Run "gh" @(
    "pr",
    "list",
    "--head",
    $BranchName,
    "--json",
    "number",
    "--jq",
    ".[0].number"
) -CaptureOutput

if ([string]::IsNullOrWhiteSpace($PrNumber)) {
    throw "PR number missing."
}
if ($PrNumber -notmatch "^\d+$") {
    throw "PR number is not numeric."
}

Run "pwsh" @(
    "-NoProfile",
    "-ExecutionPolicy",
    "Bypass",
    "-File",
    "scripts/asf_publish_step.ps1",
    "-Config",
    $ConfigPath,
    "-Phase",
    "C",
    "-PrNumber",
    $PrNumber,
    "-ApproveMerge"
)

Run "python" @("-m", "pytest")
Run "python" @("scripts/check_workflow_health.py")
Run "pwsh" @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts/verify.ps1")
Run "git" @("--no-pager", "diff", "--check")
Run "git" @("--no-pager", "status", "--short")

Get-Content -Path $LastCompact -Raw | Set-Clipboard
```

`COMPLETATO` puo' essere scritto solo dopo l'ultima verifica passata.

## 6. Regole su expected_files e changed_files

`expected_files` e `changed_files` sono dichiarazioni esplicite di scope.

Regole:

- includere tutti i file che devono essere pubblicati;
- non recuperare automaticamente lo scope da output Git quando e' gia' noto;
- non allargare lo scope in modo casuale per superare un gate;
- lasciare che `scripts/asf_publish_step.ps1` blocchi file fuori scope;
- correggere la config se un file atteso manca.

## 7. Warning LF/CRLF

I warning LF/CRLF di Git su Windows sono warning controllati, non failure
automatiche, solo quando sono nella whitelist del runner e passano:

- test;
- Workflow Health Check;
- Verification Gate;
- `git --no-pager diff --check`.

Non usare output Git catturato con `2>&1` come base per liste file: i warning
possono entrare nel testo e contaminare la logica.

Dal micro-hardening 0923, il publish runner accetta su stderr solo i warning Git
LF/CRLF noti con exit code `0`; stderr Git diverso resta fail-closed.

## 8. DOCX best-effort

Il Markdown compatto resta l'output principale. Il DOCX e' best-effort:

- se Word COM fallisce, la pubblicazione non deve fallire solo per questo;
- il warning deve comparire nel report;
- TXT/Markdown validi prevalgono sul DOCX;
- un file `.docx.failed.txt` o warning equivalente e' sufficiente.

## 9. No false COMPLETATO

Un messaggio finale positivo come `COMPLETATO` e' ammesso solo dopo:

- Phase B passata;
- PR number recuperato, non vuoto e numerico;
- Phase C passata;
- verifiche finali passate;
- diff check passato;
- stato Git finale controllato.

Non eseguire Phase C se il PR number non e' valido.

## 10. Fuori scope

Questo step non introduce:

- riscrittura generale del publish runner;
- nuova automazione Git/GitHub;
- modifiche a CI, branch protection, hook o deploy;
- installazione della skill esterna sotto `%USERPROFILE%\.agents\skills`;
- publish, merge, tag, commit o push eseguiti da Codex.

## 11. Superfici aggiornate

Superfici repository-local allineate:

- `templates/pwsh_command_pack/README.md`;
- `templates/pwsh_command_pack/as-common-pwsh-command-pack-SKILL.md`;
- `templates/pwsh_command_pack/export/as-common-pwsh-command-pack/SKILL.md`;
- `templates/pwsh_command_pack/safe_command_pack_script_template.ps1`;
- `docs/38_WORKFLOW_COMMAND_COOKBOOK.md`;
- `docs/36_WORKFLOW_QUICK_REFERENCE.md`;
- test unitari sui template PowerShell.

## 12. Prossimo step consigliato

```text
0810) Publish Runner Recovery UX and No-False-Completed Guard
```

Motivo: dopo aver sincronizzato skill/template con il flusso reale dimostrato,
resta utile migliorare UX di recovery e messaggi di blocco del runner senza
indebolire i gate umani.
