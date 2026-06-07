# Changelog

Formato ispirato a Keep a Changelog, adattato al metodo interno.

---

## [0.58.0] - 2026-06-07

### Added

- STEP 0580 - Dry-run Loop Runner.
- Script `scripts/asf_dry_run_loop_runner.py`.
- Runbook `docs/motor/0580_DRY_RUN_LOOP_RUNNER.md`.
- Esempi JSON `examples/dry_run_loop/step_0580_simulated_request.json` e `examples/dry_run_loop/step_0580_execution_plan.json`.
- Test `tests/unit/test_asf_dry_run_loop_runner.py`.

### Changed

- Il MVP Motore passa da roadmap documentale a primo ciclo dry-run locale.
- Aggiornati README, roadmap, decision log, Project Workflow Index e Workflow Health Check con il runner 0580.
- Il prossimo step consigliato diventa `0590) Risk Classifier + Gate Policy`.

### Guardrails

- Nessuna chiamata live a provider esterni.
- Nessun secret o API key richiesto o letto.
- Output runtime sotto `tmp/asf_dry_run_loop/`.
- Nessun write sul repository target da parte del runner.
- Nessun commit, push, PR, merge, deploy o release.

### Not included

- Nessun Risk Classifier completo: rimandato allo STEP 0590.
- Nessun Independent Review Node separato: rimandato allo STEP 0600.
- Nessun Controlled Codex Executor: rimandato allo STEP 0610.
- Nessun first controlled write pilot: rimandato allo STEP 0630.

---

## [0.57.0] - 2026-06-07

### Added

- STEP 0570 - ASF Supervised Gate Autonomy ADR and MVP Motor Roadmap.
- ADR `docs/adr/0570_SUPERVISED_GATE_AUTONOMY.md`.
- Roadmap motore `docs/motor/0570_MVP_MOTOR_ROADMAP.md`.
- Specifica loop a gate `docs/motor/0570_GATE_LOOP_SPEC.md`.
- Nodo revisione indipendente `docs/motor/0570_INDEPENDENT_REVIEW_NODE.md`.

### Changed

- Ri-prioritizzata la roadmap da autonomia fire-and-forget o retry live verso autonomia supervisionata a gate.
- Aggiornati README, roadmap, decision log e Project Workflow Index con la rotta MVP Motore 0570-0630.
- Esplicitato il congelamento dei nuovi step di meta-processo finche' il motore non completa almeno un giro end-to-end dry-run.

### Guardrails

- Nessun runner operativo introdotto nello STEP 0570.
- Nessuna live run OpenAI, nessun secret e nessuna evidence STEP 0560 toccata.
- Nessun commit, push, PR, merge, deploy o automazione Git.

### Not included

- Nessun Dry-run Loop Runner: rimandato allo STEP 0580.
- Nessun Controlled Codex Executor: rimandato allo STEP 0610.
- Nessun First Controlled Write Pilot: rimandato allo STEP 0630.

---

## [0.56.0] - 2026-06-06

### Added

- STEP 0560 - OpenAI API Adapter First Authorized Live Run.
- Wrapper autorizzato `scripts/asf_openai_first_authorized_live_run.py`, che passa da `scripts/asf_openai_api_adapter.py`.
- Report versionato `docs/0560-01-Report_OpenAI_API_Adapter_First_Authorized_Live_Run.md`.
- Diagnostic pack provider-side `docs/0560-03-Diagnostic_OpenAI_Provider_HTTP_Error_And_Rate_Limit.md`.
- Test mockati `tests/unit/test_asf_openai_first_authorized_live_run.py`.

### Changed

- Aggiornato il marker live smoke a `ASF_OPENAI_LIVE_SMOKE_OK`.
- Il risultato live adapter include `usage` e `response_id_hash_16` quando disponibili.
- Il wrapper distingue `success_with_marker`, `marker_missing`, `output_text_absent`, `provider_http_error`, `rate_limited`, `quota_exceeded`, `model_access_denied`, `authentication_error`, `project_limit_or_billing_block` e `unknown_provider_error`.
- Aggiornati README, roadmap, Documentation Sync, Project Workflow Index, Workflow Health Check, Quick Reference e Command Cookbook.

### Guardrails

- Live run autorizzata via `--live`, ma consolidata come provider-side block: HTTP 429 `insufficient_quota`, `BLOCKED_BY_RATE_LIMIT_OR_QUOTA`.
- Nessuna nuova chiamata live nello STEP 0560-E.
- Nessun JSON evidence creato, perche' lo step non ha prodotto una live success.
- Nessun secret, token, valore auth header o payload raw scritto nei nuovi artifact.

### Not included

- Nessun commit, push, PR, merge, release o deploy.
- Nessun retry live e nessun bypass dell'adapter.

---

## [0.55.0] - 2026-06-06

### Added

- STEP 0550 - LAST Deprecation and 4-Digit Artifact Naming Standard.
- Documento `docs/73_LAST_DEPRECATION_4_DIGIT_ARTIFACT_NAMING_STANDARD.md`.
- Utility dry-run/apply `scripts/migrate_artifact_names_4digit.py`.
- Test `tests/unit/test_migrate_artifact_names_4digit.py`.

### Changed

- Aggiornati AGENTS, README, Codex Workflow, Documentation Sync, Project Workflow Index, Workflow Health Check, Quick Reference, Command Cookbook, Status Dashboard e template PowerShell command pack.
- Aggiornati skill draft/export repository-local `as-common-pwsh-command-pack` senza modificare skill esterne installate.
- Deprecata la generazione operativa di `LAST-*`; nuovo standard `NNNN-II-Tipo_Nome.ext` con ultimo artefatto = `max(II)` per `(step, tipo)`.
- Spostato il futuro step OpenAI API Adapter First Authorized Live Run a `560)` per evitare collisione con STEP 0550.

### Guardrails

- Utility di migrazione dry-run di default, apply solo con `--apply`.
- Nessun overwrite e blocco su collisioni.
- Nessuna cancellazione di file storici `LAST-*`.
- Nessuna modifica a skill esterne o repository esterne.

### Not included

- Nessun commit, push, PR, merge, release o deploy.
- Nessuna installazione della skill fuori repository.

---

## [0.54.8] - 2026-06-06

### Added

- STEP 548 - Git Line Endings Warning Cleanup.
- Documento `docs/72_ASF_GIT_LINE_ENDINGS_WARNING_CLEANUP.md`.
- Test guardrail `tests/unit/test_git_line_endings_warning_cleanup.py`.

### Changed

- Aggiornata `.gitattributes` con policy EOL repository-level per sorgenti, documentazione, template e script Windows.
- Aggiornati roadmap, decision log, Documentation Sync, Project Workflow Index, Quick Reference e Command Cookbook con la gestione LF/CRLF controllata.
- Il prossimo step consigliato e' stato poi spostato a `560) OpenAI API Adapter First Authorized Live Run` dallo STEP 0550.

### Guardrails

- Nessuna modifica a configurazione Git globale utente.
- Nessuna rinormalizzazione massiva.
- `templates/test_plans/test_plan_template.md` esplicitamente protetto con `eol=lf`.
- Script Windows `.bat`, `.cmd` e `.ps1` lasciati compatibili con CRLF working-tree.

### Not included

- Nessun commit, push, PR, merge, release o deploy.
- Nessuna modifica agli stash.
- Nessuna modifica fuori repository ASF.

---

## [0.54.6] - 2026-06-06

### Added

- STEP 546 - Export/Install as-common-pwsh-command-pack Skill.
- Export installabile `templates/pwsh_command_pack/export/as-common-pwsh-command-pack/SKILL.md`.
- Installer dry-run/apply `scripts/install_pwsh_command_pack_skill.py`.
- Documento `docs/71_ASF_PWSH_COMMAND_PACK_SKILL_EXPORT_INSTALL.md`.
- Test guardrail `tests/unit/test_pwsh_command_pack_skill_export_install.py`.

### Changed

- Aggiornati README, roadmap, decision log, Documentation Sync, Project Workflow Index, Workflow Health Check, Quick Reference, Command Cookbook e README template con riferimenti a export/install.
- Esteso il workflow health check per proteggere export skill e installer.
- Il prossimo step consigliato e' stato poi spostato a `560) OpenAI API Adapter First Authorized Live Run` dallo STEP 0550.

### Guardrails

- Dry-run default; nessuna scrittura senza `--apply`.
- Target esplicito con `--target-user-skills` o `--target-dir`.
- Backup timestamped prima di overwrite confermato.
- Nessuna cancellazione di cartelle.
- Nessuna installazione diretta in `%USERPROFILE%\.agents\skills` durante lo step ASF.
- Nessuna modifica a `Codex_Skills`.

### Not included

- Nessun commit, push, PR, merge, release o deploy.
- Nessuna modifica agli stash.
- Nessuna scrittura fuori repository ASF eseguita da Codex.

---

## [0.54.5] - 2026-06-06

### Added

- STEP 545 - PowerShell Command Pack Skill Finalization.
- Documento `docs/70_ASF_PWSH_COMMAND_PACK_SKILL_FINALIZATION.md`.
- README template `templates/pwsh_command_pack/README.md`.
- Skill draft esportabile `templates/pwsh_command_pack/as-common-pwsh-command-pack-SKILL.md`.
- Test guardrail `tests/unit/test_pwsh_command_pack_skill_finalization.py`.

### Changed

- Aggiornati i template canonici `safe_bootstrap_template.ps1` e `safe_command_pack_script_template.ps1` con file prefix a 4 cifre, `ArgList`, parser Git `--porcelain=v1 --untracked-files=all`, scope guard e clipboard best-effort.
- Aggiornati AGENTS, README, Codex Workflow, roadmap, decision log, Project Workflow Index, Quick Reference, Command Cookbook e documento PowerShell Command Pack con richiami allo standard finalizzato.
- Confermato che lo standard STEP 536 e' stato validato concretamente dallo STEP 540 con safe bootstrap e branch/PR.
- Il prossimo step consigliato e' stato poi spostato a `560) OpenAI API Adapter First Authorized Live Run` dallo STEP 0550.

