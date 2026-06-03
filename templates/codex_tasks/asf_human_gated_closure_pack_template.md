# ASF Human-Gated Closure Pack

Questo closure pack e' manuale e human-gated. I comandi qui sotto sono generati come testo Markdown, non sono eseguiti dallo script.

## Summary

- project-name: `{{PROJECT_NAME}}`
- repo-path: `{{REPO_PATH}}`
- step: `{{STEP}}`
- branch: `{{BRANCH}}`
- main-branch: `{{MAIN_BRANCH}}`
- commit message: `{{COMMIT_MESSAGE}}`
- PR title: `{{PR_TITLE}}`
- PR body: `{{PR_BODY}}`

## Stato Git target letto

- branch corrente target: `{{CURRENT_BRANCH}}`
- working tree: `{{WORKING_TREE}}`

Working tree detail:

```text
{{WORKING_TREE_DETAIL}}
```

Diff stat:

```text
{{DIFF_STAT}}
```

Ultimi commit:

```text
{{RECENT_COMMITS}}
```

## Checklist prima del commit manuale

- [ ] Review diff completata.
- [ ] Scope verificato.
- [ ] Nessun secret o `.env` modificato.
- [ ] Nessuna modifica CI non autorizzata.
- [ ] Test locali completati.
- [ ] Verification Gate completato.
- [ ] Codex report intake letto.
- [ ] Alberto approva il passaggio manuale.

## Comandi verifica manuali

```powershell
Set-Location "{{REPO_PATH}}"
git branch --show-current
git status --short
git --no-pager diff --stat
git --no-pager diff --check
python -m pytest
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify.ps1
```

Warning LF/CRLF non sono bloccanti se `git diff --check`, test e Verification Gate passano con exit code 0.

## Comandi commit/push/PR manuali

Eseguire solo dopo review umana. Questi comandi sono manuali, human-gated e non eseguiti dallo script.

```powershell
git add .
git commit -m "{{COMMIT_MESSAGE}}"
git push -u origin {{BRANCH}}
gh pr create --base {{MAIN_BRANCH}} --head {{BRANCH}} --title "{{PR_TITLE}}" --body "{{PR_BODY}}"
```

## Gestione PR checks manuale

```powershell
$oldNativeErrorPreference = $PSNativeCommandUseErrorActionPreference
$PSNativeCommandUseErrorActionPreference = $false
gh pr checks --watch
$prChecksExitCode = $LASTEXITCODE
$PSNativeCommandUseErrorActionPreference = $oldNativeErrorPreference

if ($prChecksExitCode -ne 0) {
    Write-Host "ATTENZIONE: nessun check PR rilevato o check non disponibile. I controlli locali devono essere già stati eseguiti; verificare manualmente su GitHub se necessario."
}
```

## Merge manuale e verifica finale main

Eseguire solo dopo approval merge esplicita di Alberto.

```powershell
gh pr merge --merge --delete-branch
git switch {{MAIN_BRANCH}}
git pull origin {{MAIN_BRANCH}}
python scripts/show_workflow_status.py
python scripts/check_workflow_health.py
python -m pytest
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify.ps1
git status --short
git --no-pager log --oneline --max-count=10
```

## Step Closure Report finale

Compilare lo Step Closure Report dopo merge, pull finale di main e verifiche finali:

```text
docs/37_STEP_CLOSURE_REPORT.md
templates/codex_tasks/step_closure_report_template.md
```

Registrare eventuale attenzione su `gh pr checks --watch`, warning LF/CRLF e verifiche locali usate come evidenza.

## Limiti

- Il closure pack non approva nulla.
- Il closure pack non sostituisce review umana.
- Il closure pack non esegue comandi.
- Il closure pack non modifica GitHub.
