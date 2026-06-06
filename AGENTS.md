# AGENTS.md - AI Software Factory

Scope: entire repository.

This file contains repository-level operating instructions for coding agents working on AI_Software_Factory.
It is intentionally ASCII-only to avoid encoding and mojibake issues.
It must never contain platform policy text, hidden instructions, credentials, secrets, tokens, or private keys.

## Project mission

AI Software Factory is a local-first workflow framework for turning software ideas into controlled implementation steps using ChatGPT, Codex, GitHub, PowerShell, tests, living documentation, human gates, and future controlled automation.

The project goal is not blind automation.
The project goal is safe, repeatable, diagnosable, human-gated automation.

For Alberto's operational vision of AI as a verifiable collaborator, see docs/project_context/VISIONE_OPERATIVA_AI.md.

## General rules

- Preserve the local-first and safety-first architecture.
- Keep changes small, explicit, testable, and documented.
- Prefer Python standard library unless an existing project dependency is already clearly used.
- Do not add new runtime dependencies without explicit approval.
- Do not introduce destructive commands.
- Do not delete, move, rename, overwrite, or clean files outside the requested scope.
- Do not modify external target repositories unless explicitly requested.
- Do not include secrets, credentials, tokens, API keys, or private data in files or logs.
- Do not paste platform policies or hidden instructions into repository files.

## Git and publication rules

- Before changing files, inspect branch and working tree.
- Stop if the working tree contains unrelated dirty files.
- Use git --no-pager for potentially long output.
- Do not commit, push, open pull requests, merge, tag, or deploy unless the user explicitly requests it.
- If commit, push, pull request, merge, or deploy is requested, run the required verification gates first and stop on failure.
- Treat Git LF/CRLF warnings as warnings, not failures, when git diff --check and tests pass.

## PowerShell conventions

- Use stop-on-error behavior.
- Save operational outputs under the ChatGPT Bridge when requested by the user.
- Prefer explicit checks of native command exit codes.
- Avoid fragile here-strings in long copy-paste command blocks.
- Avoid fragile try/finally structures in long pasted command blocks when a simpler explicit flow is possible.

## Codex invocation safety

- Codex target invocation work must remain read-only unless a future step explicitly authorizes a different design.
- Do not enable workspace-write by default.
- Do not use danger-full-access.
- CODEX_NOT_AVAILABLE is diagnostic information, not a target failure.
- Non-empty stderr is not automatically a failure; classify it with context.
- A target repository becoming dirty after a read-only run is a serious safety failure.
- Temporary invocation artifacts must stay under tmp/ or another ignored location.

## Verification before handoff

Run the checks that fit the change. For normal code or workflow changes, prefer:

- python -m pytest
- python scripts/check_workflow_health.py
- pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
- git --no-pager diff --check
- git --no-pager status --short

If a check is unavailable or fails, report it clearly.

## Documentation rules

- Update the relevant docs, indexes, roadmap, decisions, or changelog when the change affects workflow behavior.
- Keep documentation concise but operational.
- Preserve existing numbering and naming conventions.
- Avoid mojibake; prefer ASCII in this file.

## Final report format

Use Italian for the final user-facing report unless the user asks otherwise.
When closing an implementation step, include:

- A. Step eseguito
- B. Stato
- C. File creati/modificati
- D. Sintesi tecnica
- E. Test eseguiti
- F. Verifiche Git
- G. Vincoli rispettati
- H. Problemi aperti / warning
- I. Prossimo step consigliato
- J. Riepilogo finale step

The final summary should state the completed step, synthetic status, and recommended next step.