### Guardrails

- Bootstrap corto con `& { ... }`, parse-check e ultima riga eseguibile.
- Logica complessa solo nel `.ps1` generato.
- `ArgList`, non `$Args`, per parametri wrapper.
- Parser Git robusto con `git status --porcelain=v1 --untracked-files=all`.
- PR-first publishing; nessun `git push origin main` come default.
- DOCX best-effort e warning LF/CRLF non bloccanti quando i gate passano.

### Not included

- Nessuna modifica alla skill esterna sotto `%USERPROFILE%\.agents\skills`.
- Nessun commit, push, PR, merge, release o deploy.
- Nessuna modifica agli stash.

---

## [0.54.0] - 2026-06-06

### Added

- STEP 540 - OpenAI API Adapter Controlled Live Execution Pack.
- Script `scripts/asf_openai_controlled_live_execution_pack.py`.
- Documento `docs/69_ASF_OPENAI_API_ADAPTER_CONTROLLED_LIVE_EXECUTION_PACK.md`.
- Template `templates/pwsh_command_pack/step_540_openai_controlled_live_execution_pack_template.ps1`.
- Test `tests/unit/test_asf_openai_controlled_live_execution_pack.py`.

### Changed

- Aggiornati README, roadmap, decision log, Documentation Sync, Project Workflow Index, Workflow Health Check, Quick Reference e Command Cookbook con i riferimenti al pack controllato.
- Rafforzata la separazione operativa tra dry-run/mock/preflight e futura live reale.
- Il prossimo step consigliato e' stato poi spostato a `560) OpenAI API Adapter First Authorized Live Run` dallo STEP 0550.

### Guardrails

- Dry-run e' il default e non usa rete.
- Live reale futuro richiede `--execution-mode live`, `ASF_OPENAI_LIVE_ENABLED=1`, `--confirm-live-openai`, credenziale presente solo nell'ambiente locale e artifact sotto `tmp/`.
- La sola presenza di `OPENAI_API_KEY` non autorizza chiamate OpenAI.
- Gli artifact indicano la credenziale solo come boolean `credential_present`.
- Il template PowerShell usa safe bootstrap, parse-check, script `.ps1`, output numerati/`LAST` e DOCX non bloccante.

### Not included

- Nessuna chiamata live OpenAI API.
- Nessun uso di API key reale.
- Nessun SDK OpenAI o nuova dipendenza.
- Nessun commit, push, PR, merge, release o deploy.
- Nessuna modifica agli stash.

---

## [0.53.6] - 2026-06-06

### Added

- STEP 536 - PowerShell Command Pack Safe Bootstrap Hardening.
- Template `templates/pwsh_command_pack/safe_bootstrap_template.ps1`.
- Template `templates/pwsh_command_pack/safe_command_pack_script_template.ps1`.
- Test documentale `tests/unit/test_pwsh_command_pack_safe_bootstrap_hardening.py`.

### Changed

- Aggiornato `docs/64_ASF_PWSH_COMMAND_PACK_SKILL_HARDENING.md` con il nuovo standard Safe Bootstrap PowerShell Command Pack.
- Aggiornati AGENTS, README, Codex Workflow, Project Workflow Index, Quick Reference e Command Cookbook con richiami a bootstrap corto, parse-check, script `.ps1` completo e PR-first publishing.
- Aggiornati roadmap e decision log con lo STEP 536.
- Confermato il prossimo step consigliato: `540) OpenAI API Adapter Controlled Live Execution Pack`.

### Guardrails

- Il blocco PowerShell incollato deve restare corto e validare lo script generato con `[scriptblock]::Create(...)`.
- Vietate here-string annidate, logica Git complessa, DOCX XML, `else` esterni e `finally` fragile nel bootstrap.
- La pubblicazione verso `main` e' branch + PR di default; `git push origin main` non e' default.
- DOCX e' best-effort e non blocca se output TXT/MD sono validi.
- Warning LF/CRLF restano non bloccanti quando `git --no-pager diff --check`, test, health check e verify gate passano.

### Not included

- Nessuna modifica alla skill esterna fuori repository.
- Nessuna modifica di logica applicativa.
- Nessun commit, push, PR, merge, release o deploy.
- Nessuna modifica agli stash.

---

## [0.53.5] - 2026-06-06

### Added

- STEP 535 - Codex Prompt Clean-First Workflow Update.
- Test documentale `tests/unit/test_codex_prompt_clean_first_workflow.py`.

### Changed

- Aggiornati `AGENTS.md` e `docs/08_CODEX_WORKFLOW.md` con la regola clean-first per i prompt Codex.
- Chiarita la separazione tra prompt Codex pulito, eventuale salvataggio Bridge, intake gate e publication command pack in Project Workflow Index, Quick Reference, Command Cookbook e documento PowerShell Command Pack.
- Aggiornati README, roadmap e decision log con il riferimento allo STEP 535.
- Confermato il prossimo step consigliato: `540) OpenAI API Adapter Controlled Live Execution Pack`.

### Guardrails

- Il prompt Codex pulito e direttamente copiabile e' il default.
- Il Codex command pack PowerShell resta valido per Bridge Dropbox / ChatGPT Bridge, file numerati, file `LAST` e audit trail formale.
- Il pwsh/publication command pack resta successivo al report Codex e all'intake gate, per pubblicazione Git controllata.
- Codex non deve fare commit, push, PR, merge o deploy salvo richiesta esplicita.

### Not included

- Nessuna modifica di logica applicativa.
- Nessun nuovo script di automazione.
- Nessuna modifica agli stash.
- Nessun commit, push, PR, merge, release o deploy.

---

## [0.53.0] - 2026-06-06

### Added

- STEP 530 - OpenAI API Adapter Live Smoke Result Hardening.
- Documento `docs/68_ASF_OPENAI_API_ADAPTER_LIVE_SMOKE_RESULT_HARDENING.md`.
- Test documentale `tests/unit/test_asf_openai_api_adapter_live_smoke_result_hardening_docs.py`.
- Artifact Markdown opzionale `--output-markdown` per riepilogo operatore sicuro.

### Changed

- Rafforzato `scripts/asf_openai_api_adapter.py` con schema live stabile `status`, `classification`, `safe_details`, `provider`, `model`, `live_enabled`, `credential_present`, `duration_ms` e `timestamp`.
- Centralizzata la classificazione live in `not_configured`, `disabled`, `credential_missing`, `live_not_allowed`, `success`, `provider_error`, `network_error`, `rate_limited`, `auth_error`, `schema_error` e `unknown_error`.
- Estesi i test mockati di `tests/unit/test_asf_openai_api_adapter_live_smoke.py` per gate mancanti, successo, auth, rate limit, provider, network, schema e unknown error.
- Aggiornati README, roadmap, decision log, Documentation Sync, Project Workflow Index, Workflow Health Check, Quick Reference, Command Cookbook, Workflow Status Dashboard e script `scripts/check_workflow_health.py` / `scripts/show_workflow_status.py` con i riferimenti allo STEP 530.
- Aggiornato il prossimo step consigliato a `540) OpenAI API Adapter Controlled Live Execution Pack`.

### Security

- I report indicano la credenziale solo come boolean `credential_present`.
- Nessuna chiave viene stampata, salvata, hashata, troncata, fingerprintata o serializzata.
- I test dello step sono mockati e non richiedono rete o credenziali reali.
- Codex non deve eseguire live test; qualunque futura prova live richiede uno step separato e autorizzazione esplicita.

### Not included

- Nessuna chiamata live OpenAI API.
- Nessun SDK OpenAI o nuova dipendenza.
- Nessun retry automatico della richiesta live.
- Nessun commit, push, PR, merge, release o deploy.

---

## [0.52.0] - 2026-06-06

### Added

- STEP 520 - OpenAI API Adapter First Controlled Live Smoke Test.
- Documento `docs/67_ASF_OPENAI_API_ADAPTER_FIRST_CONTROLLED_LIVE_SMOKE_TEST.md`.
- Template `templates/codex_tasks/asf_openai_api_live_smoke_test_template.md`.
- Test automatici `tests/unit/test_asf_openai_api_adapter_live_smoke.py` e `tests/unit/test_asf_openai_api_adapter_live_smoke_docs.py`.

### Changed

- Esteso `scripts/asf_openai_api_adapter.py` con preflight `--gate-only` e smoke live controllata per `POST https://api.openai.com/v1/responses`.
- Aggiunti campi JSON `mode`, `network_call_attempted`, `network_call_count`, `store`, `runtime_artifact_path`, `output_text_present`, `expected_marker_found` ed `error_category`.
- Aggiornati README, roadmap, decision log, Documentation Sync, Project Workflow Index, Workflow Health Check, Quick Reference, Command Cookbook, Workflow Status Dashboard e script `scripts/check_workflow_health.py` / `scripts/show_workflow_status.py` con i riferimenti allo STEP 520.
- Aggiornato il prossimo step consigliato a `530) OpenAI API Adapter Live Smoke Result Hardening`.

### Security

- La live smoke richiede `OPENAI_API_KEY`, `ASF_OPENAI_LIVE_ENABLED=1`, `--allow-live`, conferma esatta e prompt tiny non sensibile.
- La richiesta live usa `store: false`, `max_output_tokens: 32` e artifact sotto `tmp/`.
- La API key non viene stampata, loggata, salvata, hashata, troncata o fingerprintata.

### Not included

- Nessun SDK OpenAI o nuova dipendenza.
- Nessun requisito di credenziali reali o network per i test automatici.
- Nessun retry automatico della richiesta live.
- Nessuna integrazione produttiva OpenAI API.
- Nessun commit, push, PR, merge, release o deploy.

---

## [0.51.0] - 2026-06-06

### Added

