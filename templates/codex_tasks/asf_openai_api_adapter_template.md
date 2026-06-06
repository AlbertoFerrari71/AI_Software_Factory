# ASF OpenAI API Adapter Task Packet Template

## Step

```text
<STEP_NUMBER>) <TITLE>
```

Use STEP 500 for the adapter foundation already implemented here.

STEP 510 adds the live boundary and credential gate:

```text
510) OpenAI API Adapter Live Boundary and Credential Gate
```

Use the next controlled live smoke step only when the live boundary gate is green and the task explicitly authorizes a live smoke test:

```text
520) OpenAI API Adapter First Controlled Live Smoke Test
```

After STEP 520, use a result-hardening step for response parsing and report stability:

```text
530) OpenAI API Adapter Live Smoke Result Hardening
```

## Repository

```text
AlbertoFerrari71/AI_Software_Factory
C:\Users\alberto.ferrari\source\repos\AI_Software_Factory
```

## Branch

```text
<branch-name>
```

## Objective

Describe the adapter change in one paragraph.

The default for adapter work is local-first, deterministic and testable without OpenAI credentials.

## Safety constraints

- Do not make live API calls unless the step explicitly authorizes a controlled live smoke test.
- Do not require `OPENAI_API_KEY` for default tests.
- Do not paste API keys.
- Do not print, log, store or commit API key values.
- Do not add OpenAI SDK dependencies without explicit approval.
- Do not use network in dry-run or mock steps.
- Keep runtime artifacts under `tmp/`.
- Do not commit, push, open PRs, merge, tag or deploy.

## Expected adapter behavior

- Build Responses-style payloads.
- Validate model, reasoning effort and text verbosity settings.
- Check environment readiness without key leakage.
- Emit `network_performed: false` for dry-run and mock modes.
- Redact strings that resemble OpenAI API keys.
- Keep mock output deterministic.
- Keep live execution blocked unless all controlled smoke gates are present.

Required fail-closed marker:

```text
LIVE_MODE_NOT_IMPLEMENTED_IN_STEP_500
```

Current live boundary marker:

```text
LIVE_CALLS_NOT_IMPLEMENTED_IN_STEP_510
```

Current controlled live smoke markers:

```text
LIVE_SMOKE_READY_FOR_CALL
LIVE_SMOKE_EXECUTED_AND_PASSED
LIVE_SMOKE_NOT_RUN_MISSING_GATE
```

## Example commands

```powershell
python scripts/asf_openai_api_adapter.py --mode check-env --output-json tmp/asf_openai_adapter_env.json
python scripts/asf_openai_api_adapter.py --mode dry-run --input "ping" --output-json tmp/asf_openai_adapter_dry_run.json
python scripts/asf_openai_api_adapter.py --mode mock --input "ping" --output-json tmp/asf_openai_adapter_mock.json
```

## Required tests

```powershell
python -m pytest tests/unit/test_asf_openai_api_adapter.py tests/unit/test_asf_openai_api_adapter_docs.py
python -m pytest
python scripts/check_workflow_health.py
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git --no-pager diff --check
git --no-pager status --short
```

## Documentation to evaluate

- `docs/65_ASF_OPENAI_API_ADAPTER.md`
- `docs/66_ASF_OPENAI_API_ADAPTER_LIVE_BOUNDARY_CREDENTIAL_GATE.md`
- `docs/67_ASF_OPENAI_API_ADAPTER_FIRST_CONTROLLED_LIVE_SMOKE_TEST.md`
- `docs/34_PROJECT_WORKFLOW_INDEX.md`
- `docs/35_WORKFLOW_HEALTH_CHECK.md`
- `docs/36_WORKFLOW_QUICK_REFERENCE.md`
- `docs/38_WORKFLOW_COMMAND_COOKBOOK.md`
- `docs/39_WORKFLOW_STATUS_DASHBOARD.md`
- `README.md`
- `CHANGELOG.md`
- `docs/10_ROADMAP.md`
- `docs/11_DECISIONS.md`
- `docs/21_DOCUMENTATION_SYNC.md`
- `templates/codex_tasks/asf_openai_api_live_smoke_test_template.md`

## Final report

Use Italian and include:

- step eseguito;
- stato;
- branch corrente;
- file creati;
- file modificati;
- sintesi tecnica;
- sicurezza API key / live calls;
- test eseguiti;
- verifiche Git;
- vincoli rispettati;
- problemi aperti / warning;
- prossimo step consigliato.
