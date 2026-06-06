# ASF OpenAI API Live Boundary Gate Task Packet Template

## Step

```text
<STEP_NUMBER>) <TITLE>
```

Use this template for work that changes the OpenAI API Adapter live boundary, credential gate or future smoke-test prerequisites.

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

Describe the live-boundary change in one paragraph.

The default posture is deterministic, standard-library-only and no-network unless the step explicitly authorizes a controlled live smoke test.

## Safety constraints

- Do not call the OpenAI API unless the step explicitly authorizes a live smoke test.
- Do not require a real `OPENAI_API_KEY` in default tests.
- Do not paste API keys.
- Do not print, log, store, hash or partially reveal API key values.
- Do not include Authorization headers in docs, reports or fixtures.
- Do not add OpenAI SDK dependencies without explicit approval.
- Keep runtime artifacts under `tmp/`.
- Do not commit, push, open PRs, merge, tag or deploy.

## Required gate posture

For STEP 510, all gate checks produce reports only:

- `OPENAI_API_KEY` presence may be checked as a boolean;
- `ASF_OPENAI_LIVE_ENABLED=1` is required for future-live readiness;
- `--allow-live` is required for future-live readiness;
- `--live-confirm I_UNDERSTAND_THIS_CALLS_OPENAI_API` is required for future-live readiness;
- `network_performed` and `network_call_performed` must remain `false`.

Required decisions:

```text
CREDENTIAL_MISSING
LIVE_ENV_FLAG_MISSING
LIVE_FLAG_MISSING
LIVE_CONFIRMATION_MISSING
LIVE_READY_FOR_SEPARATE_SMOKE_STEP
LIVE_CALLS_NOT_IMPLEMENTED_IN_STEP_510
```

## Example commands

```powershell
python scripts/asf_openai_api_adapter.py --mode live --input "ping" --output-json tmp/asf_openai_live_boundary_gate_missing_credential.json
$env:OPENAI_API_KEY = "<set locally, never paste into chat or commit>"
$env:ASF_OPENAI_LIVE_ENABLED = "1"
python scripts/asf_openai_api_adapter.py --mode live --input "ping" --allow-live --live-confirm I_UNDERSTAND_THIS_CALLS_OPENAI_API --output-json tmp/asf_openai_live_boundary_gate_ready.json
```

## Required tests

```powershell
python -m pytest tests/unit/test_asf_openai_api_adapter.py tests/unit/test_asf_openai_api_adapter_docs.py tests/unit/test_asf_openai_api_adapter_live_boundary_gate.py tests/unit/test_asf_openai_api_adapter_live_boundary_docs.py
python -m pytest
python scripts/check_workflow_health.py
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git --no-pager diff --check
git --no-pager status --short
```

## Documentation to evaluate

- `docs/66_ASF_OPENAI_API_ADAPTER_LIVE_BOUNDARY_CREDENTIAL_GATE.md`
- `docs/65_ASF_OPENAI_API_ADAPTER.md`
- `docs/64_ASF_PWSH_COMMAND_PACK_SKILL_HARDENING.md`
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
- sicurezza API key / live boundary;
- test eseguiti;
- verifiche Git;
- vincoli rispettati;
- problemi aperti / warning;
- prossimo step consigliato.