- STEP 510 - OpenAI API Adapter Live Boundary and Credential Gate.
- Documento `docs/66_ASF_OPENAI_API_ADAPTER_LIVE_BOUNDARY_CREDENTIAL_GATE.md`.
- Template `templates/codex_tasks/asf_openai_api_live_boundary_gate_template.md`.
- Test automatici `tests/unit/test_asf_openai_api_adapter_live_boundary_gate.py` e `tests/unit/test_asf_openai_api_adapter_live_boundary_docs.py`.

### Changed

- Esteso `scripts/asf_openai_api_adapter.py` con un report JSON deterministico per il mode `live`.
- Aggiunti gate espliciti per `OPENAI_API_KEY`, `ASF_OPENAI_LIVE_ENABLED=1`, `--allow-live` e `--live-confirm I_UNDERSTAND_THIS_CALLS_OPENAI_API`.
- Aggiornati README, roadmap, decision log, Documentation Sync, Project Workflow Index, Workflow Health Check, Quick Reference, Command Cookbook, Workflow Status Dashboard e script `scripts/check_workflow_health.py` / `scripts/show_workflow_status.py` con i riferimenti allo STEP 510.
- Aggiornato il prossimo step consigliato a `520) OpenAI API Adapter First Controlled Live Smoke Test`.

### Security

- Il gate controlla solo la presenza di `OPENAI_API_KEY` e non stampa valore, lunghezza, prefisso, suffisso, hash o fingerprint.
- Il mode `live` resta no-network e produce sempre `network_performed: false` e `network_call_performed: false`.
- Rafforzata la redazione di stringhe OpenAI-key-like e secret-like prima dell'output.

### Not included

- Nessuna chiamata live OpenAI API.
- Nessun requisito di credenziali reali per i test.
- Nessun SDK OpenAI o nuova dipendenza.
- Nessun commit, push, PR, merge, release o deploy.

---

## [0.50.0] - 2026-06-06

### Added

- STEP 500 - OpenAI API Adapter.
- Script `scripts/asf_openai_api_adapter.py`.
- Documento `docs/65_ASF_OPENAI_API_ADAPTER.md`.
- Template `templates/codex_tasks/asf_openai_api_adapter_template.md`.
- Test automatici `tests/unit/test_asf_openai_api_adapter.py` e `tests/unit/test_asf_openai_api_adapter_docs.py`.

### Changed

- Aggiunto adapter standard-library-only per payload Responses-style, validazione modello/reasoning/text, `check-env`, `dry-run` e `mock` deterministici.
- Aggiornati README, roadmap, decision log, Project Workflow Index, Workflow Health Check, Quick Reference, Command Cookbook, Workflow Status Dashboard e script `scripts/check_workflow_health.py` / `scripts/show_workflow_status.py` con i riferimenti allo STEP 500.
- Aggiornato il prossimo step consigliato a `510) OpenAI API Adapter Live Boundary and Credential Gate`.

### Security

- `OPENAI_API_KEY` viene controllata solo per presenza e non viene mai scritta nei report JSON.
- Stringhe simili a chiavi OpenAI vengono redatte prima dell'output.

### Not included

- Nessuna chiamata live OpenAI API.
- Nessun requisito di `OPENAI_API_KEY`.
- Nessun SDK OpenAI o nuova dipendenza.
- Nessun uso network, commit, push, PR, merge, release o deploy.

---

## [0.49.0] - 2026-06-05

### Added

- STEP 490 - ASF PowerShell Command Pack Skill Hardening.
- Documento `docs/64_ASF_PWSH_COMMAND_PACK_SKILL_HARDENING.md`.
- Skill esterna aggiornata in `%USERPROFILE%\.agents\skills\as-common-pwsh-command-pack` con `references/` ed `examples/`.
- Template robusto `references/pwsh-command-pack-template.ps1` nella skill esterna.

### Changed

- Rafforzata la skill comune `as-common-pwsh-command-pack` per generare script `.ps1` completi, loggati, verificabili, con output numerati e `LAST-*`, Markdown/DOCX compatto, clipboard e guardrail Git/Codex/ASF.
- Aggiornati roadmap, decision log, README, Project Workflow Index, Workflow Health Check e script `scripts/check_workflow_health.py` con il riferimento allo STEP 490.

### Not included

- Nessun commit, push, PR, merge, release o deploy.
- Nessuna creazione di una seconda skill o rinomina della skill esistente.
- Nessuna modifica a PATH, profili PowerShell, CI, hook Git, secret, `.env`, `src/**` o `policies/**`.
- Nessuna modifica a repository target esterni.

---

## [0.45.0] - 2026-06-04

### Added

- STEP 450 - ASF Codex Read-Only Invocation Repeatable Trial Pack.
- Script `scripts/asf_codex_readonly_repeatable_trial.py`.
- Script `scripts/asf_codex_readonly_trial_compare.py`.
- Documenti `docs/59_ASF_CODEX_READONLY_REPEATABLE_TRIAL_PACK.md` e `docs/60_ASF_CODEX_READONLY_REPEATABLE_TRIAL_RESULTS.md`.
- Template `templates/codex_tasks/asf_codex_readonly_repeatable_trial_template.md` e `templates/codex_tasks/asf_codex_readonly_trial_compare_template.md`.
- Test automatici per prepare-only, conferma mancante, Codex non disponibile, compare e documentazione.

### Changed

- Aggiornati Project Workflow Index, Workflow Health Check, Quick Reference, Command Cookbook, Workflow Status Dashboard, roadmap, decision log e README con i riferimenti al Repeatable Trial Pack.
- Aggiornati `scripts/check_workflow_health.py` e `scripts/show_workflow_status.py` per includere documenti, script e template dello STEP 450.
- Aggiornato il prossimo step consigliato a `460) ASF Codex Read-Only Invocation Diagnostics Hardening`.

### Not included

- Nessuna esecuzione workspace-write.
- Nessun uso danger-full-access.
- Nessun commit, push, PR o merge automatico.
- Nessuna modifica a repository target esterni.
- Nessuna modifica a GitHub o GitHub API.
- Nessuna modifica a CI, hook Git, `core.hooksPath`, dipendenze, secret, `.env`, PATH o profili PowerShell.
- Nessuna modifica a `src/**` o `policies/**`.
- Nessuna modifica a `scripts/verify.ps1`.

---

## [0.44.0] - 2026-06-04

### Added

- STEP 440 - ASF Codex Read-Only Invocation Clean Target Trial.
- Documenti `docs/57_ASF_CODEX_READONLY_CLEAN_TARGET_TRIAL.md` e `docs/58_ASF_CODEX_READONLY_CLEAN_TARGET_TRIAL_RESULTS.md`.
- Test documentale `tests/unit/test_asf_codex_readonly_clean_target_trial_docs.py`.
- Trial locale sotto `tmp/asf_clean_target_trial/step_440/` con repo Git sintetica pulita, Human Approval Gate `GO`, preview, `execute-readonly`, result capture e safety gate.

### Changed

- Aggiornati Project Workflow Index, Workflow Health Check, Workflow Status Dashboard, Quick Reference, Command Cookbook, roadmap, decision log e README con i riferimenti al clean target trial.
- Aggiornati `scripts/check_workflow_health.py` e `scripts/show_workflow_status.py` per includere i documenti 57-58.
- Rafforzato `scripts/asf_codex_readonly_invoke.py` per leggere correttamente report completi del Human Approval Gate con decisione `GO` e per usare UTF-8 esplicito nella subprocess.
- Rafforzato `scripts/asf_codex_readonly_safety_gate.py` per classificare come `WARNING_REVIEW_REQUIRED` capture PASS con stderr non vuoto o output incompleto.
- Aggiornato il prossimo step consigliato a `450) ASF Codex Read-Only Invocation Repeatable Trial Pack`.

### Not included

- Nessuna esecuzione workspace-write.
- Nessun uso danger-full-access.
- Nessun commit, push, PR o merge automatico.
- Nessuna modifica a repository target esterni.
- Nessuna modifica a GitHub o GitHub API.
- Nessuna modifica a CI, hook Git, `core.hooksPath`, dipendenze, secret, `.env`, PATH o profili PowerShell.
- Nessuna modifica a `src/**` o `policies/**`.

---

## [0.43.0] - 2026-06-04

### Added

- STEP 430 - ASF Codex Read-Only Invocation First Manual Trial.
- Documenti `docs/55_ASF_CODEX_READONLY_FIRST_MANUAL_TRIAL.md` e `docs/56_ASF_CODEX_READONLY_FIRST_TRIAL_RESULTS.md`.
- Test documentale `tests/unit/test_asf_codex_readonly_first_manual_trial_docs.py`.
- Trial locale sotto `tmp/` con runner prepare, Human Approval Gate, preview read-only, result capture simulato e safety gate.

### Changed

- Aggiornati Project Workflow Index, Workflow Health Check, Quick Reference, Command Cookbook, Workflow Status Dashboard, roadmap, decision log e README con i riferimenti al first manual trial.
- Aggiornati `scripts/check_workflow_health.py` e `scripts/show_workflow_status.py` per includere i documenti 55-56 tra i file centrali.
- Rafforzato il safety gate read-only per non classificare come modifica file una frase negativa come `No target file modifications detected`.
- Aggiornato il prossimo step consigliato a `440) ASF Codex Read-Only Invocation Clean Target Trial`.

### Not included

- Nessuna esecuzione di `codex exec` durante lo step.
- Nessuna esecuzione workspace-write.
- Nessuna invocazione reale Codex perche' il Human Approval Gate del trial ASF era `HOLD`.
- Nessuna esecuzione automatica di commit, push, PR o merge.
- Nessuna modifica a repository target esterni, GitHub, CI, dipendenze, secret, `.env`, `src/**` o `policies/**`.

---

## [0.42.0] - 2026-06-03

### Added

