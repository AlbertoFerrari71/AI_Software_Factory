# ASF OpenAI API Adapter Live Boundary Credential Gate

## 1. Purpose

STEP 510 adds a deterministic live boundary and credential gate to the ASF OpenAI API Adapter.

The goal is to prepare a future controlled live smoke test without performing any live OpenAI API call in this step.

The later controlled live smoke test is documented in `docs/67_ASF_OPENAI_API_ADAPTER_FIRST_CONTROLLED_LIVE_SMOKE_TEST.md`.

The result hardening step is documented in `docs/68_ASF_OPENAI_API_ADAPTER_LIVE_SMOKE_RESULT_HARDENING.md`.

This step preserves the local-first adapter foundation from STEP 500:

- Responses-style request planning;
- default model `gpt-5.5`;
- standard-library-only implementation;
- no OpenAI SDK dependency;
- no network calls;
- no requirement for a real `OPENAI_API_KEY` in tests.

---

## 2. Implemented surface

The live boundary is implemented in:

```text
scripts/asf_openai_api_adapter.py
```

The adapter still supports:

- `check-env`;
- `dry-run`;
- `mock`;
- `live`.

In STEP 510, `live` produces a gate report only. It does not call OpenAI.

---

## 3. Credential gate

The credential gate checks only whether this environment variable is present:

```text
OPENAI_API_KEY
```

It reports only sanitized facts:

```json
{
  "credential_source": "OPENAI_API_KEY",
  "openai_api_key_present": true,
  "secret_value_logged": false
}
```

When the credential is absent, the decision is:

```text
CREDENTIAL_MISSING
```

The gate must never print, log, hash, fingerprint, truncate, store or reveal any API key value.

---

## 4. Live boundary gates

STEP 510 requires all of these signals before it classifies the system as ready for a separate future live smoke test:

- `OPENAI_API_KEY` is present in the process environment;
- `ASF_OPENAI_LIVE_ENABLED=1` is present in the process environment;
- CLI flag `--allow-live` is present;
- CLI confirmation is exactly:

```text
I_UNDERSTAND_THIS_CALLS_OPENAI_API
```

The command shape is:

```powershell
python scripts/asf_openai_api_adapter.py --mode live --input "ping" --allow-live --live-confirm I_UNDERSTAND_THIS_CALLS_OPENAI_API --output-json tmp/asf_openai_live_boundary_gate.json
```

Even when all gates are present, STEP 510 does not perform a live call.

---

## 5. Decisions

The live boundary report uses deterministic decisions:

```text
LIVE_DISABLED_BY_DEFAULT
CREDENTIAL_MISSING
LIVE_ENV_FLAG_MISSING
LIVE_FLAG_MISSING
LIVE_CONFIRMATION_MISSING
LIVE_READY_FOR_SEPARATE_SMOKE_STEP
LIVE_CALLS_NOT_IMPLEMENTED_IN_STEP_510
```

Decision order:

1. missing `OPENAI_API_KEY` -> `CREDENTIAL_MISSING`;
2. missing `ASF_OPENAI_LIVE_ENABLED=1` -> `LIVE_ENV_FLAG_MISSING`;
3. missing `--allow-live` -> `LIVE_FLAG_MISSING`;
4. missing or wrong `--live-confirm` -> `LIVE_CONFIRMATION_MISSING`;
5. all gates present -> `LIVE_READY_FOR_SEPARATE_SMOKE_STEP`.

The report also includes:

```json
{
  "live_call_status": "LIVE_CALLS_NOT_IMPLEMENTED_IN_STEP_510",
  "network_call_performed": false,
  "network_performed": false
}
```

---

## 6. Live request plan

The live request plan is no-network metadata for the future smoke step:

```json
{
  "api_surface": "responses",
  "endpoint": "/v1/responses",
  "model": "gpt-5.5",
  "store": false,
  "network_call_performed": false
}
```

The plan must not include:

- Authorization headers;
- API key values;
- key length;
- key prefix or suffix;
- key hash or fingerprint;
- environment dumps.

---

## 7. Redaction

The adapter redacts obvious OpenAI-key-like and secret-like strings before output.

Redaction applies to:

- JSON output;
- output files written through `--output-json`;
- payload previews;
- mock or dry-run payloads;
- visible error text.

The adapter may report that a credential exists, but must not reveal the credential.

---

## 8. PowerShell setup note

Do not use persistent `setx` commands for OpenAI credentials in project docs or task packets.

For a temporary local session, use:

```powershell
$env:OPENAI_API_KEY = "<set locally, never paste into chat or commit>"
```

For a permanent user-scoped variable, use a local command with a placeholder only:

```powershell
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "<set locally, never paste into chat or commit>", "User")
```

Never place a real key in this repository, in a prompt, in logs, in docs, or in a committed file.

---

## 9. Verification

Focused tests:

```powershell
python -m pytest tests/unit/test_asf_openai_api_adapter.py tests/unit/test_asf_openai_api_adapter_docs.py tests/unit/test_asf_openai_api_adapter_live_boundary_gate.py tests/unit/test_asf_openai_api_adapter_live_boundary_docs.py
```

Full local checks:

```powershell
python -m pytest
python scripts/check_workflow_health.py
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git --no-pager diff --check
git --no-pager status --short
```

The tests must not require:

- real `OPENAI_API_KEY`;
- OpenAI SDK;
- network;
- external services.

---

## 10. Out of scope

STEP 510 does not:

- call the OpenAI API;
- introduce OpenAI SDK dependencies;
- require real credentials;
- run a live smoke test;
- store secret values;
- authorize production readiness.

The next step is:

```text
520) OpenAI API Adapter First Controlled Live Smoke Test
```

STEP 520 is documented in `docs/67_ASF_OPENAI_API_ADAPTER_FIRST_CONTROLLED_LIVE_SMOKE_TEST.md`.
