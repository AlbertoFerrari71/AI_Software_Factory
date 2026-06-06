# ASF OpenAI API Adapter

## 1. Purpose

STEP 500 introduces a local-first OpenAI API Adapter foundation for ASF.

The adapter builds deterministic Responses-style payloads, validates model and response-shaping settings, checks local environment readiness without exposing secrets, and produces dry-run or mock JSON evidence.

This step makes no live API calls and does not execute live OpenAI API calls.

---

## 2. Why Responses-style payloads

OpenAI recommends the Responses API for new projects, while Chat Completions remains supported. ASF therefore stores the new adapter contract around a Responses-style payload:

```json
{
  "model": "gpt-5.5",
  "input": "ping",
  "instructions": "optional instructions",
  "reasoning": {
    "effort": "medium"
  },
  "text": {
    "verbosity": "medium"
  }
}
```

The adapter keeps the structure small and explicit so future steps can add a credential gate, live boundary and schema checks without rewriting the dry-run and mock foundation.

The official documentation facts used for this design were supplied in the STEP 500 task packet. This step did not fetch remote documentation and did not use network.

---

## 3. Implemented surface

Script:

```text
scripts/asf_openai_api_adapter.py
```

Supported modes:

- `check-env`;
- `dry-run`;
- `mock`;
- `live`, fail-closed placeholder only.

Supported reasoning efforts:

```text
none
low
medium
high
xhigh
```

Supported text verbosity values:

```text
low
medium
high
```

Default model:

```text
gpt-5.5
```

---

## 4. Security rules

`OPENAI_API_KEY` may be checked for presence only.

Rules:

- Do not paste API keys into prompts, CLI arguments, docs, tests or fixtures.
- Do not print, log, store or commit API key values.
- Load future credentials from environment variables or a secret manager, not from client-side code or repository files.
- `check-env` reports only `openai_api_key_present: true` or `false`.
- Any string resembling an OpenAI API key is redacted from JSON output.
- No OpenAI SDK is required.
- No network call is made.

Safe environment evidence shape:

```json
{
  "environment": {
    "openai_api_key_present": false
  },
  "network_performed": false,
  "status": "ENV_CHECK"
}
```

---

## 5. Dry-run examples

Check environment readiness without requiring a key:

```powershell
python scripts/asf_openai_api_adapter.py --mode check-env --output-json tmp/asf_openai_adapter_env.json
```

Build a payload and write deterministic JSON evidence:

```powershell
python scripts/asf_openai_api_adapter.py --mode dry-run --input "ping" --output-json tmp/asf_openai_adapter_dry_run.json
```

Expected core evidence:

```json
{
  "status": "DRY_RUN",
  "network_performed": false,
  "payload": {
    "model": "gpt-5.5",
    "input": "ping",
    "reasoning": {
      "effort": "medium"
    },
    "text": {
      "verbosity": "medium"
    }
  }
}
```

---

## 6. Mock examples

Generate deterministic mock content:

```powershell
python scripts/asf_openai_api_adapter.py --mode mock --input "ping" --output-json tmp/asf_openai_adapter_mock.json
```

The mock mode returns:

- `status: MOCK_RESPONSE`;
- `network_performed: false`;
- stable `mock_output_text`;
- input length;
- a stable short SHA-256 checksum.

This is enough for unit tests and downstream workflow checks without external services.

---

## 7. Live API boundary

Live mode is intentionally not implemented in STEP 500.

If selected, it fails closed with:

```text
LIVE_MODE_NOT_IMPLEMENTED_IN_STEP_500
```

The future live path must be a separate human-gated step. It must define:

- credential source and redaction checks;
- explicit stop conditions;
- no secret logging;
- request/response capture boundaries;
- network permission and failure classification;
- tests that do not require real credentials by default.

Recommended next step:

```text
510) OpenAI API Adapter Live Boundary and Credential Gate
```

---

## 8. Tests and verification

Focused tests:

```powershell
python -m pytest tests/unit/test_asf_openai_api_adapter.py tests/unit/test_asf_openai_api_adapter_docs.py
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

- OpenAI SDK;
- network;
- `OPENAI_API_KEY`;
- real external services.

---

## 9. Decision

STEP 500 creates the adapter foundation only.

It is acceptable to build payloads, validate settings, check whether `OPENAI_API_KEY` is present, redact key-like strings, and produce dry-run/mock JSON evidence.

It is not acceptable in this step to make live API calls, add SDK dependencies, require credentials, print secrets, or treat mock success as production readiness.