- MEGA-STEP 400-420 - ASF Codex Read-Only Invocation Prototype Pack.
- Script `scripts/asf_codex_readonly_invoke.py` con default `preview` e modalita' `execute-readonly` human-approved.
- Script `scripts/asf_codex_result_capture.py` per normalizzare stdout, stderr, exit code e report in PASS/WARNING/FAIL.
- Script `scripts/asf_codex_readonly_safety_gate.py` per valutare result capture read-only prima di qualunque design futuro piu' ampio.
- Documenti `docs/52_ASF_CODEX_READONLY_INVOCATION_PROTOTYPE.md`, `docs/53_ASF_CODEX_INVOCATION_RESULT_CAPTURE.md` e `docs/54_ASF_CODEX_READONLY_SAFETY_GATE.md`.
- Template `templates/codex_tasks/asf_codex_readonly_invocation_template.md`, `templates/codex_tasks/asf_codex_invocation_result_capture_template.md` e `templates/codex_tasks/asf_codex_readonly_safety_gate_template.md`.
- Test automatici per invocation preview/validation, result capture, safety gate e copertura del pack 400-420.

### Changed

- Aggiornati Workflow Health Check e Workflow Status Dashboard per includere i nuovi documenti, script e template.
- Aggiornati Project Workflow Index, Quick Reference, Command Cookbook, Release Readiness, Existing Project Pilot Onboarding e documenti runner con il nuovo passaggio read-only.
- Aggiornata roadmap: STEP 400, 410 e 420 completati; STEP 430 consigliato come ASF Codex Read-Only Invocation First Manual Trial.
- Aggiornato decision log con la scelta di mantenere il livello attivo a read-only analysis con default preview.

### Not included

- Nessuna esecuzione di `codex exec` durante lo sviluppo o i test dello step.
- Nessuna invocazione automatica di Codex in default mode.
- Nessuna esecuzione workspace-write.
- Nessuna esecuzione danger-full-access.
- Nessuna esecuzione automatica di commit, push, PR o merge.
- Nessuna modifica a repository target esterni.
- Nessuna modifica a GitHub o GitHub API.
- Nessuna modifica a CI, hook Git, `core.hooksPath`, dipendenze, secret, `.env`, PATH o profili PowerShell.
- Nessuna modifica a `src/**` o `policies/**`.
- Nessuna pubblicazione PyPI o registry.

---

## [0.39.0] - 2026-06-03

### Added

- MEGA-STEP 370-390 - ASF Automation Bridge Pack.
- Script read-only `scripts/asf_human_approval_gate.py`.
- Script `scripts/asf_codex_invocation_dry_run.py` per generare solo preview dry-run di futura invocazione Codex.
- Documenti `docs/49_ASF_HUMAN_APPROVAL_GATE.md`, `docs/50_ASF_CODEX_INVOCATION_DESIGN.md` e `docs/51_ASF_CODEX_INVOCATION_DRY_RUN_PACK.md`.
- Template `templates/codex_tasks/asf_human_approval_gate_template.md` e `templates/codex_tasks/asf_codex_invocation_dry_run_template.md`.
- Test automatici per Human Approval Gate, Codex Invocation Dry Run Pack e copertura Automation Bridge Pack.

### Changed

- Aggiornati Workflow Health Check e Workflow Status Dashboard per includere i nuovi documenti, script e template.
- Aggiornati Project Workflow Index, Quick Reference, Command Cookbook, Release Readiness, Existing Project Pilot Onboarding e documenti runner con il nuovo ponte verso l'invocazione Codex controllata.
- Aggiornata roadmap: STEP 370, 380 e 390 completati; STEP 400 consigliato come ASF Codex Invocation Read-Only Prototype.
- Aggiornato decision log con la scelta di mantenere l'invocazione Codex al livello dry-run preview.

### Not included

- Nessuna invocazione automatica di Codex.
- Nessuna esecuzione di `codex exec`.
- Nessuna esecuzione automatica di commit, push, PR o merge.
- Nessuna modifica a repository target esterni.
- Nessuna modifica a GitHub o GitHub API.
- Nessuna modifica a CI, hook Git, `core.hooksPath`, dipendenze, secret, `.env`, PATH o profili PowerShell.
- Nessuna modifica a `src/**` o `policies/**`.
- Nessuna pubblicazione PyPI o registry.

---

## [0.36.0] - 2026-05-29

### Added

- MEGA-STEP 340-360 - ASF Runner Automation Readiness Pack.
- Script read-only `scripts/asf_codex_report_intake.py`.
- Script `scripts/asf_generate_closure_pack.py` per generare closure pack Markdown human-gated.
- Documenti `docs/46_ASF_RUNNER_VERIFICATION_PACK_HARDENING.md`, `docs/47_ASF_CODEX_REPORT_INTAKE.md` e `docs/48_ASF_HUMAN_GATED_CLOSURE_PACK.md`.
- Template `templates/codex_tasks/asf_codex_report_intake_template.md` e `templates/codex_tasks/asf_human_gated_closure_pack_template.md`.
- Test automatici per hardening Verification Pack, Codex Report Intake e Human-Gated Closure Pack.

### Changed

- Rafforzato `verification_pack.md` generato da `scripts/asf_next_step.py` con controlli Pre-Codex, Post-Codex, scope checks, report checks, PR checks handling, LF/CRLF handling e human gates.
- Aggiornati Workflow Health Check, Workflow Status Dashboard, Project Workflow Index, Quick Reference e Cookbook con i nuovi strumenti.
- Aggiornata roadmap: STEP 340, 350 e 360 completati; STEP 370 consigliato come ASF Runner Human Approval Gate.
- Aggiornato decision log con la scelta dell'automation readiness pack senza automazione Codex/Git/GitHub.

### Not included

- Nessuna invocazione automatica di Codex.
- Nessuna esecuzione automatica di commit, push, PR o merge.
- Nessuna modifica a repository target esterni.
- Nessuna modifica a GitHub o GitHub API.
- Nessuna modifica a CI, hook Git, `core.hooksPath`, dipendenze, secret, `.env`, PATH o profili PowerShell.

---

## [0.33.0] - 2026-05-29

### Added

- MEGA-STEP 310-330 - ASF Runner Upgrade Pack.
- Config `config/asf_project_profiles.json` con profili iniziali `AI_Software_Factory` e `Family_Photo_Organizer`.
- Documenti `docs/43_ASF_RUNNER_PROJECT_PROFILES.md`, `docs/44_ASF_RUNNER_CODEX_HANDOFF_IMPROVEMENTS.md` e `docs/45_ASF_RUNNER_VERIFICATION_PACK.md`.
- Template `templates/codex_tasks/asf_runner_verification_pack_template.md`.
- Test automatici per profili progetto, handoff Codex migliorato e Verification Pack.

### Changed

- Potenziato `scripts/asf_next_step.py` con `--profile`, override manuali, handoff piu' completo e generazione di `verification_pack.md`.
- Aggiornato `templates/codex_tasks/asf_next_step_runner_handoff_template.md` con FASE 1, FASE 2, stato Git, note safety e Step Closure Report.
- Aggiornati Project Workflow Index, Health Check, Quick Reference, Cookbook, Dashboard, Readiness e Existing Project Pilot Onboarding con i nuovi riferimenti runner.
- Aggiornati `scripts/check_workflow_health.py` e `scripts/show_workflow_status.py` per includere documenti e config del runner upgrade nei controlli locali read-only.
- Aggiornata roadmap: STEP 310, 320 e 330 completati; STEP 340 consigliato come ASF Runner Verification Pack Hardening.
- Aggiornato decision log con la scelta di mantenere il runner local-first, read-only verso repository target e senza automazione Codex/GitHub.

### Not included

- Nessuna invocazione automatica di Codex.
- Nessuna modifica a repository target.
- Nessuna creazione branch nel repository target.
- Nessun commit, push, PR o merge automatico.
- Nessuna modifica a GitHub o GitHub API.
- Nessuna modifica a CI, hook Git, `core.hooksPath`, dipendenze, secret, `.env`, PATH o profili PowerShell.

---

## [0.30.0] - 2026-05-29

### Added

- STEP 300 - ASF Next Step Runner.
- Script `scripts/asf_next_step.py` con `prepare mode` locale e standard library only.
- Documento `docs/42_ASF_NEXT_STEP_RUNNER.md`.
- Template `templates/codex_tasks/asf_next_step_runner_handoff_template.md`.
- Test automatici in `tests/unit/test_asf_next_step_runner.py`.

### Changed

- Aggiornato `docs/34_PROJECT_WORKFLOW_INDEX.md` con il nuovo runner come entry point operativo.
- Aggiornato `docs/35_WORKFLOW_HEALTH_CHECK.md` e `scripts/check_workflow_health.py` per includere documento, script e template runner tra i riferimenti workflow centrali.
- Aggiornato `docs/36_WORKFLOW_QUICK_REFERENCE.md`, `docs/38_WORKFLOW_COMMAND_COOKBOOK.md`, `docs/39_WORKFLOW_STATUS_DASHBOARD.md`, `docs/40_RELEASE_READINESS.md` e `docs/41_EXISTING_PROJECT_PILOT_ONBOARDING.md` con i riferimenti al runner.
- Aggiornato `scripts/show_workflow_status.py` per mostrare il runner tra documenti e script centrali.
- Aggiornato `docs/21_DOCUMENTATION_SYNC.md` con il documento STEP 300.
- Aggiornato `README.md` con un rimando breve al runner.
- Aggiornata roadmap: STEP 300 completato e STEP 310 consigliato come ASF Next Step Runner Project Profiles.
- Aggiornato decision log con la scelta del prepare runner locale e prudente.

### Not included

- Nessuna invocazione automatica di Codex.
- Nessuna modifica a repository target durante prepare mode.
- Nessuna creazione branch nel repository target.
- Nessun commit, push, PR o merge automatico.
- Nessuna modifica a GitHub.
- Nessuna GitHub Release.
- Nessuna modifica a hook Git o `core.hooksPath`.
- Nessuna modifica a CI.
- Nessuna modifica a `src/**`.
- Nessuna modifica a `policies/**`.
- Nessuna nuova dipendenza.
- Nessuna modifica a secret, `.env`, PATH o profili PowerShell.
- Nessuna pubblicazione PyPI o registry.

