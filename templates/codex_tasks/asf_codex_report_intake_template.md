# ASF Codex Report Intake Template

## Summary

- project-name: `{{PROJECT_NAME}}`
- repo-path: `{{REPO_PATH}}`
- main-branch: `{{MAIN_BRANCH}}`
- step: `{{STEP}}`
- report-path: `{{REPORT_PATH}}`
- intake status: `{{INTAKE_STATUS}}`

## Sections found

{{SECTIONS_FOUND}}

## Sections missing

{{SECTIONS_MISSING}}

## Target Git status

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

## Warnings

{{WARNINGS}}

## Prossime verifiche consigliate

- Review manuale del report Codex.
- Verifica diff e scope.
- Verifica vincoli e forbidden actions.
- Eseguire test e Verification Gate manualmente.
- Usare closure pack solo come guida human-gated.

## Nota

Questo intake e' un controllo locale read-only. Non equivale ad approval, non sostituisce review Alberto/ChatGPT e non chiude lo step.
