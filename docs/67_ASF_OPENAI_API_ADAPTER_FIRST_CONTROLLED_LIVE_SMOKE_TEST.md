# ASF OpenAI API Adapter First Controlled Live Smoke Test

## 1. Purpose

STEP 520 adds the first controlled live smoke path for the ASF OpenAI API Adapter.

The live smoke is intentionally narrow:

- one Responses API request at most;
- tiny non-sensitive prompt only;
- local environment gates required;
- `store: false` mandatory;
- sanitized JSON evidence under `tmp/`;
- no OpenAI SDK dependency.

This is not a production integration. It is a controlled adapter smoke test for verifying the live boundary introduced in STEP 510.

---

## 2. Mandatory gates

The adapter may attempt the live smoke only when all gates are present:

1. `OPENAI_API_KEY` exists in the local process environment.
2. `ASF_OPENAI_LIVE_ENABLED=1` exists in the local process environment.
3. CLI flag `--allow-live` is present.
4. CLI flag `--live-confirm I_UNDERSTAND_THIS_CALLS_OPENAI_API` is present.
5. The prompt is exactly:

```text
Return exactly ASF_LIVE_SMOKE_OK.
```

6. The request payload includes `store: false`.
7. Runtime output is written only under `tmp/`.
8. The API key value is never printed, logged, hashed, truncated, fingerprinted or persisted.

If any gate is missing, the adapter does not call the API and reports `LIVE_SMOKE_NOT_RUN_MISSING_GATE`.

---

## 3. Credential setup

Do not paste API keys in chat, task packets, docs, tests, logs or tracked files.

For a temporary PowerShell session, set the key locally with a placeholder command and replace the placeholder only in your shell:

```powershell
$env:OPENAI_API_KEY = "<your local OpenAI API key>"
```

Enable the live smoke gate only for the same session:

```powershell
$env:ASF_OPENAI_LIVE_ENABLED = "1"
```

The adapter reports only whether the key is present. It never emits the key value or any derivative.

---

## 4. Gate-only preflight

Before a live call, run a gate-only command:

```powershell
python scripts/asf_openai_api_adapter.py --mode live --gate-only --allow-live --live-confirm I_UNDERSTAND_THIS_CALLS_OPENAI_API --input "Return exactly ASF_LIVE_SMOKE_OK." --reasoning-effort none --text-verbosity low --max-output-tokens 32 --output-json tmp/asf_openai_live_smoke_gate.json
```

Expected preflight decisions:

- `LIVE_SMOKE_NOT_RUN_MISSING_GATE`: one or more gates are absent; do not run the live call.
- `LIVE_SMOKE_READY_FOR_CALL`: all gates are present; gate-only mode still performs no network call.

The gate report must include:

```json
{
  "mode": "live",
  "network_call_attempted": false,
  "network_call_performed": false,
  "network_call_count": 0,
  "store": false,
  "secret_value_logged": false
}
```

---

## 5. One-call live smoke command

Run this command only after local tests pass and the gate-only preflight reports `LIVE_SMOKE_READY_FOR_CALL`:

```powershell
python scripts/asf_openai_api_adapter.py --mode live --allow-live --live-confirm I_UNDERSTAND_THIS_CALLS_OPENAI_API --input "Return exactly ASF_LIVE_SMOKE_OK." --reasoning-effort none --text-verbosity low --max-output-tokens 32 --output-json tmp/asf_openai_live_smoke_result.json
```

The request target is:

```text
POST https://api.openai.com/v1/responses
```

The payload includes:

```json
{
  "model": "gpt-5.5",
  "input": "Return exactly ASF_LIVE_SMOKE_OK.",
  "store": false,
  "max_output_tokens": 32,
  "text": {
    "verbosity": "low"
  },
  "reasoning": {
    "effort": "none"
  }
}
```

The expected cost is non-zero but minimal because the prompt and output budget are intentionally tiny.

Do not retry automatically. A second live request requires a separate human decision.

---

## 6. Result contract

After STEP 530, the live result or gate result includes a stable schema:

```json
{
  "status": "success|failed|skipped",
  "classification": "not_configured|disabled|credential_missing|live_not_allowed|success|provider_error|network_error|rate_limited|auth_error|schema_error|unknown_error",
  "safe_details": {},
  "provider": "openai",
  "credential_present": false
}
```

The live result also preserves STEP 520 compatibility fields:

```text
mode
decision
network_call_attempted
network_call_performed
network_call_count
store
model
openai_api_key_present
secret_value_logged
runtime_artifact_path
output_text_present
expected_marker_found
error_category
```

`error_category` is present when the live smoke is not run or does not pass.

The smoke passes only when:

- HTTP status is successful;
- response JSON parses;
- a response id or equivalent minimal success evidence exists;
- extracted output text contains `ASF_LIVE_SMOKE_OK`;
- `store` is false;
- exactly one network request was attempted;
- no secret value is printed or persisted;
- runtime artifact path is under `tmp/`.

---

## 7. Failure classifications

The adapter classifies expected failure modes without exposing secrets:

```text
LIVE_SMOKE_NOT_RUN_MISSING_GATE
LIVE_SMOKE_NOT_RUN_NETWORK_BLOCKED
LIVE_SMOKE_UNEXPECTED_MODEL_OUTPUT
LIVE_SMOKE_HTTP_ERROR
LIVE_SMOKE_INVALID_JSON
LIVE_SMOKE_MISSING_SUCCESS_EVIDENCE
```

STEP 530 maps these legacy categories to stable lowercase classifications:

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

If network is blocked by the execution environment, report `LIVE_SMOKE_NOT_RUN_NETWORK_BLOCKED`; this is not an adapter crash.

If the API returns valid JSON with different output text, report `LIVE_SMOKE_UNEXPECTED_MODEL_OUTPUT`.

---

## 8. Verification

Focused deterministic tests:

```powershell
python -m pytest tests/unit/test_asf_openai_api_adapter.py tests/unit/test_asf_openai_api_adapter_docs.py tests/unit/test_asf_openai_api_adapter_live_boundary_gate.py tests/unit/test_asf_openai_api_adapter_live_boundary_docs.py tests/unit/test_asf_openai_api_adapter_live_smoke.py tests/unit/test_asf_openai_api_adapter_live_smoke_docs.py
```

Full local checks:

```powershell
python -m pytest
python scripts/check_workflow_health.py
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git --no-pager diff --check
git --no-pager status --short
```

Default tests must not require a real API key or network.

---

## 9. Out of scope

STEP 520 does not:

- add an OpenAI SDK dependency;
- persist credentials;
- send repository, customer, business or source-code content;
- perform retries;
- enable production integration;
- authorize commit, push, PR, merge, tag or deploy.

The next recommended step is:

```text
540) OpenAI API Adapter Controlled Live Execution Pack
```

STEP 530 is documented in `docs/68_ASF_OPENAI_API_ADAPTER_LIVE_SMOKE_RESULT_HARDENING.md`.