---

## [0.29.0] - 2026-05-29

### Added

- STEP 290 - Existing Project Pilot Onboarding.
- Documento `docs/41_EXISTING_PROJECT_PILOT_ONBOARDING.md`.
- Template `templates/codex_tasks/existing_project_intake_template.md`.
- Template `templates/codex_tasks/first_pilot_step_packet_template.md`.
- Test automatici in `tests/unit/test_existing_project_pilot_onboarding.py`.

### Changed

- Aggiornato `docs/34_PROJECT_WORKFLOW_INDEX.md` con il protocollo Existing Project Pilot Onboarding.
- Aggiornato `docs/38_WORKFLOW_COMMAND_COOKBOOK.md` con la ricetta di intake per progetto esistente.
- Aggiornato `docs/40_RELEASE_READINESS.md` con il collegamento allo STEP 290 e al prossimo pilot reale.
- Aggiornato `docs/35_WORKFLOW_HEALTH_CHECK.md` e `scripts/check_workflow_health.py` per includere documento e template pilot onboarding tra i riferimenti workflow centrali.
- Aggiornato `docs/36_WORKFLOW_QUICK_REFERENCE.md` e `docs/39_WORKFLOW_STATUS_DASHBOARD.md` con i riferimenti al nuovo onboarding.
- Aggiornato `scripts/show_workflow_status.py` per mostrare i documenti readiness e pilot onboarding tra i documenti centrali.
- Aggiornato `docs/21_DOCUMENTATION_SYNC.md` con il documento STEP 290.
- Aggiornato `README.md` con un rimando breve al protocollo di onboarding.
- Aggiornata roadmap: STEP 290 completato e STEP 300 consigliato come First Existing Project Pilot.
- Aggiornato decision log con la scelta dell'onboarding specifico per progetti esistenti.

### Not included

- Nessuna applicazione del metodo a repository esterne.
- Nessuna modifica a repository esterne.
- Nessuna automazione cross-repository.
- Nessun refactor o migrazione.
- Nessuna modifica a CI.
- Nessuna modifica a `src/**`.
- Nessuna modifica a `policies/**`.
- Nessuna nuova dipendenza.
- Nessuna modifica a secret o `.env`.
- Nessun commit, push, PR o merge automatico.
- Nessuna modifica a GitHub.
- Nessuna GitHub Release.
- Nessuna pubblicazione PyPI o registry.

---

## [0.28.0] - 2026-05-29

### Added

- STEP 280 - Release Readiness.
- Documento `docs/40_RELEASE_READINESS.md`.
- Template `templates/codex_tasks/release_readiness_checklist.md`.
- Test automatici in `tests/unit/test_release_readiness.py`.

### Changed

- Aggiornato `docs/34_PROJECT_WORKFLOW_INDEX.md` con Release Readiness.
- Aggiornato `docs/36_WORKFLOW_QUICK_REFERENCE.md` con il riferimento alla readiness per pilot.
- Aggiornato `docs/38_WORKFLOW_COMMAND_COOKBOOK.md` con la ricetta Release Readiness.
- Aggiornato `docs/39_WORKFLOW_STATUS_DASHBOARD.md` con il link alla readiness.
- Aggiornato `docs/37_STEP_CLOSURE_REPORT.md` con la relazione tra closure e readiness.
- Aggiornato `docs/35_WORKFLOW_HEALTH_CHECK.md` e `scripts/check_workflow_health.py` per includere documento e template readiness tra i riferimenti workflow centrali.
- Aggiornato `docs/21_DOCUMENTATION_SYNC.md` con il documento STEP 280.
- Aggiornato `README.md` con un rimando breve alla checklist readiness.
- Aggiornata roadmap: STEP 280 completato e STEP 290 consigliato come Existing Project Pilot Onboarding.
- Aggiornato decision log con la scelta della readiness per pilot interno local-first.

### Not included

- Nessuna dichiarazione di readiness pubblica o SaaS.
- Nessuna GitHub API.
- Nessuna connessione internet richiesta.
- Nessuna integrazione in CI.
- Nessuna modifica a `scripts/verify.ps1`.
- Nessuno script per automatizzare commit, push, PR o merge.
- Nessuna modifica a GitHub.
- Nessuna GitHub Release.
- Nessuna pubblicazione PyPI o registry.
- Nessuna nuova dipendenza.
- Nessuna modifica a CI, `src/**`, `policies/**`, hook, script Git/GitHub esistenti, secret o `.env`.
- Nessuna installazione hook Git.
- Nessuna modifica a `git config core.hooksPath`.
- Nessuna modifica a PATH o profili PowerShell.

---

## [0.27.0] - 2026-05-29

### Added

- STEP 270 - Workflow Status Dashboard.
- Script read-only `scripts/show_workflow_status.py`.
- Documento `docs/39_WORKFLOW_STATUS_DASHBOARD.md`.
- Test automatici in `tests/unit/test_workflow_status_dashboard.py`.

### Changed

- Aggiornato `docs/34_PROJECT_WORKFLOW_INDEX.md` con la Workflow Status Dashboard.
- Aggiornato `docs/38_WORKFLOW_COMMAND_COOKBOOK.md` con la ricetta dashboard.
- Aggiornato `docs/35_WORKFLOW_HEALTH_CHECK.md` e `scripts/check_workflow_health.py` per includere documento e script dashboard tra i controlli workflow centrali.
- Aggiornato `docs/36_WORKFLOW_QUICK_REFERENCE.md` con il comando dashboard.
- Aggiornato `docs/21_DOCUMENTATION_SYNC.md` con il documento STEP 270.
- Aggiornato `README.md` con un rimando breve alla dashboard.
- Aggiornata roadmap: STEP 270 completato e STEP 280 consigliato come Release Readiness.
- Aggiornato decision log con la scelta della dashboard locale read-only.

### Not included

- Nessuna GitHub API.
- Nessuna connessione internet richiesta.
- Nessuna integrazione in CI.
- Nessuna modifica a `scripts/verify.ps1`.
- Nessuno script per automatizzare commit, push, PR o merge.
- Nessuna modifica a GitHub.
- Nessuna GitHub Release.
- Nessuna pubblicazione PyPI o registry.
- Nessuna nuova dipendenza.
- Nessuna modifica a CI, `src/**`, `policies/**`, hook, script Git/GitHub esistenti, secret o `.env`.
- Nessuna installazione hook Git.
- Nessuna modifica a `git config core.hooksPath`.
- Nessuna modifica a PATH o profili PowerShell.

---

## [0.26.0] - 2026-05-29

### Added

- STEP 260 - Workflow Command Cookbook.
- Documento `docs/38_WORKFLOW_COMMAND_COOKBOOK.md`.
- Test automatici in `tests/unit/test_workflow_command_cookbook.py`.

### Changed

- Aggiornato `docs/34_PROJECT_WORKFLOW_INDEX.md` con il Workflow Command Cookbook.
- Aggiornato `docs/36_WORKFLOW_QUICK_REFERENCE.md` con il riferimento al Cookbook per scenari specifici.
- Aggiornato `docs/37_STEP_CLOSURE_REPORT.md` con il riferimento al Cookbook per troubleshooting operativo.
- Aggiornato `docs/35_WORKFLOW_HEALTH_CHECK.md` e `scripts/check_workflow_health.py` per includere il Cookbook tra i documenti workflow centrali.
- Aggiornato `docs/21_DOCUMENTATION_SYNC.md` con il documento STEP 260.
- Aggiornato `README.md` con un rimando breve al Cookbook.
- Aggiornata roadmap: STEP 260 completato e STEP 270 consigliato come Workflow Status Dashboard.
- Aggiornato decision log con la scelta del ricettario operativo.

### Not included

- Nessuno script per automatizzare commit, push, PR o merge.
- Nessuna modifica a GitHub.
- Nessuna GitHub Release.
- Nessuna pubblicazione PyPI o registry.
- Nessuna nuova dipendenza.
- Nessuna modifica a CI, `src/**`, `policies/**`, hook, script Git/GitHub esistenti, secret o `.env`.
- Nessuna installazione hook Git.
- Nessuna modifica a `git config core.hooksPath`.
- Nessuna modifica a PATH o profili PowerShell.
- Nessun commit, push, PR o merge automatico.

---

## [0.25.0] - 2026-05-29

### Added

- STEP 250 - Step Closure Report.
- Documento `docs/37_STEP_CLOSURE_REPORT.md`.
- Template `templates/codex_tasks/step_closure_report_template.md`.
- Test automatici in `tests/unit/test_step_closure_report.py`.

### Changed

- Aggiornato `docs/32_PROMPT_PACKET_LIFECYCLE_CHECKLIST.md` con il riferimento alla chiusura step.
- Aggiornato `docs/34_PROJECT_WORKFLOW_INDEX.md` con documento e template Step Closure Report.
- Aggiornato `docs/36_WORKFLOW_QUICK_REFERENCE.md` con il passaggio di compilazione closure report.
- Aggiornato `docs/35_WORKFLOW_HEALTH_CHECK.md` e `scripts/check_workflow_health.py` per includere documento e template di closure.
- Aggiornato `docs/21_DOCUMENTATION_SYNC.md` con il documento STEP 250.
- Aggiornato `README.md` con un rimando breve allo Step Closure Report.
- Aggiornata roadmap: STEP 250 completato e STEP 260 consigliato come Workflow Command Cookbook.
- Aggiornato decision log con la scelta dello standard di chiusura step.

### Not included

- Nessuno script per automatizzare commit, push, PR o merge.
- Nessuna modifica a GitHub.
- Nessuna GitHub Release.
- Nessuna pubblicazione PyPI o registry.
- Nessuna nuova dipendenza.
- Nessuna modifica a CI, `src/**`, `policies/**`, hook, script Git/GitHub esistenti, secret o `.env`.
- Nessuna installazione hook Git.
- Nessuna modifica a `git config core.hooksPath`.
- Nessuna modifica a PATH o profili PowerShell.
- Nessun commit, push, PR o merge automatico.

