# ASF OpenAI API Adapter Live Smoke Result Hardening

## 1. Purpose

STEP 530 hardens the result contract for the ASF OpenAI API Adapter live smoke path before any further real live test.

This step does not execute live OpenAI API calls. It uses mocked tests only.

The live smoke remains fail-closed:

- missing or incomplete gates skip execution;
- provider, network, schema and unknown errors are classified;
- JSON artifacts are machine-readable;
- optional Markdown artifacts are operator-readable;
- secrets are never printed, saved, hashed, truncated, fingerprinted or serialized.

---

## 2. Stable live result schema

Live mode now emits a stable result contract with these fields:

```json
{
  "status": "success|failed|skipped",
  "classification": "not_configured|disabled|credential_missing|live_not_allowed|success|provider_error|network_error|rate_limited|auth_error|schema_error|unknown_error",
  "message": "safe human readable message",
  "safe_details": {},
  "provider": "openai",
  "model": "safe model name if configured",
  "live_enabled": false,
  "credential_present": false,
  "duration_ms": 0,
  "timestamp": "ISO-8601 timestamp"
}
```

Compatibility fields from STEP 520 are still present, including `decision`, `error_category`, `network_call_attempted`, `network_call_performed`, `network_call_count`, `store`, `runtime_artifact_path`, `output_text_present` and `expected_marker_found`.

The previous live status marker is preserved as:

```json
{
  "legacy_status": "LIVE_SMOKE"
}
```

---

## 3. Classifications

| Classification | Meaning |
|---|---|
| `not_configured` | Live configuration is incomplete, including a missing live env flag or invalid smoke prompt. |
| `disabled` | Live smoke is intentionally disabled, including gate-only preflight. |
| `credential_missing` | `OPENAI_API_KEY` is absent. |
| `live_not_allowed` | CLI authorization, confirmation or required runtime artifact is missing. |
| `success` | Mocked or real live smoke result satisfies the success contract. |
| `provider_error` | Provider/API returned a non-success status that is not auth or rate limit. |
| `network_error` | Network, timeout or connection failure. |
| `rate_limited` | Provider returned rate limit status. |
| `auth_error` | Provider returned authentication or authorization status. |
| `schema_error` | Provider response is invalid JSON or does not satisfy the response contract. |
| `unknown_error` | Controlled fallback for unexpected local errors. |

---

## 4. Artifact rules

JSON evidence remains the machine-readable artifact.

For live mode, JSON output must stay under `tmp/` before any network call can be attempted:

```powershell
python scripts/asf_openai_api_adapter.py --mode live --gate-only --allow-live --live-confirm I_UNDERSTAND_THIS_CALLS_OPENAI_API --input "Return exactly ASF_LIVE_SMOKE_OK." --reasoning-effort none --text-verbosity low --max-output-tokens 32 --output-json tmp/asf_openai_live_smoke_gate.json --output-markdown tmp/asf_openai_live_smoke_gate.md
```

The optional Markdown summary is also restricted to `tmp/` for live mode. It contains only safe fields:

- status;
- classification;
- provider;
- model;
- live gate state;
- credential presence as a boolean;
- network attempt/performed booleans;
- decision;
- safe message;
- recommended operator next step;
- `safe_details`.

---

## 5. Secret handling

The adapter may report only boolean credential presence:

```json
{
  "credential_present": true
}
```

It must not emit:

- API key value;
- API key length;
- prefix or suffix;
- hash;
- fingerprint;
- serialized key material;
- authorization header values.

This applies to console output, JSON artifacts, Markdown artifacts, logs and test artifacts.

---

## 6. Mocked verification scope

STEP 530 tests classify all required cases without network and without real credentials:

- live disabled;
- missing credential;
- missing live gate;
- live gate different from `1`;
- incomplete live smoke configuration;
- mocked success;
- mocked auth error;
- mocked rate limit;
- mocked provider error;
- mocked network or timeout error;
- mocked schema error;
- mocked unknown error;
- no visible API key or secret-derived fields in reports.

---

## 7. Future live execution

STEP 530 does not authorize another real live smoke.

A future real live execution requires the STEP 540 controlled live execution pack, a separate task packet, explicit human approval, local gate setup, `store: false`, artifact paths under `tmp/`, and tests passing before the run.

Codex must not execute live OpenAI API tests unless a future step explicitly authorizes that live execution.

STEP 540 is documented in `docs/69_ASF_OPENAI_API_ADAPTER_CONTROLLED_LIVE_EXECUTION_PACK.md`.

---

## 8. Verification

Focused tests:

```powershell
python -m pytest tests/unit/test_asf_openai_api_adapter.py tests/unit/test_asf_openai_api_adapter_docs.py tests/unit/test_asf_openai_api_adapter_live_boundary_gate.py tests/unit/test_asf_openai_api_adapter_live_boundary_docs.py tests/unit/test_asf_openai_api_adapter_live_smoke.py tests/unit/test_asf_openai_api_adapter_live_smoke_docs.py tests/unit/test_asf_openai_api_adapter_live_smoke_result_hardening_docs.py
```

Full local checks:

```powershell
python -m pytest
python scripts/check_workflow_health.py
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git --no-pager diff --check
git --no-pager status --short
```

Default tests must not require network, real credentials or live OpenAI calls.

---

## 9. Next step

```text
550) OpenAI API Adapter First Authorized Live Run
```
