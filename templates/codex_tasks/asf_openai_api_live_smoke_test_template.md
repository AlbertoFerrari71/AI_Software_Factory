# ASF OpenAI API Live Smoke Test Task Packet Template

## Step

```text
<STEP_NUMBER>) <TITLE>
```

Use this template only for a controlled OpenAI API adapter live smoke test or its hardening follow-up.

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

Describe the exact live smoke or result-hardening change in one paragraph.

The default posture is deterministic and no-network unless all live gates are explicitly present.

For result-hardening steps, Codex must use mocked tests only and must not execute a real live OpenAI API call.

## Mandatory live gates

- `OPENAI_API_KEY` must exist in the local process environment.
- `ASF_OPENAI_LIVE_ENABLED=1` must exist in the local process environment.
- `--allow-live` must be present.
- `--live-confirm I_UNDERSTAND_THIS_CALLS_OPENAI_API` must be present.
- The prompt must be exactly `Return exactly ASF_OPENAI_LIVE_SMOKE_OK.`
- The request must use `store: false`.
- Runtime artifacts must stay under `tmp/`.
- API key values must never be printed, logged, stored, hashed, truncated or fingerprinted.
- Result artifacts may report credential presence only as a boolean.

## Safety constraints

- Do not ask Alberto to paste an API key into chat or a tracked file.
- Do not include Authorization headers in docs, reports or fixtures.
- Do not add OpenAI SDK dependencies without explicit approval.
- Do not send private, business, customer, source-code or repository contents.
- Do not perform more than one live API request.
- Do not retry automatically.
- Do not commit, push, open PRs, merge, tag or deploy.

## Preflight command

```powershell
python scripts/asf_openai_api_adapter.py --mode live --gate-only --allow-live --live-confirm I_UNDERSTAND_THIS_CALLS_OPENAI_API --input "Return exactly ASF_OPENAI_LIVE_SMOKE_OK." --reasoning-effort none --text-verbosity low --max-output-tokens 32 --output-json tmp/asf_openai_live_smoke_gate.json
```

Proceed only when the decision is:

```text
LIVE_SMOKE_READY_FOR_CALL
```

## One-call live command

```powershell
python scripts/asf_openai_api_adapter.py --mode live --allow-live --live-confirm I_UNDERSTAND_THIS_CALLS_OPENAI_API --input "Return exactly ASF_OPENAI_LIVE_SMOKE_OK." --reasoning-effort none --text-verbosity low --max-output-tokens 32 --output-json tmp/asf_openai_live_smoke_result.json --output-markdown tmp/asf_openai_live_smoke_result.md
```

## Required classifications

```text
LIVE_SMOKE_EXECUTED_AND_PASSED
LIVE_SMOKE_EXECUTED_BUT_FAILED
LIVE_SMOKE_NOT_RUN_MISSING_GATE
LIVE_SMOKE_NOT_RUN_NETWORK_BLOCKED
LIVE_SMOKE_UNEXPECTED_MODEL_OUTPUT
LIVE_SMOKE_HTTP_ERROR
LIVE_SMOKE_INVALID_JSON
LIVE_SMOKE_MISSING_SUCCESS_EVIDENCE
```

STEP 530 result hardening also requires the stable lowercase classifications:

```text
not_configured
disabled
credential_missing
live_not_allowed
success
provider_error
network_error
rate_limited
auth_error
schema_error
unknown_error
```

## Required tests

```powershell
python -m pytest tests/unit/test_asf_openai_api_adapter.py tests/unit/test_asf_openai_api_adapter_docs.py tests/unit/test_asf_openai_api_adapter_live_boundary_gate.py tests/unit/test_asf_openai_api_adapter_live_boundary_docs.py tests/unit/test_asf_openai_api_adapter_live_smoke.py tests/unit/test_asf_openai_api_adapter_live_smoke_docs.py tests/unit/test_asf_openai_api_adapter_live_smoke_result_hardening_docs.py
python -m pytest
python scripts/check_workflow_health.py
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git --no-pager diff --check
git --no-pager status --short
```

## Documentation to evaluate

- `docs/67_ASF_OPENAI_API_ADAPTER_FIRST_CONTROLLED_LIVE_SMOKE_TEST.md`
- `docs/68_ASF_OPENAI_API_ADAPTER_LIVE_SMOKE_RESULT_HARDENING.md`
- `docs/66_ASF_OPENAI_API_ADAPTER_LIVE_BOUNDARY_CREDENTIAL_GATE.md`
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
- sicurezza API key / live call;
- live smoke test;
- test eseguiti;
- verifiche Git;
- vincoli rispettati;
- problemi aperti / warning;
- prossimo step consigliato.