---

## [0.24.0] - 2026-05-29

### Added

- STEP 240 - Workflow Quick Reference.
- Documento `docs/36_WORKFLOW_QUICK_REFERENCE.md`.
- Test automatici in `tests/unit/test_workflow_quick_reference.py`.

### Changed

- Aggiornato `docs/34_PROJECT_WORKFLOW_INDEX.md` con la quick reference.
- Aggiornato `docs/35_WORKFLOW_HEALTH_CHECK.md` e `scripts/check_workflow_health.py` per includere la quick reference tra i documenti workflow centrali.
- Aggiornato `docs/21_DOCUMENTATION_SYNC.md` con il documento STEP 240.
- Aggiornato `README.md` con un rimando breve alla quick reference.
- Aggiornata roadmap: STEP 240 completato e STEP 250 consigliato come Step Closure Report.
- Aggiornato decision log con la scelta della quick reference operativa.

### Not included

- Nessuno script per automatizzare commit, push, PR o merge.
- Nessuna modifica a GitHub.
- Nessuna GitHub Release.
- Nessuna pubblicazione PyPI o registry.
- Nessuna nuova dipendenza.
- Nessuna modifica a CI, `src/**`, `policies/**`, hook, script Git/GitHub esistenti, secret o `.env`.
- Nessuna installazione hook Git.
- Nessuna modifica a `git config core.hooksPath`.
- Nessuna modifica a PATH o profili PowerShell.
- Nessun commit, push, PR o merge automatico.

---

## [0.23.0] - 2026-05-29

### Added

- STEP 230 - Workflow Health Check.
- Script read-only `scripts/check_workflow_health.py`.
- Documento `docs/35_WORKFLOW_HEALTH_CHECK.md`.
- Test automatici in `tests/unit/test_workflow_health_check.py`.

### Changed

- Aggiornato `docs/34_PROJECT_WORKFLOW_INDEX.md` con il Workflow Health Check.
- Aggiornato `docs/21_DOCUMENTATION_SYNC.md` con il documento STEP 230.
- Aggiornato `README.md` con un rimando breve al Workflow Health Check.
- Aggiornata roadmap: STEP 230 completato e STEP 240 consigliato come Workflow Quick Reference.
- Aggiornato decision log con la scelta del controllo locale read-only.

### Not included

- Nessuna integrazione in CI.
- Nessuna modifica a `scripts/verify.ps1`.
- Nessuno script per automatizzare commit, push, PR o merge.
- Nessuna modifica a GitHub.
- Nessuna GitHub Release.
- Nessuna pubblicazione PyPI o registry.
- Nessuna nuova dipendenza.
- Nessuna modifica a CI, `src/**`, `policies/**`, hook, script Git/GitHub esistenti, secret o `.env`.
- Nessuna installazione hook Git.
- Nessuna modifica a `git config core.hooksPath`.
- Nessuna modifica a PATH o profili PowerShell.
- Nessun commit, push, PR o merge automatico.

---

## [0.22.0] - 2026-05-29

### Added

- STEP 220 - Project Workflow Index.
- Documento `docs/34_PROJECT_WORKFLOW_INDEX.md`.
- Test automatici in `tests/unit/test_project_workflow_index.py`.

### Changed

- Aggiornato `README.md` con un rimando breve all'indice operativo.
- Aggiornato `docs/33_PROMPT_PACKET_GENERATOR_DEVELOPER_ONBOARDING.md` con il collegamento al Project Workflow Index.
- Aggiornato `docs/21_DOCUMENTATION_SYNC.md` con il documento STEP 220.
- Aggiornata roadmap: STEP 220 completato e STEP 230 consigliato come Workflow Health Check.
- Aggiornato decision log con la scelta dell'indice operativo centrale.

### Not included

- Nessuno script per automatizzare commit, push, PR o merge.
- Nessuna modifica a GitHub.
- Nessuna GitHub Release.
- Nessuna pubblicazione PyPI o registry.
- Nessuna nuova dipendenza.
- Nessuna modifica a CI, `src/**`, `policies/**`, hook, script Git/GitHub, secret o `.env`.
- Nessuna installazione hook Git.
- Nessuna modifica a `git config core.hooksPath`.
- Nessuna modifica a PATH o profili PowerShell.
- Nessun commit, push, PR o merge automatico.

---

## [0.21.0] - 2026-05-29

### Added

- STEP 210 - Prompt Packet Generator Developer Onboarding.
- Documento `docs/33_PROMPT_PACKET_GENERATOR_DEVELOPER_ONBOARDING.md`.
- Test automatici in `tests/unit/test_prompt_packet_generator_developer_onboarding.py`.

### Changed

- Aggiornato `docs/19_PROMPT_PACKET_GENERATOR.md` con il riferimento alla guida onboarding.
- Aggiornato `docs/30_PROMPT_PACKET_GENERATOR_PACKAGING.md` con l'entry point onboarding.
- Aggiornato `docs/31_PROMPT_PACKET_GENERATOR_RELEASE_SMOKE_WORKFLOW.md` con il collegamento alla guida.
- Aggiornato `docs/32_PROMPT_PACKET_LIFECYCLE_CHECKLIST.md` con il riferimento onboarding.
- Aggiornato `docs/21_DOCUMENTATION_SYNC.md` con il documento STEP 210.
- Aggiornata roadmap: STEP 210 completato e STEP 220 consigliato come Project Workflow Index.
- Aggiornato decision log con la scelta della guida onboarding.

### Not included

- Nessuno script per automatizzare commit, push, PR o merge.
- Nessuna modifica a GitHub.
- Nessuna GitHub Release.
- Nessuna pubblicazione PyPI o registry.
- Nessuna nuova dipendenza.
- Nessuna modifica a CI, `src/**`, `policies/**`, hook, script Git/GitHub, secret o `.env`.
- Nessuna installazione hook Git.
- Nessuna modifica a `git config core.hooksPath`.
- Nessuna modifica a PATH o profili PowerShell.
- Nessun commit, push, PR o merge automatico.

---

## [0.20.0] - 2026-05-29

### Added

- STEP 200 - Prompt Packet Lifecycle Checklist.
- Documento `docs/32_PROMPT_PACKET_LIFECYCLE_CHECKLIST.md`.
- Template spuntabile `templates/codex_tasks/prompt_packet_lifecycle_checklist.md`.
- Test automatici in `tests/unit/test_prompt_packet_lifecycle_checklist.py`.

### Changed

- Aggiornato `docs/19_PROMPT_PACKET_GENERATOR.md` con il riferimento alla lifecycle checklist.
- Aggiornato `docs/30_PROMPT_PACKET_GENERATOR_PACKAGING.md` con il collegamento alla checklist.
- Aggiornato `docs/31_PROMPT_PACKET_GENERATOR_RELEASE_SMOKE_WORKFLOW.md` con il riferimento alla sequenza completa.
- Aggiornato `docs/21_DOCUMENTATION_SYNC.md` con il documento STEP 200.
- Aggiornata roadmap: STEP 200 completato e STEP 210 consigliato come Prompt Packet Generator Developer Onboarding.
- Aggiornato decision log con la scelta della checklist lifecycle manuale.

### Not included

- Nessuno script per automatizzare commit, push, PR o merge.
- Nessuna modifica a GitHub.
- Nessuna GitHub Release.
- Nessuna pubblicazione PyPI o registry.
- Nessuna nuova dipendenza.
- Nessuna modifica a CI, `src/**`, `policies/**`, hook, script Git/GitHub, secret o `.env`.
- Nessuna installazione hook Git.
- Nessuna modifica a `git config core.hooksPath`.
- Nessuna modifica a PATH o profili PowerShell.
- Nessun commit, push, PR o merge automatico.

---

## [0.19.0] - 2026-05-28

### Added

- STEP 190 - Prompt Packet Generator Release Smoke Workflow.
- Script locale `scripts/smoke_prompt_packet_release.ps1`.
- Documento `docs/31_PROMPT_PACKET_GENERATOR_RELEASE_SMOKE_WORKFLOW.md`.
- Test automatici in `tests/unit/test_prompt_packet_generator_release_smoke_workflow.py`.

### Changed

- Aggiornato `docs/19_PROMPT_PACKET_GENERATOR.md` con il comando smoke locale.
- Aggiornato `docs/29_PROMPT_PACKET_GENERATOR_CLI_HARDENING.md` con il riferimento allo smoke workflow.
- Aggiornato `docs/30_PROMPT_PACKET_GENERATOR_PACKAGING.md` con il collegamento al release smoke workflow.
- Aggiornato `docs/21_DOCUMENTATION_SYNC.md` con il documento STEP 190.
- Aggiornata roadmap: STEP 190 completato e STEP 200 consigliato come Prompt Packet Generator Developer Onboarding.
- Aggiornato decision log con la scelta di smoke workflow locale.

### Not included

- Nessuna release pubblica.
- Nessuna GitHub Release.
- Nessuna pubblicazione PyPI o registry.
- Nessuna nuova dipendenza.
- Nessuna modifica a CI, `src/**`, `policies/**`, hook, script Git/GitHub, secret o `.env`.
- Nessuna installazione hook Git.
- Nessuna modifica a `git config core.hooksPath`.
- Nessuna modifica a PATH o profili PowerShell.
- Nessun commit, push, PR o merge automatico.

---

## [0.18.0] - 2026-05-28

### Added

- STEP 180 - Prompt Packet Generator Packaging.
- Wrapper PowerShell `scripts/generate_task_packet.ps1`.
- Documento `docs/30_PROMPT_PACKET_GENERATOR_PACKAGING.md`.
- Sample generato `examples/task_packets/generated/step_180_generated_packaging_sample.md`.
- Test automatici in `tests/unit/test_prompt_packet_generator_packaging.py`.

