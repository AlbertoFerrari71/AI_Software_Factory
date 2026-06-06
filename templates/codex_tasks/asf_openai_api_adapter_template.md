# ASF OpenAI API Adapter Task Packet Template

## Step

```text
<STEP_NUMBER>) <TITLE>
```

Use STEP 500 for the adapter foundation already implemented here. Use the next gated step only when the live boundary and credential rules are explicit:

```text
510) OpenAI API Adapter Live Boundary and Credential Gate
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

- Do not make live API calls unless the step explicitly authorizes a live boundary.
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
- Fail closed for live mode until a future gated step.

Required fail-closed marker:

```text
LIVE_MODE_NOT_IMPLEMENTED_IN_STEP_500
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