### Changed

- Aggiornato `docs/19_PROMPT_PACKET_GENERATOR.md` con il packaging locale.
- Aggiornato `docs/29_PROMPT_PACKET_GENERATOR_CLI_HARDENING.md` con il collegamento allo STEP 180.
- Aggiornato `docs/21_DOCUMENTATION_SYNC.md` con il documento di packaging locale.
- Aggiornata roadmap: STEP 180 completato e STEP 190 consigliato come Prompt Packet Generator Release Smoke Workflow.
- Aggiornato decision log con la scelta di packaging locale senza pubblicazione esterna.
- Aggiornato `.gitignore` con eccezione mirata per versionare i sample in `examples/task_packets/generated/`.

### Not included

- Nessuna pubblicazione PyPI o registry.
- Nessuna nuova dipendenza.
- Nessuna modifica a CI, `src/**`, `policies/**`, hook, script Git/GitHub, secret o `.env`.
- Nessuna installazione hook Git.
- Nessuna modifica a `git config core.hooksPath`.
- Nessuna modifica a PATH o profili PowerShell.
- Nessun commit, push, PR o merge automatico.

---

## [0.17.0] - 2026-05-28

### Added

- STEP 170 - Prompt Packet Generator CLI Hardening.
- `scripts/generate_task_packet.py`.
- `docs/29_PROMPT_PACKET_GENERATOR_CLI_HARDENING.md`.
- Test automatici in `tests/unit/test_prompt_packet_generator_cli_hardening.py`.

### Changed

- Aggiornato `docs/19_PROMPT_PACKET_GENERATOR.md` con uso della CLI locale.
- Aggiornata roadmap: STEP 170 completato e STEP 180 consigliato come Prompt Packet Generator Packaging.
- Aggiornato decision log con la scelta di un generatore CLI local-first, standard library only.

### Not included

- Nessuno schema JSON/YAML formale.
- Nessuna nuova dipendenza.
- Nessuna modifica a `src/**`, `policies/**`, CI, hook, script Git/GitHub, secret o `.env`.
- Nessuna installazione hook Git.
- Nessuna modifica a `git config core.hooksPath`.
- Nessun commit, push, PR o merge automatico.

---

## [0.16.0] - 2026-05-28

### Added

- STEP 160 - Prompt Packet Validation Strict Mode.
- Flag `--strict` in `scripts/validate_task_packet.py`.
- `docs/28_PROMPT_PACKET_VALIDATION_STRICT_MODE.md`.
- Golden sample Strict valido in `examples/task_packets/valid/step_valid_strict_task_packet.md`.
- Golden sample Strict invalido in `examples/task_packets/invalid/strict_missing_bypass_guard.md`.
- Test automatici in `tests/unit/test_prompt_packet_validation_strict_mode.py`.

### Changed

- Aggiornati Prompt Packet Validation Lite, golden samples, Prompt Packet Hardening, Prompt Packet Generator, Codex Workflow, Verification Gate e Documentation Sync con riferimenti a Strict Mode.
- Aggiornata roadmap: STEP 160 completato e STEP 170 consigliato come Prompt Packet Generator CLI Hardening.
- Aggiornato decision log con la scelta di mantenere Lite default e Strict opt-in.
- Aggiornato pull request template con controllo opzionale Strict Mode.

### Not included

- Nessuno schema JSON/YAML.
- Nessuna integrazione automatica in CI o `scripts/verify.ps1`.
- Nessuna nuova dipendenza.
- Nessuna modifica a `src/**`, `policies/**`, CI, hook, script Git/GitHub, secret o `.env`.
- Nessuna installazione hook Git.
- Nessuna modifica a `git config core.hooksPath`.
- Nessun commit, push, PR o merge automatico.

---

## [0.15.0] - 2026-05-28

### Added

- STEP 150 - Prompt Packet Examples and Golden Samples.
- Golden sample valido in `examples/task_packets/valid/step_valid_minimal_task_packet.md`.
- Golden samples invalidi in `examples/task_packets/invalid/`.
- `docs/27_PROMPT_PACKET_GOLDEN_SAMPLES.md`.
- Test automatici in `tests/unit/test_prompt_packet_golden_samples.py`.

### Changed

- Aggiornati Prompt Packet Validation Lite, Prompt Packet Hardening, Prompt Packet Generator, Codex Workflow, Verification Gate e Documentation Sync con riferimenti ai golden samples.
- Aggiornata roadmap: STEP 150 completato e STEP 160 consigliato come Prompt Packet Validation Strict Mode.
- Aggiornato decision log con la scelta di golden samples valid/invalid senza introdurre modalita' strict.
- Aggiornato pull request template con controllo opzionale sui golden samples.

### Not included

- Nessuna modalita' strict.
- Nessuna nuova dipendenza.
- Nessuna modifica a `src/**`, `policies/**`, CI, hook, script Git/GitHub, secret o `.env`.
- Nessuna installazione hook Git.
- Nessuna modifica a `git config core.hooksPath`.
- Nessun commit, push, PR o merge automatico.

---

## [0.14.0] - 2026-05-28

### Added

- STEP 140 - Prompt Packet Validation Lite.
- `scripts/validate_task_packet.py`.
- `docs/26_PROMPT_PACKET_VALIDATION_LITE.md`.
- Test automatici in `tests/unit/test_prompt_packet_validation_lite.py`.

### Changed

- Aggiornati Prompt Packet Hardening, Prompt Packet Generator, Codex Workflow, workflow operativo, Verification Gate e Documentation Sync con il riferimento al validatore.
- Validato il template centrale `templates/codex_tasks/codex_task_packet_template.md` rispetto ai requisiti minimi.
- Aggiornata roadmap: STEP 140 completato e STEP 150 consigliato come Prompt Packet Examples and Golden Samples.
- Aggiornato decision log con la scelta di validazione Lite senza schema rigido.
- Aggiornato pull request template con controllo opzionale sul Prompt Packet Validation Lite.

### Not included

- Nessuna integrazione automatica in CI o `scripts/verify.ps1`.
- Nessuna nuova dipendenza.
- Nessuna modifica a `src/**`, `policies/**`, CI, hook, script Git/GitHub, secret o `.env`.
- Nessuna installazione hook Git.
- Nessuna modifica a `git config core.hooksPath`.
- Nessun commit, push, PR o merge automatico.

---

## [0.13.0] - 2026-05-28

### Added

- STEP 130 - Prompt Packet Hardening.
- `docs/25_PROMPT_PACKET_HARDENING.md`.
- Test automatici in `tests/unit/test_prompt_packet_hardening.py`.

### Changed

- Rafforzato `templates/codex_tasks/codex_task_packet_template.md` con allowed scope, forbidden scope, forbidden actions, Verification Gate, Documentation Sync, Soft Protection awareness e report finale standard.
- Rafforzati i prompt Codex ask/code/review/repair con riferimenti al Prompt Packet Hardening.
- Aggiornati workflow Codex, workflow operativo, Verification Gate, Documentation Sync e Soft Protection Guardrails.
- Aggiornata roadmap: STEP 130 completato e STEP 140 consigliato come Prompt Packet Validation Lite.
- Aggiornato decision log con la scelta di non introdurre ancora schema rigido.
- Aggiornato pull request template con controllo sul Prompt Packet Hardening.

### Not included

- Nessuno schema rigido o parser dedicato.
- Nessuna modifica a `src/**`, `policies/**`, CI, dipendenze, script, hook, secret o `.env`.
- Nessuna installazione hook Git.
- Nessuna modifica a `git config core.hooksPath`.
- Nessun commit, push, PR o merge automatico.

---

## [0.12.0] - 2026-05-28

### Added

- STEP 120 - Soft Protection Guardrails.
- Hook locali opt-in in `.githooks/pre-commit` e `.githooks/pre-push`.
- Script `scripts/git/install_soft_guardrails.ps1`.
- Script read-only `scripts/git/check_soft_guardrails.ps1`.
- Documento `docs/24_SOFT_PROTECTION_GUARDRAILS.md`.
- Test automatici in `tests/unit/test_soft_protection_guardrails.py`.

### Changed

- Aggiornati Branch Protection Policy, Branch Protection Implementation, GitHub Workflow, Verification Gate, Documentation Sync, Codex Workflow e workflow operativo con i soft guardrails.
- Aggiornata roadmap: STEP 120 completato e STEP 130 consigliato come Prompt Packet Hardening.
- Aggiornato decision log con la scelta di hook opt-in e bypass `ASF_ALLOW_MAIN_BYPASS=1`.
- Aggiornato pull request template con controllo opzionale sui Soft Protection Guardrails.

### Not included

- Nessuna installazione automatica degli hook.
- Nessuna modifica a `git config core.hooksPath`.
- Nessun commit, push, PR o merge automatico.
- Nessuna branch protection o ruleset applicato realmente su GitHub.
- Nessuna modifica a CI, dipendenze, `src/**`, policy o secret.

---

## [0.11.0] - 2026-05-28

### Added

- STEP 110 - Branch Protection Verification and Hardening.
- Soft protection fallback policy for the current private repository and GitHub plan limitation.
- Test automatici in `tests/unit/test_branch_protection_verification_hardening.py`.

### Changed

- Documentato il required check CI reale: `Verification Gate`.
- Documentato il limite GitHub plan: branch protection non disponibile sul repository privato corrente con HTTP 403.
- Migliorata la gestione di HTTP 403 in `scripts/github/verify_branch_protection.ps1` con exit code `2`.
- Rafforzato `scripts/github/apply_branch_protection.ps1` con warning sul piano GitHub prima di `-Apply`.
- Aggiornati GitHub Workflow, Verification Gate, Codex Workflow, workflow operativo, roadmap e decision log.

### Not included

- Nessuna branch protection o ruleset applicato realmente su GitHub.
- Nessuna esecuzione di `apply_branch_protection.ps1 -Apply`.
- Nessuna modifica a CI.
- Nessuna nuova dipendenza.
- Nessuna modifica a `src/**`, policy o secret.

---

## [0.10.0] - 2026-05-27

### Added

- STEP 100 - Branch Protection Implementation.
- `docs/23_BRANCH_PROTECTION_IMPLEMENTATION.md`.
- `scripts/github/detect_required_checks.ps1`.
- `scripts/github/apply_branch_protection.ps1`.
- `scripts/github/verify_branch_protection.ps1`.
- Test automatici in `tests/unit/test_branch_protection_implementation.py`.

### Changed

- Aggiornati Branch Protection Policy, GitHub Workflow, Verification Gate, Documentation Sync, Codex Workflow e workflow operativo con il runbook STEP 100.
- Aggiornata roadmap: STEP 100 completato e STEP 110 consigliato come Branch Protection Verification and Hardening.
- Aggiornato decision log con la scelta DryRun di default per gli script GitHub.
- Aggiornato pull request template con controllo sugli script che modificano GitHub.

### Not included

- Nessuna branch protection o ruleset applicato realmente su GitHub.
- Nessuna esecuzione di `apply_branch_protection.ps1 -Apply`.
- Nessuna modifica a CI.
- Nessuna nuova dipendenza.
- Nessuna modifica a `src/**`, policy o secret.

---

## [0.9.0] - 2026-05-27

### Added

- STEP 090 - Branch Protection Policy.
- `docs/22_BRANCH_PROTECTION_POLICY.md`.
- Test automatici in `tests/unit/test_branch_protection_policy.py`.

### Changed

- Documentato il livello minimo raccomandato per proteggere `main`.
- Integrati riferimenti alla Branch Protection Policy in GitHub Workflow, Verification Gate, Codex Workflow e workflow operativo.
- Aggiornata roadmap: STEP 090 completato e STEP 100 consigliato come Branch Protection Implementation.
- Aggiornato decision log con la policy per `main`.
- Aggiornato pull request template con controllo su bypass branch protection.

### Not included

- Nessuna branch protection o ruleset applicato realmente su GitHub.
- Nessuna modifica a CI.
- Nessuna nuova dipendenza.
- Nessuna modifica a `src/**`.
- Nessuna modifica a policy o secret.

---

## [0.8.0] - 2026-05-27

### Added

- STEP 080 - Documentation Sync.
- `docs/21_DOCUMENTATION_SYNC.md`.
- Test automatici in `tests/unit/test_documentation_sync.py`.

### Changed

- Integrato Documentation Sync nel Verification Gate.
- Aggiornati workflow generale e Codex workflow con responsabilita' documentali.
- Aggiornato pull request template con controllo su changelog, roadmap e decision log.
- Aggiornata roadmap: STEP 080 completato e STEP 090 consigliato come Branch Protection Policy.
- Aggiornato decision log con la regola Documentation Sync.

### Not included

- Nessuno script dedicato aggiunto.
- Nessuna nuova dipendenza.
- Nessuna modifica a CI.
- Nessuna modifica a `src/**`.
- Nessuna modifica a policy o secret.

---

## [0.7.0] - 2026-05-27

### Added

- STEP 070 - Verification Gate.
- `docs/20_VERIFICATION_GATE.md`.
- Script locale `scripts/verify.ps1`.
- Test automatici in `tests/unit/test_verification_gate.py`.

### Changed

- Allineata la CI al Verification Gate con `python -m pytest`, `git diff --check` e permessi minimi.
- Aggiunta sezione Verification Gate al pull request template.
- Aggiornati workflow, GitHub workflow, Codex workflow, roadmap e decision log.

### Not included

- Nessun commit, push, PR o merge automatico.
- Nessuna branch protection configurata automaticamente.
- Nessuna nuova dipendenza.
- Nessuna modifica a `src/**`.
- Nessun secret o file `.env` toccato.

---

## [0.6.0] - 2026-05-26

### Added

- STEP 060 - Codex Workflow.
- `docs/checklists/060_CODEX_WORKFLOW_CHECKLIST.md`.
- Esempio STEP 060 in `templates/codex_tasks/example_060_codex_workflow_task.md`.
- Test automatici in `tests/unit/test_codex_workflow.py`.

### Changed

- Esteso `docs/08_CODEX_WORKFLOW.md` con Codex CLI locale, Codex Web/Cloud, Ask/Suggest, Auto Edit controllato, Review, Repair, divieto di Full Auto, safe stop e rollback.
- Rafforzati i prompt Codex con no commit, no push, no merge, safety level, file da non toccare e output atteso.
- Aggiornato il template Codex Task Packet con safety level e file da non toccare.
- Aggiornata roadmap: STEP 060 completato.
- Aggiornato TREE con checklist, esempio e test STEP 060.

### Not included

- Nessuna logica applicativa reale.
- Nessuna modifica a `.github/workflows/ci.yml`.
- Nessuna modifica a policy di sicurezza.
- Nessuna modifica a `src/**`.
- Nessuna nuova dipendenza.
- Nessun commit, push o merge automatico.

---

## [0.5.0] - 2026-05-26

### Added

- STEP 050 - GitHub Workflow.
- Issue di tracciamento per `050) GitHub Workflow`.
- `docs/checklists/050_GITHUB_WORKFLOW_CHECKLIST.md`.
- Test automatici in `tests/unit/test_github_workflow.py`.

### Changed

- Esteso `docs/15_GITHUB_WORKFLOW.md` con issue policy, branch naming policy, commit policy, PR policy, merge policy, branch protection checklist e release/tag policy.
- Aggiornata roadmap: STEP 050 completato.
- Aggiornato TREE con checklist e test STEP 050.

### Not included

- Nessuna modifica a `.github/workflows/ci.yml`.
- Nessuna branch protection applicata automaticamente.
- Nessuna modifica a policy di sicurezza.
- Nessuna modifica a `src/**`.
- Nessuna nuova dipendenza.

---

## [0.4.0] - 2026-05-25

### Added

- STEP 040 - Prompt Packet Generator.
- `docs/19_PROMPT_PACKET_GENERATOR.md`.
- `docs/checklists/040_PROMPT_PACKET_CHECKLIST.md`.
- Esempio Family Photo Organizer in `templates/codex_tasks/example_040_family_photo_organizer_prompt_packet.md`.
- Test automatici in `tests/unit/test_prompt_templates.py`.

### Changed

- Standardizzati i prompt ChatGPT, Codex Ask, Codex Code, Codex Review e Codex Repair con sezioni minime comuni.
- Rafforzato `templates/codex_tasks/codex_task_packet_template.md` con livello L0-L4, file vietati, test/verifica e safe stop.
- Aggiornata roadmap: STEP 040 completato.
- Aggiornato decision log con DEC-021 -> DEC-023.

### Not included

- Nessuna logica applicativa reale.
- Nessuna modifica a policy di sicurezza.
- Nessuna modifica CI/CD.
- Nessuna nuova dipendenza.

---

## [0.3.0] - 2026-05-25

### Added

- STEP 030 — Safety Model operativo.
- Policy L0-L4 estesa in `docs/05_SECURITY_MODEL.md`.
- `docs/16_APPROVAL_POLICY.md`.
- `docs/17_TOOL_RISK_CLASSIFICATION.md`.
- `docs/18_ROLLBACK_STRATEGY.md`.
- `policies/safety_policy.v0.json`.
- `policies/safety_policy.v0.yaml`.
- `policies/path_policy.v0.json`.
- Template safety: approval request, dry-run report, risk assessment, rollback plan.
- Test automatici in `tests/unit/test_safety_policy.py`.

### Changed

- Aggiornato `README.md` allo stato STEP 030.
- Aggiornato `AGENTS.md` con escalation policy e file policy obbligatori.
- Aggiornato PR template con dichiarazione livello L0-L4.
- Aggiornata roadmap: STEP 030 completato.
- Aggiornato decision log con DEC-016 → DEC-020.

### Security

- L4 richiede ora esplicitamente approvazione, dry-run, backup/rollback e doppia conferma.
- MCP/tool remoti richiedono approval default e allowed tools espliciti.
- Path e secret policy introdotte come configurazioni versionate.

---

## [0.2.0] — 2026-05-25 — STEP 020 Repository Genesis

### Added

- Struttura repository completa.
- `.gitignore`.
- `.env.example`.
- `LICENSE` provvisorio.
- `pyproject.toml`.
- Package skeleton `src/ai_software_factory/`.
- Sottocartelle modulo:
  - `core/`
  - `intake/`
  - `prompts/`
  - `codex/`
  - `github/`
  - `openai_api/`
  - `mcp/`
  - `safety/`
  - `verification/`
  - `docs_sync/`
  - `audit/`
  - `ui/`
- Smoke test repository.
- GitHub Actions CI minimale.
- GitHub issue templates.
- Pull request template.
- Template per issue, PR, ADR, test plan e prompt Codex.
- Documenti placeholder per architettura, workflow, sicurezza, API, MCP, Codex, test, SaaS e case study.

### Changed

- Aggiornato `README.md` a stato STEP 020.
- Aggiornata roadmap con STEP 010 e STEP 020 completati.
- Aggiornato decision log con decisioni DEC-011 — DEC-015.

### Not included

- Nessuna logica applicativa reale.
- Nessuna chiamata API.
- Nessun database.
- Nessuna automazione distruttiva.
- Nessuna integrazione OpenAI/Codex/MCP operativa.

---

## [0.1.0] — 2026-05-25 — STEP 010 Visione e contesto

### Added

- Visione iniziale del progetto.
- README.
- AGENTS.md.
- Roadmap 010-150.
- Decision log iniziale DEC-001 — DEC-010.
- Template Codex Task Packet iniziale.
- Prompt ChatGPT progetto.
- Prompt Codex ask-only.
- Riferimenti tecnici iniziali.

### Not included

- Nessun codice applicativo.
- Nessuna automazione.
- Nessun repository remoto.
